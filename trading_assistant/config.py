# trading_assistant/config.py

import os
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
ALPACA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
ALPACA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
ALPACA_API_BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')
