"""
strategy/strategy_engine.py
Evaluates indicators and generates trade signals.
This module is PURE — no API calls, no side effects.
"""

import logging
from dataclasses import dataclass
from typing import Literal

import pandas as pd

from config.settings import SL_MULTIPLIER, TP_MULTIPLIER

logger = logging.getLogger(__name__)

Signal = Literal["BUY", "SELL", "HOLD"]


@dataclass
class TradeSetup:
    """Complete trade setup including entry levels."""
    signal: Signal
    entry_price: float
    stop_loss: float
    take_profit: float
    atr: float
    reason: str


def _histogram_crossed_above_zero(df: pd.DataFrame) -> bool:
    """
    True if the MACD histogram crossed from negative/zero to positive
    between the second-to-last and last completed candle.

    Uses the last two rows of the DataFrame (index -2 and -1).
    """
    if len(df) < 2:
        return False
    prev = df["histogram"].iloc[-2]
    curr = df["histogram"].iloc[-1]
    return (prev <= 0) and (curr > 0)


def _histogram_crossed_below_zero(df: pd.DataFrame) -> bool:
    """True if histogram crossed from positive/zero to negative."""
    if len(df) < 2:
        return False
    prev = df["histogram"].iloc[-2]
    curr = df["histogram"].iloc[-1]
    return (prev >= 0) and (curr < 0)


def generate_signal(df: pd.DataFrame) -> Signal:
    """
    Evaluate the latest candle against strategy rules and return a signal.

    Long (BUY) conditions — ALL must be true:
        close > EMA200
        SAR < low
        MACD histogram crosses above 0

    Short (SELL) conditions — ALL must be true:
        close < EMA200
        SAR > high
        MACD histogram crosses below 0

    Returns: 'BUY' | 'SELL' | 'HOLD'
    """
    required = ["close", "high", "low", "ema200", "sar", "histogram", "atr"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}. Run compute_all() first.")

    # Drop rows where key indicators are NaN
    df_clean = df.dropna(subset=required)
    if len(df_clean) < 2:
        logger.warning("Not enough data to evaluate signal.")
        return "HOLD"

    last = df_clean.iloc[-1]

    close = last["close"]
    ema200 = last["ema200"]
    sar = last["sar"]
    low = last["low"]
    high = last["high"]

    hist_up = _histogram_crossed_above_zero(df_clean)
    hist_down = _histogram_crossed_below_zero(df_clean)

    logger.info(
        f"Signal eval — close={close:.2f} EMA200={ema200:.2f} "
        f"SAR={sar:.2f} hist_cross_up={hist_up} hist_cross_down={hist_down}"
    )

    if close > ema200 and sar < low and hist_up:
        logger.info("Signal: BUY (Long)")
        return "BUY"

    if close < ema200 and sar > high and hist_down:
        logger.info("Signal: SELL (Short)")
        return "SELL"

    logger.info("Signal: HOLD")
    return "HOLD"


def compute_trade_levels(entry_price: float, atr: float, signal: Signal) -> tuple[float, float]:
    """
    Calculate stop-loss and take-profit levels based on ATR.

    Long:
        SL = entry - ATR * SL_MULTIPLIER
        TP = entry + ATR * TP_MULTIPLIER

    Short:
        SL = entry + ATR * SL_MULTIPLIER
        TP = entry - ATR * TP_MULTIPLIER

    Returns: (stop_loss, take_profit)
    """
    if signal == "BUY":
        sl = entry_price - atr * SL_MULTIPLIER
        tp = entry_price + atr * TP_MULTIPLIER
    elif signal == "SELL":
        sl = entry_price + atr * SL_MULTIPLIER
        tp = entry_price - atr * TP_MULTIPLIER
    else:
        raise ValueError(f"compute_trade_levels called with signal={signal}")

    logger.info(
        f"Trade levels — entry={entry_price:.2f} SL={sl:.2f} TP={tp:.2f} ATR={atr:.2f}"
    )
    return sl, tp


def build_trade_setup(df: pd.DataFrame) -> TradeSetup | None:
    """
    Full pipeline: generate signal, compute levels.
    Returns TradeSetup or None if HOLD.
    """
    signal = generate_signal(df)
    if signal == "HOLD":
        return None

    df_clean = df.dropna(subset=["close", "atr"])
    last = df_clean.iloc[-1]
    entry = last["close"]
    atr = last["atr"]

    sl, tp = compute_trade_levels(entry, atr, signal)

    reason = (
        f"close {'>' if signal == 'BUY' else '<'} EMA200, "
        f"SAR {'<' if signal == 'BUY' else '>'} {'low' if signal == 'BUY' else 'high'}, "
        f"MACD hist crossed {'above' if signal == 'BUY' else 'below'} 0"
    )

    return TradeSetup(
        signal=signal,
        entry_price=entry,
        stop_loss=sl,
        take_profit=tp,
        atr=atr,
        reason=reason,
    )
