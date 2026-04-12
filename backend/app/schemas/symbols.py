from pydantic import BaseModel, Field

from app.enums import ExchangeEnum, MarketTypeEnum, QuoteAssetEnum
from app.schemas.common import ExchangeMarketQuoteBase, PaginationRequest


class SyncSymbolsRequest(ExchangeMarketQuoteBase):
    """Request parameters for syncing symbols from exchange."""


class SymbolsRequest(ExchangeMarketQuoteBase, PaginationRequest):
    """Request parameters for getting symbols."""

    is_active: bool | None = Field(
        default=None,
        description="Filter by active/inactive symbols. None - all symbols",
    )


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


class UpdateSymbolsResponse(ExchangeMarketQuoteBase):
    """Response with update statistics."""

    total_active: int
    added: int
    activated: int
    deactivated: int
