"""
QuantLab Lite — Portfolio Service

Portfolio analysis with custom weights: returns, risk, benchmark comparison,
correlation/covariance matrices, asset contributions, and rebalancing simulation.

Covers spec Sections 7–9, 11.
"""

from __future__ import annotations

import logging
from datetime import date

import numpy as np
import pandas as pd

from app.core.config import TRADING_DAYS_PER_YEAR, get_risk_free_rate
from app.core.exceptions import InvalidWeightsError
from app.models.schemas import PortfolioMetrics
from app.services import metrics_service as ms
from app.utils.validation import validate_weights, validate_portfolio_size

logger = logging.getLogger(__name__)


# ======================================================================
# Section 7 — Correlation Analysis
# ======================================================================

def correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pearson correlation matrix between all assets.

    Parameters
    ----------
    returns_df : pd.DataFrame
        Returns with assets as columns, dates as index.
    """
    return returns_df.corr()


def covariance_matrix(
    returns_df: pd.DataFrame,
    annualize: bool = True,
) -> pd.DataFrame:
    """
    Covariance matrix. Optionally annualized.
    """
    cov = returns_df.cov()
    if annualize:
        cov = cov * TRADING_DAYS_PER_YEAR
    return cov


def rolling_correlation_pair(
    ret1: pd.Series,
    ret2: pd.Series,
    window: int = 63,
) -> pd.Series:
    """Rolling correlation between two return series."""
    return ret1.rolling(window).corr(ret2)


def most_correlated_pairs(
    corr_mat: pd.DataFrame,
    n: int = 5,
) -> list[tuple[str, str, float]]:
    """Find the N most correlated asset pairs (excluding self-correlation)."""
    pairs = []
    cols = corr_mat.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append((cols[i], cols[j], corr_mat.iloc[i, j]))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    return pairs[:n]


def least_correlated_pairs(
    corr_mat: pd.DataFrame,
    n: int = 5,
) -> list[tuple[str, str, float]]:
    """Find the N least correlated asset pairs (best diversifiers)."""
    pairs = []
    cols = corr_mat.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append((cols[i], cols[j], corr_mat.iloc[i, j]))
    pairs.sort(key=lambda x: abs(x[2]))
    return pairs[:n]


# ======================================================================
# Section 9 — Portfolio Analysis
# ======================================================================

def portfolio_returns(
    returns_df: pd.DataFrame,
    weights: np.ndarray,
) -> pd.Series:
    """
    Weighted portfolio returns.

    Parameters
    ----------
    returns_df : pd.DataFrame
        Asset returns (columns = assets, index = dates).
    weights : np.ndarray
        Portfolio weights (must sum to 1).

    Returns
    -------
    pd.Series
        Daily portfolio returns.
    """
    w = validate_weights(weights, n_assets=len(returns_df.columns))
    return returns_df.dot(w)


def portfolio_cumulative_return(port_returns: pd.Series) -> pd.Series:
    """Cumulative return of the portfolio."""
    return ms.cumulative_returns(port_returns)


def asset_contribution_return(
    returns_df: pd.DataFrame,
    weights: np.ndarray,
) -> dict[str, float]:
    """
    Each asset's contribution to portfolio total return.

    Contribution_i = weight_i * annualized_return_i
    """
    w = validate_weights(weights, n_assets=len(returns_df.columns))
    contributions = {}
    for i, col in enumerate(returns_df.columns):
        ann_ret = ms.annualized_return(returns_df[col])
        contributions[col] = float(w[i] * ann_ret)
    return contributions


def asset_contribution_risk(
    returns_df: pd.DataFrame,
    weights: np.ndarray,
) -> dict[str, float]:
    """
    Each asset's marginal contribution to portfolio risk (MCTR).

    MCTR_i = w_i * (Σ * w)_i / σ_portfolio
    """
    w = validate_weights(weights, n_assets=len(returns_df.columns))
    cov = covariance_matrix(returns_df, annualize=True).values

    port_var = float(w @ cov @ w)
    port_vol = np.sqrt(port_var)

    if port_vol == 0:
        return {col: 0.0 for col in returns_df.columns}

    # Marginal contribution
    marginal = (cov @ w) * w / port_vol

    return {col: float(marginal[i]) for i, col in enumerate(returns_df.columns)}


def portfolio_vs_benchmark(
    port_returns: pd.Series,
    benchmark_returns: pd.Series,
    rf: float | None = None,
) -> dict:
    """
    Compare portfolio to benchmark.

    Returns dict with: excess_return, tracking_error, info_ratio, beta, alpha, correlation.
    """
    if rf is None:
        rf = get_risk_free_rate()

    aligned = pd.concat([port_returns, benchmark_returns], axis=1).dropna()
    pr = aligned.iloc[:, 0]
    br = aligned.iloc[:, 1]

    a, b = ms.alpha_beta(pr, br, rf)

    return {
        "benchmark_total_return": ms.total_return(br),
        "excess_return": ms.total_return(pr) - ms.total_return(br),
        "tracking_error": ms.tracking_error(pr, br),
        "information_ratio": ms.information_ratio(pr, br),
        "portfolio_beta": b,
        "portfolio_alpha": a,
        "correlation_with_benchmark": ms.correlation_with_benchmark(pr, br),
    }


def portfolio_metrics(
    returns_df: pd.DataFrame,
    weights: np.ndarray | list[float],
    benchmark_returns: pd.Series | None = None,
    benchmark_symbol: str = "SPY",
    rf: float | None = None,
) -> PortfolioMetrics:
    """
    Full portfolio metrics report.

    Parameters
    ----------
    returns_df : pd.DataFrame
        Asset returns with columns = asset symbols.
    weights : array-like
        Portfolio weights.
    benchmark_returns : pd.Series or None
        Benchmark return series.
    benchmark_symbol : str
        Name of the benchmark.
    rf : float or None
        Risk-free rate.
    """
    if rf is None:
        rf = get_risk_free_rate()

    w = validate_weights(weights, n_assets=len(returns_df.columns))
    validate_portfolio_size(len(returns_df.columns))

    port_ret = portfolio_returns(returns_df, w)

    # Core metrics
    result = {
        "symbols": list(returns_df.columns),
        "weights": [float(x) for x in w],
        "start_date": returns_df.index[0].date() if hasattr(returns_df.index[0], "date") else returns_df.index[0],
        "end_date": returns_df.index[-1].date() if hasattr(returns_df.index[-1], "date") else returns_df.index[-1],
        "total_return": ms.total_return(port_ret),
        "annualized_return": ms.annualized_return(port_ret),
        "annualized_volatility": ms.annualized_volatility(port_ret),
        "sharpe_ratio": ms.sharpe_ratio(port_ret, rf),
        "sortino_ratio": ms.sortino_ratio(port_ret, rf),
        "calmar_ratio": ms.calmar_ratio(port_ret),
        "max_drawdown": ms.max_drawdown(port_ret),
        "asset_return_contribution": asset_contribution_return(returns_df, w),
        "asset_risk_contribution": asset_contribution_risk(returns_df, w),
    }

    # Benchmark comparison
    if benchmark_returns is not None:
        comparison = portfolio_vs_benchmark(port_ret, benchmark_returns, rf)
        result.update({
            "benchmark_symbol": benchmark_symbol,
            **comparison,
        })
    else:
        result.update({
            "benchmark_symbol": benchmark_symbol,
            "benchmark_total_return": 0.0,
            "excess_return": 0.0,
            "correlation_with_benchmark": 0.0,
            "tracking_error": 0.0,
            "portfolio_beta": 0.0,
            "portfolio_alpha": 0.0,
            "information_ratio": 0.0,
        })

    return PortfolioMetrics(**result)


# ======================================================================
# Section 11 — Rebalancing
# ======================================================================

def simulate_rebalancing(
    returns_df: pd.DataFrame,
    weights: np.ndarray | list[float],
    frequency: str = "monthly",
    commission: float = 0.001,
) -> pd.Series:
    """
    Simulate portfolio with periodic rebalancing.

    Parameters
    ----------
    returns_df : pd.DataFrame
        Daily asset returns.
    weights : array-like
        Target portfolio weights.
    frequency : str
        'none', 'monthly', 'quarterly', 'yearly'.
    commission : float
        Transaction cost per trade (fraction).

    Returns
    -------
    pd.Series
        Portfolio equity curve.
    """
    w = np.array(weights, dtype=float)
    n_assets = len(returns_df.columns)

    if frequency == "none":
        port_ret = portfolio_returns(returns_df, w)
        return ms.equity_curve(port_ret)

    # Determine rebalancing dates
    freq_map = {"monthly": "ME", "quarterly": "QE", "yearly": "YE"}
    resample_freq = freq_map.get(frequency, "ME")
    rebal_dates = set(returns_df.resample(resample_freq).last().index)

    # Simulate day by day
    current_weights = w.copy()
    equity = 1.0
    equity_series = []

    for dt, row in returns_df.iterrows():
        # Apply returns with current weights
        daily_ret = float(row.values @ current_weights)
        equity *= (1 + daily_ret)

        # Update weights after drift
        asset_values = current_weights * (1 + row.values)
        total = asset_values.sum()
        if total > 0:
            current_weights = asset_values / total

        # Rebalance if it's a rebalancing date
        if dt in rebal_dates:
            # Turnover = sum of absolute weight changes
            turnover = float(np.abs(current_weights - w).sum())
            cost = turnover * commission
            equity *= (1 - cost)
            current_weights = w.copy()

        equity_series.append(equity)

    return pd.Series(equity_series, index=returns_df.index, name="equity")


def compare_rebalancing_regimes(
    returns_df: pd.DataFrame,
    weights: np.ndarray | list[float],
    commission: float = 0.001,
) -> pd.DataFrame:
    """
    Compare portfolio performance under different rebalancing frequencies.

    Returns DataFrame with metrics for each regime.
    """
    regimes = ["none", "monthly", "quarterly", "yearly"]
    results = []

    for freq in regimes:
        eq = simulate_rebalancing(returns_df, weights, freq, commission)
        rets = eq.pct_change().dropna()
        results.append({
            "rebalance_frequency": freq,
            "total_return": ms.total_return(rets),
            "annualized_return": ms.annualized_return(rets),
            "annualized_volatility": ms.annualized_volatility(rets),
            "sharpe_ratio": ms.sharpe_ratio(rets),
            "max_drawdown": ms.max_drawdown(rets),
            "final_equity": float(eq.iloc[-1]),
        })

    return pd.DataFrame(results)
