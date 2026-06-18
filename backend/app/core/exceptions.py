"""
QuantLab Lite — Custom Exceptions

All domain-specific exceptions used across the application.
"""


class QuantLabError(Exception):
    """Base exception for all QuantLab errors."""
    pass


class TickerNotFoundError(QuantLabError):
    """Raised when a ticker symbol is not recognized or has no data."""

    def __init__(self, symbol: str, message: str | None = None):
        self.symbol = symbol
        self.message = message or f"Ticker '{symbol}' not found or has no data."
        super().__init__(self.message)


class DataNotAvailableError(QuantLabError):
    """Raised when requested data is not available in the database."""

    def __init__(self, symbol: str, message: str | None = None):
        self.symbol = symbol
        self.message = message or f"No data available for '{symbol}'. Download it first."
        super().__init__(self.message)


class InvalidDateRangeError(QuantLabError):
    """Raised when the date range is invalid (e.g. start > end, empty)."""

    def __init__(self, start_date=None, end_date=None, message: str | None = None):
        self.start_date = start_date
        self.end_date = end_date
        self.message = message or (
            f"Invalid date range: {start_date} to {end_date}. "
            "Start date must be before end date."
        )
        super().__init__(self.message)


class InvalidWeightsError(QuantLabError):
    """Raised when portfolio weights are invalid."""

    def __init__(self, weights=None, message: str | None = None):
        self.weights = weights
        self.message = message or "Invalid portfolio weights. Must sum to 1.0, be non-negative, and contain no NaN."
        super().__init__(self.message)


class InsufficientDataError(QuantLabError):
    """Raised when there is not enough data for the requested analysis."""

    def __init__(self, symbol: str = "", required: int = 0, available: int = 0, message: str | None = None):
        self.symbol = symbol
        self.required = required
        self.available = available
        self.message = message or (
            f"Insufficient data for '{symbol}': need {required} rows, have {available}."
        )
        super().__init__(self.message)


class InvalidIntervalError(QuantLabError):
    """Raised when an unsupported data interval is requested."""

    def __init__(self, interval: str, message: str | None = None):
        self.interval = interval
        self.message = message or f"Invalid interval '{interval}'. See config.AVAILABLE_INTERVALS."
        super().__init__(self.message)


class ValidationError(QuantLabError):
    """Generic validation error with details."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = f"Validation error on '{field}': {message}"
        super().__init__(self.message)
