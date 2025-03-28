import os
import json
import time
import asyncio
import urllib.request
import urllib.error
import logging
import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
import traceback

# --- Configuration loading ---
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            print("Config loaded.")
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

config = load_config()
OANDA_API_TOKEN = os.getenv("OANDA_API_TOKEN", config.get("OANDA_API_TOKEN", "YOUR_OANDA_API_TOKEN"))
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID", config.get("OANDA_ACCOUNT_ID", "YOUR_DEMO_ACCOUNT_ID"))
TRADE_AMOUNT_UNITS = config.get("TRADE_AMOUNT_UNITS", 1000)
TRADE_INTERVAL = config.get("TRADE_INTERVAL", 30)
SESSION_DURATION = config.get("SESSION_DURATION", 3600)
RSI_PERIOD = config.get("RSI_PERIOD", 14)
EMA_PERIOD = config.get("EMA_PERIOD", 20)
RSI_BUY_THRESHOLD = config.get("RSI_BUY_THRESHOLD", 30)
RSI_SELL_THRESHOLD = config.get("RSI_SELL_THRESHOLD", 70)
STOP_LOSS_PERCENTAGE = config.get("STOP_LOSS_PERCENTAGE", 0.02)  # 2% stop loss
TAKE_PROFIT_PERCENTAGE = config.get("TAKE_PROFIT_PERCENTAGE", 0.03)  # 3% take profit

# --- Logging Setup ---
logging.basicConfig(
    filename="trade_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# --- PyQt5 Signal Emitter ---
class SignalEmitter(QObject):
    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.last_message = ""

    def emit_signal(self, message):
        if message != self.last_message:  # Throttle repeated messages
            self.signal.emit(message)
            self.last_message = message

notifier = SignalEmitter()

# --- Oanda API Request with Retry ---
def oanda_request(url, method="GET", data=None, retries=3, backoff=2):
    req = urllib.request.Request(url, data=data)
    req.add_header("Authorization", f"Bearer {OANDA_API_TOKEN}")
    req.add_header("Content-Type", "application/json")
    req.get_method = lambda: method
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            logger.warning(f"HTTPError: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            logger.warning(f"URLError: {e.reason}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            traceback.print_exc()
        time.sleep(backoff * attempt)
    return None

# --- Fetch Price ---
async def fetch_price(pair="EUR_USD"):
    url = f"https://api-fxpractice.oanda.com/v3/accounts/{OANDA_ACCOUNT_ID}/pricing?instruments={pair}"
    result = oanda_request(url)
    logger.debug(f"API result type: {type(result)}; content: {result}")
    
    # If result is already a float, return it.
    if isinstance(result, float):
        return round(result, 5)
    
    # Check for expected structure
    if result and isinstance(result, dict) and "prices" in result and isinstance(result["prices"], list) and result["prices"]:
        try:
            bid = float(result["prices"][0]["bids"][0]["price"])
            ask = float(result["prices"][0]["asks"][0]["price"])
            return round((bid + ask) / 2, 5)  # Return the mid-price (average of bid and ask)
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error processing price for {pair}: {e}")
    else:
        logger.error(f"Unexpected API result structure for {pair}: {result}")
    return None

# --- Technical Indicator Calculations ---
def calculate_rsi(prices, period):
    if len(prices) < period + 1:
        logger.warning(f"Not enough data to calculate RSI for {len(prices)} prices.")
        return 50
    deltas = np.diff(prices)
    gains = np.maximum(deltas, 0)
    losses = np.abs(np.minimum(deltas, 0))
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def calculate_ema(prices, period):
    if len(prices) < period:
        logger.warning(f"Not enough data to calculate EMA for {len(prices)} prices.")
        return round(np.mean(prices), 5)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    return round(np.convolve(prices[-period:], weights, mode='valid')[0], 5)

# --- Place Order ---
def place_order(pair, units, stop_loss_price=None, take_profit_price=None):
    url = f"https://api-fxpractice.oanda.com/v3/accounts/{OANDA_ACCOUNT_ID}/orders"
    order_data = {
        "order": {
            "units": str(units),
            "instrument": pair,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }
    
    if stop_loss_price and take_profit_price:
        order_data["order"]["stopLossOnFill"] = {"price": stop_loss_price}
        order_data["order"]["takeProfitOnFill"] = {"price": take_profit_price}

    data = json.dumps(order_data).encode()
    result = oanda_request(url, method="POST", data=data)
    if result and "orderFillTransaction" in result:
        order_id = result["orderFillTransaction"].get("id", "")
        logger.info(f"Order placed for {pair}: {order_id}")
        notifier.emit_signal(f"Order placed for {pair}: {order_id}")
        return order_id
    logger.error(f"Order placement failed for {pair}.")
    return None

# --- Trade Logic ---
async def trade(pair, prices):
    current_price = await fetch_price(pair)
    if current_price is None:
        logger.error(f"Failed to fetch {pair} price.")
        return

    prices.append(current_price)
    if len(prices) > 100:
        prices.pop(0)

    rsi = calculate_rsi(np.array(prices), RSI_PERIOD)
    ema = calculate_ema(np.array(prices), EMA_PERIOD)
    msg = f"{pair} | Price: {current_price:.5f} | RSI: {rsi:.2f} | EMA: {ema:.5f}"
    logger.info(msg)
    notifier.emit_signal(msg)

    # Calculate stop loss and take profit (only set for buy signals in this example)
    stop_loss = round(current_price * (1 - STOP_LOSS_PERCENTAGE), 5) if rsi < RSI_BUY_THRESHOLD else None
    take_profit = round(current_price * (1 + TAKE_PROFIT_PERCENTAGE), 5) if rsi < RSI_BUY_THRESHOLD else None

    if rsi < RSI_BUY_THRESHOLD and current_price < ema:
        logger.info(f"Buy signal for {pair}")
        notifier.emit_signal(f"Buy signal for {pair}")
        place_order(pair, TRADE_AMOUNT_UNITS, stop_loss, take_profit)
    elif rsi > RSI_SELL_THRESHOLD and current_price > ema:
        logger.info(f"Sell signal for {pair}")
        notifier.emit_signal(f"Sell signal for {pair}")
        place_order(pair, -TRADE_AMOUNT_UNITS, stop_loss, take_profit)

# --- Start/Stop Functions ---
async def run_bot():
    session_end = time.time() + SESSION_DURATION
    pairs = config.get("PAIRS", ["EUR_USD"])
    price_history = {pair: [] for pair in pairs}
    logger.info("Trading session started.")
    notifier.emit_signal("Trading session started.")
    
    while time.time() < session_end:
        for pair in pairs:
            try:
                await trade(pair, price_history[pair])
            except Exception as e:
                logger.error(f"Error with {pair}: {e}")
                notifier.emit_signal(f"Error with {pair}: {e}")
        await asyncio.sleep(TRADE_INTERVAL)
    
    logger.info("Session ended.")
    notifier.emit_signal("Session ended.")

def start_bot():
    asyncio.run(run_bot())

def stop_bot():
    logger.info("Bot stopped.")
    notifier.emit_signal("Bot stopped.")

def reload_config_if_changed():
    global config
    config = load_config()
    logger.info("Config reloaded.")
    notifier.emit_signal("Config reloaded.")