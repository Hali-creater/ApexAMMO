# trading_assistant/data_handler.py

import yfinance as yf
import finnhub
import pandas as pd
from .utils import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)

def fetch_historical_data(ticker, start_date, end_date):
    """Fetches historical stock data using yfinance."""
    try:
        logger.info(f"Fetching historical data for {ticker} from {start_date} to {end_date}")
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            logger.warning(f"No historical data found for {ticker}")
            return None
        return data
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {e}")
        return None

def fetch_realtime_data(finnhub_client, ticker):
    """Fetches real-time stock data using Finnhub."""
    if finnhub_client is None:
        return None
    try:
        logger.info(f"Fetching real-time data for {ticker}")
        quote = finnhub_client.quote(ticker)
        if quote and 'c' in quote:
            return quote
        else:
            logger.warning(f"Could not retrieve real-time data for {ticker}")
            return None
    except Exception as e:
        logger.error(f"Error fetching real-time data for {ticker}: {e}")
        return None

def fetch_news_headlines(finnhub_client, ticker=None, category=None):
    """Fetches news headlines using Finnhub."""
    if finnhub_client is None:
        return None
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        if ticker:
            logger.info(f"Fetching news for {ticker}")
            news = finnhub_client.company_news(ticker, _from=start_date_str, to=end_date_str)
        elif category:
            logger.info(f"Fetching news for category {category}")
            news = finnhub_client.general_news(category=category, min_id=0)
        else:
            logger.warning("Please provide either a ticker or a category for news.")
            return None

        if news:
            return news
        else:
            logger.warning(f"No news found for ticker: {ticker} or category: {category}")
            return None
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return None
