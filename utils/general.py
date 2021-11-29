import discord
import pandas as pd

def parse_input(message):
    message = ' '.join(message.split())
    message_split = message.split(' ')

    return message_split[0].lower(), message_split[1:]
   

def create_spread_bet(game, author, league, team, is_home):
    tag = 'home' if is_home else 'away'

    bet = {
        'Username': f'{author}',
        'Date': pd.Timestamp('now').strftime('%Y-%m-%d'),
        'League': league,
        'Type': 'spread',
        'Odds': game[f'spread_odds_{tag}'],
        'Line': game[f'spread_line_{tag}'],
        'Direction': '',
        'Units': 1,
        'Home Team': game['home_team'],
        'Away Team': game['away_team'],
        'Team': team
    }

    if bet['Line'] == 'None' or bet['Odds'] == 'None':
        return None

    return bet


def create_ml_bet(game, author, league, team, is_home):
    tag = 'home' if is_home else 'away'

    bet = {
        'Username': f'{author}',
        'Date': pd.Timestamp('now').strftime('%Y-%m-%d'),
        'League': league,
        'Type': 'ml',
        'Odds': game[f'ml_{tag}'],
        'Line': '',
        'Direction': '',
        'Units': 1, 
        'Home Team': game['home_team'],
        'Away Team': game['away_team'],
        'Team': team
    }

    if bet['Odds'] == 'None':
        return None

    return bet


def create_ou_bet(game, author, league, team, direction):
    
    bet = {
        'Username': f'{author}',
        'Date': pd.Timestamp('now').strftime('%Y-%m-%d'),
        'League': league,
        'Type': 'ou',
        'Odds': game[f'ou_{direction}'],
        'Line': game['ou_value'],
        'Direction': direction,
        'Units': 1,
        'Home Team': game['home_team'],
        'Away Team': game['away_team'],
        'Team': team
    }

    if bet['Line'] == 'None' or bet['Odds'] == 'None':
        return None

    return bet


def create_bet_embed(bet, i):
    bet_type = bet['Type'].lower()
    description = ''
    
    if bet_type == 'spread':
        description = f'{bet["Team"]} ({bet["Line"]}) @ {bet["Odds"]}'
    elif bet_type == 'ml':
        description = f'{bet["Team"]} ML @ {bet["Odds"]}'
    elif bet_type == 'ou':
        direction = 'O' if bet['Direction'].lower() == 'over' else 'U'
        description = f'{bet["Team"]} {direction} {bet["Line"]} @ {bet["Odds"]}'

    embed_bet = discord.Embed(
        title=f'Bet {i+1}',
        color=discord.Color.red(),
        description=description
    )

    return embed_bet


def create_leaderboard_embed(balance_df):

    balance_df_sorted = balance_df.sort_values(by=['Balance'], ascending=False)
  
    description = ''

    for i, row in balance_df_sorted.iterrows():
        description += f'{i+1}. {row["Username"]}: {row["Balance"]} units\n'

    embed_leaderboard = discord.Embed(
        title=f'Leaderboard',
        color=discord.Color.red(),
        description=description
    )

    return embed_leaderboard

