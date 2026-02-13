from datetime import datetime

from pydantic import BaseModel, model_validator

from app.enums import ExchangeEnum, MarketTypeEnum, TimeframeEnum


class CollectKlinesRequest(BaseModel):
    exchange: ExchangeEnum = ExchangeEnum.BINANCE
    market_type: MarketTypeEnum = MarketTypeEnum.FUTURES
    symbol: str
    timeframe: TimeframeEnum = TimeframeEnum.h1
    start_time: datetime
    end_time: datetime | None = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time is not None and self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class CollectKlinesResponse(BaseModel):
    exchange: ExchangeEnum
    market_type: MarketTypeEnum
    symbol: str
    timeframe: TimeframeEnum
    fetched: int
    inserted: int
