# trading_assistant/utils.py

import logging
import sys
import os

def get_logger(name):
    """
    Configures and returns a logger.
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/trading_assistant.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(name)
