import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def update_gsheets():
    # Authenticate
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("gsheets_creds.json", scope)
    client = gspread.authorize(creds)
    
    # Update US Stocks Sheet
    us_df = pd.read_csv("data/us_stocks.csv")
    us_sheet = client.open("Wyckoff Scanner").worksheet("US Stocks")
    us_sheet.update([us_df.columns.tolist()] + us_df.values.tolist())
    
    # Update KLSE Stocks Sheet
    klse_df = pd.read_csv("data/klse_stocks.csv")
    klse_sheet = client.open("Wyckoff Scanner").worksheet("KLSE Stocks")
    klse_sheet.update([klse_df.columns.tolist()] + klse_df.values.tolist())

if __name__ == "__main__":
    update_gsheets()
