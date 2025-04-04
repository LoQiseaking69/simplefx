import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_rsi(prices, period):
    if len(prices) < period + 1:
        return 50
    deltas = np.diff(prices)
    gains = np.maximum(deltas, 0)
    losses = np.abs(np.minimum(deltas, 0))
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:]) or 1e-10
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def calculate_ema(prices, period):
    if len(prices) < period:
        return round(np.mean(prices), 5)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    return round(np.convolve(prices[-period:], weights, mode='valid')[0], 5)
