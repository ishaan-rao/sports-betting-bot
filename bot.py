import discord
import os

from bets import process_bets

from dotenv import load_dotenv

from scrapes.dk_nba_game_scrape import upload_nba_game_lines
from utils.general import create_leaderboard_embed, create_spread_bet, create_ml_bet, create_ou_bet, create_bet_embed, parse_input
from utils.nba_utils import create_nba_game_line_embed
from utils.sheets_utils import download_df, upload_df

load_dotenv()
client = discord.Client()

def find_game(df, team):
    game = df[(df['away_team'] == team) | (df['home_team'] == team)]

    if len(game) > 0:
        curr_game = game.iloc[0]
        is_home = (curr_game['home_team'] == team)

        return curr_game, is_home

    return None, None


@client.event
async def on_ready():
    print(f'{client.user} is ready.')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    author = message.author

    if message.channel.name == 'place-bets':
        command, args = parse_input(message.content)

        # sports betting bot help
        if command == '$help':
            await message.channel.send('Welcome to Sports Betting Bot! Our available commands are: `$balance`, `$bets`, `$leaderboard`, `$lines`, `$spread`, `$ml`, and `$ou`.')
            await message.channel.send('Type `help` after any of the above commands to see more details about them.')

        # get current balance
        if command == '$balance':
            if len(args) > 0:
                if args[0] == 'help':
                    await message.channel.send('Use `$balance` to see how many units you currently have.')
                else: 
                    await message.channel.send('Please use `$balance help` to see all commands.')
            else:
                balance_df = download_df('BALANCES')
                
                if f'{author}' not in balance_df['Username'].values:
                    new_row = {'Username': f'{author}', 'Balance': 100}
                    balance_df = balance_df.append(new_row, ignore_index = True)
                    
                balance = balance_df[balance_df['Username'] == f'{author}']['Balance'].squeeze()

                await message.channel.send(f'You have {balance} units currently.')
                upload_df(balance_df, 'BALANCES')


        # get upcoming lines
        if command == '$lines':
            if len(args) == 0:
                await message.channel.send('Please use `$lines help` to see all commands.')
            
            else:
                if args[0] == 'help':
                    await message.channel.send('Use `$lines <league>` to see all current game lines for a given sport.')
                    await message.channel.send('Use `$lines <league> <team>` to see the line for a specific team.')
                elif args[0].lower() == 'nba':
                    nba_game_lines_df = download_df('NBA')
                    
                    if len(nba_game_lines_df.index) > 0:
                        if len(args) > 1:
                            team = args[1].upper()

                            nba_game, _ = find_game(nba_game_lines_df, team)

                            if nba_game is not None:
                                embed_game = create_nba_game_line_embed(nba_game)
                                await message.channel.send(embed=embed_game)
                            else:
                                await message.channel.send(f'No game lines were found for {args[1]}.')
                        else: 
                            for _, nba_game in nba_game_lines_df.iterrows():
                                embed_game = create_nba_game_line_embed(nba_game)
                                await message.channel.send(embed=embed_game)
                    else:
                        await message.channel.send('No game lines are available right now. Please check later.')


        # place a spread bet
        if command == '$spread':
            if len(args) == 0:
                await message.channel.send('Please use `$spread help` to see all commands.')
            
            else:
                if args[0] == 'help':
                    await message.channel.send('Use `$spread <league> <team>` to place a spread bet.')
                    await message.channel.send('**Example:** `$spread nba LAL` will place a bet for the Lakers to cover the spread.')
                elif len(args) > 1:
                    league = args[0].lower()
                    team = args[1].upper()

                    if league == 'nba': 
                        nba_game_lines_df = download_df('NBA')

                        if len(nba_game_lines_df.index) > 0:
                            nba_game, is_home = find_game(nba_game_lines_df, team)

                            if nba_game is not None:
                                spread_bet = create_spread_bet(nba_game, author, league, team, is_home)

                                if spread_bet:
                                    bets_df = download_df('BETS')
                                    bets_df = bets_df.append(spread_bet, ignore_index=True)
                                    await message.channel.send(f'{author.mention} successfully placed a spread bet!')
                                    upload_df(bets_df, 'BETS')
                            else:
                                await message.channel.send(f'Cannot place a spread bet on this game right now.')
                        else:
                            await message.channel.send('Please use `$spread help` to see all commands.')
                    else:
                        await message.channel.send('Please use `$spread help` to see all commands.')
                else:
                    await message.channel.send('Please use `$spread help` to see all commands.')


        # place a moneyline bet
        if command == '$ml':
            if len(args) == 0:
                await message.channel.send('Please use `$ml help` to see all commands.')
            
            else:
                if args[0] == 'help':
                    await message.channel.send('Use `$ml <league> <team>` to place a moneyline bet.')
                    await message.channel.send('**Example:** `$ml nba LAL` will place a bet for the Lakers to win the game.')
                elif len(args) > 1:
                    league = args[0].lower()
                    team = args[1].upper()

                    if league == 'nba': 
                        nba_game_lines_df = download_df('NBA')

                        if len(nba_game_lines_df.index) > 0:
                            nba_game, is_home = find_game(nba_game_lines_df, team)

                            if nba_game is not None:
                                ml_bet = create_ml_bet(nba_game, author, league, team, is_home)

                                if ml_bet:
                                    bets_df = download_df('BETS')
                                    bets_df = bets_df.append(ml_bet, ignore_index=True)
                                    await message.channel.send(f'{author.mention} successfully placed a moneyline bet!')
                                    upload_df(bets_df, 'BETS')
                            else:
                                await message.channel.send(f'Cannot place a moneyline bet on this game right now.')
                        else:
                            await message.channel.send('Please use `$ml help` to see all commands.')
                    else:
                        await message.channel.send('Please use `$ml help` to see all commands.')
                else:
                    await message.channel.send('Please use `$ml help` to see all commands.')


        # place an over/under bet
        if command == '$ou':
            if len(args) == 0:
                await message.channel.send('Please use `$ou help` to see all commands.')
            
            else:
                if args[0] == 'help':
                    await message.channel.send('Use `$ou <league> <team> over` to place an over bet on the game that a team is playing in.')
                    await message.channel.send('Use `$ou <league> <team> under` to place an under bet on the game that a team is playing in.')
                    await message.channel.send('**Example:** `$ou nba LAL over` will place a bet for the Lakers game to hit the over.')
                elif len(args) > 2:
                    league = args[0].lower()
                    team = args[1].upper()
                    direction = args[2].lower()

                    if direction not in ['over', 'under']:
                        await message.channel.send('Please use `$ou help` to see all commands.')
                        return

                    if league == 'nba': 
                        nba_game_lines_df = download_df('NBA')

                        if len(nba_game_lines_df.index) > 0:
                            nba_game, is_home = find_game(nba_game_lines_df, team)

                            if nba_game is not None:
                                ou_bet = create_ou_bet(nba_game, author, league, team, direction, is_home)

                                if ou_bet:
                                    bets_df = download_df('BETS')
                                    bets_df = bets_df.append(ou_bet, ignore_index=True)
                                    await message.channel.send(f'{author.mention} successfully placed an over/under bet!')
                                    upload_df(bets_df, 'BETS')
                                else:
                                    await message.channel.send(f'Cannot place a over/under bet on this game right now.')
                            else:
                                await message.channel.send(f'Cannot place an over/under bet on this game right now.')
                        else:
                            await message.channel.send('Please use `$ou help` to see all commands.')
                    else:
                        await message.channel.send('Please use `$ou help` to see all commands.')
                else:
                    await message.channel.send('Please use `$ou help` to see all commands.')


        if command == '$bets':
            if len(args) > 0:
                if args[0] == 'help':
                    await message.channel.send('Use `$bets` to see your current outstanding bets.')
                else: 
                    await message.channel.send('Please use `$bets help` to see all commands.')
            else:
                bets_df = download_df('BETS')
                bets_df_user = bets_df[bets_df['Username'] == f'{author}']

                if len(bets_df_user.index) > 0:
                    for i, row in bets_df_user.iterrows():
                        embed_bet = create_bet_embed(row, i)
                        await message.channel.send(embed=embed_bet)
                else:
                    await message.channel.send('You have no outstanding bets.')


        if command == '$leaderboard':
            if len(args) > 0:
                if args[0] == 'help':
                    await message.channel.send('Use `$leaderboard` to see the top bettors.')
                else: 
                    await message.channel.send('Please use `$leaderboard help` to see all commands.')
            else:
                balance_df = download_df('BALANCES')

                embed_leaderboard = create_leaderboard_embed(balance_df)
                await message.channel.send(embed=embed_leaderboard)


        if command == '$scrape':
            if len(args) > 0:
                if args[0] == 'help':
                    await message.channel.send('Use `$scrape <league>` to scrape the lines for a given league.')
                elif args[0].lower() == 'nba':
                    upload_nba_game_lines()
                    await message.channel.send(f'Updated lines and odds for {args[0].upper()} games!')
                else: 
                    await message.channel.send('Please use `$scrape help` to see all commands.')
            else:
                await message.channel.send('Please use `$scrape help` to see all commands.')


        if command == '$update':
            if len(args) > 0:
                if args[0] == 'help':
                    await message.channel.send('Use `$update` to evaluate any pending bets and update balances.')
                else: 
                    await message.channel.send('Please use `$update help` to see all commands.')
            else:
                process_bets()
                await message.channel.send(f'Processed bets and updated balances!')


        if command == '$hello':
            await message.channel.send(f'Hello {author.mention}!')
        

    if message.channel.name == 'gm-gn':
        if message.content.strip().lower().startswith('gm'):
            await message.channel.send(f'gm {author.mention}!')

        if message.content.strip().lower().startswith('gn'):
            await message.channel.send(f'gn {author.mention}!')
    

client.run(os.getenv('TOKEN'))