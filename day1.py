import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

prices = yf.download(
    tickers=["BND", "SPY"],
    interval="1mo",
    period="max",
    auto_adjust=False,
    progress=False
)["Adj Close"]

prices.dropna(inplace=True)

prices.index = prices.index.to_period("M").to_timestamp()


prices.plot(title="SPY vs BND Monthly Prices")
plt.xlabel("Date")
plt.ylabel("Price")
plt.show()

rets = prices.pct_change().dropna()

rets.plot(title="SPY vs BND Monthly Returns")
plt.xlabel("Date")
plt.ylabel("Return")
plt.show()

compound_returns = (rets + 1).prod() - 1
print("compound_returns : ", (compound_returns * 100).round(2).astype('str') + '%')

print(rets.head())
print('///')
print(rets.tail())
print('///')
print(rets.size)
print('///')
print(rets.shape)
print('///')
# print(rets.index)
# print('///')
# print(rets.columns)
# print('///')

print(rets.loc['2009-02'])
print('///')
print(rets.iloc[20])
print('///')

print(f'standard deviation : {rets.std()}')
print('///')

def annualize_rets(r, periods_per_year=12):
    n_periods = r.shape[0]
    compounded_growth = (1 + r).prod()
    return compounded_growth ** (periods_per_year / n_periods) - 1

def annualize_vol(r, periods_per_year=12):
    return r.std() * np.sqrt(periods_per_year)

annual_return = annualize_rets(rets)
annual_vol = annualize_vol(rets)
raw_sharpe = annual_return / annual_vol

print(annual_return)
print(annual_vol)
print(raw_sharpe)

# ..............................................................

prices = yf.download(
    tickers="SPY",
    interval="1mo",
    period="max",
    auto_adjust=False,
    progress=False
)["Adj Close"]

# Если вернулся DataFrame с одной колонкой, превращаем его в Series.
if isinstance(prices, pd.DataFrame):
    prices = prices["SPY"]

rets = prices.pct_change().dropna()

wealth_index = (rets + 1).cumprod()

start_date = wealth_index.index.min() - pd.DateOffset(months=1)

start_value = pd.Series(
    [1],
    index=[start_date],
    name=wealth_index.name
)

wealth_index = pd.concat([start_value, wealth_index])

previous_peaks = wealth_index.cummax()
drawdowns = (wealth_index - previous_peaks) / previous_peaks

max_drawdown = drawdowns.min()
max_drawdown_date = drawdowns.idxmin()

print(max_drawdown_date, max_drawdown)

wealth_index.plot(title="Growth of $1 in SPY")
previous_peaks.plot()
drawdowns.plot()
plt.xlabel("Date")
plt.ylabel("Wealth Index")
plt.grid(True)
plt.annotate(f'Max Drawdown: {max_drawdown:.2%}', xy=(max_drawdown_date, max_drawdown),
             xytext=(max_drawdown_date + pd.DateOffset(years=2), max_drawdown * 2),
             arrowprops=dict(arrowstyle='->', lw=1), color='blue')

plt.show()







# prices.to_csv("prices.csv")
# rets.to_csv("returns.csv")
