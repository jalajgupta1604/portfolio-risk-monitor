# Portfolio Risk Collapse Early Warning System

Production-grade SaaS application for real-time portfolio risk monitoring with collapse early warning signals. Built with FastAPI, PostgreSQL, and a modular NumPy-powered risk engine.

## Tech Stack

- **Backend:** FastAPI + Uvicorn
- **Database:** PostgreSQL 16 + SQLAlchemy 2.0 (async) + Alembic
- **Risk Engine:** NumPy, SciPy, Pandas
- **Validation:** Pydantic v2
- **Containerization:** Docker + Docker Compose

## Architecture

```
app/
├── api/v1/endpoints/       # FastAPI route handlers
├── models/                 # SQLAlchemy ORM models
├── schemas/                # Pydantic request/response models
├── repositories/           # Data access layer (async)
├── services/               # Business logic orchestration
└── risk_engine/            # Pure numpy computation modules
    ├── volatility.py       # Rolling volatility (30D)
    ├── correlation.py      # Pairwise correlation matrix
    ├── beta.py             # Portfolio beta + downside beta
    ├── var.py              # 95% Value at Risk
    ├── stress.py           # Stress tests (-3%, -5%, -8%)
    ├── composite.py        # Weighted composite score (0-100)
    └── acceleration.py     # Risk acceleration + early warnings
```

## Risk Features

| Metric | Description |
|--------|-------------|
| **Rolling Volatility** | 30-day annualized portfolio volatility (252 trading days) |
| **Correlation Matrix** | Pairwise asset correlation over rolling window |
| **Portfolio Beta** | Sensitivity vs NIFTY 50 benchmark (`cov(P,B) / var(B)`) |
| **Downside Beta** | Beta computed only on negative market days |
| **95% VaR** | Max of parametric and historical Value at Risk |
| **Stress Tests** | Portfolio impact under -3%, -5%, -8% market shocks |
| **Composite Score** | Weighted risk score from 0 (safe) to 100 (critical) |
| **Risk Acceleration** | Rate of change in composite score over time |
| **Early Warnings** | Rule-based alerts for critical thresholds |

### Composite Score Weights

| Component | Weight |
|-----------|--------|
| VaR (95%) | 25% |
| Volatility | 20% |
| Beta | 15% |
| Downside Beta | 15% |
| Stress Impact | 15% |
| Correlation | 10% |

### Risk Levels

| Score | Level |
|-------|-------|
| 0–19 | LOW |
| 20–39 | MODERATE |
| 40–59 | ELEVATED |
| 60–79 | HIGH |
| 80–100 | CRITICAL |

## Quick Start

### Docker (recommended)

```bash
docker compose up -d
```

This starts PostgreSQL and the app, runs migrations automatically, and serves the API at `http://localhost:8000`.

### Local Development

```bash
# 1. Start PostgreSQL
docker compose up -d db

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run migrations
alembic upgrade head

# 5. Seed sample data
python -m scripts.seed

# 6. Start the server
uvicorn app.main:app --reload
```

### Run Tests

```bash
pip install pytest pytest-asyncio pytest-cov scipy
python -m pytest tests/ -v
```

## API Endpoints

Base path: `/api/v1`

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |

### Portfolios

| Method | Path | Description |
|--------|------|-------------|
| POST | `/portfolios` | Create portfolio with optional holdings |
| GET | `/portfolios` | List all portfolios |
| GET | `/portfolios/{id}` | Get portfolio details |
| PATCH | `/portfolios/{id}` | Update portfolio metadata |
| DELETE | `/portfolios/{id}` | Delete portfolio |
| POST | `/portfolios/{id}/holdings` | Add holding to portfolio |
| DELETE | `/portfolios/{id}/holdings/{holding_id}` | Remove holding |
| GET | `/portfolios/{id}/prices/{symbol}` | Get price history |
| POST | `/portfolios/prices/upload` | Bulk upload price data |

### Risk Analysis

| Method | Path | Description |
|--------|------|-------------|
| POST | `/risk/{id}/compute` | Compute full risk report |
| GET | `/risk/{id}/history` | Get risk score history |

### Example: Create Portfolio

```bash
curl -X POST http://localhost:8000/api/v1/portfolios \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Growth Portfolio",
    "holdings": [
      {"symbol": "RELIANCE.NS", "quantity": 40, "avg_buy_price": 2450.0},
      {"symbol": "TCS.NS", "quantity": 25, "avg_buy_price": 3750.0},
      {"symbol": "HDFCBANK.NS", "quantity": 60, "avg_buy_price": 1600.0}
    ]
  }'
```

### Example: Compute Risk

```bash
curl -X POST http://localhost:8000/api/v1/risk/{portfolio_id}/compute
```

Returns:

```json
{
  "portfolio_id": "...",
  "composite_score": 42.5,
  "risk_level": "ELEVATED",
  "rolling_volatility": 0.2834,
  "portfolio_beta": 1.12,
  "downside_beta": 1.35,
  "var_95": 0.0218,
  "var_95_amount": 21800.0,
  "risk_acceleration": 2.3,
  "correlation_matrix": { ... },
  "stress_results": [
    {"shock_pct": -3.0, "portfolio_impact_pct": -3.45, "estimated_loss": -34500.0},
    {"shock_pct": -5.0, "portfolio_impact_pct": -5.78, "estimated_loss": -57800.0},
    {"shock_pct": -8.0, "portfolio_impact_pct": -9.32, "estimated_loss": -93200.0}
  ],
  "early_warning_signals": [
    "WARNING: Composite risk score exceeds 60 — elevated risk detected"
  ]
}
```

## Configuration

All settings are configurable via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async database connection |
| `DATABASE_URL_SYNC` | `postgresql+psycopg2://...` | Sync connection (Alembic) |
| `APP_ENV` | `development` | Environment mode |
| `NIFTY_SYMBOL` | `^NSEI` | Benchmark index symbol |
| `ROLLING_WINDOW` | `30` | Calculation window (days) |
| `VAR_CONFIDENCE` | `0.95` | VaR confidence level |
| `TRADING_DAYS_PER_YEAR` | `252` | Annualization factor |
| `RISK_WEIGHT_*` | See config | Composite score weights |

## API Documentation

Once the server is running, interactive docs are available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Sample Seed Data

The seed script (`python -m scripts.seed`) creates:

- **Portfolio:** "Indian Large Cap Growth" with 5 NIFTY large-cap holdings
- **Holdings:** RELIANCE, TCS, HDFC Bank, Infosys, ICICI Bank
- **Price History:** 90 days of synthetic OHLCV data for all symbols + NIFTY benchmark
