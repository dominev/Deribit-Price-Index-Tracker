# Точка входа FastAPI

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from app.api import prices
from app.config import settings
from app.services.deribit_client import DeribitClient
from app.database import engine
from app.models import Base

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Стартап
    logger.info("Запуск...")
    async with engine.begin() as conn:
        # Создание таблиц
        await conn.run_sync(Base.metadata.create_all)

    deribit_client = DeribitClient()
    await deribit_client.start()
    app.state.deribit_client = deribit_client

    yield

    # Выкл
    logger.info("Выключение...")
    await deribit_client.stop()
    await engine.dispose()

app = FastAPI(title="Deribit Price Index Tracker", lifespan=lifespan)
app.include_router(prices.router)