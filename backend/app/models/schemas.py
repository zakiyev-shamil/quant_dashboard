"""
QuantLab Lite — Pydantic Schemas

Data transfer objects for API requests/responses and internal data structures.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ===================================================================
# Data Layer
# ===================================================================

class PriceRow(BaseModel):
    """Single row of OHLCV data."""
    symbol: str
    date: date
    interval: str = "1d"
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    adjusted_close: float | None = None
    volume: int | None = None
    source: str = "yfinance"


class DataDownloadRequest(BaseModel):
    """Request to download price data."""
    symbol: str
    start_date: date | None = None
    end_date: date | None = None
    interval: str = "1d"


class DataStatus(BaseModel):
    """Status of stored data for a symbol."""
    symbol: str
    interval: str
    first_date: date | None = None
    last_date: date | None = None
    row_count: int = 0
    last_updated: datetime | None = None
    source: str = "yfinance"


class ValidationReport(BaseModel):
    """Report from data validation checks."""
    symbol: str
    total_rows: int = 0
    missing_values: dict[str, int] = Field(default_factory=dict)
    duplicate_dates: int = 0
    negative_prices: int = 0
    date_gaps: int = 0
    is_valid: bool = True
    issues: list[str] = Field(default_factory=list)


# ===================================================================
# Asset Metrics
# ===================================================================

class AssetMetrics(BaseModel):
    """Full metrics report for a single asset."""
    symbol: str
    start_date: date
    end_date: date
    start_price: float
    end_price: float

    # Returns
    total_return: float
    annualized_return: float
    average_daily_return: float
    median_daily_return: float
    best_daily_return: float
    best_daily_return_date: date
    worst_daily_return: float
    worst_daily_return_date: date

    # Risk
    annualized_volatility: float
    daily_volatility: float
    downside_deviation: float
    skewness: float
    kurtosis: float

    # Performance ratios
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    cagr: float

    # Drawdown
    max_drawdown: float
    max_drawdown_start: date | None = None
    max_drawdown_bottom: date | None = None
    max_drawdown_recovery: date | None = None
    max_drawdown_duration_days: int | None = None

    # Benchmark comparison (optional)
    benchmark_symbol: str | None = None
    beta: float | None = None
    alpha: float | None = None
    correlation_with_benchmark: float | None = None
    tracking_error: float | None = None
    information_ratio: float | None = None


# ===================================================================
# Portfolio
# ===================================================================

class PortfolioRequest(BaseModel):
    """Request to analyze a portfolio."""
    symbols: list[str]
    weights: list[float]
    start_date: date | None = None
    end_date: date | None = None
    benchmark: str = "SPY"
    interval: str = "1d"

    @field_validator("weights")
    @classmethod
    def weights_must_sum_to_one(cls, v):
        if abs(sum(v) - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0, got {sum(v):.6f}")
        return v

    @field_validator("weights")
    @classmethod
    def weights_must_be_non_negative(cls, v):
        if any(w < 0 for w in v):
            raise ValueError("All weights must be non-negative (long-only)")
        return v


class PortfolioMetrics(BaseModel):
    """Full metrics for a portfolio."""
    symbols: list[str]
    weights: list[float]
    start_date: date
    end_date: date

    # Portfolio performance
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float

    # Benchmark comparison
    benchmark_symbol: str
    benchmark_total_return: float
    excess_return: float
    correlation_with_benchmark: float
    tracking_error: float
    portfolio_beta: float
    portfolio_alpha: float
    information_ratio: float

    # Per-asset contribution
    asset_return_contribution: dict[str, float]
    asset_risk_contribution: dict[str, float]


# ===================================================================
# Optimization
# ===================================================================

class OptimizationRequest(BaseModel):
    """Request to optimize a portfolio."""
    symbols: list[str]
    start_date: date | None = None
    end_date: date | None = None
    num_portfolios: int = Field(default=10000, ge=100, le=100000)
    interval: str = "1d"
    max_weight: float = Field(default=1.0, gt=0.0, le=1.0)
    min_weight: float = Field(default=0.0, ge=0.0, lt=1.0)


class PortfolioPoint(BaseModel):
    """A single portfolio on the efficient frontier."""
    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float


class OptimizationResult(BaseModel):
    """Result of portfolio optimization."""
    max_sharpe_portfolio: PortfolioPoint
    min_volatility_portfolio: PortfolioPoint
    all_portfolios_returns: list[float]
    all_portfolios_volatilities: list[float]
    all_portfolios_sharpes: list[float]


# ===================================================================
# Backtesting
# ===================================================================

class BacktestRequest(BaseModel):
    """Request to run a backtest."""
    symbol: str
    strategy: str  # StrategyType value
    start_date: date | None = None
    end_date: date | None = None
    params: dict = Field(default_factory=dict)
    commission: float = Field(default=0.001, ge=0.0)
    slippage: float = Field(default=0.0005, ge=0.0)
    interval: str = "1d"


class TradeRecord(BaseModel):
    """A single trade in the backtest."""
    entry_date: date
    exit_date: date
    entry_price: float
    exit_price: float
    return_pct: float
    holding_days: int
    direction: str = "long"  # always long for now


class BacktestResult(BaseModel):
    """Full backtest result."""
    symbol: str
    strategy: str
    params: dict
    start_date: date
    end_date: date
    commission: float
    slippage: float

    # Performance
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    final_equity: float

    # Trade statistics
    win_rate: float
    num_trades: int
    avg_trade_return: float
    best_trade: float
    worst_trade: float
    exposure: float  # fraction of time in market
    turnover: float

    # Benchmark comparison
    benchmark_return: float
    alpha_vs_benchmark: float
    strategy_beta: float

    # Time series (as lists for JSON serialization)
    equity_curve_dates: list[str]
    equity_curve_values: list[float]
    drawdown_values: list[float]
    signal_values: list[int]
    trades: list[TradeRecord]


# ===================================================================
# Risk
# ===================================================================

class RiskMetrics(BaseModel):
    """Risk metrics for an asset or portfolio."""
    symbol: str | None = None
    confidence_level: float = 0.95

    var_historical: float
    cvar_historical: float
    var_parametric: float

    worst_day: float
    worst_5_days: list[float]
    best_day: float
    best_5_days: list[float]

    probability_of_loss: float


class StressTestRequest(BaseModel):
    """Request for a stress test."""
    symbols: list[str]
    weights: list[float]
    shock_pct: float = Field(default=-0.10)  # -10% shock
    confidence_level: float = Field(default=0.95, gt=0.0, lt=1.0)


class StressTestResult(BaseModel):
    """Result of a stress test."""
    portfolio_loss: float
    per_asset_loss: dict[str, float]
    loss_contribution: dict[str, float]
    most_risky_asset: str
    shock_applied: float
