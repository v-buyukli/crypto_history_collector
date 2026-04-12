from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import task_store
from app.db.session import AsyncSessionLocal
from app.enums import ImportTaskStatusEnum
from app.repositories.klines import KlinesRepository
from app.schemas.klines import CollectKlinesRequest
from app.schemas.tasks import ImportTaskResponse
from app.services.mappers import EXCHANGE_CLIENTS


class KlinesService:

    @staticmethod
    async def start_import(
        session: AsyncSession,
        request: CollectKlinesRequest,
    ) -> ImportTaskResponse:
        """Validate the symbol and create a pending task. Returns task dict."""
        exchange_symbol_id = await KlinesRepository.resolve_exchange_symbol_id(
            session=session,
            exchange=request.exchange,
            market_type=request.market_type,
            symbol_name=request.symbol,
        )
        if exchange_symbol_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Symbol '{request.symbol}' not found or inactive for "
                f"{request.exchange}/{request.market_type}",
            )

        date_range = await KlinesRepository.get_date_range(
            session, exchange_symbol_id, request.timeframe
        )
        if date_range is not None:
            existing_first, existing_last = date_range
            end_time = request.end_time or datetime.now(UTC).replace(tzinfo=None)
            if existing_first <= end_time and existing_last >= request.start_time:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Data already exists for '{request.symbol}' [{request.timeframe}]: "
                        f"first={existing_first:%Y-%m-%d %H:%M}, "
                        f"last={existing_last:%Y-%m-%d %H:%M}. "
                        f"Adjust start_time / end_time."
                    ),
                )

        return task_store.create_task(request)

    @staticmethod
    async def _run_import(task_id: str, request: CollectKlinesRequest) -> None:
        """Background function: fetch klines and save to DB, updating task status."""
        task_store.update_task(
            task_id,
            status=ImportTaskStatusEnum.RUNNING,
            started_at=datetime.now(UTC),
        )

        total_fetched = 0
        total_inserted = 0

        try:
            client = EXCHANGE_CLIENTS[request.exchange]()
            async with AsyncSessionLocal() as session:
                exchange_symbol_id = await KlinesRepository.resolve_exchange_symbol_id(
                    session=session,
                    exchange=request.exchange,
                    market_type=request.market_type,
                    symbol_name=request.symbol,
                )
                if exchange_symbol_id is None:
                    raise ValueError(f"Symbol '{request.symbol}' not found or inactive")

                async for batch in client.get_klines(
                    symbol=request.symbol,
                    timeframe=request.timeframe,
                    start_time=request.start_time,
                    end_time=request.end_time,
                    market_type=request.market_type,
                ):
                    inserted = await KlinesRepository.save_klines(
                        session=session,
                        exchange_symbol_id=exchange_symbol_id,
                        timeframe=request.timeframe,
                        klines=batch,
                    )
                    total_fetched += len(batch)
                    total_inserted += inserted

        except Exception as e:
            task_store.update_task(
                task_id,
                status=ImportTaskStatusEnum.FAILED,
                error=str(e),
                finished_at=datetime.now(UTC),
            )
            return

        task_store.update_task(
            task_id,
            status=ImportTaskStatusEnum.DONE,
            fetched=total_fetched,
            inserted=total_inserted,
            finished_at=datetime.now(UTC),
        )
