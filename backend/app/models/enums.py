"""
QuantLab Lite — Enumerations

All enum types used across the application.
"""

from enum import Enum


class Interval(str, Enum):
    """Supported data intervals from yfinance."""
    MIN_1 = "1m"
    MIN_2 = "2m"
    MIN_5 = "5m"
    MIN_15 = "15m"
    MIN_30 = "30m"
    MIN_60 = "60m"
    MIN_90 = "90m"
    HOUR_1 = "1h"
    DAY_1 = "1d"
    DAY_5 = "5d"
    WEEK_1 = "1wk"
    MONTH_1 = "1mo"
    MONTH_3 = "3mo"


class StrategyType(str, Enum):
    """Available backtesting strategies."""
    BUY_AND_HOLD = "buy_and_hold"
    SMA_CROSSOVER = "sma_crossover"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    RSI = "rsi"
    BOLLINGER_BANDS = "bollinger_bands"


class OptimizationTarget(str, Enum):
    """Portfolio optimization objectives."""
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"


class RebalanceFrequency(str, Enum):
    """Portfolio rebalancing frequency."""
    NONE = "none"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class MarketRegime(str, Enum):
    """Market regime classification."""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"


class DataSource(str, Enum):
    """Supported data sources."""
    YFINANCE = "yfinance"
