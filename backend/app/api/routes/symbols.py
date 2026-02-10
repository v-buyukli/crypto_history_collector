from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.mappers import EXCHANGE_CLIENTS
from app.repositories.symbols import SymbolsRepository
from app.schemas.symbols import SymbolsRequest, SymbolsResponse, UpdateSymbolsResponse


router = APIRouter(prefix="/api/symbols", tags=["symbols"])


@router.get("/", response_model=SymbolsResponse)
async def get_symbols(
    params: Annotated[SymbolsRequest, Query()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> SymbolsResponse:
    """Get list of active trading symbols from database."""
    try:
        symbols = await SymbolsRepository.get_active_symbols(
            session=session,
            exchange=params.exchange,
            market_type=params.market_type,
            quote_asset=params.quote_asset,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch symbols: {str(e)}",
        )

    return SymbolsResponse(
        exchange=params.exchange,
        market_type=params.market_type,
        quote_asset=params.quote_asset,
        symbols=symbols,
        count=len(symbols),
    )


@router.post("/update", response_model=UpdateSymbolsResponse)
async def update_symbols(
    params: SymbolsRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UpdateSymbolsResponse:
    """Fetch symbols from exchange API and update database."""
    if params.exchange not in EXCHANGE_CLIENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported exchange: {params.exchange}",
        )

    client_class = EXCHANGE_CLIENTS[params.exchange]

    try:
        current_symbols = await client_class.get_active_symbols(
            market_type=params.market_type,
            quote_asset=params.quote_asset,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch symbols from exchange: {str(e)}",
        )

    try:
        stats = await SymbolsRepository.update_symbols(
            session=session,
            exchange=params.exchange,
            market_type=params.market_type,
            current_symbols=current_symbols,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update symbols in database: {str(e)}",
        )

    return UpdateSymbolsResponse(
        exchange=params.exchange,
        market_type=params.market_type,
        quote_asset=params.quote_asset,
        **stats,
    )
