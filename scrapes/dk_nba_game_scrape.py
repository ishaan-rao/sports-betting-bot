import pandas as pd
import requests

from bs4 import BeautifulSoup

# TODO: remove this block into separate file
import gspread
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
##################################

NBA_GAME_URL = 'https://sportsbook.draftkings.com/leagues/basketball/88670846?category=game-lines&subcategory=game'

def convert_nba_name(team):
    split = team.split(' ')
    city = split[0]
    mascot = split[1]

    if len(city) == 2:
        city = city + mascot[0]

    return city


def nba_game_scrape():

    response = requests.get(NBA_GAME_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    rows = soup.findAll('tr')

    teams = []
    spread_lines, spread_odds = [], []
    ou_lines, ou_odds = [], []
    ml_odds = []

    for row in rows:
        team_div = row.find('div', {'class': 'event-cell__name-text'})
        if team_div:
            team = team_div.text
            teams.append(team)

            tds = row.findAll('td')
            if len(tds) == 3:
                spread_td = tds[0]
                ou_td = tds[1]
                ml_td = tds[2]
            
                spread_line = spread_td.find('span', {'class': 'sportsbook-outcome-cell__line'})
                spread_odd = spread_td.find('span', {'class': 'sportsbook-odds'})

                ou_line = ou_td.find('span', {'class': 'sportsbook-outcome-cell__line'})
                ou_odd = ou_td.find('span', {'class': 'sportsbook-odds'})

                ml_odd = ml_td.find('span', {'class': 'sportsbook-odds'})

                spread_lines.append(spread_line.text if spread_line else spread_line)
                spread_odds.append(spread_odd.text if spread_odd else spread_odd)

                ou_lines.append(ou_line.text if ou_line else ou_line)
                ou_odds.append(ou_odd.text if ou_odd else ou_odd)

                ml_odds.append(ml_odd.text if ml_odd else ml_odd)

        

    teams = [convert_nba_name(team) for team in teams]
    away_teams = teams[::2]
    home_teams = teams[1::2]

    nba_game_lines_df = pd.DataFrame()

    for i in range(len(away_teams)):
        nba_game_line = {
            'home_team': home_teams[i],
            'away_team': away_teams[i],
            'game_str': f'{away_teams[i]} vs. {home_teams[i]}',
            'spread_str': f'{away_teams[i]} ({spread_lines[2*i]}) vs. {home_teams[i]} ({spread_lines[2*i + 1]})',
            'ml_str': f'{away_teams[i]} ({ml_odds[2*i]}) vs. {home_teams[i]} ({ml_odds[2*i + 1]})',
            'ou_str': f'O/U {ou_lines[2*i]}',
            'spread_odds_away': f'{spread_odds[2*i]}',
            'spread_odds_home': f'{spread_odds[2*i + 1]}',
            # 'spread_odds': {
            #     f'{away_teams[i]}': f'{spread_odds[2*i]}',
            #     f'{home_teams[i]}': f'{spread_odds[2*i + 1]}',
            # }, 
            'spread_line_away': f'{spread_lines[2*i]}',
            'spread_line_home': f'{spread_lines[2*i + 1]}',
            # 'spread_line': {
            #     f'{away_teams[i]}': f'{spread_lines[2*i]}',
            #     f'{home_teams[i]}': f'{spread_lines[2*i + 1]}',
            # }, 
            'ml_away': f'{ml_odds[2*i]}',
            'ml_home': f'{ml_odds[2*i + 1]}', 
            # 'ml': {
            #     f'{away_teams[i]}': f'{ml_odds[2*i]}',
            #     f'{home_teams[i]}': f'{ml_odds[2*i + 1]}',
            # },
            'ou_over': f'{ou_odds[2*i]}',
            'ou_under': f'{ou_odds[2*i + 1]}',
            'ou_value': f'{ou_lines[2*i]}'
            # 'ou': {
            #     f'over': f'{ou_odds[2*i]}',
            #     f'under': f'{ou_odds[2*i + 1]}',
            #     'value': f'{ou_lines[2*i]}'
            # }
        }

        nba_game_lines_df = nba_game_lines_df.append(nba_game_line, ignore_index=True)

    return nba_game_lines_df


def upload_nba_game_lines():
    df = nba_game_scrape()
    upload_df(df, 'NBA')


if __name__ == '__main__':
    upload_nba_game_lines()