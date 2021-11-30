import os

from dotenv import load_dotenv

load_dotenv()

# SPORTS_BETTING_GENERAL_ID = 913510229419909150
# GM_GN_ID = 911472276145307698

## GOOGLE SHEETS API
JSON_KEYFILE = {
    "type": "service_account",
    "project_id": "sports-betting-bot",
    "private_key_id": os.getenv('PRIVATE_KEY_ID'),
    "private_key": os.getenv('PRIVATE_KEY'),
    "client_email": os.getenv('CLIENT_EMAIL'),
    "client_id": os.getenv('CLIENT_ID'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv('CLIENT_CERT_URL')
}

SCOPE = [
    'https://spreadsheets.google.com/feeds', 
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file', 
    'https://www.googleapis.com/auth/drive'
]

SHEET_NAMES = ['BETS', 'BALANCES', 'NBA', 'UCL']


## SCRAPE URLS
NBA_GAME_URL = 'https://sportsbook.draftkings.com/leagues/basketball/88670846?category=game-lines&subcategory=game'
