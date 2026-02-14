from datetime import datetime, timezone

from pydantic import BaseModel, field_validator, model_validator

from app.enums import ExchangeEnum, MarketTypeEnum, TimeframeEnum


class CollectKlinesRequest(BaseModel):
    exchange: ExchangeEnum = ExchangeEnum.BINANCE
    market_type: MarketTypeEnum = MarketTypeEnum.FUTURES
    symbol: str
    timeframe: TimeframeEnum = TimeframeEnum.h1
    start_time: datetime
    end_time: datetime | None = None

    @field_validator("start_time", "end_time", mode="after")
    @classmethod
    def strip_timezone(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v

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
