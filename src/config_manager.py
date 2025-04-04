import json
import os
import logging

logger = logging.getLogger(__name__)
CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "PAIRS": ["EUR_USD"],
    "TRADE_AMOUNT_UNITS": 1000,
    "TRADE_INTERVAL": 30,
    "SESSION_DURATION": 3600,
    "RSI_PERIOD": 14,
    "EMA_PERIOD": 20,
    "RSI_BUY_THRESHOLD": 30,
    "RSI_SELL_THRESHOLD": 70,
    "STOP_LOSS_PERCENTAGE": 0.02,
    "TAKE_PROFIT_PERCENTAGE": 0.03
}

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return {**DEFAULT_CONFIG, **config}
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return DEFAULT_CONFIG.copy()
