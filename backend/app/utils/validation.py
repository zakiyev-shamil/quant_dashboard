"""
QuantLab Lite — Input Validation

Covers spec items 291–304: comprehensive input validation
to protect against bad data and user errors.
"""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Sequence

import numpy as np

from app.core.config import AVAILABLE_INTERVALS, get_ticker_registry
from app.core.exceptions import (
    InvalidDateRangeError,
    InvalidIntervalError,
    InvalidWeightsError,
    InsufficientDataError,
    ValidationError,
    TickerNotFoundError,
)


def validate_ticker(symbol: str, strict: bool = False) -> str:
    """
    Validate a ticker symbol.

    Parameters
    ----------
    symbol : str
        Ticker to validate.
    strict : bool
        If True, require the ticker to be in the SEC registry.
        If False, accept any non-empty string (yfinance will validate on download).

    Returns
    -------
    str
        Uppercased ticker symbol.

    Raises
    ------
    TickerNotFoundError
        If the ticker is invalid.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        raise TickerNotFoundError("", "Ticker symbol cannot be empty.")

    if strict:
        registry = get_ticker_registry()
        # Allow crypto tickers (contain "-") and ETFs not in SEC registry
        if "-" not in symbol and symbol not in registry:
            raise TickerNotFoundError(symbol, f"Ticker '{symbol}' not found in SEC registry.")

    return symbol


def validate_date_range(
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> tuple[date | None, date | None]:
    """
    Validate that start_date < end_date.

    Parameters
    ----------
    start_date : date or str or None
    end_date : date or str or None

    Returns
    -------
    tuple[date | None, date | None]
        Parsed (start_date, end_date).

    Raises
    ------
    InvalidDateRangeError
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    if start_date and end_date and start_date >= end_date:
        raise InvalidDateRangeError(start_date, end_date)

    if end_date and end_date > date.today():
        raise InvalidDateRangeError(
            start_date, end_date,
            f"End date {end_date} is in the future.",
        )

    return start_date, end_date


def validate_interval(interval: str) -> str:
    """
    Validate a data interval.

    Raises
    ------
    InvalidIntervalError
    """
    if interval not in AVAILABLE_INTERVALS:
        raise InvalidIntervalError(interval)
    return interval


def validate_weights(
    weights: Sequence[float],
    n_assets: int | None = None,
    tolerance: float = 1e-6,
) -> np.ndarray:
    """
    Validate portfolio weights.

    Checks:
    - Sum equals 1.0 (within tolerance)
    - All weights >= 0 (long-only)
    - No NaN values
    - Length matches n_assets if provided

    Returns
    -------
    np.ndarray
        Validated weights as numpy array.

    Raises
    ------
    InvalidWeightsError
    """
    w = np.array(weights, dtype=float)

    if np.any(np.isnan(w)):
        raise InvalidWeightsError(weights, "Weights contain NaN values.")

    if n_assets is not None and len(w) != n_assets:
        raise InvalidWeightsError(
            weights,
            f"Expected {n_assets} weights, got {len(w)}.",
        )

    if np.any(w < 0):
        raise InvalidWeightsError(weights, "Weights must be non-negative (long-only portfolio).")

    if abs(w.sum() - 1.0) > tolerance:
        raise InvalidWeightsError(
            weights,
            f"Weights must sum to 1.0, got {w.sum():.6f}.",
        )

    return w


def validate_window(window: int, data_length: int, name: str = "window") -> int:
    """
    Validate that a rolling window fits within the data.

    Raises
    ------
    InsufficientDataError
    """
    if window <= 0:
        raise ValidationError(name, f"{name} must be positive, got {window}.")
    if window >= data_length:
        raise InsufficientDataError(
            required=window,
            available=data_length,
            message=f"{name}={window} exceeds data length={data_length}.",
        )
    return window


def validate_windows(short_window: int, long_window: int) -> tuple[int, int]:
    """
    Validate that short_window < long_window.

    Raises
    ------
    ValidationError
    """
    if short_window <= 0 or long_window <= 0:
        raise ValidationError("windows", "Both windows must be positive.")
    if short_window >= long_window:
        raise ValidationError(
            "windows",
            f"short_window ({short_window}) must be less than long_window ({long_window}).",
        )
    return short_window, long_window


def validate_commission(rate: float) -> float:
    """Validate commission rate is non-negative."""
    if rate < 0:
        raise ValidationError("commission", f"Commission must be non-negative, got {rate}.")
    return rate


def validate_slippage(rate: float) -> float:
    """Validate slippage rate is non-negative."""
    if rate < 0:
        raise ValidationError("slippage", f"Slippage must be non-negative, got {rate}.")
    return rate


def validate_confidence_level(level: float) -> float:
    """Validate confidence level is between 0 and 1 exclusive."""
    if not (0 < level < 1):
        raise ValidationError(
            "confidence_level",
            f"Must be between 0 and 1 exclusive, got {level}.",
        )
    return level


def validate_risk_free_rate(rate: float) -> float:
    """Validate risk-free rate is reasonable (between -0.1 and 0.5)."""
    if not (-0.1 <= rate <= 0.5):
        raise ValidationError(
            "risk_free_rate",
            f"Risk-free rate {rate} seems unreasonable. Expected between -0.1 and 0.5.",
        )
    return rate


def validate_portfolio_size(n_assets: int, min_assets: int = 2) -> int:
    """Validate that a portfolio contains at least min_assets."""
    if n_assets < min_assets:
        raise ValidationError(
            "portfolio",
            f"Portfolio must contain at least {min_assets} assets, got {n_assets}.",
        )
    return n_assets
