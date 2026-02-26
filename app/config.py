from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Portfolio Risk Collapse Early Warning System"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://riskadmin:riskpass123@localhost:5432/portfolio_risk"
    DATABASE_URL_SYNC: str = (
        "postgresql+psycopg2://riskadmin:riskpass123@localhost:5432/portfolio_risk"
    )
    NIFTY_SYMBOL: str = "^NSEI"

    ROLLING_WINDOW: int = 30
    VAR_CONFIDENCE: float = 0.95
    TRADING_DAYS_PER_YEAR: int = 252

    RISK_WEIGHT_VOLATILITY: float = 0.20
    RISK_WEIGHT_VAR: float = 0.25
    RISK_WEIGHT_BETA: float = 0.15
    RISK_WEIGHT_DOWNSIDE_BETA: float = 0.15
    RISK_WEIGHT_CORRELATION: float = 0.10
    RISK_WEIGHT_STRESS: float = 0.15

    # Alerts (opt-in: leave empty to disable)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = ""
    SMTP_USE_TLS: bool = True
    ALERT_EMAIL_TO: str = ""
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET: str = ""
    ALERT_ON_RISK_LEVELS: str = "HIGH,CRITICAL"

    # OAuth bridge (shared secret between NextAuth and backend)
    OAUTH_BRIDGE_SECRET: str = ""

    # JWT Authentication
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440  # 24 hours

    # WebSocket / API
    API_BASE_URL: str = "http://localhost:8000"


settings = Settings()
