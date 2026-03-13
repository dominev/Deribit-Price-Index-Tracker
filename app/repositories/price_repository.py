# Работа с БД (SQLAlchemy)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import PriceRecord
from app.schemas import PriceRecordCreate

class PriceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, record: PriceRecordCreate) -> PriceRecord:
        db_record = PriceRecord(**record.model_dump())
        self.db.add(db_record)
        await self.db.commit()
        await self.db.refresh(db_record)
        return db_record

    async def get_by_ticker(self, ticker: str) -> list[PriceRecord]:
        result = await self.db.execute(
            select(PriceRecord).where(PriceRecord.ticker == ticker)
        )
        return result.scalars().all()

    async def get_latest_by_ticker(self, ticker: str) -> PriceRecord | None:
        result = await self.db.execute(
            select(PriceRecord)
            .where(PriceRecord.ticker == ticker)
            .order_by(PriceRecord.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def filter_by_ticker_and_date_range(
            self, ticker: str, from_date: int | None, to_date: int | None
    ) -> list[PriceRecord]:
        query = select(PriceRecord).where(PriceRecord.ticker == ticker)
        if from_date:
            query = query.where(PriceRecord.timestamp >= from_date)
        if to_date:
            query = query.where(PriceRecord.timestamp <= to_date)
        query = query.order_by(PriceRecord.timestamp)
        result = await self.db.execute(query)
        return result.scalars().all()