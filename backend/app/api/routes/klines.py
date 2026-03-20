from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas.klines import CollectKlinesRequest, CollectKlinesResponse
from app.services.klines import KlinesService


router = APIRouter(prefix="/klines", tags=["klines"])


@router.post("/import", response_model=CollectKlinesResponse)
async def import_klines(
    collect_klines_request: CollectKlinesRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> CollectKlinesResponse:
    """Import historical klines (candles) from the exchange API into the database."""
    return await KlinesService.collect(
        session=session,
        collect_klines_request=collect_klines_request,
    )
