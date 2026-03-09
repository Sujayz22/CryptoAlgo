"""
indicators/indicators.py
All technical indicator calculations for the trading strategy.
Uses the `ta` library for TradingView-compatible outputs.
"""

import logging
import pandas as pd
import ta

from config.settings import (
    EMA_PERIOD,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    ATR_PERIOD,
    SAR_STEP,
    SAR_MAX_STEP,
)

logger = logging.getLogger(__name__)


def compute_ema200(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add EMA-200 column to the DataFrame.

    TradingView EMA uses RMA (recursive moving average with Wilder smoothing)
    for some indicators, but plain EMA for `ta.trend.ema_indicator`.
    We use `ta` which matches TradingView's EMA calculation.

    Adds column: ema200
    """
    df = df.copy()
    df["ema200"] = ta.trend.ema_indicator(close=df["close"], window=EMA_PERIOD, fillna=False)
    logger.debug(f"EMA{EMA_PERIOD} computed. Latest value: {df['ema200'].iloc[-1]:.2f}")
    return df


def compute_macd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add MACD, Signal, and Histogram columns.

    Formula:
        MACD      = EMA(12) - EMA(26)
        Signal    = EMA(MACD, 9)
        Histogram = MACD - Signal

    Adds columns: macd, signal, histogram

    TradingView MACD uses EMA of close for fast/slow, then EMA of macd for signal.
    The `ta` library replicates this exactly.
    """
    df = df.copy()
    macd_obj = ta.trend.MACD(
        close=df["close"],
        window_fast=MACD_FAST,
        window_slow=MACD_SLOW,
        window_sign=MACD_SIGNAL,
        fillna=False,
    )
    df["macd"] = macd_obj.macd()
    df["signal"] = macd_obj.macd_signal()
    df["histogram"] = macd_obj.macd_diff()

    logger.debug(
        f"MACD computed. Latest histogram: {df['histogram'].iloc[-1]:.6f}"
    )
    return df


def compute_sar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Parabolic SAR column.

    Parameters match TradingView defaults:
        Start (step)  = 0.02
        Maximum       = 0.2

    Adds column: sar

    Note: `ta` library's SAR implementation matches TradingView values.
    """
    df = df.copy()

    try:
        ps = ta.trend.PSARIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            step=SAR_STEP,
            max_step=SAR_MAX_STEP,
            fillna=False,
        )
        df["sar"] = ps.psar()
    except Exception as exc:
        logger.error(f"SAR computation failed: {exc}")
        df["sar"] = float("nan")

    logger.debug(f"SAR computed. Latest value: {df['sar'].iloc[-1]:.2f}")
    return df


def compute_atr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ATR (Average True Range) column.

    ATR Period = 14 (matches TradingView default).
    Uses Wilder's smoothing (same as TradingView) via `ta.volatility.AverageTrueRange`.

    Adds column: atr
    """
    df = df.copy()
    atr_obj = ta.volatility.AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=ATR_PERIOD,
        fillna=False,
    )
    df["atr"] = atr_obj.average_true_range()
    logger.debug(f"ATR computed. Latest value: {df['atr'].iloc[-1]:.2f}")
    return df


def compute_all(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function: compute all indicators in sequence.
    Returns DataFrame with added columns: ema200, macd, signal, histogram, sar, atr.
    """
    df = compute_ema200(df)
    df = compute_macd(df)
    df = compute_sar(df)
    df = compute_atr(df)
    logger.info("All indicators computed successfully.")
    return df
