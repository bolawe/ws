import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from klse_scraper import get_klse_data  # Local module

def detect_wyckoff(df, ticker):
    """Wyckoff Accumulation Detection Logic"""
    # Phase B: Consolidation (20-day range <5%)
    max_price = df["Close"].rolling(20).max().iloc[-1]
    min_price = df["Close"].rolling(20).min().iloc[-1]
    range_pct = (max_price - min_price) / min_price
    is_consolidating = range_pct < 0.05
    
    # Volume: Declining in consolidation
    vol_avg = df["Volume"].rolling(20).mean().iloc[-1]
    is_low_vol = df["Volume"].iloc[-1] < vol_avg * 0.7
    
    # Phase C: Spring (false breakdown)
    spring = (df["Low"].iloc[-1] < min_price) and (df["Close"].iloc[-1] > min_price)
    
    # Phase D: Breakout (price > resistance + volume spike)
    is_breaking_out = (df["Close"].iloc[-1] > max_price) and (df["Volume"].iloc[-1] > vol_avg * 1.5)
    
    return {
        "Ticker": ticker,
        "Close": df["Close"].iloc[-1],
        "Resistance": max_price,
        "Volume Spike": df["Volume"].iloc[-1] > vol_avg * 1.5,
        "Wyckoff Phase": "Breakout" if is_breaking_out else "Accumulation" if is_consolidating else "None"
    }

def scan_us_stocks():
    """Scan S&P 500 stocks"""
    sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    results = []
    for ticker in sp500["Symbol"].tolist()[:50]:  # Test first 50 for speed
        try:
            df = yf.Ticker(ticker).history(period="3mo")
            results.append(detect_wyckoff(df, ticker))
        except:
            continue
    pd.DataFrame(results).to_csv("data/us_stocks.csv")

def scan_klse_stocks():
    """Scan Bursa Malaysia stocks"""
    klse_stocks = ["MAYBANK", "PUBLICBANK", "TENAGA"]  # Example tickers
    results = []
    for ticker in klse_stocks:
        df = get_klse_data(ticker)
        results.append(detect_wyckoff(df, ticker))
    pd.DataFrame(results).to_csv("data/klse_stocks.csv")

if __name__ == "__main__":
    scan_us_stocks()
    scan_klse_stocks()
