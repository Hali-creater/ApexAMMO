# trading_assistant/analysis.py

import pandas as pd
import pandas_ta as ta
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from trading_assistant.utils import get_logger
from urllib.error import URLError

logger = get_logger(__name__)

# Download VADER lexicon for sentiment analysis
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    try:
        nltk.download('vader_lexicon')
    except URLError:
        logger.error("Failed to download vader_lexicon due to a network error.")


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates technical indicators and adds them as new columns to the DataFrame.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning("Input is not a valid pandas DataFrame or is empty.")
        return pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(1)

    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df.columns for col in required_cols):
        logger.error(f"DataFrame must contain the following columns: {required_cols}")
        return df

    try:
        logger.info("Calculating technical indicators...")
        df.ta.rsi(append=True)
        df.ta.macd(append=True)
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        return df
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        return df

def determine_market_personality(df: pd.DataFrame) -> str:
    """
    Determines the market personality based on technical indicators.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning("Input is not a valid pandas DataFrame or is empty.")
        return 'Undetermined'

    if isinstance(df.columns, pd.MultiIndex):
         df.columns = df.columns.get_level_values(1)

    try:
        logger.info("Determining market personality...")
        df['SMA_20'] = df['SMA_20'].fillna(0)
        df['SMA_50'] = df['SMA_50'].fillna(0)

        if df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1] and df['Close'].iloc[-1] > df['SMA_20'].iloc[-1]:
            if 'MACDH_12_26_9' in df.columns and df['MACDH_12_26_9'].iloc[-1] > 0:
                 return 'Trending Up'
            elif 'MACDH_12_26_9' not in df.columns:
                 return 'Trending Up'

        elif df['SMA_20'].iloc[-1] < df['SMA_50'].iloc[-1] and df['Close'].iloc[-1] < df['SMA_20'].iloc[-1]:
            if 'MACDH_12_26_9' in df.columns and df['MACDH_12_26_9'].iloc[-1] < 0:
                return 'Trending Down'
            elif 'MACDH_12_26_9' not in df.columns:
                 return 'Trending Down'

        if 'RSI_14' in df.columns and 40 < df['RSI_14'].iloc[-1] < 60:
             if abs(df['SMA_20'].iloc[-1] - df['SMA_50'].iloc[-1]) / df['SMA_50'].iloc[-1] < 0.02:
                 return 'Range-Bound'

        return 'Undetermined'
    except Exception as e:
        logger.error(f"Error determining market personality: {e}")
        return 'Undetermined'

def analyze_sentiment(headline: str) -> dict:
    """
    Analyzes the sentiment of a news headline using NLTK's VADER.
    """
    if not isinstance(headline, str) or not headline:
        logger.warning("Input is not a valid string or is empty.")
        return {"error": "Invalid input headline"}
    try:
        analyzer = SentimentIntensityAnalyzer()
        sentiment_scores = analyzer.polarity_scores(headline)
        return sentiment_scores
    except Exception as e:
        logger.error(f"Error analyzing sentiment for headline '{headline}': {e}")
        return {"error": str(e)}
