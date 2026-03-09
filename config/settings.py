"""
config/settings.py
Central configuration for the Delta Exchange Trading Bot.
Loads environment variables and exposes strategy parameters.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── API Connectivity ──────────────────────────────────────────────────────────

DELTA_API_KEY: str = os.getenv("API_KEY", "")
DELTA_API_SECRET: str = os.getenv("API_SECRET", "")

# Testnet endpoint (switch to live when ready)
DELTA_BASE_URL: str = os.getenv(
    "DELTA_BASE_URL", "https://cdn-ind.testnet.deltaex.org"
)

# ── Trading Mode ──────────────────────────────────────────────────────────────

# Set PAPER_MODE=True to run without placing real orders
PAPER_MODE: bool = os.getenv("PAPER_MODE", "True").lower() in ("true", "1", "yes")

# ── Trading Universe ──────────────────────────────────────────────────────────

SYMBOLS: list[str] = ["BTCUSD", "ETHUSD"]  # Delta Exchange perpetual symbols

# ── Timeframe ─────────────────────────────────────────────────────────────────

RESOLUTION: str = "1D"         # Daily candles
CANDLE_LIMIT: int = 500        # Number of candles to fetch

# ── Indicator Parameters ──────────────────────────────────────────────────────

EMA_PERIOD: int = 200

MACD_FAST: int = 12
MACD_SLOW: int = 26
MACD_SIGNAL: int = 9

ATR_PERIOD: int = 14

SAR_STEP: float = 0.02
SAR_MAX_STEP: float = 0.2

# ── Risk Management ───────────────────────────────────────────────────────────

SL_MULTIPLIER: float = 1.5     # ATR multiples for stop-loss
TP_MULTIPLIER: float = 2.5     # ATR multiples for take-profit
MAX_RISK_PCT: float = 0.01     # Max 1% account risk per trade

# ── Order Settings ────────────────────────────────────────────────────────────

ORDER_TYPE: str = "limit_order"
ORDER_SIZE: float = 1.0        # Contract size (adjust based on account)

# ── Scheduler ─────────────────────────────────────────────────────────────────

SCHEDULE_TIME_UTC: str = "00:05"  # Run daily at 00:05 UTC

# ── Logging ───────────────────────────────────────────────────────────────────

LOG_FILE: str = "logs/trading.log"
LOG_LEVEL: str = "INFO"

# ── Retry Settings ────────────────────────────────────────────────────────────

MAX_RETRIES: int = 3
RETRY_DELAY_SECONDS: int = 5
