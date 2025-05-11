import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime, timedelta

os.makedirs("data", exist_ok=True)

def get_yfinance_data(ticker, max_retries=3, delay=1):
    """Robust yfinance data fetcher with retries"""
    for attempt in range(max_retries):
        try:
            data = yf.Ticker(ticker).history(period="3mo")
            if not data.empty:
                return data
            time.sleep(delay)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {ticker}: {str(e)}")
            time.sleep(delay)
    return pd.DataFrame()

def detect_wyckoff(df, ticker):
    if df.empty or len(df) < 20:
        return None
        
    try:
        max_price = df["Close"].rolling(20).max().iloc[-1]
        min_price = df["Close"].rolling(20).min().iloc[-1]
        range_pct = (max_price - min_price) / min_price
        
        vol_avg = df["Volume"].rolling(20).mean().iloc[-1]
        
        return {
            "Ticker": ticker,
            "Close": df["Close"].iloc[-1],
            "Resistance": max_price,
            "Support": min_price,
            "Range%": round(range_pct*100, 2),
            "Volume%": round((df["Volume"].iloc[-1]/vol_avg - 1)*100, 2) if vol_avg > 0 else 0,
            "Status": "Breakout" if df["Close"].iloc[-1] > max_price else 
                     "Accumulation" if range_pct < 0.05 else "None"
        }
    except Exception as e:
        print(f"Analysis failed for {ticker}: {str(e)}")
        return None

def scan_us_stocks():
    try:
        sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        results = []
        
        for ticker in sp500["Symbol"].unique()[:20]:  # Test with fewer tickers first
            try:
                print(f"Processing {ticker}...")
                df = get_yfinance_data(ticker)
                
                if not df.empty:
                    result = detect_wyckoff(df, ticker)
                    if result:
                        results.append(result)
                else:
                    print(f"No data for {ticker} after retries")
            except Exception as e:
                print(f"Failed to process {ticker}: {str(e)}")
                continue
                
        if results:
            pd.DataFrame(results).to_csv("data/us_stocks.csv", index=False)
    except Exception as e:
        print(f"Failed to fetch S&P 500 list: {str(e)}")

if __name__ == "__main__":
    scan_us_stocks()
