"""Backtest API — run strategy backtests."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.data_service import DataService
from app.services import backtest_service as bt
from app.core.exceptions import DataNotAvailableError

router = APIRouter()


class BacktestRequest(BaseModel):
    symbol: str
    strategy: str
    start_date: str | None = None
    end_date: str | None = None
    params: dict = Field(default_factory=dict)
    commission: float = 0.001
    slippage: float = 0.0005
    interval: str = "1d"


@router.post("")
def run_backtest(req: BacktestRequest):
    try:
        df = DataService.load_prices(req.symbol, req.start_date, req.end_date, req.interval)
        prices = df["adjusted_close"]
        result = bt.full_backtest(prices, req.symbol.upper(), req.strategy, req.params, req.commission, req.slippage)
        return result.model_dump()
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/strategies")
def list_strategies():
    return {"strategies": bt.get_available_strategies()}
