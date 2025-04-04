import time
import asyncio
import logging
import numpy as np
from .api_handler import fetch_price, place_order
from .indicators import calculate_rsi, calculate_ema
from .signal_emitter import notifier
from .config_manager import load_config

logger = logging.getLogger(__name__)
config = load_config()

async def trade(pair, prices, account_id, token):
    price = await fetch_price(account_id, token, pair)
    if price is None:
        logger.error(f"Price fetch failed for {pair}")
        return

    prices.append(price)
    if len(prices) > 100:
        prices.pop(0)

    rsi = calculate_rsi(np.array(prices), config["RSI_PERIOD"])
    ema = calculate_ema(np.array(prices), config["EMA_PERIOD"])
    msg = f"{pair} | Price: {price:.5f} | RSI: {rsi:.2f} | EMA: {ema:.5f}"
    logger.info(msg)
    notifier.emit_signal(msg)

    units = config["TRADE_AMOUNT_UNITS"]
    stop_loss = take_profit = None

    if rsi < config["RSI_BUY_THRESHOLD"] and price < ema:
        stop_loss = round(price * (1 - config["STOP_LOSS_PERCENTAGE"]), 5)
        take_profit = round(price * (1 + config["TAKE_PROFIT_PERCENTAGE"]), 5)
        order_id = place_order(account_id, token, pair, units, stop_loss, take_profit)
        if order_id:
            notifier.emit_signal(f"Buy order placed: {order_id}")
    elif rsi > config["RSI_SELL_THRESHOLD"] and price > ema:
        stop_loss = round(price * (1 + config["STOP_LOSS_PERCENTAGE"]), 5)
        take_profit = round(price * (1 - config["TAKE_PROFIT_PERCENTAGE"]), 5)
        order_id = place_order(account_id, token, pair, -units, stop_loss, take_profit)
        if order_id:
            notifier.emit_signal(f"Sell order placed: {order_id}")

async def run_bot(account_id, token):
    config = load_config()
    end_time = time.time() + config["SESSION_DURATION"]
    price_history = {pair: [] for pair in config["PAIRS"]}

    logger.info("Trading session started.")
    notifier.emit_signal("Trading session started.")

    while time.time() < end_time:
        for pair in config["PAIRS"]:
            try:
                await trade(pair, price_history[pair], account_id, token)
            except Exception as e:
                err = f"{pair} trade error: {e}"
                logger.error(err)
                notifier.emit_signal(err)
        await asyncio.sleep(config["TRADE_INTERVAL"])

    logger.info("Session ended.")
    notifier.emit_signal("Session ended.")
