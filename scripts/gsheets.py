import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

def update_gsheets():
    try:
        # Load credentials from environment variable
        creds_json = json.loads(os.environ['GSHEETS_CREDS'])
        
        scope = ["https://spreadsheets.google.com/feeds", 
                "https://www.googleapis.com/auth/drive"]
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        client = gspread.authorize(creds)
        
        # Update US Stocks
        us_df = pd.read_csv("data/us_stocks.csv")
        us_sheet = client.open("Wyckoff Scanner").worksheet("US Stocks")
        us_sheet.clear()
        us_sheet.update([us_df.columns.values.tolist()] + us_df.values.tolist())
        
        print("Successfully updated Google Sheets")
    except Exception as e:
        print(f"Failed to update Google Sheets: {str(e)}")

if __name__ == "__main__":
    update_gsheets()
