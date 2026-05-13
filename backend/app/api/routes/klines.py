from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import task_store
from app.db import get_async_session
from app.schemas.klines import CollectKlinesRequest
from app.schemas.tasks import ImportTaskResponse
from app.services.klines import KlinesService


router = APIRouter(prefix="/klines", tags=["klines"])


@router.post(
    "/import",
    status_code=202,
    response_model=ImportTaskResponse,
    response_model_exclude_none=True,
)
async def import_klines(
    collect_klines_request: CollectKlinesRequest,
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ImportTaskResponse:
    """Import historical klines (candles) from the exchange API into the database."""

    task = await KlinesService.start_import(session, collect_klines_request)
    background_tasks.add_task(
        KlinesService._run_import, task.id, collect_klines_request
    )

    return task


@router.get(
    "/tasks/{task_id}",
    response_model=ImportTaskResponse,
    response_model_exclude_none=True,
)
async def get_import_task(task_id: str) -> ImportTaskResponse:
    """Get the status of a klines import task."""

    task = task_store.get_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return task
