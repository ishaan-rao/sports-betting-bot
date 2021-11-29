import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

sheet_names = ['BETS', 'BALANCES', 'NBA', 'UCL']

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

CLIENT_SECRET = {
    "type": "service_account",
    "project_id": "sports-betting-bot",
    "private_key_id": "220f3a2d2a44966a08c3a5d79ddd5f26debf28e8",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCsWJrx5ULTHoq6\n3b1ztXVroMryx/CA0PXn3i9JcbMkkk8ZQRpVrRevn4INimLX9HYBeo9owTiT6A/p\nFNwMBRDBNLGUcBaQDSK5PM38L+BdCHafmH+n4gBEYJX6Z6crDx0EzASH0J8j01qD\nI+NKZKmwP4PbAtbyT4SPAIF/k3y3XrJGus6dK6vSIXAmhwdFNeQ02uF69E7F6tf0\ndZ+MY6f3Y68YOhbCMHYwiId22B8IH5U+5JdjLrfSRvOP4FWE2xf6VluQuTg4lJWg\ns50Ls/ku5MpXIk6syLVIJY+93Am9HmMPg87xvPDbiKYOJX/8fcQlR2K4XwRwANgE\nxnmB5M0VAgMBAAECggEAG9GC07qwCkhqwiDah0Zp4+vPS615eiwVv829j5BFBzPV\nL/wHK9RwTKO60plcvQOI11JDZaLn5qUq3vIZVpisDKjcZQZL+LJ2FrTkLBRE6x9b\nmQUneHS38FGFbnwJSp+k4nT/4jWKtQtUwnLU1C7is5UnoP6YrVdSdovxWyNLmoPv\n5k8DLzFVQlaubhr1Hhno0NdAW7iyarOBeTrf23bSis9oFGlYCB6yNaXwZXRntDgv\nBCoyLAoL+dEzaVRKUNYxP4NdNFnjYUL5bFyre0G4xZseX8byqWd4M1zCCYjP3iv0\n/0doVLAqTtc0fsY5ar83VJcX9s8+qJDNZti9dxPHnQKBgQDrsTk6TEkma3DsAc+x\nJqZqB8AB9yaI+i8GlyzpK2OaHE7LqTVUDIEc+cgOPwpHuWzPflbQ3kCgZjSi+8kH\nff0yU1ntWKTyNvu2kdHXkSG5Tk2VhfWByU0zq3wFqHqhQJw8tF05bkExPDQ/fsOE\nGBcWT3qNs7j63u590FgFped40wKBgQC7MiAScYr6LyKHqFtkxnyHxEiGwaihNhip\nmfhhjmyPf4putiASdolam/JArzKTUDe1KpxqqCkZjAk3yuFB+uIjXtZ/y6KJvVPJ\najIlDlmm8m3S+CNPrNvj1FDumMzpqyWWVW38FKhfyeLDdTiINwWoYO0T7Ok25g1o\nf+aqIx/xdwKBgQC5I4VonfP4Ef2p5eJXrZybPWs+H/5NKvk1nBrTLhoXPJVItaoG\nU6w4Lp1PU4WnwagPdZaMi4kIdkBypoXLNNRna8IABtnKyhX/25uSUZbEERYwlgG7\n6XyTUekiKK3rbO1NYgC41DqxijEgj1rVsHayN8x08vAjYGrGuZnrFd81sQKBgAXu\nv791476sEb8U4diexcGTweyrZIm/aiat34ZP+jbOBvgdQ4TyRsYdXR8ZrlOm3i0a\nrZxfufW6T2x6PItXxSTz0353WK5e1rHycKZl/wdgdYSTIqNayhk9WFdHdm8NYoKS\nMIslqHRotIwXQfRnMgG1GK5h+r4nqlMegpPvywpfAoGBANn4CXThmW+7I+pAHkqB\nuO7v5jtlbLFFNUxJD7PiXWSZvtFs+Y3gSkHNNYJZCzyGTI4eo4PtNbq8Kjs/u7aq\nGrEl7PoZCgES8VRmeEHDFByzrjR2NVzsGgEGXdImzYnYxN/X1fSlwPm/4rdBueSd\nDOkE96Vrzj5+1mjGsc1MlJQi\n-----END PRIVATE KEY-----\n",
    "client_email": "sports-betting-bot@sports-betting-bot.iam.gserviceaccount.com",
    "client_id": "113262066328643350253",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sports-betting-bot%40sports-betting-bot.iam.gserviceaccount.com"
}

credentials = ServiceAccountCredentials.from_json_keyfile_dict(CLIENT_SECRET, scope)
client = gspread.authorize(credentials)

spreadsheet = client.open('Sports Betting Bot')


def upload_df(df, sheet_name):
    sheet_name = sheet_name.upper()

    if sheet_name in sheet_names:
        spreadsheet.worksheet(sheet_name).clear()
        spreadsheet.worksheet(sheet_name).update([df.columns.values.tolist()] + df.values.tolist())


def download_df(sheet_name):
    sheet_name = sheet_name.upper()

    if sheet_name in sheet_names:
        data = spreadsheet.worksheet(sheet_name).get_all_values()
        df = pd.DataFrame.from_records(data[1:], columns=data[0])

        return df

    return None


if __name__ == '__main__':
    df = download_df('BETS')
    print(df)