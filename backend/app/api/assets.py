"""Assets API — single-asset metrics, returns, drawdown, rolling analytics."""

from fastapi import APIRouter, HTTPException

from app.services.data_service import DataService
from app.services import metrics_service as ms
from app.core.config import get_risk_free_rate
from app.core.exceptions import DataNotAvailableError

router = APIRouter()


def _load_adj_close(symbol, start_date=None, end_date=None, interval="1d"):
    df = DataService.load_prices(symbol, start_date, end_date, interval)
    return df["adjusted_close"]


@router.get("/{symbol}/metrics")
def get_metrics(symbol: str, start_date: str = None, end_date: str = None, interval: str = "1d"):
    try:
        prices = _load_adj_close(symbol, start_date, end_date, interval)
        # Try to load SPY as benchmark
        bench = None
        if symbol.upper() != "SPY":
            try:
                bench = _load_adj_close("SPY", start_date, end_date, interval)
            except Exception:
                pass
        report = ms.full_asset_report(prices, symbol.upper(), bench, get_risk_free_rate())
        return report.model_dump()
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/returns")
def get_returns(symbol: str, start_date: str = None, end_date: str = None, interval: str = "1d"):
    try:
        prices = _load_adj_close(symbol, start_date, end_date, interval)
        rets = ms.simple_returns(prices)
        cum = ms.cumulative_returns(rets)
        return {
            "symbol": symbol.upper(),
            "dates": [d.strftime("%Y-%m-%d") for d in rets.index],
            "daily_returns": rets.tolist(),
            "cumulative_returns": cum.tolist(),
        }
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/drawdown")
def get_drawdown(symbol: str, start_date: str = None, end_date: str = None, interval: str = "1d"):
    try:
        prices = _load_adj_close(symbol, start_date, end_date, interval)
        rets = ms.simple_returns(prices)
        dd = ms.drawdown_series(rets)
        details = ms.max_drawdown_details(rets)
        return {
            "symbol": symbol.upper(),
            "dates": [d.strftime("%Y-%m-%d") for d in dd.index],
            "drawdown": dd.tolist(),
            "max_drawdown": details,
        }
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/rolling-volatility")
def get_rolling_vol(
    symbol: str,
    window: int = 21,
    start_date: str = None,
    end_date: str = None,
    interval: str = "1d",
):
    try:
        prices = _load_adj_close(symbol, start_date, end_date, interval)
        rets = ms.simple_returns(prices)
        rv = ms.rolling_volatility(rets, window).dropna()
        return {
            "symbol": symbol.upper(), "window": window,
            "dates": [d.strftime("%Y-%m-%d") for d in rv.index],
            "rolling_volatility": rv.tolist(),
        }
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/price")
def get_price(symbol: str, start_date: str = None, end_date: str = None, interval: str = "1d"):
    try:
        prices = _load_adj_close(symbol, start_date, end_date, interval)
        return {
            "symbol": symbol.upper(),
            "dates": [d.strftime("%Y-%m-%d") for d in prices.index],
            "prices": prices.tolist(),
        }
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))
