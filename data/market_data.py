"""
data/market_data.py
Fetches OHLCV candlestick data from the Delta Exchange REST API.
"""

import logging
import time
import requests
import pandas as pd

from config.settings import (
    DELTA_BASE_URL,
    CANDLE_LIMIT,
    RESOLUTION,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
)

logger = logging.getLogger(__name__)


# Delta Exchange resolution strings for the /v2/history/candles endpoint
RESOLUTION_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1D": "1d",
}


def get_candles(symbol: str, resolution: str = RESOLUTION, limit: int = CANDLE_LIMIT) -> pd.DataFrame:
    """
    Fetch historical OHLCV candles from Delta Exchange.

    Args:
        symbol:     Product symbol, e.g. 'BTCUSD'
        resolution: Candle timeframe, e.g. '1D'
        limit:      Number of candles to retrieve (max 500)

    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume
        Sorted ascending by timestamp.

    Raises:
        RuntimeError: if the API call fails after MAX_RETRIES attempts.
    """
    res = RESOLUTION_MAP.get(resolution, "1d")
    url = f"{DELTA_BASE_URL}/v2/history/candles"

    params = {
        "resolution": res,
        "symbol": symbol,
        "limit": limit,
    }

    logger.info(f"Fetching {limit} {resolution} candles for {symbol} …")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            payload = response.json()
            break
        except requests.exceptions.RequestException as exc:
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                raise RuntimeError(
                    f"Failed to fetch candles for {symbol} after {MAX_RETRIES} attempts"
                ) from exc

    candles = payload.get("result", [])
    if not candles:
        logger.warning(f"Empty candle response for {symbol}")
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    df = pd.DataFrame(candles)

    # Delta returns: time, open, high, low, close, volume
    df = df.rename(columns={"time": "timestamp"})

    df = _normalize(df)

    logger.info(f"Fetched {len(df)} candles for {symbol} (latest: {df['timestamp'].iloc[-1]})")
    return df


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw DataFrame:
    - Convert price/volume columns to float
    - Convert timestamp to datetime
    - Sort ascending by timestamp
    - Drop rows with any NaN in OHLCV columns
    """
    price_cols = ["open", "high", "low", "close", "volume"]

    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "timestamp" in df.columns:
        # Delta Exchange returns UNIX timestamps in seconds
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)

    df = df.sort_values("timestamp").reset_index(drop=True)
    df = df.dropna(subset=price_cols)

    return df[["timestamp", "open", "high", "low", "close", "volume"]]
