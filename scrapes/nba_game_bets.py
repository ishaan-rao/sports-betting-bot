import datetime
import pandas as pd

from nba_api.stats.endpoints import leaguegamefinder

# get_games_by_date() - 
# Function for getting NBA games and results on a certain date
# 
# input: Date String, must be in the format "MM/DD/YYYY". Must be in the past
# or present day.
# 
# returns: A pandas data frame, each row is a game result. Columns denote
# who won, who lost (using 3 letter abbreviations), the total sum
# of points scored (for over/under), and the spread (how much winner won by)
def get_games_by_date(date):

    # error handling: if date is in the future, function throws an error    
    req_date = datetime.datetime.strptime(date, "%m/%d/%Y")
    if (req_date.date() > datetime.date.today()):
        raise ValueError("Input Date must be in the past")

    # queries the NBA API, to get the games from that day
    gamefinder = leaguegamefinder.LeagueGameFinder(
        season_nullable = '2021-22',
        date_to_nullable=date,
        date_from_nullable=date,
        league_id_nullable="00",
        outcome_nullable="W"
        )
    games = gamefinder.get_data_frames(
        )[0][["TEAM_ABBREVIATION", "GAME_DATE", "MATCHUP", "PTS", "PLUS_MINUS"]]

    
    # rename columns to make more sense for our purposes
    games = games.rename(
        columns={"TEAM_ABBREVIATION": "WINNER", 
                 "PTS": "WINNER_PTS", 
                 "PLUS_MINUS": "SPREAD"}
        )                                                            
    
    # parse matchup string for abbreviation of losing team 
    games["LOSER"] = [vs[-3:] for vs in games["MATCHUP"]]
    # determine amount of points losing team scored
    games["LOSER_PTS"] = games["WINNER_PTS"] - games["SPREAD"]
    # determine sum of points for over under
    games["SUM_PTS"] = games["WINNER_PTS"] + games["LOSER_PTS"]
    
    home_teams = []
    rd_teams = []
    for match in games["MATCHUP"]:
        if ("vs." in match):
            home_teams.append(match[:3])
            rd_teams.append(match[-3:])
        else:
            home_teams.append(match[-3:])
            rd_teams.append(match[:3])
    
    games["HOME"] = home_teams
    games["ROAD"] = rd_teams
    
    
    return games


if __name__ == '__main__':
    df = get_games_by_date('11/27/2021')
    print(df)