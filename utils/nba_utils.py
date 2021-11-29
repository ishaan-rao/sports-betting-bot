import discord
from scrapes.dk_nba_game_scrape import NBA_GAME_URL


def create_nba_game_line_embed(nba_game):
    embed_game = discord.Embed(
        title=f'{nba_game["game_str"]}',
        url=NBA_GAME_URL,
        color=discord.Color.blue()
    )
    embed_game.set_thumbnail(url='https://theundefeated.com/wp-content/uploads/2017/06/nbalogo.jpg?w=1024')
    embed_game.add_field(name='Spread', value=f'{nba_game["spread_str"]}', inline=False)
    embed_game.add_field(name='Moneyline', value=f'{nba_game["ml_str"]}', inline=False)
    embed_game.add_field(name='Over/Under', value=f'{nba_game["ou_str"]}', inline=False)
    embed_game.add_field(name='Home Team', value=f'{nba_game["home_team"]}', inline=True)
    embed_game.add_field(name='Away Team', value=f'{nba_game["away_team"]}', inline=True)

    return embed_game