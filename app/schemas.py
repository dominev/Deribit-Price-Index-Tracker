# Pydantic схемы

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class PriceRecordBase(BaseModel):
    ticker: str
    price: float
    timestamp: int

class PriceRecordCreate(PriceRecordBase):
    pass

class PriceRecordResponse(PriceRecordBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class PriceFilterParams(BaseModel):
    ticker: str
    from_date: int | None = Field(None, description="UNIX timestamp (seconds)")
    to_date: int | None = Field(None, description="UNIX timestamp (seconds)")