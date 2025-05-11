import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

def detect_wyckoff(df, ticker):
    """Wyckoff Accumulation Detection Logic"""
    if df.empty or len(df) < 20:
        return None
        
    try:
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
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        return None

def scan_us_stocks():
    """Scan S&P 500 stocks"""
    try:
        sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        results = []
        
        for ticker in sp500["Symbol"].tolist()[:50]:  # Test first 50 for speed
            try:
                # Add .TO for Canadian stocks, remove for others
                actual_ticker = f"{ticker}.TO" if ticker in ['SHOP', 'NTR'] else ticker
                df = yf.Ticker(actual_ticker).history(period="3mo")
                
                if not df.empty:
                    result = detect_wyckoff(df, ticker)
                    if result:
                        results.append(result)
                else:
                    print(f"No data for {ticker}, may be delisted")
            except Exception as e:
                print(f"Failed to process {ticker}: {str(e)}")
                continue
                
        pd.DataFrame(results).to_csv("data/us_stocks.csv")
    except Exception as e:
        print(f"Failed to fetch S&P 500 list: {str(e)}")

if __name__ == "__main__":
    scan_us_stocks()
