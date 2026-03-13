# Настройки из переменных окружения

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # БД
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "prices_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    # Redis / Celery
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(..., env="CELERY_RESULT_BACKEND")

    # Deribit API
    DERIBIT_API_URL: str = "https://www.deribit.com/api/v2/public/get_index_price"
    REQUEST_TIMEOUT: int = 10
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    RATE_LIMIT: int = 5  # Запросы в сек. (на все валюты)

    # Лог
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()