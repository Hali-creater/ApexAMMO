# app.py

import streamlit as st
import pandas as pd
from trading_assistant.data_handler import fetch_historical_data, fetch_realtime_data, fetch_news_headlines
from trading_assistant.analysis import calculate_technical_indicators, determine_market_personality, analyze_sentiment
from trading_assistant.trading_logic import make_trading_decision, initialize_alpaca_api, check_alpaca_connection, place_order
from trading_assistant.risk_management import calculate_position_size, calculate_stop_loss, calculate_target_profit
from trading_assistant.ml_model import prepare_data_for_ml, train_ml_model, get_ml_prediction, load_ml_model
from trading_assistant.utils import get_logger
from trading_assistant.config import FINNHUB_API_KEY
from alpaca.trading.enums import OrderSide
import finnhub
import plotly.graph_objects as go

logger = get_logger(__name__)

def main():
    st.title("AI Trading Assistant")

    st.sidebar.header("User Input")
    ticker = st.sidebar.text_input("Enter a stock ticker:", "AAPL").upper()
    start_date = st.sidebar.date_input("Start date", pd.to_datetime("2022-01-01"))
    end_date = st.sidebar.date_input("End date", pd.to_datetime("today"))
    total_capital = st.sidebar.number_input("Total Capital", 10000)
    risk_percentage = st.sidebar.slider("Risk Percentage", 0.01, 0.1, 0.01)

    if st.sidebar.button("Analyze"):
        with st.spinner("Fetching data..."):
            historical_data = fetch_historical_data(ticker, start_date, end_date)
            if historical_data is None:
                st.error("Failed to fetch historical data.")
                return

        with st.spinner("Calculating technical indicators..."):
            df_with_indicators = calculate_technical_indicators(historical_data.copy())
            if df_with_indicators.empty:
                st.error("Failed to calculate technical indicators.")
                return

        with st.spinner("Determining market personality..."):
            market_personality = determine_market_personality(df_with_indicators.copy())

        with st.spinner("Fetching news..."):
            finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
            news = fetch_news_headlines(finnhub_client, ticker)
            if news is None:
                st.warning("Could not fetch news headlines.")
                sentiment_scores = {'compound': 0}
            else:
                headlines = [article['headline'] for article in news[:10]]
                sentiments = [analyze_sentiment(headline) for headline in headlines]
                sentiment_scores = {'compound': sum(s['compound'] for s in sentiments) / len(sentiments)}

        with st.spinner("Loading ML model..."):
            model = load_ml_model()
            features = ['RSI_14', 'MACD_12_26_9', 'MACDH_12_26_9', 'MACDS_12_26_9', 'SMA_20', 'SMA_50']
            if model is None:
                st.warning("No pre-trained model found. Training a new model...")
                df_for_ml = prepare_data_for_ml(df_with_indicators.copy())
                model, features = train_ml_model(df_for_ml)

        with st.spinner("Making trading decision..."):
            ml_prediction = None
            if model is not None:
                ml_prediction = get_ml_prediction(model, df_with_indicators.tail(1), features)

            trading_decision = make_trading_decision(df_with_indicators, sentiment_scores, ml_prediction)

        st.header(f"Analysis for {ticker}")
        st.subheader("Market Personality")
        st.write(market_personality)

        st.subheader("Trading Signal")
        st.write(trading_decision)

        st.subheader("Risk Management")
        entry_price = df_with_indicators['Close'].iloc[-1]
        stop_loss = calculate_stop_loss(entry_price, risk_percentage, is_long=(trading_decision == 'BUY'))
        target_profit = calculate_target_profit(entry_price, risk_percentage * 2, is_long=(trading_decision == 'BUY'))
        position_size = calculate_position_size(total_capital, risk_percentage, stop_loss, entry_price)

        st.write(f"Entry Price: {entry_price:.2f}")
        st.write(f"Stop-Loss: {stop_loss:.2f}")
        st.write(f"Target Profit: {target_profit:.2f}")
        st.write(f"Position Size: {position_size:.2f} shares")

        st.subheader("Price Chart")
        fig = go.Figure(data=[go.Candlestick(x=df_with_indicators.index,
                                               open=df_with_indicators['Open'],
                                               high=df_with_indicators['High'],
                                               low=df_with_indicators['Low'],
                                               close=df_with_indicators['Close'])])
        st.plotly_chart(fig)

        st.subheader("Data")
        st.dataframe(df_with_indicators.tail())

        if trading_decision in ["BUY", "SELL"]:
            if st.button(f"Place {trading_decision} Order"):
                trading_client = initialize_alpaca_api(st.secrets["ALPACA_API_KEY_ID"], st.secrets["ALPACA_API_SECRET_KEY"])
                if check_alpaca_connection(trading_client):
                    side = OrderSide.BUY if trading_decision == "BUY" else OrderSide.SELL
                    place_order(trading_client, ticker, position_size, side)
                    st.success(f"{trading_decision} order placed for {position_size:.2f} shares of {ticker}.")
                else:
                    st.error("Failed to connect to Alpaca.")

    if st.sidebar.button("Retrain Model"):
        with st.spinner("Fetching data..."):
            historical_data = fetch_historical_data(ticker, start_date, end_date)
            if historical_data is None:
                st.error("Failed to fetch historical data.")
                return
        with st.spinner("Training new model..."):
            df_with_indicators = calculate_technical_indicators(historical_data.copy())
            df_for_ml = prepare_data_for_ml(df_with_indicators.copy())
            train_ml_model(df_for_ml)
            st.success("ML model retrained and saved.")

if __name__ == "__main__":
    main()
