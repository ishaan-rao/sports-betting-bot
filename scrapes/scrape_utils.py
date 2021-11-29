import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

sheet_names = ['BETS', 'BALANCES', 'NBA', 'UCL']

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('../client_secret.json', scope)
client = gspread.authorize(credentials)

spreadsheet = client.open('Sports Betting Bot')


def upload_df(df, sheet_name):
    sheet_name = sheet_name.upper()

    if sheet_name in sheet_names:
        spreadsheet.worksheet(sheet_name).clear()
        spreadsheet.worksheet(sheet_name).update([df.columns.values.tolist()] + df.values.tolist())
