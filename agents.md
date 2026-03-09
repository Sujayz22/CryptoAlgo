# AI Agent Context – Delta Exchange Automated Strategy

## Project Overview

This project implements an **automated trading system for Delta Exchange Testnet** based on a TradingView strategy.

The strategy was originally developed and backtested in TradingView using PineScript and will now be executed via a Python trading bot.

The system runs **once per day** and trades **daily timeframe signals**.

Primary goal:

* Automate paper trading and eventually live trading
* Maintain deterministic strategy execution
* Ensure reproducibility between TradingView and Python implementation

---

# Strategy Logic

## Indicators Used

The strategy uses three indicators:

### 1. EMA 200

Defines the long-term trend.

Bullish Trend:

```
close > EMA200
```

Bearish Trend:

```
close < EMA200
```

---

### 2. Parabolic SAR

Used for directional confirmation.

Long condition:

```
SAR < Low
```

Short condition:

```
SAR > High
```

---

### 3. MACD Histogram Crossing Zero

MACD calculation:

```
MACD = EMA(12) - EMA(26)
Signal = EMA(MACD, 9)
Delta = MACD - Signal
```

Long signal trigger:

```
delta crosses above 0
```

Short signal trigger:

```
delta crosses below 0
```

---

# Entry Conditions

### Long Entry

All conditions must be true:

```
close > EMA200
SAR < Low
MACD histogram crosses above zero
```

### Short Entry

```
close < EMA200
SAR > High
MACD histogram crosses below zero
```

---

# Exit Logic

The strategy uses **ATR-based risk management**.

Stop Loss:

```
Entry Price - ATR * SL_MULTIPLIER
```

Take Profit:

```
Entry Price + ATR * TP_MULTIPLIER
```

Default values:

```
SL_MULTIPLIER = 1.5
TP_MULTIPLIER = 2.5
ATR Length = 14
```

---

# Trading Frequency

Timeframe:

```
1 Day
```

Expected trades:

```
~5–20 per year
```

This is a **low-frequency swing strategy**.

---

# Architecture

The system does NOT rely on TradingView alerts.

Instead, indicators are recalculated in Python.

Pipeline:

```
Exchange API
     ↓
Fetch OHLC data
     ↓
Compute indicators
     ↓
Evaluate strategy rules
     ↓
Place order
```

---

# System Components

## 1. Data Layer

Responsible for fetching historical candles.

Source:

```
Delta Exchange API
```

Resolution:

```
1D candles
```

---

## 2. Strategy Engine

Computes indicators:

```
EMA200
MACD
Parabolic SAR
ATR
```

Evaluates signals.

---

## 3. Execution Engine

Responsible for:

* order placement
* position management
* risk management

Uses:

```
Delta Exchange REST API
```

Endpoint example:

```
POST /v2/orders
```

---

## 4. Scheduler

The bot runs once daily.

Example execution time:

```
00:05 UTC
```

Implementation options:

* Python `schedule`
* cron job

---

# Environment

Language:

```
Python 3.10+
```

Core libraries:

```
pandas
numpy
requests
ta
schedule
```

---

# Security

API keys must be stored using environment variables.

Example:

```
DELTA_API_KEY
DELTA_API_SECRET
```

Never hardcode keys.

---

# Deployment

Recommended deployment:

```
VPS
```

Examples:

* DigitalOcean
* AWS Lightsail
* Vultr

Minimum resources:

```
1 CPU
1 GB RAM
```

---

# Testing Stages

Stage 1

```
Backtest in TradingView
```

Stage 2

```
Python simulation (no orders)
```

Stage 3

```
Delta Testnet trading
```

Stage 4

```
Live trading with small capital
```

---

# Logging

The system must log:

* signal generation
* trade entries
* trade exits
* errors
* API responses

Logs should be written to:

```
logs/trading.log
```

---

# Future Improvements

Potential enhancements:

* volatility filter
* position sizing based on ATR
* portfolio of multiple coins
* database storage of trades
* dashboard UI

---

# Important Constraints

Agents must follow these rules:

1. Strategy logic must remain deterministic.
2. Indicators must match TradingView calculations.
3. Bot must not place multiple orders for the same signal.
4. All trades must be logged.
5. System must run autonomously once deployed.

---

# Expected Repository Structure

```
project/
│
├─ agents.md
├─ config.py
├─ main.py
├─ strategy/
│   └─ strategy_engine.py
├─ execution/
│   └─ delta_client.py
├─ data/
│   └─ market_data.py
├─ logs/
│
└─ requirements.txt
```

---

# Objective for AI Agents

Build a **robust automated trading bot** capable of executing the described strategy on Delta Exchange Testnet.

Focus areas:

* reliability
* reproducibility
* clean architecture
* clear logging
* safe order execution

The system should run autonomously once deployed.
