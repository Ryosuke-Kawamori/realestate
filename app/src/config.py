from pydantic import BaseModel, Field
import os

class Settings(BaseModel):
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="rakumachi")
    POSTGRES_HOST: str = Field(default="db")
    POSTGRES_PORT: int = Field(default=5432)

    DISCORD_WEBHOOK_URL: str | None = None

    RESIDUAL_PCT_THRESHOLD: float = -0.15
    MIN_PRICE_JPY: int = 5_000_000

    SCRAPE_INTERVAL_MIN: int = 30
    RETRAIN_CRON: str = "0 5 * * *"
    SCAN_INTERVAL_MIN: int = 10

    RAKUMACHI_USER: str | None = None
    RAKUMACHI_PASS: str | None = None

    TARGET_LIST_URL: str | None = None

def get_settings() -> Settings:
    # .env は docker-compose の env_file から読み込まれる
    return Settings(
        POSTGRES_USER=os.getenv("POSTGRES_USER","postgres"),
        POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD","postgres"),
        POSTGRES_DB=os.getenv("POSTGRES_DB","rakumachi"),
        POSTGRES_HOST=os.getenv("POSTGRES_HOST","db"),
        POSTGRES_PORT=int(os.getenv("POSTGRES_PORT","5432")),
        DISCORD_WEBHOOK_URL=os.getenv("DISCORD_WEBHOOK_URL"),
        RESIDUAL_PCT_THRESHOLD=float(os.getenv("RESIDUAL_PCT_THRESHOLD","-0.15")),
        MIN_PRICE_JPY=int(os.getenv("MIN_PRICE_JPY","5000000")),
        SCRAPE_INTERVAL_MIN=int(os.getenv("SCRAPE_INTERVAL_MIN","30")),
        RETRAIN_CRON=os.getenv("RETRAIN_CRON","0 5 * * *"),
        SCAN_INTERVAL_MIN=int(os.getenv("SCAN_INTERVAL_MIN","10")),
        RAKUMACHI_USER=os.getenv("RAKUMACHI_USER"),
        RAKUMACHI_PASS=os.getenv("RAKUMACHI_PASS"),
        TARGET_LIST_URL=os.getenv("TARGET_LIST_URL")
    )
