import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

# API Sports Settings (Example using API-Football or similar)
SPORTS_API_KEY = os.getenv("SPORTS_API_KEY", "YOUR_SPORTS_API_KEY_HERE")
CLEARSPORTS_API_KEY = os.getenv("CLEARSPORTS_API_KEY", "sk_live_LBPFK045ql-rypka2bu1rB135IADagvJSFmKRtu2EFs")
THE_ODDS_API_KEY = os.getenv("THE_ODDS_API_KEY", "156d0fb040fd48259cd7bec657e3d421")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

CLEARSPORTS_BASE_URL = "https://api.clearsportsapi.com/v1"
THE_ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
SPORTS_API_BASE_URL = "https://v3.football.api-sports.io" # Legacy if needed

# Base directory
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CONFIG_DIR)

# Database Settings
DB_PATH = os.path.join(BASE_DIR, "data", "matches.db")
JSON_DATA_PATH = os.path.join(BASE_DIR, "data")

# Analysis Settings
MIN_VALUE_BET_THRESHOLD = 0.05 # 5% edge
DEFAULT_BANKROLL = 1000.0
STAKE_STRATEGY = "fixed" # options: "fixed", "kelly", "variable"
DEFAULT_STAKE_PERCENT = 0.02 # 2% of bankroll

# Market Settings
SUPPORTED_MARKETS = [
    "match_winner",
    "double_chance",
    "over_under_goals",
    "both_teams_to_score",
    "asian_handicap"
]
