from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.mappers import EXCHANGE_CLIENTS
from app.repositories.klines import KlinesRepository
from app.schemas.klines import CollectKlinesRequest, CollectKlinesResponse


router = APIRouter(prefix="/api/klines", tags=["klines"])


@router.post("/collect", response_model=CollectKlinesResponse)
async def collect_klines(
    body: CollectKlinesRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> CollectKlinesResponse:
    """Fetch candles from exchange API and save to database."""
    exchange_symbol_id = await KlinesRepository.resolve_exchange_symbol_id(
        session=session,
        exchange=body.exchange,
        market_type=body.market_type,
        symbol_name=body.symbol,
    )
    if exchange_symbol_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol '{body.symbol}' not found or inactive for "
            f"{body.exchange}/{body.market_type}",
        )

    client_class = EXCHANGE_CLIENTS[body.exchange]
    client = client_class()

    try:
        klines = await client.get_klines(
            symbol=body.symbol,
            timeframe=body.timeframe,
            start_time=body.start_time,
            end_time=body.end_time,
            market_type=body.market_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch klines from exchange: {str(e)}",
        )

    inserted = await KlinesRepository.save_klines(
        session=session,
        exchange_symbol_id=exchange_symbol_id,
        timeframe=body.timeframe,
        klines=klines,
    )

    return CollectKlinesResponse(
        exchange=body.exchange,
        market_type=body.market_type,
        symbol=body.symbol,
        timeframe=body.timeframe,
        fetched=len(klines),
        inserted=inserted,
    )
