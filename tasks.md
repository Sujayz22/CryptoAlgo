# tasks.md

Development Roadmap for Delta Exchange Automated Trading Bot

---

# Phase 1 — Repository Setup

## Task 1.1 — Initialize Project Structure

Create repository layout:

```
delta-trading-bot/

agents.md
tasks.md
README.md
requirements.txt

config/
data/
indicators/
strategy/
execution/
scheduler/
logs/
```

Acceptance criteria:

* Folder structure exists
* Project installs with `pip install -r requirements.txt`

---

## Task 1.2 — Environment Configuration

Create `.env` loader for API keys.

Required variables:

```
DELTA_API_KEY
DELTA_API_SECRET
DELTA_BASE_URL
```

Acceptance criteria:

* Bot loads environment variables
* No API keys are hardcoded

---

# Phase 2 — Market Data Layer

## Task 2.1 — Fetch OHLC Data

File:

```
data/market_data.py
```

Function:

```
get_candles(symbol, resolution)
```

Requirements:

* Fetch 1D candles from Delta Exchange
* Return pandas DataFrame
* Columns:

```
timestamp
open
high
low
close
volume
```

Acceptance criteria:

* Fetch last 500 candles successfully
* DataFrame sorted by time

---

## Task 2.2 — Data Normalization

Ensure:

* numeric columns converted to float
* timestamps converted to datetime

Acceptance criteria:

* No missing values
* Data ready for indicator calculations

---

# Phase 3 — Indicator Engine

## Task 3.1 — EMA 200 Calculation

File:

```
indicators/indicators.py
```

Function:

```
compute_ema200(df)
```

Adds column:

```
ema200
```

Acceptance criteria:

* Matches TradingView EMA200 values

---

## Task 3.2 — MACD Calculation

Function:

```
compute_macd(df)
```

Adds columns:

```
macd
signal
histogram
```

Acceptance criteria:

* Matches PineScript MACD outputs

---

## Task 3.3 — Parabolic SAR

Function:

```
compute_sar(df)
```

Adds column:

```
sar
```

Acceptance criteria:

* SAR flips match TradingView

---

## Task 3.4 — ATR

Function:

```
compute_atr(df)
```

Adds column:

```
atr
```

Acceptance criteria:

* ATR matches TradingView

---

# Phase 4 — Strategy Engine

## Task 4.1 — Signal Logic

File:

```
strategy/strategy_engine.py
```

Function:

```
generate_signal(df)
```

Output:

```
BUY
SELL
HOLD
```

Strategy rules:

Long signal:

```
close > EMA200
SAR < low
MACD histogram crosses above 0
```

Short signal:

```
close < EMA200
SAR > high
MACD histogram crosses below 0
```

Acceptance criteria:

* Signals match TradingView backtest

---

# Phase 5 — Risk Management

## Task 5.1 — Stop Loss and Take Profit

Function:

```
compute_trade_levels(entry_price, atr)
```

Outputs:

```
stop_loss
take_profit
```

Formula:

```
SL = entry - ATR * 1.5
TP = entry + ATR * 2.5
```

Acceptance criteria:

* Levels calculated correctly

---

# Phase 6 — Execution Engine

## Task 6.1 — Delta Exchange API Client

File:

```
execution/delta_client.py
```

Functions:

```
place_order()
get_position()
close_position()
```

Requirements:

* Signed requests
* Retry logic
* API error handling

Acceptance criteria:

* Orders executed on testnet

---

## Task 6.2 — Order Manager

File:

```
execution/order_manager.py
```

Responsibilities:

* prevent duplicate trades
* ensure only 1 open position
* attach SL/TP orders

Acceptance criteria:

* System never opens multiple trades

---

# Phase 7 — Scheduler

## Task 7.1 — Daily Execution

File:

```
scheduler/run_bot.py
```

Behavior:

```
1. fetch market data
2. compute indicators
3. evaluate strategy
4. place order if needed
```

Run time:

```
00:05 UTC daily
```

Acceptance criteria:

* Script runs automatically each day

---

# Phase 8 — Logging System

## Task 8.1 — Logging Framework

All modules must log events.

Log file:

```
logs/trading.log
```

Required events:

```
market data fetched
signal generated
order placed
order result
errors
```

Acceptance criteria:

* Logs readable and timestamped

---

# Phase 9 — Paper Trading Mode

## Task 9.1 — Simulation Mode

Add configuration flag:

```
PAPER_MODE = True
```

Behavior:

* signals executed without real orders
* simulated position tracking

Acceptance criteria:

* bot runs without sending exchange orders

---

# Phase 10 — Deployment

## Task 10.1 — VPS Deployment

Recommended environment:

```
Ubuntu 22.04
Python 3.10+
```

Deployment steps:

```
git clone repo
install dependencies
set environment variables
run bot
```

Acceptance criteria:

* bot runs continuously on server

---

# Phase 11 — Testnet Trading

Run system on:

```
Delta Exchange Testnet
```

Testing duration:

```
2–4 weeks
```

Monitor:

```
trade frequency
execution accuracy
API stability
```

Acceptance criteria:

* strategy behaves as expected

---

# Phase 12 — Live Deployment

Requirements before live trading:

* minimum 2 weeks stable testnet operation
* logs verified
* risk limits enforced

Initial live risk:

```
≤1% account per trade
```

---

# End Goal

The final system should:

* autonomously run once per day
* replicate TradingView signals
* trade on Delta Exchange
* maintain detailed logs
* operate safely with minimal supervision

---
