import os
import argparse
import asyncio
import logging
from src.trader import run_bot
from src.config_manager import load_config
from src.signal_emitter import notifier

logging.basicConfig(filename="trade_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="OANDA Trading Bot CLI")
    parser.add_argument("--start", action="store_true", help="Start trading session")
    parser.add_argument("--status", action="store_true", help="Print current config")
    parser.add_argument("--reload", action="store_true", help="Reload config")

    args = parser.parse_args()
    config = load_config()

    if args.start:
        account_id = os.getenv("OANDA_ACCOUNT_ID", config.get("OANDA_ACCOUNT_ID"))
        token = os.getenv("OANDA_API_TOKEN", config.get("OANDA_API_TOKEN"))
        if not account_id or not token:
            logger.error("Missing OANDA credentials.")
            return
        asyncio.run(run_bot(account_id, token))

    elif args.status:
        print("Current config:")
        for k, v in config.items():
            print(f"{k}: {v}")

    elif args.reload:
        load_config()
        logger.info("Config reloaded via CLI.")
        print("Config reloaded.")

if __name__ == "__main__":
    main()
