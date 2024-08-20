from datetime import timedelta

import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data
def load_data(stock):
    texto_tickers = " ".join(stock)
    stock_data = yf.Tickers(texto_tickers)
    stock_quotes = stock_data.history(period="1d", start="2010-01-01", end="2024-08-01")
    stock_quotes = stock_quotes["Close"]
    return stock_quotes


@st.cache_data
def load_tickers_stocks():
    base_tickers = pd.read_csv("IBOV.csv", sep=";")
    tickers = list(base_tickers["Código"])
    tickers = [item + ".SA" for item in tickers]
    return tickers


stocks = load_tickers_stocks()
data = load_data(stocks)

st.write(
    """
# Stock Price App
The chart below represents the evolution of stock prices over the years 2010 to 2024.
"""
)

st.sidebar.header("filter")

list_stocks = st.sidebar.multiselect("Choose stocks to view:", data.columns)
if list_stocks:
    data = data[list_stocks]
    if len(list_stocks) == 1:
        unique_stock = list_stocks[0]
        data = data.rename(columns={unique_stock: "Close"})

start_date = data.index.min().to_pydatetime()
end_date = data.index.max().to_pydatetime()
date_range = st.sidebar.slider(
    "Select date",
    min_value=start_date,
    max_value=end_date,
    value=(start_date, end_date),
    step=timedelta(days=1),
)

data = data.loc[date_range[0] : date_range[1]]

st.line_chart(data)

texto_performance_stocks = ""

if len(list_stocks) == 0:
    list_stocks = list(data.columns)
elif len(list_stocks) == 1:
    data = data.rename(columns={"Close": unique_stock})

portfolio_investment = [1000 for stock in list_stocks]
total_initial_investment = sum(portfolio_investment)

for i, stock in enumerate(list_stocks):
    performance_stocks = data[stock].iloc[-1] / data[stock].iloc[0] - 1
    performance_stocks = float(performance_stocks)

    portfolio_investment[i] = portfolio_investment[i] * (1 + performance_stocks)

    if performance_stocks > 0:
        # :cor[texto]
        texto_performance_stocks = (
            texto_performance_stocks + f"  \n{stock}: :green[{performance_stocks:.1%}]"
        )
    elif performance_stocks < 0:
        texto_performance_stocks = (
            texto_performance_stocks + f"  \n{stock}: :red[{performance_stocks:.1%}]"
        )
    else:
        texto_performance_stocks = (
            texto_performance_stocks + f"  \n{stock}: {performance_stocks:.1%}"
        )

total_final_investment = sum(portfolio_investment)
portfolio_performance = total_final_investment / total_initial_investment - 1


if portfolio_performance > 0:
    texto_performance_portfolio = (
        f"\nPortfolio performance with all stocks: :green[{portfolio_performance:.1%}]"
    )
elif portfolio_performance < 0:
    texto_performance_portfolio = (
        f"\nPortfolio performance with all stocks: :red[{portfolio_performance:.1%}]"
    )
else:
    texto_performance_portfolio = (
        f"Portfolio performance with all stocks: {portfolio_performance:.1%}"
    )

st.write(
    f"""
### Stock Performance
This was the performance of each asset in the selected period:

{texto_performance_stocks}
{texto_performance_portfolio}
"""
)
