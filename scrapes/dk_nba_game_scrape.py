import pandas as pd
import requests

from bs4 import BeautifulSoup

from utils.sheets_utils import upload_df

# # TODO: remove this block into separate file
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

from constants import JSON_KEYFILE, NBA_GAME_URL, SCOPE, SHEET_NAMES

# credentials = ServiceAccountCredentials.from_json_keyfile_dict(JSON_KEYFILE, SCOPE)
# client = gspread.authorize(credentials)

# spreadsheet = client.open('Sports Betting Bot')


# def upload_df(df, sheet_name):
#     sheet_name = sheet_name.upper()

#     if sheet_name in SHEET_NAMES:
#         spreadsheet.worksheet(sheet_name).clear()
#         spreadsheet.worksheet(sheet_name).update([df.columns.values.tolist()] + df.values.tolist())
# ##################################


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
            'spread_line_away': f'{spread_lines[2*i]}',
            'spread_line_home': f'{spread_lines[2*i + 1]}',
            'ml_away': f'{ml_odds[2*i]}',
            'ml_home': f'{ml_odds[2*i + 1]}', 
            'ou_over': f'{ou_odds[2*i]}',
            'ou_under': f'{ou_odds[2*i + 1]}',
            'ou_value': f'{ou_lines[2*i]}'
        }

        nba_game_lines_df = nba_game_lines_df.append(nba_game_line, ignore_index=True)

    return nba_game_lines_df


def upload_nba_game_lines():
    df = nba_game_scrape()
    upload_df(df, 'NBA')


if __name__ == '__main__':
    upload_nba_game_lines()