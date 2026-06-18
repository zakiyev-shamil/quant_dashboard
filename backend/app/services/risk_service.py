"""
QuantLab Lite — Risk Service

VaR, CVaR, stress testing, and risk analytics.
Covers spec Sections 12–13.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

from app.core.config import TRADING_DAYS_PER_YEAR
from app.models.schemas import RiskMetrics, StressTestResult
from app.services import metrics_service as ms
from app.utils.validation import validate_confidence_level, validate_weights


# ======================================================================
# VaR / CVaR (Section 12)
# ======================================================================

def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    validate_confidence_level(confidence)
    return float(returns.quantile(1 - confidence))


def historical_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    validate_confidence_level(confidence)
    var = historical_var(returns, confidence)
    return float(returns[returns <= var].mean())


def parametric_var(returns: pd.Series, confidence: float = 0.95) -> float:
    validate_confidence_level(confidence)
    mu = float(returns.mean())
    sigma = float(returns.std())
    z = sp_stats.norm.ppf(1 - confidence)
    return mu + z * sigma


def portfolio_var(returns_df: pd.DataFrame, weights, confidence: float = 0.95) -> float:
    w = validate_weights(weights, n_assets=len(returns_df.columns))
    port_ret = returns_df.dot(w)
    return historical_var(port_ret, confidence)


def portfolio_cvar(returns_df: pd.DataFrame, weights, confidence: float = 0.95) -> float:
    w = validate_weights(weights, n_assets=len(returns_df.columns))
    port_ret = returns_df.dot(w)
    return historical_cvar(port_ret, confidence)


def probability_of_loss(returns: pd.Series) -> float:
    return float((returns < 0).mean())


def probability_of_drawdown(returns: pd.Series, threshold: float = 0.1) -> float:
    dd = ms.drawdown_series(returns)
    return float((dd < -threshold).mean())


def risk_at_confidence_levels(returns: pd.Series) -> dict:
    result = {}
    for conf in [0.90, 0.95, 0.99]:
        result[f"var_{int(conf*100)}"] = historical_var(returns, conf)
        result[f"cvar_{int(conf*100)}"] = historical_cvar(returns, conf)
    return result


def full_risk_report(returns: pd.Series, symbol: str = None, confidence: float = 0.95) -> RiskMetrics:
    worst5 = ms.worst_n_days(returns, 5)
    best5 = ms.best_n_days(returns, 5)
    return RiskMetrics(
        symbol=symbol, confidence_level=confidence,
        var_historical=historical_var(returns, confidence),
        cvar_historical=historical_cvar(returns, confidence),
        var_parametric=parametric_var(returns, confidence),
        worst_day=float(returns.min()), worst_5_days=worst5.tolist(),
        best_day=float(returns.max()), best_5_days=best5.tolist(),
        probability_of_loss=probability_of_loss(returns),
    )


# ======================================================================
# Stress Testing (Section 13)
# ======================================================================

def fixed_shock(weights, shock_pct: float = -0.10) -> float:
    w = np.array(weights, dtype=float)
    return float(w.sum() * shock_pct)


def asset_shock(returns_df: pd.DataFrame, weights, shocked_asset: str, shock_pct: float) -> float:
    w = validate_weights(weights, n_assets=len(returns_df.columns))
    symbols = list(returns_df.columns)
    idx = symbols.index(shocked_asset)
    asset_loss = w[idx] * shock_pct
    cov = returns_df.cov() * TRADING_DAYS_PER_YEAR
    other_loss = 0.0
    for i, sym in enumerate(symbols):
        if i == idx:
            continue
        corr = cov.iloc[i, idx] / (np.sqrt(cov.iloc[i, i]) * np.sqrt(cov.iloc[idx, idx]))
        other_loss += w[i] * shock_pct * corr
    return float(asset_loss + other_loss)


def loss_contribution(returns_df: pd.DataFrame, weights, shock_pct: float = -0.10) -> dict:
    w = validate_weights(weights, n_assets=len(returns_df.columns))
    contributions = {}
    for i, col in enumerate(returns_df.columns):
        contributions[col] = float(w[i] * shock_pct)
    return contributions


def volatility_spike_test(returns_df: pd.DataFrame, weights, vol_multiplier: float = 2.0) -> float:
    w = validate_weights(weights, n_assets=len(returns_df.columns))
    cov = returns_df.cov().values * TRADING_DAYS_PER_YEAR
    normal_vol = float(np.sqrt(w @ cov @ w))
    stressed_vol = normal_vol * vol_multiplier
    return stressed_vol


def stress_test(
    returns_df: pd.DataFrame, weights, shock_pct: float = -0.10, confidence: float = 0.95,
) -> StressTestResult:
    w = validate_weights(weights, n_assets=len(returns_df.columns))
    symbols = list(returns_df.columns)
    per_asset = {sym: float(w[i] * shock_pct) for i, sym in enumerate(symbols)}
    portfolio_loss = float(sum(per_asset.values()))
    total_abs = sum(abs(v) for v in per_asset.values())
    lc = {sym: abs(v) / total_abs if total_abs > 0 else 0.0 for sym, v in per_asset.items()}
    most_risky = max(per_asset.items(), key=lambda x: abs(x[1]))[0]
    return StressTestResult(
        portfolio_loss=portfolio_loss, per_asset_loss=per_asset,
        loss_contribution=lc, most_risky_asset=most_risky, shock_applied=shock_pct,
    )
