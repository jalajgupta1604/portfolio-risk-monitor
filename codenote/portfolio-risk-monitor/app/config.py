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


settings = Settings()
