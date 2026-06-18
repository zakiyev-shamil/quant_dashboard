"""
QuantLab Lite — Optimizer Service

Random portfolio optimization: generate N portfolios, find max Sharpe
and min volatility, produce efficient frontier data.

Covers spec Section 10.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from app.core.config import TRADING_DAYS_PER_YEAR, get_risk_free_rate
from app.models.schemas import OptimizationResult, PortfolioPoint
from app.services import metrics_service as ms
from app.services.portfolio_service import covariance_matrix

logger = logging.getLogger(__name__)


def generate_random_weights(
    n_assets: int,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> np.ndarray:
    """
    Generate a single set of random portfolio weights.

    Weights are uniformly distributed, constrained to [min_weight, max_weight],
    and normalized to sum to 1.
    """
    if n_assets <= 0:
        raise ValueError("At least one asset is required for optimization.")
    if min_weight > max_weight:
        raise ValueError("min_weight cannot be greater than max_weight.")
    if min_weight * n_assets > 1.0 or max_weight * n_assets < 1.0:
        raise ValueError(
            "Weight constraints are infeasible for the selected number of assets."
        )

    while True:
        w = np.random.uniform(min_weight, max_weight, n_assets)
        total = w.sum()
        if total > 0:
            w = w / total
            # Check constraints after normalization
            if np.all(w >= min_weight) and np.all(w <= max_weight):
                return w


def generate_random_portfolios(
    returns_df: pd.DataFrame,
    n_portfolios: int = 10000,
    rf: float | None = None,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> pd.DataFrame:
    """
    Generate N random portfolios and calculate their metrics.

    Parameters
    ----------
    returns_df : pd.DataFrame
        Daily returns with assets as columns.
    n_portfolios : int
        Number of random portfolios to generate.
    rf : float or None
        Risk-free rate.
    min_weight : float
        Minimum weight per asset.
    max_weight : float
        Maximum weight per asset.

    Returns
    -------
    pd.DataFrame
        Columns: [w_{asset1}, ..., w_{assetN}, return, volatility, sharpe]
    """
    if rf is None:
        rf = get_risk_free_rate()

    n_assets = len(returns_df.columns)
    symbols = list(returns_df.columns)

    # Pre-compute for speed
    mean_returns = returns_df.mean().values * TRADING_DAYS_PER_YEAR
    cov_annual = returns_df.cov().values * TRADING_DAYS_PER_YEAR

    results = []

    for _ in range(n_portfolios):
        w = generate_random_weights(n_assets, min_weight, max_weight)

        # Portfolio return
        port_ret = float(w @ mean_returns)
        # Portfolio volatility
        port_vol = float(np.sqrt(w @ cov_annual @ w))
        # Sharpe ratio
        port_sharpe = float((port_ret - rf) / port_vol) if port_vol > 0 else 0.0

        row = {f"w_{symbols[i]}": float(w[i]) for i in range(n_assets)}
        row["return"] = port_ret
        row["volatility"] = port_vol
        row["sharpe"] = port_sharpe

        results.append(row)

    return pd.DataFrame(results)


def max_sharpe_portfolio(
    random_portfolios: pd.DataFrame,
    symbols: list[str],
) -> PortfolioPoint:
    """Find the portfolio with the maximum Sharpe ratio."""
    idx = random_portfolios["sharpe"].idxmax()
    row = random_portfolios.loc[idx]

    weights = {s: float(row[f"w_{s}"]) for s in symbols}
    return PortfolioPoint(
        weights=weights,
        expected_return=float(row["return"]),
        volatility=float(row["volatility"]),
        sharpe_ratio=float(row["sharpe"]),
    )


def min_volatility_portfolio(
    random_portfolios: pd.DataFrame,
    symbols: list[str],
) -> PortfolioPoint:
    """Find the portfolio with the minimum volatility."""
    idx = random_portfolios["volatility"].idxmin()
    row = random_portfolios.loc[idx]

    weights = {s: float(row[f"w_{s}"]) for s in symbols}
    return PortfolioPoint(
        weights=weights,
        expected_return=float(row["return"]),
        volatility=float(row["volatility"]),
        sharpe_ratio=float(row["sharpe"]),
    )


def optimize(
    returns_df: pd.DataFrame,
    n_portfolios: int = 10000,
    rf: float | None = None,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> OptimizationResult:
    """
    Full optimization pipeline: generate random portfolios, find optimal ones.

    Parameters
    ----------
    returns_df : pd.DataFrame
        Daily returns with assets as columns.
    n_portfolios : int
        Number of random portfolios.
    rf : float or None
        Risk-free rate.
    min_weight : float
        Minimum weight constraint.
    max_weight : float
        Maximum weight constraint.

    Returns
    -------
    OptimizationResult
        Contains max Sharpe, min volatility, and all portfolio data.
    """
    symbols = list(returns_df.columns)

    logger.info(f"Generating {n_portfolios} random portfolios for {symbols}")

    portfolios = generate_random_portfolios(
        returns_df, n_portfolios, rf, min_weight, max_weight,
    )

    ms_port = max_sharpe_portfolio(portfolios, symbols)
    mv_port = min_volatility_portfolio(portfolios, symbols)

    logger.info(f"Max Sharpe: {ms_port.sharpe_ratio:.4f}, Min Vol: {mv_port.volatility:.4f}")

    return OptimizationResult(
        max_sharpe_portfolio=ms_port,
        min_volatility_portfolio=mv_port,
        all_portfolios_returns=portfolios["return"].tolist(),
        all_portfolios_volatilities=portfolios["volatility"].tolist(),
        all_portfolios_sharpes=portfolios["sharpe"].tolist(),
    )


def compare_equal_vs_optimized(
    returns_df: pd.DataFrame,
    rf: float | None = None,
    n_portfolios: int = 10000,
) -> dict:
    """
    Compare equal-weight portfolio with optimized portfolios.

    Returns dict with equal_weight, max_sharpe, and min_vol portfolio details.
    """
    if rf is None:
        rf = get_risk_free_rate()

    n_assets = len(returns_df.columns)
    equal_w = np.ones(n_assets) / n_assets

    # Equal weight metrics
    mean_returns = returns_df.mean().values * TRADING_DAYS_PER_YEAR
    cov_annual = returns_df.cov().values * TRADING_DAYS_PER_YEAR

    eq_ret = float(equal_w @ mean_returns)
    eq_vol = float(np.sqrt(equal_w @ cov_annual @ equal_w))
    eq_sharpe = float((eq_ret - rf) / eq_vol) if eq_vol > 0 else 0.0

    # Optimized
    result = optimize(returns_df, n_portfolios, rf)

    return {
        "equal_weight": {
            "weights": {col: float(equal_w[i]) for i, col in enumerate(returns_df.columns)},
            "return": eq_ret,
            "volatility": eq_vol,
            "sharpe": eq_sharpe,
        },
        "max_sharpe": result.max_sharpe_portfolio.model_dump(),
        "min_volatility": result.min_volatility_portfolio.model_dump(),
    }
