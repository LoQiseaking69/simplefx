import os
import json
import time
import urllib.request
import urllib.error
import logging

logger = logging.getLogger(__name__)
API_URL = "https://api-fxpractice.oanda.com/v3"

def oanda_request(url, token, method="GET", data=None, retries=3, backoff=2):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            logger.warning(f"Attempt {attempt}: {e}")
            time.sleep(backoff * attempt)
    return None

def fetch_price(account_id, token, pair):
    url = f"{API_URL}/accounts/{account_id}/pricing?instruments={pair}"
    result = oanda_request(url, token)
    if isinstance(result, dict) and "prices" in result and result["prices"]:
        try:
            bid = float(result["prices"][0]["bids"][0]["price"])
            ask = float(result["prices"][0]["asks"][0]["price"])
            return round((bid + ask) / 2, 5)
        except Exception as e:
            logger.error(f"Price parse error: {e}")
    return None

def place_order(account_id, token, pair, units, stop_loss=None, take_profit=None):
    url = f"{API_URL}/accounts/{account_id}/orders"
    order = {
        "order": {
            "units": str(units),
            "instrument": pair,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }
    if stop_loss and take_profit:
        order["order"]["stopLossOnFill"] = {"price": str(stop_loss)}
        order["order"]["takeProfitOnFill"] = {"price": str(take_profit)}
    data = json.dumps(order).encode()
    result = oanda_request(url, token, method="POST", data=data)
    if result and "orderFillTransaction" in result:
        return result["orderFillTransaction"].get("id", "")
    return None
