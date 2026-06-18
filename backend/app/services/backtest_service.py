"""
QuantLab Lite — Backtest Service

Engine for backtesting rule-based trading strategies with transaction costs.
Covers spec Sections 15–18, 21.
"""

from __future__ import annotations

import logging
from datetime import date

import numpy as np
import pandas as pd

from app.core.config import TRADING_DAYS_PER_YEAR, get_risk_free_rate
from app.models.schemas import BacktestResult, TradeRecord
from app.services import metrics_service as ms
from app.utils.validation import validate_commission, validate_slippage

logger = logging.getLogger(__name__)


# ======================================================================
# Signal Generation (Section 15)
# ======================================================================

def sma_crossover_signal(prices, short_window=20, long_window=50):
    sma_s = prices.rolling(short_window).mean()
    sma_l = prices.rolling(long_window).mean()
    return (sma_s > sma_l).astype(int)


def momentum_signal(prices, lookback=60):
    ret = prices.pct_change(lookback)
    return (ret > 0).astype(int)


def mean_reversion_signal(prices, window=20, threshold=0.03):
    sma_val = prices.rolling(window).mean()
    dist = (prices - sma_val) / sma_val
    sig = pd.Series(0, index=prices.index)
    in_pos = False
    for i in range(len(prices)):
        if pd.isna(dist.iloc[i]):
            continue
        if not in_pos and dist.iloc[i] < -threshold:
            in_pos = True
        elif in_pos and dist.iloc[i] > 0:
            in_pos = False
        sig.iloc[i] = 1 if in_pos else 0
    return sig


def rsi_signal(prices, window=14, oversold=30, overbought=70):
    rsi_vals = ms.rsi(prices, window)
    sig = pd.Series(0, index=prices.index)
    in_pos = False
    for i in range(len(prices)):
        if pd.isna(rsi_vals.iloc[i]):
            continue
        if not in_pos and rsi_vals.iloc[i] < oversold:
            in_pos = True
        elif in_pos and rsi_vals.iloc[i] > overbought:
            in_pos = False
        sig.iloc[i] = 1 if in_pos else 0
    return sig


def bollinger_signal(prices, window=20, num_std=2.0):
    bands = ms.bollinger_bands(prices, window, num_std)
    sig = pd.Series(0, index=prices.index)
    in_pos = False
    for i in range(len(prices)):
        lo = bands["lower"].iloc[i]
        hi = bands["upper"].iloc[i]
        p = prices.iloc[i]
        if pd.isna(lo) or pd.isna(hi):
            continue
        if not in_pos and p < lo:
            in_pos = True
        elif in_pos and p > hi:
            in_pos = False
        sig.iloc[i] = 1 if in_pos else 0
    return sig


def get_signal(prices, strategy, params=None):
    if params is None:
        params = {}
    s = strategy.lower()
    if s == "buy_and_hold":
        return pd.Series(1, index=prices.index)
    elif s == "sma_crossover":
        return sma_crossover_signal(prices, params.get("short_window", 20), params.get("long_window", 50))
    elif s == "momentum":
        return momentum_signal(prices, params.get("lookback", 60))
    elif s == "mean_reversion":
        return mean_reversion_signal(prices, params.get("window", 20), params.get("threshold", 0.03))
    elif s == "rsi":
        return rsi_signal(prices, params.get("window", 14), params.get("oversold", 30), params.get("overbought", 70))
    elif s == "bollinger_bands":
        return bollinger_signal(prices, params.get("window", 20), params.get("num_std", 2.0))
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


# ======================================================================
# Backtesting Engine (Section 17)
# ======================================================================

def run_backtest(prices, signal, commission=0.001, slippage=0.0005):
    """Run backtest. Positions shifted by 1 day to prevent look-ahead bias."""
    validate_commission(commission)
    validate_slippage(slippage)
    returns = prices.pct_change().dropna()
    signal = signal.reindex(returns.index).fillna(0).astype(int)
    positions = signal.shift(1).fillna(0).astype(int)
    trades_mask = positions.diff().fillna(0).abs()
    cost_per_trade = commission + slippage
    transaction_costs = trades_mask * cost_per_trade
    returns_gross = positions * returns
    returns_net = returns_gross - transaction_costs
    equity = (1 + returns_net).cumprod()
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    return {
        "equity_curve": equity, "drawdown": drawdown, "positions": positions,
        "signal": signal, "returns_gross": returns_gross, "returns_net": returns_net,
        "trades_mask": trades_mask, "transaction_costs": transaction_costs,
        "benchmark_returns": returns.copy(),
    }


def extract_trades(prices, positions):
    """Extract individual trades from position series."""
    trades = []
    in_trade = False
    entry_date = entry_price = None
    p = prices.reindex(positions.index)
    for i in range(len(positions)):
        dt = positions.index[i]
        pos = positions.iloc[i]
        price = p.iloc[i]
        if pd.isna(price):
            continue
        if not in_trade and pos == 1:
            in_trade, entry_date, entry_price = True, dt, price
        elif in_trade and pos == 0:
            in_trade = False
            ret = (price / entry_price) - 1
            trades.append(TradeRecord(
                entry_date=entry_date.date() if hasattr(entry_date, "date") else entry_date,
                exit_date=dt.date() if hasattr(dt, "date") else dt,
                entry_price=float(entry_price), exit_price=float(price),
                return_pct=float(ret), holding_days=(dt - entry_date).days, direction="long",
            ))
    if in_trade and entry_price is not None:
        last_idx = positions.index[-1]
        last_price = p.iloc[-1]
        if not pd.isna(last_price):
            trades.append(TradeRecord(
                entry_date=entry_date.date() if hasattr(entry_date, "date") else entry_date,
                exit_date=last_idx.date() if hasattr(last_idx, "date") else last_idx,
                entry_price=float(entry_price), exit_price=float(last_price),
                return_pct=float((last_price / entry_price) - 1),
                holding_days=(last_idx - entry_date).days, direction="long",
            ))
    return trades


def strategy_metrics(backtest_data, prices, rf=None):
    if rf is None:
        rf = get_risk_free_rate()
    equity = backtest_data["equity_curve"]
    rn = backtest_data["returns_net"]
    pos = backtest_data["positions"]
    br = backtest_data["benchmark_returns"]
    trades = extract_trades(prices, pos)
    trade_rets = [t.return_pct for t in trades]
    n_trades = len(trades)
    winning = [r for r in trade_rets if r > 0]
    a, b = ms.alpha_beta(rn, br, rf)
    return {
        "total_return": ms.total_return(rn), "annualized_return": ms.annualized_return(rn),
        "annualized_volatility": ms.annualized_volatility(rn), "sharpe_ratio": ms.sharpe_ratio(rn, rf),
        "sortino_ratio": ms.sortino_ratio(rn, rf), "calmar_ratio": ms.calmar_ratio(rn),
        "max_drawdown": ms.max_drawdown(rn), "final_equity": float(equity.iloc[-1]),
        "win_rate": len(winning) / n_trades if n_trades > 0 else 0.0,
        "num_trades": n_trades,
        "avg_trade_return": float(np.mean(trade_rets)) if trade_rets else 0.0,
        "best_trade": max(trade_rets) if trade_rets else 0.0,
        "worst_trade": min(trade_rets) if trade_rets else 0.0,
        "exposure": float(pos.mean()), "turnover": float(pos.diff().abs().sum() / len(pos)),
        "benchmark_return": ms.total_return(br), "alpha_vs_benchmark": a, "strategy_beta": b,
        "trades": trades,
    }


def break_even_cost(returns_gross, benchmark_returns, trades_mask):
    excess = ms.total_return(returns_gross) - ms.total_return(benchmark_returns)
    total_trades = float(trades_mask.sum())
    return excess / total_trades if total_trades > 0 else float("inf")


def classify_regime(benchmark_returns, window=63):
    rolling_ret = benchmark_returns.rolling(window).mean() * TRADING_DAYS_PER_YEAR
    regime = pd.Series("sideways", index=benchmark_returns.index)
    regime[rolling_ret > 0.05] = "bull"
    regime[rolling_ret < -0.05] = "bear"
    return regime


def strategy_by_regime(returns_net, regimes):
    results = {}
    for name in ["bull", "bear", "sideways"]:
        mask = regimes == name
        if mask.sum() == 0:
            continue
        r = returns_net[mask]
        results[name] = {
            "total_return": ms.total_return(r), "annualized_return": ms.annualized_return(r),
            "sharpe_ratio": ms.sharpe_ratio(r), "max_drawdown": ms.max_drawdown(r),
            "num_days": int(mask.sum()),
        }
    return results


def full_backtest(prices, symbol, strategy, params=None, commission=0.001, slippage=0.0005, rf=None):
    if params is None:
        params = {}
    signal = get_signal(prices, strategy, params)
    data = run_backtest(prices, signal, commission, slippage)
    metrics = strategy_metrics(data, prices, rf)
    eq = data["equity_curve"]
    dd = data["drawdown"]
    sig = data["signal"]
    return BacktestResult(
        symbol=symbol, strategy=strategy, params=params,
        start_date=eq.index[0].date() if hasattr(eq.index[0], "date") else eq.index[0],
        end_date=eq.index[-1].date() if hasattr(eq.index[-1], "date") else eq.index[-1],
        commission=commission, slippage=slippage,
        total_return=metrics["total_return"], annualized_return=metrics["annualized_return"],
        annualized_volatility=metrics["annualized_volatility"], sharpe_ratio=metrics["sharpe_ratio"],
        sortino_ratio=metrics["sortino_ratio"], calmar_ratio=metrics["calmar_ratio"],
        max_drawdown=metrics["max_drawdown"], final_equity=metrics["final_equity"],
        win_rate=metrics["win_rate"], num_trades=metrics["num_trades"],
        avg_trade_return=metrics["avg_trade_return"], best_trade=metrics["best_trade"],
        worst_trade=metrics["worst_trade"], exposure=metrics["exposure"], turnover=metrics["turnover"],
        benchmark_return=metrics["benchmark_return"], alpha_vs_benchmark=metrics["alpha_vs_benchmark"],
        strategy_beta=metrics["strategy_beta"],
        equity_curve_dates=[d.strftime("%Y-%m-%d") for d in eq.index],
        equity_curve_values=eq.tolist(), drawdown_values=dd.tolist(),
        signal_values=sig.reindex(eq.index).fillna(0).astype(int).tolist(),
        trades=metrics["trades"],
    )


def compare_strategies(prices, symbol, strategies, commission=0.001, slippage=0.0005):
    rows = []
    for name, params in strategies.items():
        r = full_backtest(prices, symbol, name, params, commission, slippage)
        rows.append({"strategy": name, "total_return": r.total_return, "sharpe_ratio": r.sharpe_ratio,
                      "max_drawdown": r.max_drawdown, "win_rate": r.win_rate, "num_trades": r.num_trades,
                      "exposure": r.exposure, "alpha_vs_benchmark": r.alpha_vs_benchmark})
    return pd.DataFrame(rows).set_index("strategy")


def get_available_strategies():
    return [
        {"name": "buy_and_hold", "display_name": "Buy and Hold", "params": {}},
        {"name": "sma_crossover", "display_name": "SMA Crossover", "params": {"short_window": 20, "long_window": 50}},
        {"name": "momentum", "display_name": "Momentum", "params": {"lookback": 60}},
        {"name": "mean_reversion", "display_name": "Mean Reversion", "params": {"window": 20, "threshold": 0.03}},
        {"name": "rsi", "display_name": "RSI Strategy", "params": {"window": 14, "oversold": 30, "overbought": 70}},
        {"name": "bollinger_bands", "display_name": "Bollinger Bands", "params": {"window": 20, "num_std": 2.0}},
    ]
