"""Risk API — VaR, CVaR, stress testing."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.data_service import DataService
from app.services import risk_service as rs
from app.services import metrics_service as ms
from app.core.exceptions import DataNotAvailableError

router = APIRouter()


class StressTestRequest(BaseModel):
    symbols: list[str]
    weights: list[float]
    shock_pct: float = -0.10
    start_date: str | None = None
    end_date: str | None = None
    interval: str = "1d"


@router.get("/{symbol}/var")
def get_var(symbol: str, confidence: float = 0.95, start_date: str = None, end_date: str = None):
    try:
        df = DataService.load_prices(symbol, start_date, end_date)
        rets = ms.simple_returns(df["adjusted_close"])
        return {
            "symbol": symbol.upper(), "confidence": confidence,
            "var_historical": rs.historical_var(rets, confidence),
            "var_parametric": rs.parametric_var(rets, confidence),
        }
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/cvar")
def get_cvar(symbol: str, confidence: float = 0.95, start_date: str = None, end_date: str = None):
    try:
        df = DataService.load_prices(symbol, start_date, end_date)
        rets = ms.simple_returns(df["adjusted_close"])
        return {
            "symbol": symbol.upper(), "confidence": confidence,
            "cvar_historical": rs.historical_cvar(rets, confidence),
        }
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/report")
def get_risk_report(symbol: str, confidence: float = 0.95, start_date: str = None, end_date: str = None):
    try:
        df = DataService.load_prices(symbol, start_date, end_date)
        rets = ms.simple_returns(df["adjusted_close"])
        report = rs.full_risk_report(rets, symbol.upper(), confidence)
        return report.model_dump()
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stress-test")
def run_stress_test(req: StressTestRequest):
    try:
        import pandas as pd
        data = DataService.load_multiple(req.symbols, req.start_date, req.end_date, req.interval)
        frames = {sym: ms.simple_returns(df["adjusted_close"]) for sym, df in data.items()}
        returns_df = pd.DataFrame(frames).dropna()
        result = rs.stress_test(returns_df, req.weights, req.shock_pct)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
