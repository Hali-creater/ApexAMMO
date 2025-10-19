# trading_assistant/ml_model.py

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import numpy as np
from trading_assistant.utils import get_logger
import joblib
import os

logger = get_logger(__name__)
MODEL_FILE = "trading_model.joblib"

def prepare_data_for_ml(df_with_indicators):
    """
    Prepares the data for ML model training.
    """
    if df_with_indicators.empty:
        logger.error("Input DataFrame is empty. Cannot prepare data for ML.")
        return pd.DataFrame()

    df_with_indicators['Target'] = (df_with_indicators['Close'].shift(-1) > df_with_indicators['Close']).astype(int)
    df_with_indicators.dropna(subset=['Target'], inplace=True)
    return df_with_indicators

def train_ml_model(df_model):
    """
    Trains the machine learning model and saves it to a file.
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

    # Save the trained model
    joblib.dump(model, MODEL_FILE)
    logger.info(f"Model saved to {MODEL_FILE}")

    return model, features

def load_ml_model():
    """
    Loads a pre-trained machine learning model from a file.
    """
    if os.path.exists(MODEL_FILE):
        logger.info(f"Loading model from {MODEL_FILE}")
        return joblib.load(MODEL_FILE)
    else:
        logger.warning("No pre-trained model found.")
        return None

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
