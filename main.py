"""
main.py
Main entry point for the Delta Exchange Automated Trading Bot.

Usage:
    # Run one trading cycle immediately (for testing):
    python main.py

    # Run the scheduled daily bot:
    python scheduler/run_bot.py
"""

import logging

from utils.logging_setup import setup_logging
from config.settings import SYMBOLS, PAPER_MODE
from data.market_data import get_candles
from indicators.indicators import compute_all
from strategy.strategy_engine import build_trade_setup
from execution.order_manager import OrderManager

setup_logging()
logger = logging.getLogger(__name__)


def run_trading_cycle(symbol: str) -> None:
    """
    Full trading pipeline for a single symbol.

    Steps:
        1. Fetch daily OHLCV candles
        2. Compute all indicators (EMA200, MACD, SAR, ATR)
        3. Evaluate strategy signals
        4. Execute order (or simulate in paper mode)

    Args:
        symbol: Trading pair symbol, e.g. 'BTCUSD'
    """
    logger.info(f"{'─' * 60}")
    logger.info(f"Trading cycle START — {symbol}")
    logger.info(f"Mode: {'PAPER (simulation)' if PAPER_MODE else 'LIVE'}")

    # Step 1 — Fetch market data
    try:
        df = get_candles(symbol)
    except RuntimeError as exc:
        logger.error(f"Market data fetch failed for {symbol}: {exc}")
        return

    if df.empty:
        logger.warning(f"No candle data returned for {symbol}. Skipping.")
        return

    # Step 2 — Compute indicators
    try:
        df = compute_all(df)
    except Exception as exc:
        logger.error(f"Indicator computation failed for {symbol}: {exc}")
        return

    # Step 3 — Evaluate strategy signal
    try:
        setup = build_trade_setup(df)
    except Exception as exc:
        logger.error(f"Strategy evaluation failed for {symbol}: {exc}")
        return

    if setup is None:
        logger.info(f"Signal: HOLD for {symbol} — no trade taken.")
        return

    logger.info(f"Signal: {setup.signal} | Entry: {setup.entry_price:.2f} | SL: {setup.stop_loss:.2f} | TP: {setup.take_profit:.2f}")

    # Step 4 — Execute order
    try:
        manager = OrderManager()
        result = manager.execute(symbol, setup)
        if result:
            logger.info(f"Order result for {symbol}: {result}")
        else:
            logger.info(f"Order skipped for {symbol} (position already open or error).")
    except Exception as exc:
        logger.exception(f"Order execution failed for {symbol}: {exc}")

    logger.info(f"Trading cycle DONE — {symbol}")
    logger.info(f"{'─' * 60}")


if __name__ == "__main__":
    logger.info("=== Delta Exchange Trading Bot Starting ===")
    for symbol in SYMBOLS:
        run_trading_cycle(symbol)
    logger.info("=== Cycle complete ===")
