"""
QuantLab Lite — Metrics Service

All financial calculations for a single asset:
returns, risk, performance ratios, drawdowns, volume analysis,
technical indicators, rolling analysis, and asset comparison.

Covers spec Sections 2–6, 14, 19–20.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Sequence

import numpy as np
import pandas as pd
from scipy import stats

from app.core.config import TRADING_DAYS_PER_YEAR, get_risk_free_rate
from app.models.schemas import AssetMetrics

logger = logging.getLogger(__name__)


# ======================================================================
# Section 2 — Returns
# ======================================================================

def simple_returns(prices: pd.Series) -> pd.Series:
    """
    Simple (arithmetic) returns: r_t = p_t / p_{t-1} - 1

    Parameters
    ----------
    prices : pd.Series
        Price series with DatetimeIndex.

    Returns
    -------
    pd.Series
        Daily returns (first value is NaN, dropped).
    """
    return prices.pct_change().dropna()


def log_returns(prices: pd.Series) -> pd.Series:
    """
    Logarithmic returns: r_t = ln(p_t / p_{t-1})
    """
    return np.log(prices / prices.shift(1)).dropna()


def cumulative_returns(returns: pd.Series) -> pd.Series:
    """
    Cumulative (compounded) returns starting from 0.

    (1 + r_1) * (1 + r_2) * ... - 1
    """
    return (1 + returns).cumprod() - 1


def total_return(returns: pd.Series) -> float:
    """Total compounded return over the entire period."""
    return float((1 + returns).prod() - 1)


def annualized_return(returns: pd.Series, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
    """
    Annualize compounded returns.

    CAGR = (1 + total_return)^(periods_per_year / n_periods) - 1
    """
    n = len(returns)
    if n == 0:
        return 0.0
    total = (1 + returns).prod()
    return float(total ** (periods_per_year / n) - 1)


def monthly_returns(returns: pd.Series) -> pd.Series:
    """Resample daily returns to monthly returns."""
    return (1 + returns).resample("ME").prod() - 1


def yearly_returns(returns: pd.Series) -> pd.Series:
    """Resample daily returns to yearly returns."""
    return (1 + returns).resample("YE").prod() - 1


def best_day(returns: pd.Series) -> tuple[date, float]:
    """Return (date, return) of the best single day."""
    idx = returns.idxmax()
    return idx.date() if hasattr(idx, "date") else idx, float(returns.max())


def worst_day(returns: pd.Series) -> tuple[date, float]:
    """Return (date, return) of the worst single day."""
    idx = returns.idxmin()
    return idx.date() if hasattr(idx, "date") else idx, float(returns.min())


def best_n_days(returns: pd.Series, n: int = 5) -> pd.Series:
    """Top N days by return (descending)."""
    return returns.nlargest(n)


def worst_n_days(returns: pd.Series, n: int = 5) -> pd.Series:
    """Bottom N days by return (ascending)."""
    return returns.nsmallest(n)


# ======================================================================
# Section 3 — Risk
# ======================================================================

def daily_volatility(returns: pd.Series) -> float:
    """Daily standard deviation of returns."""
    return float(returns.std())


def annualized_volatility(
    returns: pd.Series,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Annualized volatility = daily_vol * sqrt(periods_per_year)."""
    return float(returns.std() * np.sqrt(periods_per_year))


def rolling_volatility(returns: pd.Series, window: int = 21) -> pd.Series:
    """Rolling annualized volatility."""
    return returns.rolling(window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)


def rolling_mean_return(returns: pd.Series, window: int = 21) -> pd.Series:
    """Rolling annualized mean return."""
    return returns.rolling(window).mean() * TRADING_DAYS_PER_YEAR


def rolling_sharpe(
    returns: pd.Series,
    window: int = 63,
    rf: float | None = None,
) -> pd.Series:
    """Rolling Sharpe ratio (annualized)."""
    if rf is None:
        rf = get_risk_free_rate()
    daily_rf = rf / TRADING_DAYS_PER_YEAR
    excess = returns - daily_rf
    roll_mean = excess.rolling(window).mean() * TRADING_DAYS_PER_YEAR
    roll_std = returns.rolling(window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    return roll_mean / roll_std


def downside_deviation(returns: pd.Series, mar: float = 0.0) -> float:
    """
    Downside deviation (semi-deviation below the minimum acceptable return).

    Parameters
    ----------
    mar : float
        Minimum acceptable return (default 0).
    """
    downside = returns[returns < mar] - mar
    if len(downside) == 0:
        return 0.0
    return float(np.sqrt((downside ** 2).mean()))


def skewness(returns: pd.Series) -> float:
    """Skewness of the return distribution."""
    return float(returns.skew())


def kurtosis(returns: pd.Series) -> float:
    """Excess kurtosis of the return distribution."""
    return float(returns.kurtosis())


def return_quantiles(
    returns: pd.Series,
    quantiles: Sequence[float] = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99),
) -> dict[str, float]:
    """Quantiles of the return distribution."""
    return {f"q{int(q * 100):02d}": float(returns.quantile(q)) for q in quantiles}


def variance(returns: pd.Series) -> float:
    """Variance of returns."""
    return float(returns.var())


# ======================================================================
# Section 4 — Performance Ratios
# ======================================================================

def sharpe_ratio(
    returns: pd.Series,
    rf: float | None = None,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """
    Sharpe Ratio = (annualized_return - rf) / annualized_volatility
    """
    if rf is None:
        rf = get_risk_free_rate()
    ann_ret = annualized_return(returns, periods_per_year)
    ann_vol = annualized_volatility(returns, periods_per_year)
    if ann_vol == 0:
        return 0.0
    return float((ann_ret - rf) / ann_vol)


def sortino_ratio(
    returns: pd.Series,
    rf: float | None = None,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """
    Sortino Ratio = (annualized_return - rf) / annualized_downside_deviation
    """
    if rf is None:
        rf = get_risk_free_rate()
    ann_ret = annualized_return(returns, periods_per_year)
    dd = downside_deviation(returns, mar=rf / periods_per_year)
    ann_dd = dd * np.sqrt(periods_per_year)
    if ann_dd == 0:
        return 0.0
    return float((ann_ret - rf) / ann_dd)


def calmar_ratio(
    returns: pd.Series,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """
    Calmar Ratio = annualized_return / |max_drawdown|
    """
    ann_ret = annualized_return(returns, periods_per_year)
    mdd = max_drawdown(returns)
    if mdd == 0:
        return 0.0
    return float(ann_ret / abs(mdd))


def cagr(prices: pd.Series) -> float:
    """
    Compound Annual Growth Rate.

    CAGR = (end_price / start_price)^(1 / years) - 1
    """
    if len(prices) < 2:
        return 0.0
    start_price = float(prices.iloc[0])
    end_price = float(prices.iloc[-1])
    if start_price <= 0:
        return 0.0
    days = (prices.index[-1] - prices.index[0]).days
    if days <= 0:
        return 0.0
    years = days / 365.25
    return float((end_price / start_price) ** (1 / years) - 1)


def information_ratio(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Information Ratio = mean(excess_return) / tracking_error."""
    excess = returns - benchmark_returns
    te = float(excess.std() * np.sqrt(TRADING_DAYS_PER_YEAR))
    if te == 0:
        return 0.0
    return float(excess.mean() * TRADING_DAYS_PER_YEAR / te)


def tracking_error(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Annualized tracking error = std(excess_returns) * sqrt(252)."""
    excess = returns - benchmark_returns
    return float(excess.std() * np.sqrt(TRADING_DAYS_PER_YEAR))


def alpha_beta(
    returns: pd.Series,
    benchmark_returns: pd.Series,
    rf: float | None = None,
) -> tuple[float, float]:
    """
    CAPM alpha and beta via linear regression.

    returns = alpha + beta * benchmark_returns + epsilon
    """
    if rf is None:
        rf = get_risk_free_rate()
    daily_rf = rf / TRADING_DAYS_PER_YEAR

    y = returns - daily_rf
    x = benchmark_returns - daily_rf

    # Align lengths
    aligned = pd.concat([y, x], axis=1).dropna()
    if len(aligned) < 2:
        return 0.0, 1.0

    y_aligned = aligned.iloc[:, 0]
    x_aligned = aligned.iloc[:, 1]

    slope, intercept, _, _, _ = stats.linregress(x_aligned, y_aligned)
    # Annualize alpha
    alpha_annual = float(intercept * TRADING_DAYS_PER_YEAR)
    return alpha_annual, float(slope)


def beta(returns: pd.Series, benchmark_returns: pd.Series, rf: float | None = None) -> float:
    """CAPM beta."""
    _, b = alpha_beta(returns, benchmark_returns, rf)
    return b


def alpha(returns: pd.Series, benchmark_returns: pd.Series, rf: float | None = None) -> float:
    """CAPM alpha (annualized)."""
    a, _ = alpha_beta(returns, benchmark_returns, rf)
    return a


def correlation_with_benchmark(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Pearson correlation between asset and benchmark returns."""
    aligned = pd.concat([returns, benchmark_returns], axis=1).dropna()
    if len(aligned) < 2:
        return 0.0
    return float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))


# ======================================================================
# Section 5 — Drawdowns
# ======================================================================

def equity_curve(returns: pd.Series, initial: float = 1.0) -> pd.Series:
    """Growth of $initial invested. Equity curve = initial * cumprod(1 + r)."""
    return initial * (1 + returns).cumprod()


def drawdown_series(returns: pd.Series) -> pd.Series:
    """
    Drawdown series: how far below the running maximum at each point.

    Returns negative values (e.g. -0.10 = 10% drawdown).
    """
    eq = equity_curve(returns)
    running_max = eq.cummax()
    return (eq - running_max) / running_max


def max_drawdown(returns: pd.Series) -> float:
    """Maximum drawdown (negative number, e.g. -0.25 = 25% loss)."""
    dd = drawdown_series(returns)
    return float(dd.min())


def max_drawdown_details(returns: pd.Series) -> dict:
    """
    Detailed information about the maximum drawdown.

    Returns dict with: start, bottom, recovery, duration_days, max_dd.
    """
    eq = equity_curve(returns)
    running_max = eq.cummax()
    dd = (eq - running_max) / running_max

    bottom_idx = dd.idxmin()
    bottom_val = float(dd.min())

    # Find the peak before the bottom
    peak_eq = running_max.loc[:bottom_idx].iloc[-1]
    peak_dates = eq.loc[:bottom_idx][eq.loc[:bottom_idx] == peak_eq].index
    start_idx = peak_dates[0] if len(peak_dates) > 0 else dd.index[0]

    # Find recovery (first time equity returns to peak after bottom)
    post_bottom = eq.loc[bottom_idx:]
    recovery_dates = post_bottom[post_bottom >= peak_eq].index
    recovery_idx = recovery_dates[0] if len(recovery_dates) > 0 else None

    duration = None
    if recovery_idx is not None:
        duration = (recovery_idx - start_idx).days

    return {
        "max_dd": bottom_val,
        "start": start_idx.date() if hasattr(start_idx, "date") else start_idx,
        "bottom": bottom_idx.date() if hasattr(bottom_idx, "date") else bottom_idx,
        "recovery": recovery_idx.date() if recovery_idx is not None and hasattr(recovery_idx, "date") else recovery_idx,
        "duration_days": duration,
    }


def top_n_drawdowns(returns: pd.Series, n: int = 5) -> list[dict]:
    """
    Find the top-N largest drawdowns.

    Identifies separate drawdown periods and returns details for each.
    """
    eq = equity_curve(returns)
    running_max = eq.cummax()
    dd = (eq - running_max) / running_max

    drawdowns = []
    in_drawdown = False
    current_start = None
    current_bottom = None
    current_bottom_val = 0.0

    for i, (idx, val) in enumerate(dd.items()):
        if val < 0:
            if not in_drawdown:
                in_drawdown = True
                current_start = idx
                current_bottom = idx
                current_bottom_val = val
            elif val < current_bottom_val:
                current_bottom = idx
                current_bottom_val = val
        else:
            if in_drawdown:
                drawdowns.append({
                    "max_dd": current_bottom_val,
                    "start": current_start.date() if hasattr(current_start, "date") else current_start,
                    "bottom": current_bottom.date() if hasattr(current_bottom, "date") else current_bottom,
                    "recovery": idx.date() if hasattr(idx, "date") else idx,
                })
                in_drawdown = False

    # Handle ongoing drawdown
    if in_drawdown:
        drawdowns.append({
            "max_dd": current_bottom_val,
            "start": current_start.date() if hasattr(current_start, "date") else current_start,
            "bottom": current_bottom.date() if hasattr(current_bottom, "date") else current_bottom,
            "recovery": None,
        })

    # Sort by magnitude and take top N
    drawdowns.sort(key=lambda x: x["max_dd"])
    return drawdowns[:n]


def average_drawdown(returns: pd.Series) -> float:
    """Average drawdown value (negative number)."""
    dd = drawdown_series(returns)
    dd_periods = dd[dd < 0]
    if len(dd_periods) == 0:
        return 0.0
    return float(dd_periods.mean())


# ======================================================================
# Section 6 — Volume Analysis
# ======================================================================

def avg_volume(volume: pd.Series) -> float:
    """Average daily trading volume."""
    return float(volume.mean())


def rolling_avg_volume(volume: pd.Series, window: int = 21) -> pd.Series:
    """Rolling average volume."""
    return volume.rolling(window).mean()


def anomalous_volume_days(
    volume: pd.Series,
    threshold: float = 2.0,
) -> pd.DataFrame:
    """
    Find days with anomalously high volume (>threshold * rolling mean).

    Returns DataFrame with date, volume, rolling_avg, ratio.
    """
    rolling_avg = volume.rolling(21).mean()
    ratio = volume / rolling_avg
    mask = ratio > threshold
    result = pd.DataFrame({
        "volume": volume[mask],
        "rolling_avg": rolling_avg[mask],
        "ratio": ratio[mask],
    })
    return result.sort_values("ratio", ascending=False)


def volume_return_correlation(volume: pd.Series, returns: pd.Series) -> float:
    """Pearson correlation between volume and absolute returns."""
    aligned = pd.concat([volume, returns.abs()], axis=1).dropna()
    if len(aligned) < 2:
        return 0.0
    return float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))


# ======================================================================
# Section 14 — Technical Indicators
# ======================================================================

def sma(prices: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return prices.rolling(window).mean()


def ema(prices: pd.Series, window: int) -> pd.Series:
    """Exponential Moving Average."""
    return prices.ewm(span=window, adjust=False).mean()


def bollinger_bands(
    prices: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> pd.DataFrame:
    """
    Bollinger Bands: middle (SMA), upper, lower.
    """
    middle = sma(prices, window)
    std = prices.rolling(window).std()
    return pd.DataFrame({
        "middle": middle,
        "upper": middle + num_std * std,
        "lower": middle - num_std * std,
    })


def rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """
    Relative Strength Index.
    """
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
    avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """
    MACD: macd_line, signal_line, histogram.
    """
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram,
    })


def momentum(prices: pd.Series, window: int) -> pd.Series:
    """Momentum: price_t - price_{t-window}."""
    return prices - prices.shift(window)


def rate_of_change(prices: pd.Series, window: int) -> pd.Series:
    """Rate of Change: (price_t - price_{t-window}) / price_{t-window}."""
    return (prices - prices.shift(window)) / prices.shift(window)


def zscore_price(prices: pd.Series, window: int) -> pd.Series:
    """Z-score of price relative to rolling window."""
    roll_mean = prices.rolling(window).mean()
    roll_std = prices.rolling(window).std()
    return (prices - roll_mean) / roll_std


def zscore_returns(returns: pd.Series, window: int) -> pd.Series:
    """Z-score of returns relative to rolling window."""
    roll_mean = returns.rolling(window).mean()
    roll_std = returns.rolling(window).std()
    return (returns - roll_mean) / roll_std


def distance_from_ma(prices: pd.Series, window: int) -> pd.Series:
    """Percentage distance from moving average."""
    ma = sma(prices, window)
    return (prices - ma) / ma


def rolling_high(prices: pd.Series, window: int) -> pd.Series:
    """Rolling maximum price."""
    return prices.rolling(window).max()


def rolling_low(prices: pd.Series, window: int) -> pd.Series:
    """Rolling minimum price."""
    return prices.rolling(window).min()


# ======================================================================
# Section 20 — Rolling Analysis
# ======================================================================

def rolling_beta(
    returns: pd.Series,
    benchmark_returns: pd.Series,
    window: int = 63,
) -> pd.Series:
    """Rolling CAPM beta."""
    aligned = pd.concat([returns, benchmark_returns], axis=1).dropna()
    r = aligned.iloc[:, 0]
    b = aligned.iloc[:, 1]
    cov = r.rolling(window).cov(b)
    var = b.rolling(window).var()
    return cov / var


def rolling_correlation(
    returns: pd.Series,
    benchmark_returns: pd.Series,
    window: int = 63,
) -> pd.Series:
    """Rolling correlation between returns and benchmark."""
    aligned = pd.concat([returns, benchmark_returns], axis=1).dropna()
    return aligned.iloc[:, 0].rolling(window).corr(aligned.iloc[:, 1])


def rolling_max_drawdown(returns: pd.Series, window: int = 252) -> pd.Series:
    """Rolling maximum drawdown over a window."""
    result = pd.Series(index=returns.index, dtype=float)
    for i in range(window, len(returns)):
        window_returns = returns.iloc[i - window:i]
        result.iloc[i] = max_drawdown(window_returns)
    return result


def rolling_var(
    returns: pd.Series,
    window: int = 252,
    confidence: float = 0.95,
) -> pd.Series:
    """Rolling historical VaR."""
    return returns.rolling(window).quantile(1 - confidence)


def rolling_skewness(returns: pd.Series, window: int = 252) -> pd.Series:
    """Rolling skewness."""
    return returns.rolling(window).skew()


def rolling_kurtosis(returns: pd.Series, window: int = 252) -> pd.Series:
    """Rolling excess kurtosis."""
    return returns.rolling(window).kurt()


# ======================================================================
# Section 19 — Asset Comparison
# ======================================================================

def compare_assets(
    price_dict: dict[str, pd.Series],
    rf: float | None = None,
) -> pd.DataFrame:
    """
    Compare multiple assets across all key metrics.

    Parameters
    ----------
    price_dict : dict[str, pd.Series]
        Mapping of symbol → adjusted close prices.

    Returns
    -------
    pd.DataFrame
        Comparison table with assets as rows and metrics as columns.
    """
    if rf is None:
        rf = get_risk_free_rate()

    rows = []
    for symbol, prices in price_dict.items():
        rets = simple_returns(prices)
        rows.append({
            "symbol": symbol,
            "total_return": total_return(rets),
            "annualized_return": annualized_return(rets),
            "annualized_volatility": annualized_volatility(rets),
            "sharpe_ratio": sharpe_ratio(rets, rf),
            "sortino_ratio": sortino_ratio(rets, rf),
            "calmar_ratio": calmar_ratio(rets),
            "max_drawdown": max_drawdown(rets),
            "skewness": skewness(rets),
            "kurtosis": kurtosis(rets),
            "best_day": rets.max(),
            "worst_day": rets.min(),
        })

    return pd.DataFrame(rows).set_index("symbol")


def rank_assets(
    price_dict: dict[str, pd.Series],
    metric: str = "sharpe_ratio",
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Rank assets by a given metric.

    Parameters
    ----------
    metric : str
        Column name from compare_assets output.
    ascending : bool
        If True, lower is better (e.g. max_drawdown).
    """
    comparison = compare_assets(price_dict)
    return comparison.sort_values(metric, ascending=ascending)


# ======================================================================
# Full Asset Report
# ======================================================================

def full_asset_report(
    prices: pd.Series,
    symbol: str = "UNKNOWN",
    benchmark_prices: pd.Series | None = None,
    rf: float | None = None,
) -> AssetMetrics:
    """
    Generate a complete metrics report for a single asset.

    Parameters
    ----------
    prices : pd.Series
        Adjusted close prices with DatetimeIndex.
    symbol : str
        Ticker symbol.
    benchmark_prices : pd.Series or None
        Benchmark prices for relative metrics.
    rf : float or None
        Risk-free rate. Uses config default if None.

    Returns
    -------
    AssetMetrics
        Full Pydantic schema with all metrics.
    """
    if rf is None:
        rf = get_risk_free_rate()

    rets = simple_returns(prices)

    best_d, best_v = best_day(rets)
    worst_d, worst_v = worst_day(rets)
    dd_details = max_drawdown_details(rets)

    result = {
        "symbol": symbol,
        "start_date": prices.index[0].date() if hasattr(prices.index[0], "date") else prices.index[0],
        "end_date": prices.index[-1].date() if hasattr(prices.index[-1], "date") else prices.index[-1],
        "start_price": float(prices.iloc[0]),
        "end_price": float(prices.iloc[-1]),

        # Returns
        "total_return": total_return(rets),
        "annualized_return": annualized_return(rets),
        "average_daily_return": float(rets.mean()),
        "median_daily_return": float(rets.median()),
        "best_daily_return": best_v,
        "best_daily_return_date": best_d,
        "worst_daily_return": worst_v,
        "worst_daily_return_date": worst_d,

        # Risk
        "annualized_volatility": annualized_volatility(rets),
        "daily_volatility": daily_volatility(rets),
        "downside_deviation": downside_deviation(rets),
        "skewness": skewness(rets),
        "kurtosis": kurtosis(rets),

        # Performance
        "sharpe_ratio": sharpe_ratio(rets, rf),
        "sortino_ratio": sortino_ratio(rets, rf),
        "calmar_ratio": calmar_ratio(rets),
        "cagr": cagr(prices),

        # Drawdown
        "max_drawdown": dd_details["max_dd"],
        "max_drawdown_start": dd_details["start"],
        "max_drawdown_bottom": dd_details["bottom"],
        "max_drawdown_recovery": dd_details["recovery"],
        "max_drawdown_duration_days": dd_details["duration_days"],
    }

    # Benchmark comparison
    if benchmark_prices is not None:
        bench_rets = simple_returns(benchmark_prices)
        # Align
        aligned = pd.concat([rets, bench_rets], axis=1).dropna()
        asset_rets = aligned.iloc[:, 0]
        bench_rets_aligned = aligned.iloc[:, 1]

        a, b = alpha_beta(asset_rets, bench_rets_aligned, rf)
        result.update({
            "benchmark_symbol": "SPY",
            "beta": b,
            "alpha": a,
            "correlation_with_benchmark": correlation_with_benchmark(asset_rets, bench_rets_aligned),
            "tracking_error": tracking_error(asset_rets, bench_rets_aligned),
            "information_ratio": information_ratio(asset_rets, bench_rets_aligned),
        })

    return AssetMetrics(**result)
