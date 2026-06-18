"""Data API — download, load, status endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.data_service import DataService
from app.core.config import DEFAULT_TICKERS, get_ticker_registry
from app.core.exceptions import TickerNotFoundError, DataNotAvailableError

router = APIRouter()


class DownloadRequest(BaseModel):
    symbol: str
    start_date: str | None = None
    end_date: str | None = None
    interval: str = "1d"


@router.get("/symbols")
def get_symbols():
    """List default tickers and available (downloaded) symbols."""
    available = DataService.get_available_symbols()
    return {"default_tickers": DEFAULT_TICKERS, "available": available}


@router.get("/symbols/search")
def search_symbols(q: str = ""):
    """Search tickers from the SEC registry."""
    if not q or len(q) < 1:
        return {"results": []}
    registry = get_ticker_registry()
    q_upper = q.upper()
    results = [
        {"ticker": ticker, "name": name}
        for ticker, name in registry.items()
        if q_upper in ticker or q_upper in name.upper()
    ][:50]
    return {"results": results}


@router.post("/download")
def download_data(req: DownloadRequest):
    """Download price data from yfinance and save to database."""
    try:
        df = DataService.download_prices(req.symbol, req.start_date, req.end_date, req.interval)
        rows = DataService.save_prices(req.symbol, df, req.interval)
        return {"symbol": req.symbol, "rows_saved": rows, "status": "ok"}
    except TickerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}")
def get_data(symbol: str, start_date: str = None, end_date: str = None, interval: str = "1d"):
    """Get stored price data for a symbol."""
    try:
        df = DataService.load_prices(symbol, start_date, end_date, interval)
        records = []
        for idx, row in df.iterrows():
            records.append({
                "date": idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx),
                "open": row.get("open"), "high": row.get("high"),
                "low": row.get("low"), "close": row.get("close"),
                "adjusted_close": row.get("adjusted_close"), "volume": row.get("volume"),
            })
        return {"symbol": symbol.upper(), "count": len(records), "data": records}
    except DataNotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/status")
def get_status(symbol: str, interval: str = "1d"):
    """Get data freshness status."""
    status = DataService.get_symbol_status(symbol, interval)
    if status is None:
        return {"symbol": symbol.upper(), "status": "no_data"}
    return status.model_dump()
