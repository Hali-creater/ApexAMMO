# trading_assistant/trading_logic.py

import pandas as pd
from .utils import get_logger
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

logger = get_logger(__name__)

def initialize_alpaca_api(api_key, api_secret):
    """Initializes the Alpaca API client."""
    try:
        trading_client = TradingClient(api_key, api_secret, paper=True)
        return trading_client
    except Exception as e:
        logger.error(f"Error initializing Alpaca API: {e}")
        return None

def check_alpaca_connection(trading_client):
    """Checks the connection to the Alpaca API."""
    try:
        account = trading_client.get_account()
        logger.info(f"Alpaca connection successful. Account status: {account.status}")
        return True
    except Exception as e:
        logger.error(f"Error checking Alpaca connection: {e}")
        return False

def place_order(trading_client, symbol, qty, side):
    """Places a market order."""
    try:
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY
        )
        market_order = trading_client.submit_order(order_data=market_order_data)
        logger.info(f"Market order placed for {qty} shares of {symbol}: {market_order.id}")
        return market_order
    except Exception as e:
        logger.error(f"Error placing order for {symbol}: {e}")
        return None

def generate_trading_signal(technical_data: pd.DataFrame, sentiment_scores: dict) -> str:
    """
    Generates a trading signal (BUY, SELL, HOLD) based on technical indicators
    and sentiment analysis results.
    """
    if not isinstance(technical_data, pd.DataFrame) or technical_data.empty:
        logger.warning("Technical data input is not a valid pandas DataFrame or is empty.")
        return 'UNDETERMINED'
    if not isinstance(sentiment_scores, dict) or 'compound' not in sentiment_scores:
        logger.warning("Sentiment scores input is not a valid dictionary or is missing 'compound' score.")
        return 'UNDETERMINED'

    required_tech_cols = ['RSI_14', 'MACD_12_26_9', 'MACDH_12_26_9', 'MACDS_12_26_9', 'SMA_20', 'SMA_50', 'Close']
    if not all(col in technical_data.columns for col in required_tech_cols):
        logger.error(f"Technical data DataFrame must contain the following columns: {required_tech_cols}")
        return 'UNDETERMINED'

    latest_data = technical_data.iloc[-1]
    tech_buy_signal = False
    tech_sell_signal = False

    if technical_data.shape[0] >= 2:
        if technical_data['SMA_20'].iloc[-2] <= technical_data['SMA_50'].iloc[-2] and latest_data['SMA_20'] > latest_data['SMA_50']:
            tech_buy_signal = True
        if latest_data['RSI_14'] < 30:
             if technical_data['RSI_14'].iloc[-2] <= latest_data['RSI_14']:
                 tech_buy_signal = True
        if technical_data['MACD_12_26_9'].iloc[-2] <= technical_data['MACDS_12_26_9'].iloc[-2] and latest_data['MACD_12_26_9'] > latest_data['MACDS_12_26_9']:
             tech_buy_signal = True
        if technical_data['SMA_20'].iloc[-2] >= technical_data['SMA_50'].iloc[-2] and latest_data['SMA_20'] < latest_data['SMA_50']:
            tech_sell_signal = True
        if latest_data['RSI_14'] > 70:
             if technical_data['RSI_14'].iloc[-2] >= latest_data['RSI_14']:
                 tech_sell_signal = True
        if technical_data['MACD_12_26_9'].iloc[-2] >= technical_data['MACDS_12_26_9'].iloc[-2] and latest_data['MACD_12_26_9'] < latest_data['MACDS_12_26_9']:
             tech_sell_signal = True

    sentiment_compound_score = sentiment_scores.get('compound', 0)
    sentiment_positive = sentiment_compound_score > 0.1
    sentiment_negative = sentiment_compound_score < -0.1

    if tech_buy_signal and sentiment_positive:
        return 'BUY'
    elif tech_sell_signal and sentiment_negative:
        return 'SELL'
    elif tech_buy_signal and not sentiment_negative:
        return 'BUY'
    elif tech_sell_signal and not sentiment_positive:
         return 'SELL'
    else:
        return 'HOLD'

def make_trading_decision(technical_data: pd.DataFrame, sentiment_scores: dict, ml_prediction: str = None) -> str:
    """
    Combines rule-based trading signals and ML model predictions to make a final trading decision.
    """
    logger.info("Making trading decision...")
    rule_based_signal = generate_trading_signal(technical_data, sentiment_scores)
    logger.info(f"Rule-based signal: {rule_based_signal}")

    final_signal = 'UNDETERMINED'

    if ml_prediction is None:
        logger.warning("ML prediction not available. Relying solely on rule-based signal.")
        final_signal = rule_based_signal
    else:
        logger.info(f"ML prediction available: {ml_prediction}")
        if rule_based_signal == 'BUY' and ml_prediction == 'Up':
            final_signal = 'BUY'
        elif rule_based_signal == 'SELL' and ml_prediction == 'Down':
            final_signal = 'SELL'
        elif rule_based_signal == 'HOLD' and ml_prediction == 'Up':
            final_signal = 'BUY'
        elif rule_based_signal == 'HOLD' and ml_prediction == 'Down':
            final_signal = 'SELL'
        elif rule_based_signal == 'UNDETERMINED' and ml_prediction == 'Up':
             final_signal = 'BUY'
        elif rule_based_signal == 'UNDETERMINED' and ml_prediction == 'Down':
             final_signal = 'SELL'
        else:
            final_signal = 'HOLD'
            logger.info("ML prediction contradicts rule-based signal or rules are not met. Defaulting to HOLD.")

    logger.info(f"Final combined trading signal: {final_signal}")
    return final_signal
