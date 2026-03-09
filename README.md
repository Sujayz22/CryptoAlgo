# Delta Exchange Automated Trading Bot

Automated swing trading bot for **Delta Exchange Testnet**, implementing a trend-following strategy using EMA 200, Parabolic SAR, and MACD Histogram crossovers on the daily timeframe.

---

## Strategy

| Indicator | Parameter | Role |
|-----------|-----------|------|
| EMA 200 | Period: 200 | Trend filter |
| Parabolic SAR | Step: 0.02, Max: 0.2 | Direction confirmation |
| MACD Histogram | 12/26/9 | Entry trigger |
| ATR | Period: 14 | Risk sizing |

**Long entry:** `close > EMA200` AND `SAR < Low` AND `MACD histogram crosses above 0`  
**Short entry:** `close < EMA200` AND `SAR > High` AND `MACD histogram crosses below 0`

**Risk:** SL = entry ± ATR × 1.5 | TP = entry ± ATR × 2.5

---

## Project Structure

```
CryptoAlgo/
├── main.py                  # Run one trading cycle manually
├── requirements.txt
├── .env                     # API keys (never commit)
├── config/
│   └── settings.py          # All constants and env vars
├── data/
│   └── market_data.py       # Fetch OHLCV from Delta Exchange
├── indicators/
│   └── indicators.py        # EMA200, MACD, SAR, ATR
├── strategy/
│   └── strategy_engine.py   # Signal logic + SL/TP computation
├── execution/
│   ├── delta_client.py      # Signed REST client
│   └── order_manager.py     # Duplicate prevention, paper mode
├── scheduler/
│   └── run_bot.py           # Daily scheduled execution
├── utils/
│   └── logging_setup.py     # Console + rotating file logs
└── logs/
    └── trading.log          # Auto-created on first run
```

---

## Setup

```bash
# 1. Clone and enter the project
cd CryptoAlgo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Edit .env:
DELTA_API_KEY=your_key
DELTA_API_SECRET=your_secret
DELTA_BASE_URL=https://cdn-ind.testnet.deltaex.org
PAPER_MODE=True   # Set to False for live trading
```

---

## Running

### Manual cycle (one-shot)

```bash
python main.py
```

### Scheduled daily bot

```bash
python scheduler/run_bot.py
```

---

## Testing Stages

| Stage | Description |
|-------|-------------|
| 1 | `PAPER_MODE=True` — validate signals, no orders placed |
| 2 | Delta Testnet with real API keys |
| 3 | Live trading with small position size |

---

## Configuration

Edit `config/settings.py` to tune:

| Setting | Default | Description |
|---------|---------|-------------|
| `SYMBOLS` | `['BTCUSD', 'ETHUSD']` | Markets to trade |
| `SL_MULTIPLIER` | `1.5` | ATR multiples for stop-loss |
| `TP_MULTIPLIER` | `2.5` | ATR multiples for take-profit |
| `ORDER_SIZE` | `1.0` | Contracts per trade |
| `SCHEDULE_TIME_UTC` | `"00:05"` | Daily run time |
| `PAPER_MODE` | `True` | Disable live orders |

---

## Logs

All activity logged to `logs/trading.log` (rotating, max 5MB × 3 backups).

Events captured:

- Market data fetch
- Indicator values
- Signal decisions
- Orders placed or simulated
- Errors

---

## Safety

- Bot never opens multiple positions on the same symbol simultaneously
- Paper mode is `True` by default — you must explicitly set `PAPER_MODE=False` to go live
- API keys are loaded from `.env`, never hardcoded
