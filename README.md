# TRC20 USDT Deposit Telegram Bot

Production-ready Telegram bot for USDT (TRC20) deposits with referral system, built with **aiogram 3**, **PostgreSQL**, and **async Python**.

## Features

- **User registration** with deep-link referral support (`/start REF_CODE`)
- **Unique TRC20 deposit addresses** per user
- **Automatic deposit detection** via background worker
- **Referral commissions** — configurable % with auto-credit or pending-for-admin modes
- **Inline keyboard UI** — Balance, Deposit, Referral, Transactions
- **Admin panel** — `/admin` for stats, users, deposits, referrals, commission management
- **Swappable blockchain layer** — mock provider for testing, TronGrid for production
- **Rate limiting** and structured logging

## Project Structure

```
├── main.py                 # Entry point
├── config.py               # Environment-based configuration
├── db/
│   ├── connection.py       # Async SQLAlchemy engine & session
│   └── models.py           # ORM models (users, deposits, transactions, referrals, commissions)
├── services/
│   ├── user_service.py     # Registration, balance, lookup
│   ├── wallet_service.py   # Deposit address management
│   ├── deposit_service.py  # Transaction recording
│   ├── referral_service.py # Referral tracking & commissions
│   └── admin_service.py    # Aggregated admin stats
├── blockchain/
│   ├── base.py             # Abstract BlockchainProvider interface
│   ├── mock_provider.py    # In-memory mock for testing
│   └── trongrid_provider.py# Real TronGrid TRC20 provider
├── handlers/
│   ├── start.py            # /start with deep-link referral
│   ├── menu.py             # Main menu & balance
│   ├── deposit.py          # Deposit address screen
│   ├── referral.py         # Referral link & stats
│   ├── transactions.py     # Transaction history
│   └── admin.py            # Admin panel
├── bot/
│   ├── keyboards.py        # Inline keyboard builders
│   └── middlewares.py       # Logging & rate-limit middlewares
├── workers/
│   └── deposit_monitor.py  # Background deposit scanner
├── utils/
│   └── helpers.py          # Logging setup
├── requirements.txt
├── Procfile                # Railway deployment
└── .env.example
```

## Quick Start

```bash
# 1. Clone and enter the project
cd "tg bot tron"

# 2. Create virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your BOT_TOKEN, DATABASE_URL, ADMIN_IDS, etc.

# 5. Run
python main.py
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `BOT_TOKEN` | Telegram bot token (required) | — |
| `DATABASE_URL` | PostgreSQL connection URL (required) | — |
| `ADMIN_IDS` | Comma-separated Telegram user IDs | — |
| `BLOCKCHAIN_PROVIDER` | `mock` or `trongrid` | `mock` |
| `TRONGRID_API_KEY` | TronGrid API key | — |
| `REFERRAL_COMMISSION_PCT` | Commission percentage | `10` |
| `AUTO_CREDIT_REFERRAL` | Auto-credit (`true`) or hold pending (`false`) | `false` |
| `DEPOSIT_CHECK_INTERVAL` | Seconds between deposit scans | `60` |
| `LOG_LEVEL` | Python log level | `INFO` |

## Mock Mode

Set `BLOCKCHAIN_PROVIDER=mock` in `.env`. The mock provider generates deterministic fake addresses and allows simulating deposits programmatically for testing.

## Railway Deployment

1. Push to GitHub
2. Connect repo to Railway
3. Add PostgreSQL plugin → Railway sets `DATABASE_URL` automatically
4. Set remaining env vars in Railway dashboard
5. Railway uses `Procfile` (`worker: python main.py`) automatically

## Database

Tables are auto-created on first run via SQLAlchemy `create_all`. For production migrations, integrate Alembic (dependency included).
