from pydantic import BaseModel, Field

from app.enums import ExchangeEnum, MarketTypeEnum, QuoteAssetEnum


class SymbolsRequest(BaseModel):
    """Request parameters for getting active symbols."""

    exchange: ExchangeEnum = Field(
        default=ExchangeEnum.BINANCE, description="Exchange name"
    )
    market_type: MarketTypeEnum = Field(
        default=MarketTypeEnum.FUTURES, description="Market type"
    )
    quote_asset: QuoteAssetEnum = Field(
        default=QuoteAssetEnum.USDT, description="Quote asset filter"
    )


class SymbolsResponse(BaseModel):
    """Response with list of active symbols."""

    exchange: ExchangeEnum = Field(..., description="Exchange name")
    market_type: MarketTypeEnum = Field(..., description="Market type")
    quote_asset: QuoteAssetEnum = Field(..., description="Quote asset filter")
    symbols: list[str] = Field(..., description="List of active symbol names")
    count: int = Field(..., description="Number of symbols returned")


class UpdateSymbolsResponse(BaseModel):
    """Response with update statistics."""

    exchange: ExchangeEnum
    market_type: MarketTypeEnum
    quote_asset: QuoteAssetEnum
    total_active: int
    added: int
    activated: int
    deactivated: int
