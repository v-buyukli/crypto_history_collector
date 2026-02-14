from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.klines import KlinesRepository
from app.schemas.klines import CollectKlinesRequest, CollectKlinesResponse
from app.services.mappers import EXCHANGE_CLIENTS


class KlinesService:

    @staticmethod
    async def collect(
        session: AsyncSession,
        collect_klines_request: CollectKlinesRequest,
    ) -> CollectKlinesResponse:
        exchange_symbol_id = await KlinesRepository.resolve_exchange_symbol_id(
            session=session,
            exchange=collect_klines_request.exchange,
            market_type=collect_klines_request.market_type,
            symbol_name=collect_klines_request.symbol,
        )
        if exchange_symbol_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Symbol '{collect_klines_request.symbol}' not found or inactive for "
                f"{collect_klines_request.exchange}/{collect_klines_request.market_type}",
            )

        client = EXCHANGE_CLIENTS[collect_klines_request.exchange]()

        total_fetched = 0
        total_inserted = 0

        try:
            async for batch in client.get_klines(
                symbol=collect_klines_request.symbol,
                timeframe=collect_klines_request.timeframe,
                start_time=collect_klines_request.start_time,
                end_time=collect_klines_request.end_time,
                market_type=collect_klines_request.market_type,
            ):
                inserted = await KlinesRepository.save_klines(
                    session=session,
                    exchange_symbol_id=exchange_symbol_id,
                    timeframe=collect_klines_request.timeframe,
                    klines=batch,
                )
                total_fetched += len(batch)
                total_inserted += inserted
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch klines from exchange: {e}",
            )

        return CollectKlinesResponse(
            exchange=collect_klines_request.exchange,
            market_type=collect_klines_request.market_type,
            symbol=collect_klines_request.symbol,
            timeframe=collect_klines_request.timeframe,
            fetched=total_fetched,
            inserted=total_inserted,
        )
