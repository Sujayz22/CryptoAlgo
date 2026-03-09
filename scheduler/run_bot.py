"""
scheduler/run_bot.py
Main scheduling loop — runs the trading pipeline once per day at 00:05 UTC.
"""

import logging
import schedule
import time

from config.settings import SCHEDULE_TIME_UTC, SYMBOLS
from main import run_trading_cycle

logger = logging.getLogger(__name__)


def start() -> None:
    """
    Start the scheduler.
    Registers the trading cycle to run once daily at SCHEDULE_TIME_UTC.
    Blocks indefinitely.
    """
    logger.info(f"Scheduler started. Will execute daily at {SCHEDULE_TIME_UTC} UTC.")

    schedule.every().day.at(SCHEDULE_TIME_UTC).do(_execute_cycle)

    while True:
        schedule.run_pending()
        time.sleep(30)


def _execute_cycle() -> None:
    """Wrapper so schedule can call run_trading_cycle with proper error handling."""
    logger.info("=== Scheduled execution triggered ===")
    for symbol in SYMBOLS:
        try:
            run_trading_cycle(symbol)
        except Exception as exc:
            logger.exception(f"Unhandled error in trading cycle for {symbol}: {exc}")


if __name__ == "__main__":
    from utils.logging_setup import setup_logging
    setup_logging()
    start()
