import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dataApi = {
  getSymbols: () => client.get('/data/symbols'),
  getRegistry: (limit = 100, offset = 0) =>
    client.get('/data/symbols/registry', { params: { limit, offset } }),
  searchSymbols: (q, limit = 100) =>
    client.get('/data/symbols/search', { params: { q, limit } }),
  downloadData: (symbol, start, end, interval = '1d') =>
    client.post('/data/download', { symbol, start_date: start, end_date: end, interval }),
  loadData: (symbol, start, end, interval = '1d') =>
    client.get(`/data/${symbol}`, { params: { start_date: start, end_date: end, interval } }),
  getStatus: (symbol, interval = '1d') =>
    client.get(`/data/${symbol}/status`, { params: { interval } }),
};

export const assetsApi = {
  getMetrics: (symbol, start, end, interval = '1d') =>
    client.get(`/assets/${symbol}/metrics`, { params: { start_date: start, end_date: end, interval } }),
  getReturns: (symbol, start, end, interval = '1d') =>
    client.get(`/assets/${symbol}/returns`, { params: { start_date: start, end_date: end, interval } }),
  getDrawdown: (symbol, start, end, interval = '1d') =>
    client.get(`/assets/${symbol}/drawdown`, { params: { start_date: start, end_date: end, interval } }),
  getRollingVol: (symbol, window, start, end, interval = '1d') =>
    client.get(`/assets/${symbol}/rolling-volatility`, { params: { window, start_date: start, end_date: end, interval } }),
  getPrice: (symbol, start, end, interval = '1d') =>
    client.get(`/assets/${symbol}/price`, { params: { start_date: start, end_date: end, interval } }),
};

export const portfolioApi = {
  analyze: (symbols, weights, start, end, benchmark = 'SPY', interval = '1d') =>
    client.post('/portfolio/analyze', { symbols, weights, start_date: start, end_date: end, benchmark, interval }),
  optimize: (symbols, start, end, numPortfolios = 10000, minWeight = 0.0, maxWeight = 1.0, interval = '1d') =>
    client.post('/portfolio/optimize', { symbols, start_date: start, end_date: end, num_portfolios: numPortfolios, min_weight: minWeight, max_weight: maxWeight, interval }),
};

export const backtestApi = {
  run: (symbol, strategy, params = {}, commission = 0.001, slippage = 0.0005, start, end, interval = '1d') =>
    client.post('/backtest', { symbol, strategy, params, commission, slippage, start_date: start, end_date: end, interval }),
  getStrategies: () => client.get('/backtest/strategies'),
};

export const riskApi = {
  getVar: (symbol, confidence = 0.95, start, end) =>
    client.get(`/risk/${symbol}/var`, { params: { confidence, start_date: start, end_date: end } }),
  getCvar: (symbol, confidence = 0.95, start, end) =>
    client.get(`/risk/${symbol}/cvar`, { params: { confidence, start_date: start, end_date: end } }),
  getReport: (symbol, confidence = 0.95, start, end) =>
    client.get(`/risk/${symbol}/report`, { params: { confidence, start_date: start, end_date: end } }),
  stressTest: (symbols, weights, shockPct = -0.10, start, end, interval = '1d') =>
    client.post('/risk/stress-test', { symbols, weights, shock_pct: shockPct, start_date: start, end_date: end, interval }),
};
