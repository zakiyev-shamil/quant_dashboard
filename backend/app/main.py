"""
QuantLab Lite — FastAPI Application

Main entry point for the REST API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import data, assets, portfolio, backtest, risk

app = FastAPI(
    title="QuantLab Lite",
    description="Quantitative finance dashboard API for portfolio analysis and backtesting",
    version="0.6.0",
)

# CORS — allow Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(data.router, prefix="/data", tags=["Data"])
app.include_router(assets.router, prefix="/assets", tags=["Assets"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(backtest.router, prefix="/backtest", tags=["Backtest"])
app.include_router(risk.router, prefix="/risk", tags=["Risk"])


@app.get("/")
def root():
    return {"app": "QuantLab Lite", "version": "0.6.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}
