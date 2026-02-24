# Portfolio Risk Collapse Early Warning System

Production-grade SaaS application for real-time portfolio risk monitoring with collapse early warning signals. Built with FastAPI, PostgreSQL, Next.js, and a modular NumPy-powered risk engine. Features JWT authentication, SMTP/webhook alerts, and WebSocket live updates.

## Tech Stack

- **Backend:** FastAPI + Uvicorn
- **Frontend:** Next.js 14 + React 18 + TypeScript + Tailwind CSS + Recharts
- **Database:** PostgreSQL 16 + SQLAlchemy 2.0 (async) + Alembic
- **Risk Engine:** NumPy, SciPy, Pandas
- **Auth:** JWT (python-jose) + bcrypt password hashing
- **Real-time:** WebSocket push updates via ConnectionManager
- **Alerts:** SMTP email + webhook (with HMAC signing)
- **Validation:** Pydantic v2
- **Containerization:** Docker + Docker Compose

## Architecture

```
app/
├── api/v1/endpoints/       # FastAPI route handlers
│   ├── auth.py             # Register, login, me
│   ├── portfolios.py       # Portfolio CRUD (user-scoped)
│   ├── risk.py             # Risk compute + history
│   └── ws.py               # WebSocket connections
├── models/                 # SQLAlchemy ORM models
│   ├── user.py             # User (email, hashed_password)
│   ├── portfolio.py        # Portfolio (user_id FK), Holding, PriceHistory
│   └── risk_snapshot.py    # RiskSnapshot
├── schemas/                # Pydantic request/response models
│   ├── auth.py             # UserCreate, UserLogin, TokenResponse
│   ├── portfolio.py        # Portfolio schemas
│   └── risk.py             # RiskReport, RiskHistory
├── repositories/           # Data access layer (async)
├── services/               # Business logic orchestration
│   ├── auth_service.py     # JWT + password verification
│   ├── alert_service.py    # SMTP + webhook alerts
│   ├── portfolio_service.py
│   └── risk_service.py
├── risk_engine/            # Pure numpy computation modules
│   ├── volatility.py       # Rolling volatility (30D)
│   ├── correlation.py      # Pairwise correlation matrix
│   ├── beta.py             # Portfolio beta + downside beta
│   ├── var.py              # 95% Value at Risk
│   ├── stress.py           # Stress tests (-3%, -5%, -8%)
│   ├── composite.py        # Weighted composite score (0-100)
│   └── acceleration.py     # Risk acceleration + early warnings
└── websocket.py            # ConnectionManager singleton

frontend/src/
├── app/
│   ├── layout.tsx          # Root layout with AuthProvider + NavBar
│   ├── page.tsx            # Landing page
│   ├── login/page.tsx      # Login form
│   ├── register/page.tsx   # Registration form
│   ├── dashboard/page.tsx  # Risk dashboard with WebSocket live updates
│   └── portfolios/page.tsx # Portfolio management
├── components/
│   ├── AuthProvider.tsx     # Auth context (token, user, login/logout)
│   ├── NavBar.tsx           # Dynamic navigation
│   ├── RiskGauge.tsx        # Donut chart risk gauge
│   ├── MetricCard.tsx       # Metric display card
│   ├── CorrelationHeatmap.tsx
│   ├── StressTestChart.tsx
│   └── RiskTrendChart.tsx
├── lib/
│   ├── api.ts              # API client with Bearer auth + 401 handling
│   └── types.ts            # TypeScript interfaces
├── middleware.ts            # Edge middleware (auth redirect)
└── ...

scripts/
├── market_worker.py        # Yahoo Finance price fetcher + risk compute + alerts + WS notify
└── seed.py                 # Sample data seeder
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

This starts PostgreSQL, the FastAPI backend, and the Next.js frontend. Migrations run automatically.

- **API:** http://localhost:8000
- **Frontend:** http://localhost:3000
- **Swagger docs:** http://localhost:8000/docs

### Local Development

```bash
# 1. Start PostgreSQL
docker compose up -d db

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run migrations
alembic upgrade head

# 5. Seed sample data
python -m scripts.seed

# 6. Start the API server
uvicorn app.main:app --reload

# 7. Start the frontend (separate terminal)
cd frontend && npm install && npm run dev
```

### Run Tests

```bash
python -m pytest tests/ -v
```

## Authentication

All portfolio and risk endpoints require a JWT Bearer token. The auth flow:

1. **Register** a new user
2. **Login** to get a JWT token
3. **Include** the token in all requests as `Authorization: Bearer <token>`

Tokens expire after 24 hours (configurable via `JWT_EXPIRY_MINUTES`).

A default admin user is created by the migration:
- **Email:** `admin@riskmonitor.local`
- **Password:** `admin123`

## API Endpoints

Base path: `/api/v1`

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create a new user account |
| POST | `/auth/login` | No | Login and receive JWT token |
| GET | `/auth/me` | Yes | Get current user profile |

### Portfolios (all require auth)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/portfolios` | Create portfolio with optional holdings |
| GET | `/portfolios` | List user's portfolios |
| GET | `/portfolios/{id}` | Get portfolio details |
| PATCH | `/portfolios/{id}` | Update portfolio metadata |
| DELETE | `/portfolios/{id}` | Delete portfolio |
| POST | `/portfolios/{id}/holdings` | Add holding to portfolio |
| DELETE | `/portfolios/{id}/holdings/{holding_id}` | Remove holding |
| GET | `/portfolios/{id}/prices/{symbol}` | Get price history |
| POST | `/portfolios/prices/upload` | Bulk upload price data |

### Risk Analysis (all require auth)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/risk/{id}/compute` | Compute full risk report |
| GET | `/risk/{id}/history` | Get risk score history |

### WebSocket

| Protocol | Path | Description |
|----------|------|-------------|
| WS | `/ws/{portfolio_id}` | Live risk updates for a portfolio |

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |

### Example: Register and Login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword", "full_name": "Jane Doe"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword"}'
# Returns: {"access_token": "eyJ...", "token_type": "bearer"}
```

### Example: Create Portfolio (with auth)

```bash
curl -X POST http://localhost:8000/api/v1/portfolios \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
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
curl -X POST http://localhost:8000/api/v1/risk/{portfolio_id}/compute \
  -H "Authorization: Bearer eyJ..."
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

## Alerts

Alerts are opt-in and triggered when risk levels match `ALERT_ON_RISK_LEVELS` (default: `HIGH,CRITICAL`).

**SMTP Email:** Set `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`, and `ALERT_EMAIL_TO` to enable HTML email alerts.

**Webhook:** Set `WEBHOOK_URL` to receive JSON POST notifications. Optionally set `WEBHOOK_SECRET` for HMAC-SHA256 signed payloads (header: `X-Signature-SHA256`).

## WebSocket Live Updates

The dashboard connects to `ws://localhost:8000/api/v1/ws/{portfolio_id}` and receives real-time risk report updates when:

- A user clicks "Compute Risk" in the dashboard
- The market worker completes a risk computation cycle

The connection includes a 30-second keepalive ping. A green "Live" indicator appears when connected.

## Market Worker

The market worker fetches real prices from Yahoo Finance, updates holdings, computes risk, sends alerts, and notifies WebSocket clients.

```bash
# One-shot run
python -m scripts.market_worker

# Continuous loop (every hour)
python -m scripts.market_worker --loop --interval 3600
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
| `JWT_SECRET` | `change-me-in-production` | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_EXPIRY_MINUTES` | `1440` | Token expiry (24h) |
| `SMTP_HOST` | *(empty)* | SMTP server host |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USER` | *(empty)* | SMTP username |
| `SMTP_PASS` | *(empty)* | SMTP password |
| `SMTP_FROM` | *(empty)* | Sender email address |
| `ALERT_EMAIL_TO` | *(empty)* | Recipient email address |
| `WEBHOOK_URL` | *(empty)* | Webhook endpoint URL |
| `WEBHOOK_SECRET` | *(empty)* | HMAC signing secret |
| `ALERT_ON_RISK_LEVELS` | `HIGH,CRITICAL` | Risk levels that trigger alerts |
| `API_BASE_URL` | `http://localhost:8000` | API URL for worker WS notifications |

## API Documentation

Once the server is running, interactive docs are available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Sample Seed Data

The seed script (`python -m scripts.seed`) creates:

- **Portfolio:** "Indian Large Cap Growth" with 5 NIFTY large-cap holdings
- **Holdings:** RELIANCE, TCS, HDFC Bank, Infosys, ICICI Bank
- **Price History:** 90 days of synthetic OHLCV data for all symbols + NIFTY benchmark
