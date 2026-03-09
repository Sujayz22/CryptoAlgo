# agents.md

AI Development Context for Automated Trading System

---

# 1. Project Mission

Build a **reliable automated trading bot** that executes a validated TradingView strategy on **Delta Exchange Testnet**.

The system must:

* reproduce TradingView signals exactly
* run autonomously
* trade once per day
* log all activity
* support safe deployment to live markets

This project prioritizes **robustness and clarity over complexity**.

---

# 2. Strategy Description

The strategy is a **trend-following swing system**.

Timeframe:

```
1 Day
```

Markets:

```
BTCUSDT
ETHUSDT
```

Trade frequency:

```
~5–20 trades per year
```

---

# 3. Indicators

### EMA 200

Defines macro trend.

Bullish regime:

```
close > EMA200
```

Bearish regime:

```
close < EMA200
```

---

### Parabolic SAR

Directional confirmation.

Long signal:

```
SAR < Low
```

Short signal:

```
SAR > High
```

---

### MACD Histogram

MACD formula:

```
MACD = EMA(12) - EMA(26)
Signal = EMA(MACD,9)
Histogram = MACD - Signal
```

Entry triggers:

Long:

```
Histogram crosses above 0
```

Short:

```
Histogram crosses below 0
```

---

# 4. Entry Logic

## Long Entry

All must be true:

```
close > EMA200
SAR < Low
MACD Histogram crosses above 0
```

---

## Short Entry

```
close < EMA200
SAR > High
MACD Histogram crosses below 0
```

---

# 5. Exit Logic

Risk management uses ATR.

Stop Loss:

```
Entry - ATR * SL_MULTIPLIER
```

Take Profit:

```
Entry + ATR * TP_MULTIPLIER
```

Default parameters:

```
ATR_LENGTH = 14
SL_MULTIPLIER = 1.5
TP_MULTIPLIER = 2.5
```

---

# 6. System Architecture

The trading bot must follow a **layered architecture**.

```
Market Data Layer
        ↓
Indicator Engine
        ↓
Strategy Engine
        ↓
Risk Manager
        ↓
Execution Engine
        ↓
Exchange API
```

---

# 7. System Components

## Market Data Module

Responsibilities:

* fetch OHLC candles
* maintain historical dataframe
* normalize API responses

Data source:

```
Delta Exchange REST API
```

Resolution:

```
1D
```

---

## Indicator Engine

Calculates indicators.

Required indicators:

```
EMA200
MACD
Parabolic SAR
ATR
```

Indicator outputs must match TradingView calculations.

---

## Strategy Engine

Evaluates trading conditions.

Outputs:

```
BUY
SELL
HOLD
```

The engine must remain **pure and deterministic**.

No API calls or side effects.

---

## Risk Manager

Calculates:

* stop loss
* take profit
* position size

Risk constraints:

```
max 1 open trade
risk < 2% account
```

---

## Execution Engine

Responsible for:

* placing orders
* closing positions
* handling API errors

Exchange:

```
Delta Exchange
```

Primary endpoint:

```
POST /v2/orders
```

---

# 8. Scheduler

Strategy runs once daily.

Execution time:

```
00:05 UTC
```

Implementation options:

```
cron
Python schedule
systemd timer
```

---

# 9. Technology Stack

Language:

```
Python 3.10+
```

Libraries:

```
pandas
numpy
requests
ta
schedule
python-dotenv
```

---

# 10. Environment Variables

API keys must be loaded from environment.

Required variables:

```
DELTA_API_KEY
DELTA_API_SECRET
DELTA_BASE_URL
```

Example:

```
https://api.delta.exchange
```

Testnet:

```
https://testnet-api.delta.exchange
```

---

# 11. Repository Structure

Expected project layout:

```
delta-trading-bot/

agents.md
README.md
requirements.txt

config/
    settings.py

data/
    market_data.py

indicators/
    indicators.py

strategy/
    strategy_engine.py

execution/
    delta_client.py
    order_manager.py

scheduler/
    run_bot.py

logs/
```

---

# 12. Logging

All system activity must be logged.

Log file:

```
logs/trading.log
```

Required log events:

```
data fetch
indicator calculation
signal generation
order submission
order result
errors
```

---

# 13. Development Rules for AI Agents

Agents must follow these constraints:

1. Never modify strategy logic without explicit instruction.
2. Keep modules independent and testable.
3. Ensure reproducibility of indicator calculations.
4. All API calls must handle retries and errors.
5. Avoid hidden state or implicit behavior.

---

# 14. Testing Pipeline

Development must proceed through stages.

Stage 1

```
Strategy replication from PineScript
```

Stage 2

```
Offline backtest in Python
```

Stage 3

```
Testnet trading
```

Stage 4

```
Live trading with small capital
```

---

# 15. Performance Metrics

The system should track:

```
total trades
win rate
profit factor
max drawdown
average trade duration
```

Metrics should be stored locally.

---

# 16. Safety Constraints

The bot must never:

* open multiple trades simultaneously
* exceed configured position size
* trade when API connectivity fails

---

# 17. Future Extensions

Possible improvements:

```
multi-asset trading
portfolio risk management
volatility filters
database storage
web dashboard
machine learning regime detection
```

---

# 18. AI Agent Objective

Agents are tasked with constructing a **robust automated trading system** implementing the defined strategy.

Priorities:

```
correctness
stability
clean architecture
risk safety
```

Performance optimization is secondary.

---
