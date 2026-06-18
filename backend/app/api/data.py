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


def _clamp_limit(limit: int, default: int = 100, maximum: int = 500) -> int:
    if limit <= 0:
        return default
    return min(limit, maximum)


@router.get("/symbols")
def get_symbols():
    """List default tickers, downloaded symbols, and registry size."""
    storage_status = "ok"
    try:
        available = DataService.get_available_symbols()
    except Exception:
        available = []
        storage_status = "unavailable"
    registry = get_ticker_registry()
    return {
        "default_tickers": DEFAULT_TICKERS,
        "available": available,
        "registry_count": len(registry),
        "storage_status": storage_status,
    }


@router.get("/symbols/registry")
def get_symbol_registry(limit: int = 100, offset: int = 0):
    """Return a paginated slice of all SEC tickers from company_tickers.json."""
    registry = get_ticker_registry()
    items = [{"ticker": ticker, "name": name} for ticker, name in registry.items()]
    safe_limit = _clamp_limit(limit)
    safe_offset = max(offset, 0)
    return {
        "total": len(items),
        "limit": safe_limit,
        "offset": safe_offset,
        "results": items[safe_offset:safe_offset + safe_limit],
    }


@router.get("/symbols/search")
def search_symbols(q: str = "", limit: int = 100):
    """Search tickers from the SEC registry."""
    registry = get_ticker_registry()
    safe_limit = _clamp_limit(limit)
    if not q or len(q) < 1:
        preview = [{"ticker": ticker, "name": name} for ticker, name in list(registry.items())[:safe_limit]]
        return {"query": q, "total_matches": len(registry), "results": preview}

    q_upper = q.upper()
    matches = []
    for ticker, name in registry.items():
        name_upper = name.upper()
        if q_upper not in ticker and q_upper not in name_upper:
            continue
        if ticker == q_upper:
            score = 0
        elif ticker.startswith(q_upper):
            score = 1
        elif name_upper.startswith(q_upper):
            score = 2
        elif q_upper in ticker:
            score = 3
        else:
            score = 4
        matches.append((score, ticker, name))

    matches.sort(key=lambda item: (item[0], item[1]))
    results = [{"ticker": ticker, "name": name} for _, ticker, name in matches[:safe_limit]]
    return {"query": q, "total_matches": len(matches), "results": results}


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
