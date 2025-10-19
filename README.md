# AI Trading Assistant

This is a comprehensive AI trading assistant that combines deep stock analysis with autonomous trading execution.

## Features

- **Stock Analysis:** Analyzes stock price history, market trends, and sentiment from news headlines.
- **Intelligent Trading Recommendations:** Generates BUY, SELL, or HOLD signals based on combined technical and sentiment analysis.
- **Risk Management:** Provides detailed risk management plans for each trade, including suggested position size, stop-loss levels, and target profit prices.
- **Advanced Trading Infrastructure:** Supports multi-broker trading capability (starting with Alpaca), real-time trade execution, and comprehensive technical analysis.
- **Comprehensive Dashboard:** Provides an interactive web-based trading interface using Streamlit.

## Setup

1.  **Clone the repository:**
    ```
    git clone https://github.com/your-username/ai-trading-assistant.git
    ```
2.  **Install the dependencies:**
    ```
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file** in the root of the project and add your API keys:
    ```
    FINNHUB_API_KEY=YOUR_FINNHUB_API_KEY
    APCA_API_KEY_ID=YOUR_ALPACA_API_KEY_ID
    APCA_API_SECRET_KEY=YOUR_ALPACA_API_SECRET_KEY
    ```

## Usage

Run the Streamlit application with the following command:
```
streamlit run app.py
```

## Deployment

When deploying to Streamlit Cloud, you will need to set the following secrets:

```
FINNHUB_API_KEY="YOUR_FINNHUB_API_KEY"
APCA_API_KEY_ID="YOUR_ALPACA_API_KEY_ID"
APCA_API_SECRET_KEY="YOUR_ALPACA_API_SECRET_KEY"
```
