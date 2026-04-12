from pydantic import BaseModel, Field

from app.enums import ExchangeEnum, MarketTypeEnum, QuoteAssetEnum


class ExchangeMarketBase(BaseModel):
    exchange: ExchangeEnum = Field(
        default=ExchangeEnum.BINANCE, description="Exchange name"
    )
    market_type: MarketTypeEnum = Field(
        default=MarketTypeEnum.FUTURES, description="Market type"
    )


class ExchangeMarketQuoteBase(ExchangeMarketBase):
    quote_asset: QuoteAssetEnum = Field(
        default=QuoteAssetEnum.USDT, description="Quote asset"
    )


class PaginationRequest(BaseModel):
    limit: int = Field(
        default=500, ge=1, le=5000, description="Max number of items to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
