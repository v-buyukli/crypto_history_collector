from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas.symbols import SymbolsRequest, SymbolsResponse, UpdateSymbolsResponse
from app.services.symbols import SymbolsService


router = APIRouter(prefix="/api/symbols", tags=["symbols"])


@router.get("/", response_model=SymbolsResponse)
async def get_symbols(
    symbols_request: Annotated[SymbolsRequest, Query()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> SymbolsResponse:
    """Get list of active trading symbols from database."""
    return await SymbolsService.get_active(
        session=session,
        symbols_request=symbols_request,
    )


@router.post("/update", response_model=UpdateSymbolsResponse)
async def update_symbols(
    symbols_request: SymbolsRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UpdateSymbolsResponse:
    """Fetch symbols from exchange API and update database."""
    return await SymbolsService.update(
        session=session,
        symbols_request=symbols_request,
    )
