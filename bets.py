import pandas as pd

from scrapes.nba_game_bets import get_games_by_date
from utils.sheets_utils import download_df, upload_df

def find_result(results, team):
    game = results[(results['WINNER'] == team) | (results['LOSER'] == team)]

    return game


def process_bet(bet):
    
    league = bet['League'].lower()
    bet_type = bet['Type'].lower()
    team = bet['Team'].upper()

    if league == 'nba':
        yday = pd.Timestamp('now') - pd.Timedelta(days=1)
        results = get_games_by_date(yday.strftime('%m/%d/%Y'))
        result = find_result(results, team)

        if bet_type == 'spread':
            margin = float(result['SPREAD'])
            won_game = result['WINNER'] == team
            spread_dir, spread = bet['Line'][0], float(bet['Line'][1:])

            if won_game.squeeze():
                if spread_dir == '+':
                    update_balance_win(bet['Username'], bet['Odds'], bet['Units'])
                elif spread > margin:
                    update_balance_win(bet['Username'], bet['Odds'], bet['Units'])
                else:
                    update_balance_loss(bet['Username'], bet['Units'])
            else:
                if spread_dir == '-':
                    update_balance_loss(bet['Username'], bet['Units'])
                elif spread > margin:
                    update_balance_win(bet['Username'], bet['Odds'], bet['Units'])
                else:
                    update_balance_loss(bet['Username'], bet['Units'])

            return None

        elif bet_type == 'ml':            
            if result['WINNER'] == team:
                update_balance_win(bet['Username'], bet['Odds'], bet['Units'])
            else:
                update_balance_loss(bet['Username'], bet['Units'])

            return None

        elif bet_type == 'ou':
            total = float(result['SUM_PTS'])
            direction = bet['Direction'].lower()
            line = float(bet['Line'])

            if (direction == 'over' and total > line) or (direction == 'under' and total < line):
                update_balance_win(bet['Username'], bet['Odds'], bet['Units'])
            elif (direction == 'over' and total < line) or (direction == 'under' and total > line):
                update_balance_loss(bet['Username'], bet['Units'])

            return None

        else:
            return bet
    else:
        return bet


def process_bets():
    bets_df = download_df('BETS')
    pending_bets_df = pd.DataFrame(columns=['Username', 'Date', 'League', 'Type', 'Odds', 'Line', 'Direction', 'Units', 'Home Team', 'Away Team', 'Team'])

    for i, bet in bets_df.iterrows():
        processed_bet = process_bet(bet)

        if processed_bet is not None:
            pending_bets_df = pending_bets_df.append(processed_bet, ignore_index=True)
    
    upload_df(pending_bets_df, 'BETS')


def calculate_profit(odds, units):
    neg = odds[0] == '-'
    odds = int(odds[1:])
    units = float(units)

    if neg:
        profit = 100 * units / odds
    else:
        profit = odds * units / 100

    return profit


def update_balance_win(user, odds, units):
    balance_df = download_df('BALANCES')
                
    if user not in balance_df['Username'].values:
        new_row = {'Username': user, 'Balance': 100}
        balance_df = balance_df.append(new_row, ignore_index = True)

    profit = calculate_profit(odds, units)
    curr_balance = balance_df[balance_df['Username'] == user]

    balance_df.loc[curr_balance.index, 'Balance'] = str(float(curr_balance['Balance']) + profit)
    upload_df(balance_df, 'BALANCES')


def update_balance_loss(user, units):
    balance_df = download_df('BALANCES')
                
    if user not in balance_df['Username'].values:
        new_row = {'Username': user, 'Balance': 100}
        balance_df = balance_df.append(new_row, ignore_index = True)

    curr_balance = balance_df[balance_df['Username'] == user]

    balance_df.loc[curr_balance.index, 'Balance'] = str(float(curr_balance['Balance']) - float(units))
    upload_df(balance_df, 'BALANCES')
    

if __name__ == '__main__':
    process_bets()