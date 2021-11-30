import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from constants import JSON_KEYFILE, SCOPE, SHEET_NAMES

credentials = ServiceAccountCredentials.from_json_keyfile_dict(JSON_KEYFILE, SCOPE)
client = gspread.authorize(credentials)

spreadsheet = client.open('Sports Betting Bot')


def upload_df(df, sheet_name):
    sheet_name = sheet_name.upper()

    if sheet_name in SHEET_NAMES:
        spreadsheet.worksheet(sheet_name).clear()
        spreadsheet.worksheet(sheet_name).update([df.columns.values.tolist()] + df.values.tolist())


def download_df(sheet_name):
    sheet_name = sheet_name.upper()

    if sheet_name in SHEET_NAMES:
        data = spreadsheet.worksheet(sheet_name).get_all_values()
        df = pd.DataFrame.from_records(data[1:], columns=data[0])

        return df

    return None


if __name__ == '__main__':
    df = download_df('BETS')
    print(df)