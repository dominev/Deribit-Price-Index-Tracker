# логика работы с ценами

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.price_repository import PriceRepository
from app.schemas import PriceRecordCreate, PriceFilterParams
from app.services.deribit_client import DeribitClient

logger = logging.getLogger(__name__)

class PriceService:
    def __init__(self, db: AsyncSession, deribit_client: DeribitClient):
        self.repo = PriceRepository(db)
        self.deribit_client = deribit_client

    async def save_price(self, ticker: str, price: float, timestamp: int):
        record = PriceRecordCreate(
            ticker=ticker,
            price=price,
            timestamp=timestamp
        )
        created = await self.repo.create(record)
        logger.info(f"Saved price for {ticker}: {price}")
        return created

    async def fetch_and_save_currency(self, currency: str):
        data = await self.deribit_client.fetch_index_price(currency)
        await self.save_price(data["ticker"], data["price"], data["timestamp"])

    async def get_all_prices(self, ticker: str):
        return await self.repo.get_by_ticker(ticker)

    async def get_latest_price(self, ticker: str):
        return await self.repo.get_latest_by_ticker(ticker)

    async def filter_prices(self, params: PriceFilterParams):
        return await self.repo.filter_by_ticker_and_date_range(
            ticker=params.ticker,
            from_date=params.from_date,
            to_date=params.to_date,
        )