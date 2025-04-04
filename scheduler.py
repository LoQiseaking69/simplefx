import asyncio
import os
import logging
from datetime import datetime
from src.trader import run_bot
from src.config_manager import load_config

logging.basicConfig(filename="scheduler_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def within_schedule(cfg):
    now = datetime.utcnow()
    if cfg.get("WEEKDAYS_ONLY") and now.weekday() >= 5:
        return False
    start = cfg.get("START_HOUR", 0)
    end = cfg.get("END_HOUR", 23)
    return start <= now.hour <= end

async def scheduler_loop():
    cfg = load_config()
    account_id = os.getenv("OANDA_ACCOUNT_ID", cfg.get("OANDA_ACCOUNT_ID"))
    token = os.getenv("OANDA_API_TOKEN", cfg.get("OANDA_API_TOKEN"))
    if not account_id or not token:
        logger.error("Missing OANDA credentials.")
        return

    logger.info("Scheduler started.")
    while True:
        if within_schedule(cfg):
            logger.info("Starting scheduled session.")
            await run_bot(account_id, token)
            logger.info("Scheduled session completed.")
        await asyncio.sleep(300)  # Check every 5 minutes

def main():
    asyncio.run(scheduler_loop())

if __name__ == "__main__":
    main()
