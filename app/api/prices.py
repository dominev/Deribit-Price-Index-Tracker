# Маршруты для /prices

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.price_service import PriceService
from app.services.deribit_client import DeribitClient
from app.schemas import PriceRecordResponse, PriceFilterParams
from app.dependencies import get_db_session, get_deribit_client

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("", response_model=list[PriceRecordResponse])
async def get_all_prices(
        ticker: str = Query(..., description="Currency pair, e.g. btc_usd"),
        db: AsyncSession = Depends(get_db_session),
        deribit_client: DeribitClient = Depends(get_deribit_client),
):
    service = PriceService(db, deribit_client)
    records = await service.get_all_prices(ticker)
    return records

@router.get("/latest", response_model=PriceRecordResponse | None)
async def get_latest_price(
        ticker: str = Query(..., description="Currency pair"),
        db: AsyncSession = Depends(get_db_session),
        deribit_client: DeribitClient = Depends(get_deribit_client),
):
    service = PriceService(db, deribit_client)
    record = await service.get_latest_price(ticker)
    if not record:
        raise HTTPException(status_code=404, detail="No records found")
    return record

@router.get("/filter", response_model=list[PriceRecordResponse])
async def filter_prices(
        ticker: str = Query(...),
        from_date: int | None = Query(None, description="UNIX timestamp from"),
        to_date: int | None = Query(None, description="UNIX timestamp to"),
        db: AsyncSession = Depends(get_db_session),
        deribit_client: DeribitClient = Depends(get_deribit_client),
):
    params = PriceFilterParams(ticker=ticker, from_date=from_date, to_date=to_date)
    service = PriceService(db, deribit_client)
    records = await service.filter_prices(params)
    return records