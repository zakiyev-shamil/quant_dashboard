"""
QuantLab Lite — Data Service

Handles all data operations: downloading from yfinance, storing in PostgreSQL,
loading, updating, and validation.

Covers spec Section 1 (items 1–16).
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Sequence

import numpy as np
import pandas as pd
import yfinance as yf
from sqlalchemy import text

from app.core.config import DEFAULT_TICKERS, DEFAULT_INTERVAL
from app.core.database import get_engine
from app.core.exceptions import (
    TickerNotFoundError,
    DataNotAvailableError,
    InvalidDateRangeError,
    InsufficientDataError,
)
from app.models.schemas import DataStatus, ValidationReport
from app.utils.validation import validate_ticker, validate_date_range, validate_interval
from app.utils.dates import sync_dates, find_date_gaps

logger = logging.getLogger(__name__)


class DataService:
    """
    Service for managing price data.

    Downloads OHLCV data from yfinance, stores it in PostgreSQL,
    and provides retrieval and validation utilities.
    """

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    @staticmethod
    def download_prices(
        symbol: str,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Download historical OHLCV data from yfinance.

        Parameters
        ----------
        symbol : str
            Ticker symbol (e.g. "SPY", "BTC-USD").
        start_date : date or str or None
            Start of the period. None = max available.
        end_date : date or str or None
            End of the period. None = today.
        interval : str
            Data interval (e.g. "1d", "1h", "1wk").

        Returns
        -------
        pd.DataFrame
            Cleaned DataFrame with columns:
            [open, high, low, close, adjusted_close, volume, symbol, source]
            and DatetimeIndex named 'date'.
        """
        symbol = validate_ticker(symbol)
        validate_interval(interval)
        start_date, end_date = validate_date_range(start_date, end_date)

        logger.info(f"Downloading {symbol} [{interval}] from {start_date} to {end_date}")

        # Download from yfinance
        ticker = yf.Ticker(symbol)
        kwargs = {"interval": interval, "auto_adjust": False}
        if start_date:
            kwargs["start"] = str(start_date)
        if end_date:
            kwargs["end"] = str(end_date)
        if not start_date and not end_date:
            kwargs["period"] = "max"

        df = ticker.history(**kwargs)

        if df.empty:
            raise TickerNotFoundError(
                symbol,
                f"No data returned for '{symbol}'. Check if the ticker is valid.",
            )

        # Standardize column names
        df = DataService._standardize_columns(df, symbol)

        logger.info(f"Downloaded {len(df)} rows for {symbol}")
        return df

    @staticmethod
    def download_multiple(
        symbols: Sequence[str],
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        interval: str = "1d",
    ) -> dict[str, pd.DataFrame]:
        """
        Download data for multiple symbols.

        Returns
        -------
        dict[str, pd.DataFrame]
            Mapping of symbol → DataFrame.
        """
        result = {}
        errors = []

        for symbol in symbols:
            try:
                df = DataService.download_prices(symbol, start_date, end_date, interval)
                result[symbol] = df
            except Exception as e:
                logger.warning(f"Failed to download {symbol}: {e}")
                errors.append((symbol, str(e)))

        if errors and not result:
            raise DataNotAvailableError(
                ", ".join(s for s, _ in errors),
                f"Failed to download any data. Errors: {errors}",
            )

        return result

    # ------------------------------------------------------------------
    # Save / Load (PostgreSQL)
    # ------------------------------------------------------------------

    @staticmethod
    def save_prices(symbol: str, df: pd.DataFrame, interval: str = "1d") -> int:
        """
        Save price data to PostgreSQL.

        Uses INSERT ... ON CONFLICT to upsert (update existing rows).

        Parameters
        ----------
        symbol : str
            Ticker symbol.
        df : pd.DataFrame
            Price data with standardized columns.
        interval : str
            Data interval.

        Returns
        -------
        int
            Number of rows saved.
        """
        symbol = symbol.upper()
        engine = get_engine()

        # Prepare data for insertion
        records = []
        for idx, row in df.iterrows():
            dt = idx
            if isinstance(dt, pd.Timestamp):
                dt = dt.date()

            records.append({
                "symbol": symbol,
                "date": dt,
                "interval": interval,
                "open": float(row["open"]) if pd.notna(row["open"]) else None,
                "high": float(row["high"]) if pd.notna(row["high"]) else None,
                "low": float(row["low"]) if pd.notna(row["low"]) else None,
                "close": float(row["close"]) if pd.notna(row["close"]) else None,
                "adjusted_close": float(row["adjusted_close"]) if pd.notna(row["adjusted_close"]) else None,
                "volume": int(row["volume"]) if pd.notna(row["volume"]) else None,
                "source": row.get("source", "yfinance"),
            })

        if not records:
            return 0

        # Upsert using ON CONFLICT
        upsert_sql = text("""
            INSERT INTO prices (symbol, date, interval, open, high, low, close, adjusted_close, volume, source)
            VALUES (:symbol, :date, :interval, :open, :high, :low, :close, :adjusted_close, :volume, :source)
            ON CONFLICT (symbol, date, interval)
            DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                adjusted_close = EXCLUDED.adjusted_close,
                volume = EXCLUDED.volume,
                source = EXCLUDED.source
        """)

        with engine.begin() as conn:
            conn.execute(upsert_sql, records)

        # Update data_status
        DataService._update_status(symbol, interval)

        logger.info(f"Saved {len(records)} rows for {symbol} [{interval}]")
        return len(records)

    @staticmethod
    def load_prices(
        symbol: str,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Load price data from PostgreSQL.

        Parameters
        ----------
        symbol : str
            Ticker symbol.
        start_date : date or str or None
            Start filter.
        end_date : date or str or None
            End filter.
        interval : str
            Data interval filter.

        Returns
        -------
        pd.DataFrame
            Price data with DatetimeIndex.

        Raises
        ------
        DataNotAvailableError
            If no data is found for the symbol.
        """
        symbol = symbol.upper()
        engine = get_engine()

        query = "SELECT date, open, high, low, close, adjusted_close, volume, source FROM prices WHERE symbol = :symbol AND interval = :interval"
        params = {"symbol": symbol, "interval": interval}

        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            query += " AND date >= :start_date"
            params["start_date"] = start_date

        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            query += " AND date <= :end_date"
            params["end_date"] = end_date

        query += " ORDER BY date ASC"

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params, parse_dates=["date"])

        if df.empty:
            raise DataNotAvailableError(symbol)

        df.set_index("date", inplace=True)
        df["symbol"] = symbol
        df.index.name = "date"

        return df

    @staticmethod
    def load_multiple(
        symbols: Sequence[str],
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        interval: str = "1d",
        sync: bool = True,
    ) -> dict[str, pd.DataFrame]:
        """
        Load data for multiple symbols, optionally synchronizing dates.

        Parameters
        ----------
        symbols : Sequence[str]
            List of ticker symbols.
        sync : bool
            If True, synchronize dates (inner join).

        Returns
        -------
        dict[str, pd.DataFrame]
        """
        result = {}
        for symbol in symbols:
            result[symbol] = DataService.load_prices(symbol, start_date, end_date, interval)

        if sync and len(result) > 1:
            result = sync_dates(result)

        return result

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    @staticmethod
    def update_prices(symbol: str, interval: str = "1d") -> pd.DataFrame:
        """
        Update data for a symbol by downloading only new data since the last stored date.

        Returns
        -------
        pd.DataFrame
            The newly downloaded data.
        """
        symbol = symbol.upper()
        status = DataService.get_symbol_status(symbol, interval)

        if status and status.last_date:
            # Download from day after last stored date
            from datetime import timedelta
            start = status.last_date + timedelta(days=1)
            if start >= date.today():
                logger.info(f"{symbol} is already up to date")
                return pd.DataFrame()
        else:
            start = None

        df = DataService.download_prices(symbol, start_date=start, interval=interval)
        if not df.empty:
            DataService.save_prices(symbol, df, interval)

        return df

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_prices(df: pd.DataFrame) -> ValidationReport:
        """
        Run validation checks on price data.

        Checks:
        - Missing values per column
        - Duplicate dates
        - Negative prices
        - Date gaps (business days)

        Parameters
        ----------
        df : pd.DataFrame
            Price data with DatetimeIndex.

        Returns
        -------
        ValidationReport
        """
        symbol = df["symbol"].iloc[0] if "symbol" in df.columns and len(df) > 0 else "unknown"
        issues = []

        # Missing values
        price_cols = ["open", "high", "low", "close", "adjusted_close", "volume"]
        missing = {}
        for col in price_cols:
            if col in df.columns:
                n_missing = int(df[col].isna().sum())
                if n_missing > 0:
                    missing[col] = n_missing
                    issues.append(f"{col}: {n_missing} missing values")

        # Duplicate dates
        dupes = int(df.index.duplicated().sum())
        if dupes > 0:
            issues.append(f"{dupes} duplicate dates")

        # Negative prices
        neg_count = 0
        for col in ["open", "high", "low", "close", "adjusted_close"]:
            if col in df.columns:
                neg = int((df[col] < 0).sum())
                neg_count += neg
        if neg_count > 0:
            issues.append(f"{neg_count} negative price values")

        # Date gaps
        if isinstance(df.index, pd.DatetimeIndex) and len(df) > 1:
            gaps = find_date_gaps(df.index)
            n_gaps = len(gaps)
        else:
            n_gaps = 0
        if n_gaps > 0:
            issues.append(f"{n_gaps} missing business days")

        return ValidationReport(
            symbol=symbol,
            total_rows=len(df),
            missing_values=missing,
            duplicate_dates=dupes,
            negative_prices=neg_count,
            date_gaps=n_gaps,
            is_valid=len(issues) == 0,
            issues=issues,
        )

    # ------------------------------------------------------------------
    # Status & Info
    # ------------------------------------------------------------------

    @staticmethod
    def get_symbol_status(symbol: str, interval: str = "1d") -> DataStatus | None:
        """Get the data status for a symbol from the data_status table."""
        symbol = symbol.upper()
        engine = get_engine()

        query = text("""
            SELECT symbol, interval, first_date, last_date, row_count, last_updated, source
            FROM data_status
            WHERE symbol = :symbol AND interval = :interval
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {"symbol": symbol, "interval": interval}).fetchone()

        if result is None:
            return None

        return DataStatus(
            symbol=result[0],
            interval=result[1],
            first_date=result[2],
            last_date=result[3],
            row_count=result[4],
            last_updated=result[5],
            source=result[6],
        )

    @staticmethod
    def get_available_symbols(interval: str = "1d") -> list[str]:
        """Get list of symbols that have data stored in the database."""
        engine = get_engine()

        query = text("""
            SELECT DISTINCT symbol FROM data_status
            WHERE interval = :interval AND row_count > 0
            ORDER BY symbol
        """)

        with engine.connect() as conn:
            rows = conn.execute(query, {"interval": interval}).fetchall()

        return [row[0] for row in rows]

    @staticmethod
    def get_all_statuses(interval: str = "1d") -> list[DataStatus]:
        """Get data status for all stored symbols."""
        engine = get_engine()

        query = text("""
            SELECT symbol, interval, first_date, last_date, row_count, last_updated, source
            FROM data_status
            WHERE interval = :interval
            ORDER BY symbol
        """)

        with engine.connect() as conn:
            rows = conn.execute(query, {"interval": interval}).fetchall()

        return [
            DataStatus(
                symbol=r[0], interval=r[1], first_date=r[2],
                last_date=r[3], row_count=r[4], last_updated=r[5], source=r[6],
            )
            for r in rows
        ]

    @staticmethod
    def get_default_tickers() -> list[str]:
        """Return the default ticker list."""
        return list(DEFAULT_TICKERS)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _standardize_columns(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Standardize column names from yfinance format to our internal format.

        yfinance returns: Open, High, Low, Close, Adj Close, Volume
        We want:          open, high, low, close, adjusted_close, volume, symbol, source
        """
        # Handle multi-level columns (yfinance sometimes returns MultiIndex)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Rename columns
        rename_map = {
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adjusted_close",
            "Volume": "volume",
        }
        df = df.rename(columns=rename_map)

        # Ensure all expected columns exist
        for col in ["open", "high", "low", "close", "adjusted_close", "volume"]:
            if col not in df.columns:
                df[col] = np.nan

        if df["adjusted_close"].isna().all() and "close" in df.columns:
            df["adjusted_close"] = df["close"]

        # Add metadata columns
        df["symbol"] = symbol.upper()
        df["source"] = "yfinance"

        # Keep only our standard columns
        df = df[["open", "high", "low", "close", "adjusted_close", "volume", "symbol", "source"]]

        # Ensure index is DatetimeIndex named 'date'
        df.index.name = "date"

        # Drop rows with all NaN prices
        price_cols = ["open", "high", "low", "close", "adjusted_close"]
        df = df.dropna(subset=price_cols, how="all")

        return df

    @staticmethod
    def _update_status(symbol: str, interval: str) -> None:
        """Update the data_status table after a save operation."""
        engine = get_engine()

        query = text("""
            INSERT INTO data_status (symbol, interval, first_date, last_date, row_count, last_updated, source)
            SELECT
                :symbol,
                :interval,
                MIN(date),
                MAX(date),
                COUNT(*),
                NOW(),
                'yfinance'
            FROM prices
            WHERE symbol = :symbol AND interval = :interval
            ON CONFLICT (symbol, interval)
            DO UPDATE SET
                first_date = EXCLUDED.first_date,
                last_date = EXCLUDED.last_date,
                row_count = EXCLUDED.row_count,
                last_updated = NOW()
        """)

        with engine.begin() as conn:
            conn.execute(query, {"symbol": symbol, "interval": interval})
