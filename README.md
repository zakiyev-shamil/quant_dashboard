# QuantLab Lite

QuantLab Lite - это full-stack dashboard для quantitative finance.
Он загружает исторические цены активов, считает доходность и риск, анализирует портфель, строит Monte Carlo Efficient Frontier и запускает простые backtests.

Проект учебный. Он помогает понять, как работают данные, доходность, drawdown, volatility, Sharpe ratio, VaR/CVaR и стратегии. Это не финансовый совет.

## Что внутри

- `backend/` - FastAPI API, PostgreSQL, yfinance, pandas, NumPy, SciPy.
- `frontend/` - Vue 3 + Vite dashboard, Chart.js графики.
- `backend/db_schema.sql` - схема базы данных.
- `company_tickers.json` - SEC ticker registry для поиска компаний.
- `day1.py` - учебный Python-скрипт с yfinance, pandas и matplotlib.
- `docs/concepts-and-formulas.md` - финансовые понятия и формулы простым языком.

## Что умеет проект

1. Data Manager
   - делает доступными все tickers из `company_tickers.json`
   - ищет tickers по SEC registry
   - загружает OHLCV prices через yfinance
   - сохраняет данные в PostgreSQL
   - показывает, какие symbols уже есть локально

2. Asset Analyzer
   - считает returns
   - считает CAGR, total return, volatility
   - считает Sharpe, Sortino, Calmar
   - строит price chart, cumulative return, drawdown, rolling volatility

3. Portfolio Analyzer
   - принимает список assets и weights
   - считает portfolio returns
   - показывает correlation matrix и covariance matrix
   - считает contribution to return и contribution to risk
   - сравнивает портфель с benchmark

4. Portfolio Optimizer
   - генерирует random portfolios
   - строит Efficient Frontier
   - находит Maximum Sharpe Portfolio
   - находит Minimum Volatility Portfolio

5. Backtesting Lab
   - тестирует buy and hold, SMA crossover, momentum, mean reversion, RSI, Bollinger Bands
   - учитывает commission и slippage
   - сдвигает signal на 1 день, чтобы убрать look-ahead bias

6. Risk Dashboard
   - считает historical VaR
   - считает historical CVaR
   - показывает worst / best return days
   - запускает fixed shock stress test

## Основные формулы

### Returns

Returns - это процентное изменение цены.

```python
returns = prices.pct_change().dropna()
```

Формула:

```text
r_t = P_t / P_(t-1) - 1
```

### Total return

Total return - это общий рост за весь период.

```python
total_return = (1 + returns).prod() - 1
```

### Annualized return

Annualized return - это доходность, приведённая к году.

```python
annualized_return = (1 + total_return) ** (periods_per_year / n_periods) - 1
```

### Wealth index

Wealth index показывает рост $1, вложенного в актив.

```python
wealth_index = (1 + returns).cumprod()
```

### Drawdown

Drawdown - это насколько текущая стоимость ниже прошлого максимума.

```python
previous_peaks = wealth_index.cummax()
drawdowns = (wealth_index - previous_peaks) / previous_peaks
max_drawdown = drawdowns.min()
max_drawdown_date = drawdowns.idxmin()
```

### Volatility

Volatility - это насколько сильно returns двигаются вверх и вниз.

```python
annualized_volatility = returns.std() * np.sqrt(252)
```

### Sharpe ratio

Sharpe ratio показывает доходность сверх risk-free rate на единицу риска.

```python
sharpe = (annualized_return - risk_free_rate) / annualized_volatility
```

### Portfolio returns

Portfolio return - это сумма returns активов с учётом weights.

```python
portfolio_returns = returns_df.dot(weights)
```

Формула:

```text
R_portfolio = w1*r1 + w2*r2 + ... + wn*rn
```

### Portfolio volatility

```python
portfolio_volatility = np.sqrt(weights.T @ covariance_matrix @ weights)
```

### VaR и CVaR

VaR показывает возможный loss threshold при выбранном confidence level.

```python
var = returns.quantile(1 - confidence)
```

CVaR показывает average loss в плохих случаях, когда loss хуже VaR.

```python
cvar = returns[returns <= var].mean()
```

## Как запустить локально

### 1. Database

Создай PostgreSQL database и выполни schema:

```bash
psql -U your_username -d your_database -f backend/db_schema.sql
```

### 2. Backend env

Создай `backend/.env` по примеру `backend/.env.example`:

```env
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/your_database
RISK_FREE_RATE=0.05
TRADING_DAYS_PER_YEAR=252
DEFAULT_INTERVAL=1d
```

### 3. Backend API

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API будет доступен на `http://localhost:8000`.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на `http://localhost:5173`.

Если backend запущен не на `localhost:8000`, создай `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Проверки перед push

```bash
python -m compileall backend/app day1.py day2.py
cd frontend
npm run build
```

В git нельзя отправлять:

- `backend/.env`
- `backend/.venv/`
- `frontend/node_modules/`
- `frontend/dist/`
- `__pycache__/`
- локальные CSV/XLSX/parquet exports

Корневой `.gitignore` уже закрывает эти файлы.

## Disclaimer

Проект работает с историческими рыночными данными. Прошлая доходность не гарантирует будущую доходность.
Акции, ETF, mutual funds и другие инвестиции могут падать в цене. Можно потерять часть денег или всё вложение.
