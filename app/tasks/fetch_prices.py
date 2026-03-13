# Celery задача для периодического сбора

import asyncio
from celery import Celery
from app.config import settings
from app.services.deribit_client import DeribitClient
from app.services.price_service import PriceService
from app.database import async_session_factory

celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.beat_schedule = {
    "fetch-btc-every-minute": {
        "task": "app.tasks.fetch_prices.fetch_btc_price",
        "schedule": 60.0,  # Каждую минуту
    },
    "fetch-eth-every-minute": {
        "task": "app.tasks.fetch_prices.fetch_eth_price",
        "schedule": 60.0,
    },
}
celery_app.conf.timezone = "UTC"

@celery_app.task
def fetch_btc_price():
    """Celery задача для получения цены BTC/USD."""
    return _fetch_currency("btc_usd")

@celery_app.task
def fetch_eth_price():
    """Celery задача для получения цены ETH/USD."""
    return _fetch_currency("eth_usd")

def _fetch_currency(currency: str):
    """Синхронная обёртка для запуска асинхронного кода."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async_fetch(currency))
    finally:
        loop.close()

async def _async_fetch(currency: str):
    """Асинхронное получение и сохранение цены."""
    client = DeribitClient()
    await client.start()
    try:
        async with async_session_factory() as session:
            service = PriceService(session, client)
            await service.fetch_and_save_currency(currency)
    finally:
        await client.stop()