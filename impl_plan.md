информация по проекту который нужно сделать : Этот проект помогает не тем, что “сделаешь дашборд и сразу станешь трейдером”. Он помогает проверить, подходит ли тебе финансовая тема, и собрать портфолио под реальные роли.

Главная польза: ты переводишь универские темы в рабочие сущности.

Регрессия, статистика, временные ряды, оптимизация и стохастика перестают быть абстрактными предметами. Они превращаются в вопросы:

“Какой актив дал больше доходности?”
“Какой актив рискованнее?”
“Как собрать портфель с меньшей просадкой?”
“Почему стратегия красиво выглядит на графике, но с комиссиями умирает?”
“Можно ли доверять результату бэктеста?”
“Что будет с портфелем, если рынок упадёт на 20%?”
“Какие активы реально диверсифицируют друг друга, а какие просто падают вместе?”

То есть проект учит не “предсказывать рынок”, а думать как финансовый инженер.

Практически он помогает в 5 вещах.

Во-первых, ты понимаешь, нравится ли тебе эта область. Сейчас тебе кажется: “финансы, деньги, графики, большие ребята”. После проекта ты увидишь реальность: данные, риски, расчёты, баги, модели, отчёты, ложные сигналы. Если это всё равно интересно — значит, направление твоё.

Во-вторых, ты получаешь портфолио. Не “я знаю Python/FastAPI/Vue”, а:

“Я сделал систему для анализа активов и портфелей: загрузка рыночных данных, расчёт доходности, волатильности, Sharpe, drawdown, корреляций, оптимизация портфеля, бэктест стратегий с комиссиями”.

Это уже звучит как проект под quant developer / financial data analyst / risk analytics / fintech backend.

В-третьих, ты тренируешь именно тот стек, который нужен в финансовой разработке:

Python для расчётов;
pandas/numpy для данных;
FastAPI для сервисов;
PostgreSQL для хранения;
Vue для интерфейса;
Docker для деплоя;
C++ потенциально для ускорения отдельных модулей.

То есть это не учебная тетрадка, а инженерный проект.

В-четвёртых, ты начинаешь понимать, где математика реально нужна.

Пример:
оптимизация нужна, чтобы подобрать веса портфеля;
ковариация нужна, чтобы понять общий риск портфеля;
волатильность нужна, чтобы оценивать риск;
Sharpe нужен, чтобы сравнивать доходность с учётом риска;
drawdown нужен, чтобы видеть, насколько больно стратегия может просесть;
временные ряды нужны, потому что цены — это временные ряды;
GARCH нужен, если хочешь моделировать изменчивую волатильность;
Monte Carlo нужен, если хочешь симулировать сценарии рынка.

В-пятых, проект помогает выбрать карьеру.

После него станет понятнее:

Если тебе больше понравилось строить backend, API, данные, хранение, скорость — тебе ближе quant developer / fintech backend / trading systems developer.

Если больше понравилось исследовать стратегии, риски, гипотезы, портфели — ближе quant analyst / risk analyst / portfolio analytics.

Если больше понравилось делать интерфейс и продукт — ближе fintech product engineer / fullstack developer в finance.

Если не понравилось вообще — хорошо, ты это понял на проекте, а не после магистратуры.

Ещё важный момент: этот проект защищает тебя от финансовой романтики. В фильмах всё выглядит так: умные люди смотрят на экраны и делают деньги. В реальности первый уровень профессионализма — понять, что рынок шумный, бэктесты врут, комиссии важны, риск важнее доходности, а “крутая стратегия” часто разваливается при нормальной проверке.

Поэтому этот проект — это не “машина для денег”. Это тренажёр финансового мышления и доказательство твоих навыков.

Самая ценная версия проекта для резюме выглядела бы так:

“Built a full-stack quantitative finance dashboard for portfolio analysis and backtesting. Implemented data ingestion, return/risk metrics, correlation analysis, Markowitz portfolio optimization, strategy backtesting with transaction costs, and benchmark comparison.” Функционал проекта с одним источником данных — yfinance. Делай как modular monolith: сначала Python core, потом FastAPI, потом Vue.

Название проекта

QuantLab Lite

Смысл: full-stack приложение для анализа активов, портфелей и простых стратегий на исторических данных из yfinance.

1. Data Layer

Источник данных: yfinance.

Функции
Скачать исторические OHLCV-данные
Обновить данные по тикеру
Сохранить данные локально
Загрузить данные из локального хранилища
Проверить пропуски
Проверить дубликаты
Проверить диапазон дат
Поддерживаемые тикеры на старте
SPY
QQQ
TLT
GLD
AAPL
MSFT
NVDA
JPM
XOM
BTC-USD
ETH-USD
Поля данных
symbol
date
open
high
low
close
adjusted_close
volume
source
Локальное хранение

На старте:

/data/raw/{symbol}.parquet
/data/processed/{symbol}.parquet

Позже можно перенести в PostgreSQL.

Backend-функции
download_prices(symbol, start_date, end_date, interval="1d")
save_prices(symbol, df)
load_prices(symbol)
update_prices(symbol)
validate_prices(df)
2. Asset Analyzer

Анализ одного актива.

Функционал
Показать график цены
Показать график cumulative return
Посчитать daily returns
Посчитать log returns
Посчитать total return
Посчитать annualized return
Посчитать annualized volatility
Посчитать Sharpe ratio
Посчитать Sortino ratio
Посчитать max drawdown
Посчитать best day / worst day
Посчитать skewness
Посчитать kurtosis
Показать histogram returns
Показать rolling volatility
Показать rolling mean return
Метрики
Start price
End price
Total return
Annualized return
Annualized volatility
Sharpe ratio
Sortino ratio
Max drawdown
Best daily return
Worst daily return
Average daily return
Median daily return
Skewness
Kurtosis
Минимальный результат

Пользователь выбирает:

Ticker: SPY
Start: 2015-01-01
End: 2025-01-01

Получает:

график цены
график доходности
таблицу метрик
график просадки
3. Portfolio Analyzer

Анализ портфеля с заданными весами.

Функционал
Выбрать несколько тикеров
Задать веса
Проверить, что сумма весов = 100%
Загрузить цены всех активов
Синхронизировать даты
Посчитать доходности каждого актива
Посчитать доходность портфеля
Посчитать cumulative return портфеля
Посчитать annualized return
Посчитать annualized volatility
Посчитать Sharpe ratio
Посчитать max drawdown
Показать correlation matrix
Показать covariance matrix
Показать вклад активов в портфель
Сравнить портфель с benchmark
Пример портфеля
SPY 50%
QQQ 30%
GLD 20%
Benchmark

На старте один benchmark:

SPY
Метрики
Portfolio total return
Portfolio annualized return
Portfolio annualized volatility
Portfolio Sharpe ratio
Portfolio Sortino ratio
Portfolio max drawdown
Benchmark total return
Excess return vs benchmark
Correlation with benchmark
Tracking error
4. Portfolio Optimizer

Оптимизация портфеля.

Сначала не делай сложную математику через scipy.optimize. Начни с random portfolios.

Функционал
Пользователь выбирает тикеры
Пользователь выбирает период
Система генерирует N случайных портфелей
Для каждого портфеля считает return, volatility, Sharpe
Находит портфель с максимальным Sharpe
Находит портфель с минимальной volatility
Показывает efficient frontier scatter plot
Показывает веса оптимальных портфелей
Ограничения на старте
Long-only portfolio
Вес каждого актива >= 0
Сумма весов = 1
Без short selling
Без leverage
Вход
{
  "symbols": ["SPY", "QQQ", "GLD", "TLT"],
  "start": "2015-01-01",
  "end": "2025-01-01",
  "num_portfolios": 10000
}
Выход
Max Sharpe portfolio
Min Volatility portfolio
Efficient frontier
Weights table
5. Backtesting Lab

Бэктест простых стратегий.

Стратегия 1: Buy and Hold
Купил актив в начале периода
Держишь до конца периода
Стратегия 2: SMA Crossover
Если SMA_short > SMA_long → position = 1
Если SMA_short <= SMA_long → position = 0

Параметры:

short_window = 20
long_window = 50
Стратегия 3: Momentum
Если доходность за последние N дней > 0 → position = 1
Иначе → position = 0

Параметры:

lookback = 60
Стратегия 4: Mean Reversion
Если цена ниже SMA_N на X% → buy
Если цена выше SMA_N → exit

Параметры:

window = 20
threshold = 0.03
Обязательные правила
Использовать position вчерашнего дня для сегодняшней доходности
Не допускать look-ahead bias
Учитывать комиссии
Учитывать slippage
Сравнивать с Buy and Hold
Метрики стратегии
Total return
Annualized return
Annualized volatility
Sharpe ratio
Sortino ratio
Max drawdown
Win rate
Number of trades
Average trade return
Best trade
Worst trade
Exposure
Turnover
Final equity
Benchmark return
Alpha vs benchmark
Вход
{
  "symbol": "SPY",
  "strategy": "sma_crossover",
  "start": "2015-01-01",
  "end": "2025-01-01",
  "params": {
    "short_window": 20,
    "long_window": 50
  },
  "commission": 0.001,
  "slippage": 0.0005
}
Выход
Equity curve
Drawdown chart
Signal chart
Trades table
Metrics table
Comparison with Buy and Hold
6. Risk Module

Отдельный модуль для риска.

Функционал
Historical VaR
Historical CVaR
Rolling volatility
Rolling Sharpe
Rolling max drawdown
Worst N days
Best N days
Stress test by fixed shock
VaR / CVaR

Например:

VaR 95%
VaR 99%
CVaR 95%
CVaR 99%
Stress test

Простые сценарии:

Market shock: -5%
Market shock: -10%
Market shock: -20%
Volatility spike

Для портфеля:

Если каждый актив падает на X%, сколько теряет портфель?
Если SPY падает на 20%, что было бы с портфелем при исторической корреляции?

На первом этапе делай простой fixed shock.

7. API на FastAPI

Минимальные endpoints.

Data
GET /symbols
POST /data/download
GET /data/{symbol}
GET /data/{symbol}/status
Asset Analyzer
GET /assets/{symbol}/metrics
GET /assets/{symbol}/returns
GET /assets/{symbol}/drawdown
GET /assets/{symbol}/rolling-volatility
Portfolio
POST /portfolio/analyze
POST /portfolio/optimize
Backtesting
POST /backtest
GET /strategies
Risk
GET /risk/{symbol}/var
GET /risk/{symbol}/cvar
POST /risk/stress-test
8. Frontend на Vue

Страницы:

Home Dashboard
Asset Analyzer
Portfolio Analyzer
Portfolio Optimizer
Backtesting Lab
Risk Dashboard
Data Manager
Home Dashboard

Показывает:

список доступных тикеров
последняя дата обновления данных
мини-карточки по SPY, QQQ, GLD, BTC-USD
Asset Analyzer

Пользователь выбирает:

ticker
start date
end date

Видит:

price chart
cumulative return chart
drawdown chart
metrics table
returns histogram
rolling volatility chart
Portfolio Analyzer

Пользователь выбирает:

тикеры
веса
benchmark
period

Видит:

portfolio equity curve
benchmark comparison
portfolio metrics
correlation matrix
weights chart
drawdown chart
Portfolio Optimizer

Пользователь выбирает:

тикеры
period
number of random portfolios

Видит:

efficient frontier
max Sharpe weights
min volatility weights
metrics table
Backtesting Lab

Пользователь выбирает:

symbol
strategy
parameters
commission
slippage
period

Видит:

equity curve
buy and hold comparison
drawdown chart
trades table
metrics table
signals on price chart
Risk Dashboard

Пользователь выбирает:

symbol или portfolio
confidence level
period

Видит:

VaR
CVaR
worst days
rolling volatility
stress test result
9. Архитектура проекта
quantlab-lite/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── data.py
│   │   │   ├── assets.py
│   │   │   ├── portfolio.py
│   │   │   ├── backtest.py
│   │   │   └── risk.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── services/
│   │   │   ├── data_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── portfolio_service.py
│   │   │   ├── optimizer_service.py
│   │   │   ├── backtest_service.py
│   │   │   └── risk_service.py
│   │   │
│   │   ├── models/
│   │   │   ├── schemas.py
│   │   │   └── enums.py
│   │   │
│   │   └── utils/
│   │       ├── dates.py
│   │       └── validation.py
│   │
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/
│   │   └── charts/
│   └── package.json
│
├── notebooks/
│   ├── 01_data_download.ipynb
│   ├── 02_asset_metrics.ipynb
│   ├── 03_portfolio_analysis.ipynb
│   ├── 04_backtesting.ipynb
│   └── 05_risk.ipynb
│
└── README.md
10. Порядок разработки
Версия 0.1 — только notebook

Сделай в Jupyter:

скачать SPY
посчитать returns
посчитать volatility
посчитать Sharpe
посчитать max drawdown
нарисовать графики
Версия 0.2 — Python modules

Вынеси код в функции:

data_loader.py
metrics.py
plots.py
Версия 0.3 — portfolio

Добавь:

несколько тикеров
веса
portfolio returns
correlation matrix
Версия 0.4 — optimizer

Добавь:

random portfolios
max Sharpe
min volatility
efficient frontier
Версия 0.5 — backtester

Добавь:

buy and hold
SMA crossover
momentum
mean reversion
commission
slippage
Версия 0.6 — FastAPI

Сделай API поверх готовых функций.

Версия 0.7 — Vue

Сделай простой интерфейс.

Версия 1.0 — нормальный README

В README должны быть:

описание проекта
скриншоты
как запустить
какие данные используются
какие метрики считаются
какие ограничения
пример анализа SPY/QQQ/GLD/TLT
11. Что считать “готовым MVP”

MVP готов, если пользователь может:

выбрать тикер
скачать данные через yfinance
увидеть график цены
увидеть доходность и риск
собрать портфель
увидеть корреляции
оптимизировать веса
прогнать простую стратегию
увидеть отчёт бэктеста

То есть минимальный MVP:

Asset Analyzer
Portfolio Analyzer
Backtesting Lab

Optimizer и Risk Dashboard можно добавить после.

12. Что писать в README как ограничения

Обязательно напиши честно:

Проект предназначен для обучения и исследования.
Данные берутся из yfinance.
Данные могут иметь задержки, пропуски или расхождения.
Бэктест не гарантирует будущую доходность.
Комиссии и slippage моделируются упрощённо.
Нет исполнения реальных сделок.
Нет финансовых рекомендаций.

Это важно: проект выглядит профессиональнее, когда ты понимаешь ограничения.

13. Самая короткая формулировка проекта для резюме
Built a full-stack quantitative finance dashboard using Python, FastAPI, Vue, and yfinance. Implemented historical data ingestion, asset risk metrics, portfolio analysis, random portfolio optimization, and backtesting of rule-based trading strategies with transaction costs.

По-русски:

Разработал full-stack приложение для количественного анализа финансовых активов на Python, FastAPI, Vue и yfinance. Реализовал загрузку исторических данных, расчёт метрик риска и доходности, анализ портфеля, случайную оптимизацию портфеля и бэктест торговых стратегий с учётом транзакционных издержек.

Первый конкретный шаг: сделай notebook 01_asset_metrics.ipynb, где по SPY считаются returns, annualized return, annualized volatility, Sharpe, max drawdown и строятся 3 графика: цена, cumulative return, drawdown. Функционал проекта без backend/frontend, только логика и расчёты.

1. Работа с данными из yfinance
Скачать исторические данные по одному тикеру.
Скачать исторические данные по нескольким тикерам.
Выбрать период: start date / end date.
Выбрать интервал данных: 1d, позже можно 1h, 1wk, 1mo.
Получить OHLCV-данные:
Open, High, Low, Close, Adj Close, Volume.
Сохранить данные локально в csv или parquet.
Загрузить уже сохранённые данные.
Проверить пропуски в данных.
Проверить дубликаты дат.
Проверить, есть ли пустые значения в ценах.
Проверить, хватает ли данных для анализа.
Синхронизировать даты для нескольких активов.
Удалить даты, где нет данных хотя бы по одному активу.
Привести данные к единому формату.
Добавить колонку symbol.
Добавить колонку source = yfinance.
2. Доходности
Посчитать простую доходность:

return_t = price_t / price_{t-1} - 1

Посчитать логарифмическую доходность:

log_return_t = ln(price_t / price_{t-1})

Посчитать кумулятивную доходность.
Посчитать доходность за весь период.
Посчитать дневную среднюю доходность.
Посчитать месячную доходность.
Посчитать годовую доходность.
Перевести дневную доходность в годовую.
Сравнить доходности нескольких активов.
Найти лучший день по доходности.
Найти худший день по доходности.
Найти лучшие N дней.
Найти худшие N дней.
3. Риск одного актива
Посчитать дисперсию доходностей.
Посчитать стандартное отклонение доходностей.
Посчитать дневную волатильность.
Посчитать годовую волатильность.
Посчитать rolling volatility.
Посчитать rolling mean return.
Посчитать rolling Sharpe ratio.
Посчитать downside deviation.
Посчитать skewness.
Посчитать kurtosis.
Посчитать медианную доходность.
Посчитать квантили доходностей.
Построить распределение доходностей.
Сравнить распределение доходностей с нормальным распределением.
4. Метрики эффективности
Посчитать Sharpe ratio.
Посчитать Sortino ratio.
Посчитать Calmar ratio.
Посчитать CAGR.
Посчитать total return.
Посчитать excess return над risk-free rate.
Посчитать information ratio.
Посчитать tracking error.
Сравнить актив с benchmark.
Посчитать alpha относительно benchmark.
Посчитать beta относительно benchmark.
Посчитать корреляцию с benchmark.
5. Просадки
Посчитать equity curve.
Посчитать running maximum.
Посчитать drawdown series.
Найти maximum drawdown.
Найти дату начала maximum drawdown.
Найти дату дна maximum drawdown.
Найти дату восстановления после просадки.
Посчитать длительность просадки.
Найти топ-N самых больших просадок.
Посчитать среднюю просадку.
Посчитать время восстановления после просадок.
6. Анализ объёма
Посчитать средний объём торгов.
Посчитать rolling average volume.
Найти дни с аномально высоким объёмом.
Найти дни с аномально низким объёмом.
Посчитать изменение объёма.
Проверить связь между объёмом и доходностью.
Проверить связь между объёмом и волатильностью.
7. Корреляционный анализ
Посчитать корреляцию между активами.
Построить correlation matrix.
Посчитать rolling correlation.
Найти наиболее коррелированные пары.
Найти наименее коррелированные пары.
Найти активы, которые дают диверсификацию.
Сравнить корреляцию в разные периоды.
Проверить корреляцию актива с рынком.
8. Ковариации
Посчитать ковариационную матрицу.
Посчитать годовую ковариационную матрицу.
Проверить положительную полуопределённость ковариационной матрицы.
Использовать covariance matrix для расчёта риска портфеля.
Использовать correlation matrix для анализа диверсификации.
9. Анализ портфеля
Задать список активов.
Задать веса активов.
Проверить, что сумма весов равна 1.
Проверить, что веса не отрицательные.
Посчитать доходность каждого актива.
Посчитать доходность портфеля.
Посчитать cumulative return портфеля.
Посчитать total return портфеля.
Посчитать annualized return портфеля.
Посчитать annualized volatility портфеля.
Посчитать Sharpe ratio портфеля.
Посчитать Sortino ratio портфеля.
Посчитать Calmar ratio портфеля.
Посчитать maximum drawdown портфеля.
Посчитать correlation matrix портфеля.
Посчитать covariance matrix портфеля.
Посчитать вклад каждого актива в доходность портфеля.
Посчитать вклад каждого актива в риск портфеля.
Сравнить портфель с benchmark.
Сравнить портфель с отдельными активами.
Посчитать portfolio beta.
Посчитать portfolio alpha.
Посчитать tracking error портфеля.
Посчитать information ratio портфеля.
10. Оптимизация портфеля
Сгенерировать случайные веса портфеля.
Сгенерировать N случайных портфелей.
Для каждого портфеля посчитать return.
Для каждого портфеля посчитать volatility.
Для каждого портфеля посчитать Sharpe ratio.
Найти портфель с максимальным Sharpe ratio.
Найти портфель с минимальной volatility.
Найти портфель с максимальной доходностью при заданном риске.
Найти портфель с минимальным риском при заданной доходности.
Построить efficient frontier.
Ограничить веса: long-only.
Ограничить максимальный вес одного актива.
Ограничить минимальный вес одного актива.
Добавить risk-free asset.
Посчитать capital allocation line.
Сравнить равновесный портфель с оптимизированным.
Проверить устойчивость оптимальных весов на разных периодах.
11. Ребалансировка портфеля
Посчитать портфель без ребалансировки.
Посчитать портфель с ежемесячной ребалансировкой.
Посчитать портфель с квартальной ребалансировкой.
Посчитать портфель с ежегодной ребалансировкой.
Сравнить доходность разных режимов ребалансировки.
Сравнить риск разных режимов ребалансировки.
Посчитать turnover при ребалансировке.
Посчитать комиссии от ребалансировки.
Проверить, как ребалансировка влияет на просадку.
12. Risk Metrics
Посчитать historical VaR.
Посчитать historical CVaR.
Посчитать parametric VaR.
Посчитать rolling VaR.
Посчитать rolling CVaR.
Посчитать VaR для одного актива.
Посчитать VaR для портфеля.
Посчитать CVaR для одного актива.
Посчитать CVaR для портфеля.
Посчитать worst-case loss за период.
Посчитать expected shortfall.
Посчитать probability of loss.
Посчитать probability of drawdown больше X%.
Посчитать риск при разных confidence levels: 90%, 95%, 99%.
13. Stress Testing
Смоделировать падение актива на 5%.
Смоделировать падение актива на 10%.
Смоделировать падение актива на 20%.
Смоделировать падение всего портфеля на X%.
Смоделировать рост волатильности.
Смоделировать падение benchmark.
Смоделировать кризисный сценарий.
Посмотреть, какой актив сильнее всего влияет на убыток.
Посмотреть, какой вес портфеля наиболее рискованный.
Посчитать loss contribution по активам.
14. Технические индикаторы
Simple Moving Average.
Exponential Moving Average.
Rolling standard deviation.
Bollinger Bands.
RSI.
MACD.
Momentum.
Rate of Change.
Z-score цены.
Z-score доходности.
Moving average spread.
Distance from moving average.
Rolling high.
Rolling low.
Breakout level.
15. Сигналы без полноценного бэктеста
Сгенерировать сигнал SMA crossover.
Сгенерировать momentum signal.
Сгенерировать mean reversion signal.
Сгенерировать RSI signal.
Сгенерировать Bollinger Bands signal.
Сравнить сигналы разных стратегий.
Посчитать, сколько дней сигнал был long.
Посчитать, сколько дней сигнал был cash.
Проверить частоту смены сигнала.
Проверить среднюю доходность после сигнала.
16. Простая логика стратегии
Buy and Hold.
SMA crossover.
Momentum.
Mean Reversion.
RSI-based strategy.
Bollinger Bands strategy.
Portfolio rebalancing strategy.
Equal-weight strategy.
Minimum-volatility strategy.
Maximum-Sharpe strategy.
17. Бэктестинг
Посчитать позиции по сигналам.
Сдвинуть позиции на один день вперёд, чтобы не было look-ahead bias.
Посчитать strategy returns.
Посчитать equity curve стратегии.
Посчитать drawdown стратегии.
Посчитать total return стратегии.
Посчитать annualized return стратегии.
Посчитать annualized volatility стратегии.
Посчитать Sharpe ratio стратегии.
Посчитать Sortino ratio стратегии.
Посчитать Calmar ratio стратегии.
Посчитать max drawdown стратегии.
Посчитать win rate.
Посчитать количество сделок.
Посчитать среднюю доходность сделки.
Посчитать лучшую сделку.
Посчитать худшую сделку.
Посчитать exposure.
Посчитать turnover.
Посчитать benchmark return.
Посчитать alpha vs benchmark.
Посчитать strategy beta.
Сравнить стратегию с Buy and Hold.
Сравнить несколько стратегий между собой.
18. Комиссии и издержки
Задать commission rate.
Задать slippage rate.
Посчитать turnover.
Посчитать transaction cost.
Посчитать strategy return до комиссий.
Посчитать strategy return после комиссий.
Сравнить результат до и после комиссий.
Проверить, убивают ли комиссии стратегию.
Посчитать break-even transaction cost.
Посчитать влияние частоты сделок на итоговый результат.
19. Сравнение активов
Сравнить несколько активов по total return.
Сравнить несколько активов по annual return.
Сравнить несколько активов по volatility.
Сравнить несколько активов по Sharpe.
Сравнить несколько активов по max drawdown.
Сравнить несколько активов по Sortino.
Сравнить несколько активов по Calmar.
Сравнить несколько активов по beta.
Сравнить несколько активов по correlation with benchmark.
Сделать ranking активов.
Найти актив с лучшим risk-adjusted return.
20. Rolling-анализ
Rolling return.
Rolling volatility.
Rolling Sharpe.
Rolling beta.
Rolling correlation.
Rolling max drawdown.
Rolling VaR.
Rolling skewness.
Rolling kurtosis.
Анализ стабильности метрик во времени.
21. Режимы рынка
Разделить периоды на bull market / bear market.
Разделить периоды по волатильности.
Разделить периоды по доходности benchmark.
Проверить стратегию в разных рыночных режимах.
Проверить портфель в кризисные периоды.
Проверить активы в периоды роста ставок.
Проверить активы в периоды падения рынка.
Проверить, какие активы лучше защищают портфель.
22. Отчёты
Сформировать отчёт по одному активу.
Сформировать отчёт по портфелю.
Сформировать отчёт по стратегии.
Сформировать таблицу метрик.
Сформировать список рисков.
Сформировать выводы по сравнению с benchmark.
Экспортировать отчёт в Markdown.
Экспортировать отчёт в HTML.
Экспортировать таблицы в CSV.
Экспортировать графики в PNG.
23. Графики
График цены.
График adjusted close.
График daily returns.
График cumulative returns.
График equity curve.
График drawdown.
Гистограмма доходностей.
Boxplot доходностей.
Rolling volatility chart.
Rolling Sharpe chart.
Correlation heatmap.
Covariance heatmap.
Efficient frontier.
Portfolio weights chart.
Benchmark comparison chart.
Strategy signal chart.
Trades chart.
VaR chart.
Rolling beta chart.
Volume chart.
Price + moving averages chart.
Bollinger Bands chart.
24. Валидация и защита от ошибок
Проверить, что тикер существует.
Проверить, что дата начала меньше даты конца.
Проверить, что период не пустой.
Проверить, что данные скачались.
Проверить, что нет отрицательных цен.
Проверить, что веса портфеля суммируются в 1.
Проверить, что веса не содержат NaN.
Проверить, что rolling window меньше длины данных.
Проверить, что short window меньше long window.
Проверить, что commission не отрицательный.
Проверить, что slippage не отрицательный.
Проверить, что benchmark есть в данных.
Проверить, что портфель содержит минимум 2 актива.
Проверить, что risk-free rate задан корректно.
25. Минимальный MVP

Для первой рабочей версии достаточно вот этого:

Скачать данные из yfinance.
Посчитать доходности.
Посчитать total return.
Посчитать annualized return.
Посчитать annualized volatility.
Посчитать Sharpe ratio.
Посчитать max drawdown.
Сравнить несколько активов.
Собрать портфель с заданными весами.
Посчитать метрики портфеля.
Посчитать correlation matrix.
Сгенерировать случайные портфели.
Найти max Sharpe portfolio.
Найти min volatility portfolio.
Построить efficient frontier.
Сделать Buy and Hold.
Сделать SMA crossover.
Посчитать метрики стратегии.
Учесть комиссии.
Сравнить стратегию с Buy and Hold. ;  company_tickers.json - тут те тикеры которые нужно будет сделать доступными  :

1) Phasing strategy: The spec describes versions 0.1–1.0. Since you already did the notebook-style exploration in day1.py, I propose starting directly with v0.2 (Python modules) and building all core logic as importable modules before touching FastAPI/Vue. Is that correct? - yes ; Ticker list: company_tickers.json has ~10K+ tickers. The spec says "start with SPY, QQQ, TLT, GLD, AAPL, MSFT, NVDA, JPM, XOM, BTC-USD, ETH-USD" as defaults. Should I make all tickers from company_tickers.json searchable/available, or strictly limit the initial version to the 11 default tickers? create default ticker list and then i will change it ; The spec says start with parquet files at /data/raw/{symbol}.parquet and /data/processed/{symbol}.parquet, then migrate to PostgreSQL later. Confirmed? immideatly use postgress ;  What value should be the default risk-free rate for Sharpe/Sortino? Standard is 0.02 (2%) or 0.05 (current US ~5%). Should it be configurable? create function that returns that coef (take it from config file) than i write how it must be calculated   ;;; The spec examples use 2015-01-01 to 2025-01-01. Should the default be dynamic (e.g., last 10 years from today)? max range with dropna()  ;;; BTC-USD and ETH-USD trade 24/7 including weekends. When syncing dates with stock tickers, the extra weekend dates will be dropped. Is that acceptable? yes ;;; i will create postgress by myself ;;
# QuantLab Lite — Implementation Plan

## Overview

Full-stack quantitative finance dashboard for portfolio analysis and backtesting. Built as a **modular monolith**: Python core → FastAPI → Vue.

**Current state**: `day1.py` has initial explorations (SPY/BND returns, Sharpe, drawdown). `functionality.md` has the full 304-item feature spec. `company_tickers.json` has ~10K+ tickers from SEC.

**Goal**: Skip the notebook phase (v0.1) since `day1.py` already covers those basics, and jump directly to building **production-quality Python modules** (v0.2+).

---

## User Review Required

All decisions confirmed by user:

---

## Decisions (Confirmed)

1. **Phasing**: Skip v0.1, start with v0.2 Python modules ✅
2. **Tickers**: Create default ticker list, user will modify later ✅
3. **Storage**: PostgreSQL immediately (user creates the DB) ✅
4. **Risk-free rate**: Read from config file via a dedicated function ✅
5. **Date range**: Max available range with `dropna()` ✅
6. **Crypto dates**: Drop weekends when syncing with stocks ✅
7. **Intervals**: All available yfinance intervals (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo) ✅

---

## Proposed Changes

The project will be built inside the existing workspace with the following structure:

```
c:\Users\zakiy\Desktop\Quant Dashboard\
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app (v0.6)
│   │   ├── api/                       # API routers (v0.6)
│   │   │   ├── __init__.py
│   │   │   ├── data.py
│   │   │   ├── assets.py
│   │   │   ├── portfolio.py
│   │   │   ├── backtest.py
│   │   │   └── risk.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # PostgreSQL connection
│   │   │   ├── config.py              # Central config
│   │   │   └── exceptions.py          # Custom exceptions
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── data_service.py        # v0.2 — Data layer
│   │   │   ├── metrics_service.py     # v0.2 — Returns, risk, performance
│   │   │   ├── portfolio_service.py   # v0.3 — Portfolio analysis
│   │   │   ├── optimizer_service.py   # v0.4 — Portfolio optimization
│   │   │   ├── backtest_service.py    # v0.5 — Backtesting engine
│   │   │   └── risk_service.py        # v0.5 — VaR, CVaR, stress testing
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py             # Pydantic schemas
│   │   │   └── enums.py               # Strategy types, intervals, etc.
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── dates.py               # Date helpers
│   │       └── validation.py          # Input validation
│   ├── db_schema.sql                  # PostgreSQL schema
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_data_service.py
│   │   ├── test_metrics_service.py
│   │   ├── test_portfolio_service.py
│   │   ├── test_optimizer_service.py
│   │   ├── test_backtest_service.py
│   │   └── test_risk_service.py
│   └── requirements.txt
├── frontend/                          # Vue app (v0.7)
├── company_tickers.json               # Existing
├── day1.py                            # Existing exploration
├── functionality.md                   # Existing spec
└── README.md
```

---

### Phase 1: Foundation (v0.2) — Core Modules

Build the core calculation engine as pure Python modules. No FastAPI, no Vue.

---

#### [NEW] [config.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/core/config.py)

Central configuration:
- `DEFAULT_TICKERS`: SPY, QQQ, TLT, GLD, AAPL, MSFT, NVDA, JPM, XOM, BTC-USD, ETH-USD
- `get_risk_free_rate()` function reading from config
- `DATABASE_URL`: PostgreSQL connection string from `.env`
- `DEFAULT_INTERVAL`: "1d"
- `AVAILABLE_INTERVALS`: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
- `TRADING_DAYS_PER_YEAR`: 252
- Ticker registry loaded from `company_tickers.json`

#### [NEW] [exceptions.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/core/exceptions.py)

Custom exceptions:
- `TickerNotFoundError`
- `DataNotAvailableError`
- `InvalidDateRangeError`
- `InvalidWeightsError`
- `InsufficientDataError`
- `ValidationError`

#### [NEW] [database.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/core/database.py)

PostgreSQL connection management via SQLAlchemy:
- `get_engine()` — creates engine from DATABASE_URL
- `get_session()` — session factory
- Connection pooling configuration

#### [NEW] [db_schema.sql](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/db_schema.sql)

PostgreSQL schema:
- `prices` table (symbol, date, interval, open, high, low, close, adjusted_close, volume, source)
- Indexes on (symbol, date, interval)
- User runs this manually to create tables

#### [NEW] [enums.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/models/enums.py)

- `Interval`: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
- `StrategyType`: buy_and_hold, sma_crossover, momentum, mean_reversion
- `OptimizationTarget`: max_sharpe, min_volatility
- `RebalanceFrequency`: none, monthly, quarterly, yearly

#### [NEW] [schemas.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/models/schemas.py)

Pydantic models for all inputs/outputs:
- `AssetMetrics`, `PortfolioRequest`, `PortfolioMetrics`
- `BacktestRequest`, `BacktestResult`, `TradeRecord`
- `OptimizationRequest`, `OptimizationResult`
- `RiskMetrics`, `StressTestRequest`, `StressTestResult`

#### [NEW] [validation.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/utils/validation.py)

Input validation (covers spec items 291–304):
- `validate_ticker(symbol)` — check against `company_tickers.json` + yfinance
- `validate_date_range(start, end)`
- `validate_weights(weights)` — sum=1, no negatives, no NaN
- `validate_window(window, data_length)`
- `validate_commission(rate)`
- `validate_slippage(rate)`

#### [NEW] [dates.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/utils/dates.py)

- `sync_dates(dataframes)` — align multiple assets to common dates
- `get_trading_days(start, end)`
- `parse_date(date_str)`

---

#### [NEW] [data_service.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/services/data_service.py)

Covers spec **Section 1** (items 1–16):

```python
class DataService:
    def download_prices(symbol, start_date, end_date, interval="1d") -> pd.DataFrame
    def download_multiple(symbols, start_date, end_date, interval="1d") -> Dict[str, pd.DataFrame]
    def save_prices(symbol, df, format="parquet")
    def load_prices(symbol) -> pd.DataFrame
    def update_prices(symbol) -> pd.DataFrame
    def validate_prices(df) -> ValidationReport  # checks gaps, dupes, nulls, negatives
    def sync_dates(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]
    def get_available_symbols() -> List[str]
    def get_symbol_status(symbol) -> dict  # last date, row count, etc.
```

Data format after processing:
| Column | Type |
|--------|------|
| date | datetime (index) |
| open | float |
| high | float |
| low | float |
| close | float |
| adjusted_close | float |
| volume | int |
| symbol | str |
| source | str ("yfinance") |

---

#### [NEW] [metrics_service.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/services/metrics_service.py)

Covers spec **Sections 2–6, 14, 19–20** (returns, risk, performance, drawdowns, volume, indicators, comparisons, rolling):

```python
class MetricsService:
    # --- Returns (Section 2) ---
    def simple_returns(prices: pd.Series) -> pd.Series
    def log_returns(prices: pd.Series) -> pd.Series
    def cumulative_returns(returns: pd.Series) -> pd.Series
    def total_return(returns: pd.Series) -> float
    def annualized_return(returns: pd.Series, periods_per_year=252) -> float
    def monthly_returns(returns: pd.Series) -> pd.Series
    def best_day(returns: pd.Series) -> Tuple[date, float]
    def worst_day(returns: pd.Series) -> Tuple[date, float]
    def best_n_days(returns: pd.Series, n=5) -> pd.Series
    def worst_n_days(returns: pd.Series, n=5) -> pd.Series

    # --- Risk (Section 3) ---
    def daily_volatility(returns: pd.Series) -> float
    def annualized_volatility(returns: pd.Series, periods_per_year=252) -> float
    def rolling_volatility(returns: pd.Series, window=21) -> pd.Series
    def rolling_mean_return(returns: pd.Series, window=21) -> pd.Series
    def rolling_sharpe(returns: pd.Series, window=63, rf=0.02) -> pd.Series
    def downside_deviation(returns: pd.Series, mar=0.0) -> float
    def skewness(returns: pd.Series) -> float
    def kurtosis(returns: pd.Series) -> float
    def return_quantiles(returns: pd.Series, quantiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]) -> dict

    # --- Performance (Section 4) ---
    def sharpe_ratio(returns: pd.Series, rf=0.02, periods_per_year=252) -> float
    def sortino_ratio(returns: pd.Series, rf=0.02, periods_per_year=252) -> float
    def calmar_ratio(returns: pd.Series, periods_per_year=252) -> float
    def cagr(prices: pd.Series) -> float
    def information_ratio(returns: pd.Series, benchmark_returns: pd.Series) -> float
    def tracking_error(returns: pd.Series, benchmark_returns: pd.Series) -> float
    def alpha(returns: pd.Series, benchmark_returns: pd.Series, rf=0.02) -> float
    def beta(returns: pd.Series, benchmark_returns: pd.Series) -> float

    # --- Drawdowns (Section 5) ---
    def equity_curve(returns: pd.Series, initial=1.0) -> pd.Series
    def drawdown_series(returns: pd.Series) -> pd.Series
    def max_drawdown(returns: pd.Series) -> float
    def max_drawdown_details(returns: pd.Series) -> dict  # start, bottom, recovery, duration
    def top_n_drawdowns(returns: pd.Series, n=5) -> List[dict]
    def average_drawdown(returns: pd.Series) -> float

    # --- Volume (Section 6) ---
    def avg_volume(volume: pd.Series) -> float
    def rolling_avg_volume(volume: pd.Series, window=21) -> pd.Series
    def anomalous_volume_days(volume: pd.Series, threshold=2.0) -> pd.DataFrame
    def volume_return_correlation(volume: pd.Series, returns: pd.Series) -> float

    # --- Technical Indicators (Section 14) ---
    def sma(prices: pd.Series, window: int) -> pd.Series
    def ema(prices: pd.Series, window: int) -> pd.Series
    def bollinger_bands(prices: pd.Series, window=20, num_std=2) -> pd.DataFrame
    def rsi(prices: pd.Series, window=14) -> pd.Series
    def macd(prices: pd.Series, fast=12, slow=26, signal=9) -> pd.DataFrame
    def momentum(prices: pd.Series, window: int) -> pd.Series
    def rate_of_change(prices: pd.Series, window: int) -> pd.Series
    def zscore(series: pd.Series, window: int) -> pd.Series

    # --- Rolling Analysis (Section 20) ---
    def rolling_beta(returns, benchmark_returns, window=63) -> pd.Series
    def rolling_correlation(returns, benchmark_returns, window=63) -> pd.Series
    def rolling_max_drawdown(returns, window=252) -> pd.Series
    def rolling_var(returns, window=252, confidence=0.95) -> pd.Series
    def rolling_skewness(returns, window=252) -> pd.Series
    def rolling_kurtosis(returns, window=252) -> pd.Series

    # --- Comparison (Section 19) ---
    def compare_assets(price_dict: Dict[str, pd.Series]) -> pd.DataFrame
    def rank_assets(price_dict: Dict[str, pd.Series], metric="sharpe") -> pd.DataFrame

    # --- Full Report ---
    def full_asset_report(prices: pd.Series, benchmark_prices: pd.Series = None, rf=0.02) -> AssetMetrics
```

---

### Phase 2: Portfolio Analysis (v0.3)

#### [NEW] [portfolio_service.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/services/portfolio_service.py)

Covers spec **Sections 7–9, 11** (correlation, covariance, portfolio analysis, rebalancing):

```python
class PortfolioService:
    # --- Correlation & Covariance (Sections 7–8) ---
    def correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame
    def covariance_matrix(returns_df: pd.DataFrame, annualize=True) -> pd.DataFrame
    def rolling_correlation(ret1, ret2, window=63) -> pd.Series
    def most_correlated_pairs(corr_matrix, n=5) -> List[Tuple]
    def least_correlated_pairs(corr_matrix, n=5) -> List[Tuple]

    # --- Portfolio Analysis (Section 9) ---
    def portfolio_returns(returns_df: pd.DataFrame, weights: np.array) -> pd.Series
    def portfolio_cumulative_return(port_returns: pd.Series) -> pd.Series
    def portfolio_metrics(returns_df, weights, benchmark_returns=None, rf=0.02) -> PortfolioMetrics
    def asset_contribution_return(returns_df, weights) -> pd.Series
    def asset_contribution_risk(returns_df, weights) -> pd.Series
    def portfolio_vs_benchmark(port_returns, benchmark_returns) -> dict

    # --- Rebalancing (Section 11) ---
    def simulate_rebalancing(returns_df, weights, frequency="monthly", commission=0.001) -> pd.Series
    def compare_rebalancing_regimes(returns_df, weights, commission=0.001) -> pd.DataFrame
```

---

### Phase 3: Optimization (v0.4)

#### [NEW] [optimizer_service.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/services/optimizer_service.py)

Covers spec **Section 10** (portfolio optimization):

```python
class OptimizerService:
    def generate_random_weights(n_assets: int) -> np.array
    def generate_random_portfolios(returns_df, n_portfolios=10000, rf=0.02) -> pd.DataFrame
    def max_sharpe_portfolio(random_portfolios) -> dict  # weights, return, vol, sharpe
    def min_volatility_portfolio(random_portfolios) -> dict
    def efficient_frontier_data(random_portfolios) -> dict  # for plotting
    def compare_equal_vs_optimized(returns_df, rf=0.02) -> dict
    def weight_stability_check(returns_df, rf=0.02, n_periods=5) -> pd.DataFrame
```

---

### Phase 4: Backtesting & Risk (v0.5)

#### [NEW] [backtest_service.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/services/backtest_service.py)

Covers spec **Sections 15–18, 21** (signals, strategies, backtesting, costs, market regimes):

```python
class BacktestService:
    # --- Signals (Section 15) ---
    def sma_crossover_signal(prices, short_window=20, long_window=50) -> pd.Series
    def momentum_signal(prices, lookback=60) -> pd.Series
    def mean_reversion_signal(prices, window=20, threshold=0.03) -> pd.Series
    def rsi_signal(prices, window=14, oversold=30, overbought=70) -> pd.Series
    def bollinger_signal(prices, window=20, num_std=2) -> pd.Series

    # --- Backtesting Engine (Section 17) ---
    def run_backtest(prices, signal, commission=0.001, slippage=0.0005) -> BacktestResult
    def buy_and_hold(prices) -> BacktestResult

    # --- Strategy metrics ---
    def strategy_metrics(equity_curve, benchmark_returns, trades) -> dict
    # win_rate, num_trades, avg_trade_return, best/worst trade,
    # exposure, turnover, alpha, beta

    # --- Transaction Costs (Section 18) ---
    def calculate_turnover(positions: pd.Series) -> pd.Series
    def apply_costs(returns, positions, commission, slippage) -> pd.Series
    def break_even_cost(strategy_returns, benchmark_returns) -> float

    # --- Market Regimes (Section 21) ---
    def classify_regime(benchmark_returns, window=63) -> pd.Series  # bull/bear
    def strategy_by_regime(backtest_result, regimes) -> dict

    # --- Comparison ---
    def compare_strategies(results: Dict[str, BacktestResult]) -> pd.DataFrame
```

#### [NEW] [risk_service.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/services/risk_service.py)

Covers spec **Sections 12–13** (risk metrics, stress testing):

```python
class RiskService:
    # --- VaR / CVaR (Section 12) ---
    def historical_var(returns, confidence=0.95) -> float
    def historical_cvar(returns, confidence=0.95) -> float
    def parametric_var(returns, confidence=0.95) -> float
    def portfolio_var(returns_df, weights, confidence=0.95) -> float
    def portfolio_cvar(returns_df, weights, confidence=0.95) -> float
    def probability_of_loss(returns) -> float
    def probability_of_drawdown(returns, threshold=0.1) -> float

    # --- Stress Testing (Section 13) ---
    def fixed_shock(portfolio_weights, shock_pct) -> float
    def asset_shock(returns_df, weights, shocked_asset, shock_pct) -> float
    def historical_scenario(returns_df, weights, crisis_start, crisis_end) -> dict
    def loss_contribution(returns_df, weights, shock_pct) -> pd.Series
    def volatility_spike_test(returns_df, weights, vol_multiplier=2.0) -> float
```

---

### Phase 5: FastAPI Backend (v0.6)

#### [NEW] [main.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/main.py)

FastAPI app with CORS, routers.

#### [NEW] [api/data.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/api/data.py)

```
GET  /symbols              — list available tickers
POST /data/download        — download data for a symbol
GET  /data/{symbol}        — get stored data
GET  /data/{symbol}/status — data freshness info
```

#### [NEW] [api/assets.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/api/assets.py)

```
GET /assets/{symbol}/metrics            — full metrics table
GET /assets/{symbol}/returns            — return series
GET /assets/{symbol}/drawdown           — drawdown series
GET /assets/{symbol}/rolling-volatility — rolling vol series
```

#### [NEW] [api/portfolio.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/api/portfolio.py)

```
POST /portfolio/analyze   — analyze portfolio with weights
POST /portfolio/optimize  — run random portfolio optimization
```

#### [NEW] [api/backtest.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/api/backtest.py)

```
POST /backtest     — run backtest
GET  /strategies   — list available strategies
```

#### [NEW] [api/risk.py](file:///c:/Users/zakiy/Desktop/Quant%20Dashboard/backend/app/api/risk.py)

```
GET  /risk/{symbol}/var      — VaR for asset
GET  /risk/{symbol}/cvar     — CVaR for asset
POST /risk/stress-test       — stress test portfolio
```

---

### Phase 6: Vue Frontend (v0.7)

7 pages as specified:
1. **Home Dashboard** — ticker cards, data status
2. **Asset Analyzer** — price/return/drawdown charts, metrics table
3. **Portfolio Analyzer** — equity curve, benchmark comparison, correlation matrix
4. **Portfolio Optimizer** — efficient frontier, optimal weights
5. **Backtesting Lab** — equity curve, signals, trades, metrics
6. **Risk Dashboard** — VaR/CVaR, stress testing, rolling risk
7. **Data Manager** — download/update data

Chart library: **Chart.js** or **ECharts** for all visualizations.

---

### Phase 7: Polish (v1.0)

- `README.md` with screenshots, usage, limitations
- Docker setup (Dockerfile, docker-compose.yml)
- Tests for all services

---

## Execution Order

| Step | Version | What gets built | Spec coverage |
|------|---------|-----------------|---------------|
| 1 | v0.2 | `config`, `exceptions`, `enums`, `schemas`, `validation`, `dates`, `data_service`, `metrics_service` | Sections 1–6, 14, 19–20, 24 |
| 2 | v0.3 | `portfolio_service` | Sections 7–9, 11 |
| 3 | v0.4 | `optimizer_service` | Section 10 |
| 4 | v0.5 | `backtest_service`, `risk_service` | Sections 12–18, 21 |
| 5 | v0.6 | FastAPI `main.py` + all API routers | Section 7 (API) |
| 6 | v0.7 | Vue frontend (all 7 pages) | Section 8 (Frontend) |
| 7 | v1.0 | README, Docker, tests | Sections 9–13 |

---

## Verification Plan

### Automated Tests
- Unit tests for each service using `pytest`
- Test against known values (e.g., SPY Sharpe should be roughly 0.5–1.0 over 10y)
- Test validation edge cases (negative prices, empty data, NaN weights)
- Integration test: download SPY → compute all metrics → verify no errors

### Manual Verification
- Run `python -c "from backend.app.services.data_service import DataService; ..."` to verify each module works independently
- After FastAPI: test each endpoint with curl/httpie
- After Vue: visual check of all 7 pages in browser

### Acceptance Criteria (MVP)
User can:
- [x] Select a ticker and download data
- [x] See price chart, returns, drawdown, metrics
- [x] Build a portfolio with weights
- [x] See correlation matrix
- [x] Optimize portfolio (random portfolios → efficient frontier)
- [x] Run SMA crossover & Buy-and-Hold backtest with commissions
- [x] See backtest report
