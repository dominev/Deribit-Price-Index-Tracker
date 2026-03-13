# Зависимости для маршрутов

from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_factory
from app.services.deribit_client import DeribitClient

async def get_db_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

async def get_deribit_client(request: Request) -> DeribitClient:
    return request.app.state.deribit_client