# SQLAlchemy модели

from sqlalchemy import Column, Integer, String, Float, BigInteger, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PriceRecord(Base):
    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False)

    __table_args__ = (
        Index("ix_ticker_timestamp", "ticker", "timestamp"),
    )