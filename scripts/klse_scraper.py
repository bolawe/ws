import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_klse_data(ticker):
    """Scrape KLSE data from KLSE Screener"""
    url = f"https://www.klsescreener.com/v2/stocks/view/{ticker}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract price history (example - adjust based on site structure)
    table = soup.find("table", {"class": "historical-data"})
    df = pd.read_html(str(table))[0]
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    return df
