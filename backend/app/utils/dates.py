"""
QuantLab Lite — Date Utilities

Helper functions for date handling, trading calendar operations,
and multi-asset date synchronization.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Sequence

import pandas as pd


def parse_date(value: str | date | datetime | None) -> date | None:
    """
    Parse a date from various formats.

    Accepts:
    - None → None
    - date object → returned as-is
    - datetime object → .date()
    - str in "YYYY-MM-DD" format
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    raise TypeError(f"Cannot parse date from {type(value)}: {value}")


def sync_dates(dataframes: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Synchronize dates across multiple DataFrames.

    Keeps only dates present in ALL DataFrames (inner join on index).
    This drops weekends for crypto when mixed with stock data.

    Parameters
    ----------
    dataframes : dict[str, pd.DataFrame]
        Mapping of symbol → DataFrame with DatetimeIndex.

    Returns
    -------
    dict[str, pd.DataFrame]
        Same mapping but with synchronized date indexes.
    """
    if not dataframes:
        return dataframes

    if len(dataframes) == 1:
        return dataframes

    # Find common dates across all DataFrames
    common_dates = None
    for df in dataframes.values():
        idx = df.index
        if common_dates is None:
            common_dates = set(idx)
        else:
            common_dates &= set(idx)

    if not common_dates:
        return {symbol: df.iloc[0:0] for symbol, df in dataframes.items()}

    # Sort the common dates
    common_dates = sorted(common_dates)

    # Filter each DataFrame
    return {
        symbol: df.loc[df.index.isin(common_dates)].sort_index()
        for symbol, df in dataframes.items()
    }


def get_trading_days_between(start: date, end: date) -> int:
    """
    Estimate the number of trading days between two dates.

    Uses the approximation of 252 trading days per year.
    """
    calendar_days = (end - start).days
    return int(calendar_days * 252 / 365)


def date_to_string(d: date | None) -> str | None:
    """Convert date to ISO string, or None."""
    if d is None:
        return None
    return d.isoformat()


def find_date_gaps(dates: pd.DatetimeIndex, freq: str = "B") -> pd.DatetimeIndex:
    """
    Find missing business dates in a DatetimeIndex.

    Parameters
    ----------
    dates : pd.DatetimeIndex
        The actual dates in the data.
    freq : str
        Expected frequency. 'B' = business days (default).

    Returns
    -------
    pd.DatetimeIndex
        Dates that are expected but missing.
    """
    if len(dates) < 2:
        return pd.DatetimeIndex([])

    expected = pd.date_range(start=dates.min(), end=dates.max(), freq=freq)
    return expected.difference(dates)
