from pydantic import BaseModel, Field

from app.enums import ExchangeEnum, MarketTypeEnum, QuoteAssetEnum


class SymbolsRequest(BaseModel):
    """Request parameters for getting symbols."""

    exchange: ExchangeEnum = Field(
        default=ExchangeEnum.BINANCE, description="Exchange name"
    )
    market_type: MarketTypeEnum = Field(
        default=MarketTypeEnum.FUTURES, description="Market type"
    )
    quote_asset: QuoteAssetEnum = Field(
        default=QuoteAssetEnum.USDT, description="Quote asset filter"
    )
    is_active: bool | None = Field(
        default=None,
        description="Filter by active/inactive symbols. None - all symbols",
    )
    limit: int = Field(
        default=500, ge=1, le=5000, description="Max number of symbols to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of symbols to skip")


class SymbolsResponse(BaseModel):
    """Response with list of symbols."""

    exchange: ExchangeEnum = Field(..., description="Exchange name")
    market_type: MarketTypeEnum = Field(..., description="Market type")
    quote_asset: QuoteAssetEnum = Field(..., description="Quote asset filter")
    is_active: bool | None = Field(
        ..., description="Active/inactive filter applied. None - all"
    )
    symbols: list[str] = Field(..., description="List of symbol names")
    count: int = Field(..., description="Number of symbols returned")
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")


class SyncSymbolsRequest(BaseModel):
    """Request parameters for syncing symbols from exchange."""

    exchange: ExchangeEnum = Field(
        default=ExchangeEnum.BINANCE, description="Exchange name"
    )
    market_type: MarketTypeEnum = Field(
        default=MarketTypeEnum.FUTURES, description="Market type"
    )
    quote_asset: QuoteAssetEnum = Field(
        default=QuoteAssetEnum.USDT, description="Quote asset filter"
    )


class UpdateSymbolsResponse(BaseModel):
    """Response with update statistics."""

    exchange: ExchangeEnum
    market_type: MarketTypeEnum
    quote_asset: QuoteAssetEnum
    total_active: int
    added: int
    activated: int
    deactivated: int
