"""Portfolio API — analyze and optimize portfolios."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.data_service import DataService
from app.services import portfolio_service as ps
from app.services import optimizer_service as opt
from app.services import metrics_service as ms
from app.core.config import get_risk_free_rate
from app.core.exceptions import DataNotAvailableError, InvalidWeightsError

router = APIRouter()


class AnalyzeRequest(BaseModel):
    symbols: list[str]
    weights: list[float]
    start_date: str | None = None
    end_date: str | None = None
    benchmark: str = "SPY"
    interval: str = "1d"


class OptimizeRequest(BaseModel):
    symbols: list[str]
    start_date: str | None = None
    end_date: str | None = None
    num_portfolios: int = 10000
    interval: str = "1d"
    min_weight: float = 0.0
    max_weight: float = 1.0


@router.post("/analyze")
def analyze_portfolio(req: AnalyzeRequest):
    try:
        data = DataService.load_multiple(req.symbols, req.start_date, req.end_date, req.interval)
        returns_df = _build_returns_df(data)
        bench_rets = None
        if req.benchmark:
            try:
                bench_df = DataService.load_prices(req.benchmark, req.start_date, req.end_date, req.interval)
                bench_rets = ms.simple_returns(bench_df["adjusted_close"])
            except Exception:
                pass
        result = ps.portfolio_metrics(returns_df, req.weights, bench_rets, req.benchmark, get_risk_free_rate())
        corr = ps.correlation_matrix(returns_df)
        cov = ps.covariance_matrix(returns_df)
        return {
            "metrics": result.model_dump(),
            "correlation_matrix": {
                "columns": list(corr.columns),
                "data": corr.values.tolist(),
            },
            "covariance_matrix": {
                "columns": list(cov.columns),
                "data": cov.values.tolist(),
            },
        }
    except (DataNotAvailableError, InvalidWeightsError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/optimize")
def optimize_portfolio(req: OptimizeRequest):
    try:
        data = DataService.load_multiple(req.symbols, req.start_date, req.end_date, req.interval)
        returns_df = _build_returns_df(data)
        result = opt.optimize(returns_df, req.num_portfolios, get_risk_free_rate(), req.min_weight, req.max_weight)
        return result.model_dump()
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _build_returns_df(data: dict):
    import pandas as pd
    frames = {}
    for symbol, df in data.items():
        frames[symbol] = ms.simple_returns(df["adjusted_close"])
    returns_df = pd.DataFrame(frames).dropna()
    return returns_df
