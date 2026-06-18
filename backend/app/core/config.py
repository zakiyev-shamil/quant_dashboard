"""
QuantLab Lite — Core Configuration

Central configuration for the entire application.
All settings are loaded from environment variables / .env file.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from backend/ directory
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
_PROJECT_DIR = _BACKEND_DIR.parent  # Quant Dashboard/

load_dotenv(_BACKEND_DIR / ".env")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://quantlab:quantlab@localhost:5432/quantlab",
)

# ---------------------------------------------------------------------------
# Trading calendar
# ---------------------------------------------------------------------------
TRADING_DAYS_PER_YEAR: int = int(os.getenv("TRADING_DAYS_PER_YEAR", "252"))

# ---------------------------------------------------------------------------
# Default data settings
# ---------------------------------------------------------------------------
DEFAULT_INTERVAL: str = os.getenv("DEFAULT_INTERVAL", "1d")

AVAILABLE_INTERVALS: list[str] = [
    "1m", "2m", "5m", "15m", "30m", "60m", "90m",
    "1h", "1d", "5d", "1wk", "1mo", "3mo",
]

# ---------------------------------------------------------------------------
# Default tickers
# ---------------------------------------------------------------------------
DEFAULT_TICKERS: list[str] = [
    "SPY", "QQQ", "TLT", "GLD",
    "AAPL", "MSFT", "NVDA", "JPM", "XOM",
    "BTC-USD", "ETH-USD",
]

# ---------------------------------------------------------------------------
# Ticker registry — loaded from company_tickers.json
# ---------------------------------------------------------------------------
_TICKERS_FILE = _PROJECT_DIR / "company_tickers.json"

_TICKER_REGISTRY: dict[str, str] = {}  # ticker -> company name


def _load_ticker_registry() -> dict[str, str]:
    """Load ticker -> company name mapping from SEC company_tickers.json."""
    global _TICKER_REGISTRY
    if _TICKER_REGISTRY:
        return _TICKER_REGISTRY

    if not _TICKERS_FILE.exists():
        return _TICKER_REGISTRY

    with open(_TICKERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    _TICKER_REGISTRY = {
        entry["ticker"]: entry["title"]
        for entry in data.values()
        if "ticker" in entry and "title" in entry
    }
    return _TICKER_REGISTRY


def get_ticker_registry() -> dict[str, str]:
    """Return the full ticker -> company name mapping."""
    return _load_ticker_registry()


def is_known_ticker(symbol: str) -> bool:
    """Check if a ticker is in the SEC registry."""
    registry = _load_ticker_registry()
    return symbol.upper() in registry


def get_company_name(symbol: str) -> str | None:
    """Get company name for a ticker, or None if unknown."""
    registry = _load_ticker_registry()
    return registry.get(symbol.upper())


# ---------------------------------------------------------------------------
# Risk-free rate
# ---------------------------------------------------------------------------
def get_risk_free_rate() -> float:
    """
    Return the annualized risk-free rate from configuration.

    Reads from the RISK_FREE_RATE environment variable / .env file.
    The user controls how this value is set and calculated.
    """
    return float(os.getenv("RISK_FREE_RATE", "0.02"))
