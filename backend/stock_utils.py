import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol: str, period: str = "10y") -> pd.DataFrame:
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)
    if hist.empty:
        raise ValueError("No data found for the given symbol and period.")
    return hist.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]]