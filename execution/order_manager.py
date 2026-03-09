"""
execution/order_manager.py
Orchestrates order execution: prevents duplicates, enforces single open position,
attaches SL/TP orders, supports paper trading mode.
"""

import logging
from typing import Any

from config.settings import ORDER_SIZE, ORDER_TYPE, PAPER_MODE
from execution.delta_client import DeltaClient
from strategy.strategy_engine import TradeSetup

logger = logging.getLogger(__name__)


class OrderManager:
    """
    Manages the full lifecycle of a trade:
    1. Check for existing open position
    2. Execute entry order with bracket SL/TP
    3. Prevent duplicate trades
    4. Paper trading support (no real orders sent)
    """

    def __init__(self) -> None:
        self.client = DeltaClient()
        self._product_cache: dict[str, int] = {}

    def _get_product_id(self, symbol: str) -> int | None:
        if symbol not in self._product_cache:
            pid = self.client.get_product_id(symbol)
            if pid is not None:
                self._product_cache[symbol] = pid
        return self._product_cache.get(symbol)

    def has_open_position(self, symbol: str) -> bool:
        """Check whether a live position already exists for the symbol."""
        if PAPER_MODE:
            return False  # Paper mode never blocks entry
        product_id = self._get_product_id(symbol)
        if product_id is None:
            logger.error(f"Cannot resolve product_id for {symbol}")
            return False
        pos = self.client.get_position(product_id)
        return pos is not None

    def execute(self, symbol: str, setup: TradeSetup) -> dict[str, Any] | None:
        """
        Execute a trade based on a TradeSetup.

        Steps:
        - Skip if PAPER_MODE is enabled (log only)
        - Skip if position already open (prevent duplicates)
        - Place order with bracket SL/TP
        - Return API response or simulation dict

        Returns: Order result dict or None if skipped.
        """
        logger.info(
            f"{'[PAPER] ' if PAPER_MODE else ''}Executing {setup.signal} on {symbol} | "
            f"Entry: {setup.entry_price:.2f} | SL: {setup.stop_loss:.2f} | TP: {setup.take_profit:.2f}"
        )
        logger.info(f"Reason: {setup.reason}")

        # Paper trading: log only, no order submission
        if PAPER_MODE:
            sim = {
                "mode": "paper",
                "symbol": symbol,
                "signal": setup.signal,
                "entry_price": setup.entry_price,
                "stop_loss": setup.stop_loss,
                "take_profit": setup.take_profit,
                "size": ORDER_SIZE,
                "status": "simulated",
            }
            logger.info(f"[PAPER] Simulated order: {sim}")
            return sim

        # Live mode: guard against duplicate positions
        if self.has_open_position(symbol):
            logger.warning(
                f"Skipping {setup.signal} on {symbol} — open position already exists."
            )
            return None

        product_id = self._get_product_id(symbol)
        if product_id is None:
            logger.error(f"Cannot place order: product_id not found for {symbol}")
            return None

        side = "buy" if setup.signal == "BUY" else "sell"

        result = self.client.place_order(
            product_id=product_id,
            side=side,
            order_type=ORDER_TYPE,
            size=ORDER_SIZE,
            limit_price=setup.entry_price,
            stop_loss=setup.stop_loss,
            take_profit=setup.take_profit,
        )

        logger.info(f"Order placed for {symbol}: {result}")
        return result
