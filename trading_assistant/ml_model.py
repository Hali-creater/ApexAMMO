# trading_assistant/ml_model.py

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import numpy as np
from .utils import get_logger

logger = get_logger(__name__)

def prepare_data_for_ml(df_with_indicators):
    """
    Prepares the data for ML model training.
    """
    if 'df_with_indicators' not in locals() or df_with_indicators.empty:
        logger.warning("Using dummy data as 'df_with_indicators' was not found or is empty.")
        data = {
            'Open': np.random.rand(100) * 100 + 50,
            'High': np.random.rand(100) * 100 + 55,
            'Low': np.random.rand(100) * 100 + 45,
            'Close': np.random.rand(100) * 100 + 50,
            'Volume': np.random.rand(100) * 1000000,
            'RSI_14': np.random.rand(100) * 50 + 25,
            'MACD_12_26_9': np.random.rand(100) * 5 - 2.5,
            'MACDH_12_26_9': np.random.rand(100) * 2 - 1,
            'MACDS_12_26_9': np.random.rand(100) * 4 - 2,
        }
        index = pd.date_range(start='2023-01-01', periods=100, freq='D')
        df_with_indicators = pd.DataFrame(data, index=index)
        df_with_indicators['SMA_20'] = df_with_indicators['Close'].rolling(window=20).mean().fillna(0)
        df_with_indicators['SMA_50'] = df_with_indicators['Close'].rolling(window=50).mean().fillna(0)

    df_with_indicators['Target'] = (df_with_indicators['Close'].shift(-1) > df_with_indicators['Close']).astype(int)
    df_with_indicators.dropna(subset=['Target'], inplace=True)
    return df_with_indicators

def train_ml_model(df_model):
    """
    Trains the machine learning model.
    """
    if df_model.empty:
        logger.error("DataFrame is empty. Cannot train ML model.")
        return None, None

    features = ['RSI_14', 'MACD_12_26_9', 'MACDH_12_26_9', 'MACDS_12_26_9', 'SMA_20', 'SMA_50']
    df_model.dropna(subset=features + ['Target'], inplace=True)

    if df_model.empty:
        logger.error("DataFrame is empty after dropping rows with missing values. Cannot train ML model.")
        return None, None

    X = df_model[features]
    y = df_model['Target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    classification_rep = classification_report(y_test, y_pred)

    logger.info(f"Model Accuracy: {accuracy}")
    logger.info(f"Classification Report:\\n{classification_rep}")

    return model, features

def get_ml_prediction(model, data, features):
    """
    Gets a prediction from the ML model.
    """
    if model is None:
        return None

    data.dropna(subset=features, inplace=True)

    if data.empty:
        return None

    prediction = model.predict(data[features])
    return "Up" if prediction[0] == 1 else "Down"
