"""In-memory store for import task state.

Tasks are lost on server restart — acceptable for a personal tool.
Completed tasks are auto-cleaned after TASK_TTL_HOURS.
"""

import uuid
from datetime import UTC, datetime, timedelta

from app.enums import ImportTaskStatusEnum
from app.schemas.klines import CollectKlinesRequest
from app.schemas.tasks import ImportTaskResponse


_tasks: dict[str, ImportTaskResponse] = {}


def create_task(request: CollectKlinesRequest) -> ImportTaskResponse:
    task = ImportTaskResponse(
        id=str(uuid.uuid4()),
        status=ImportTaskStatusEnum.PENDING,
        exchange=request.exchange,
        market_type=request.market_type,
        symbol=request.symbol,
        timeframe=request.timeframe,
        start_time=request.start_time,
        end_time=request.end_time,
        fetched=None,
        inserted=None,
        error=None,
        created_at=datetime.now(UTC),
        started_at=None,
        finished_at=None,
    )
    _tasks[task.id] = task
    return task


def get_task(task_id: str) -> ImportTaskResponse | None:
    return _tasks.get(task_id)


def update_task(task_id: str, **kwargs) -> None:
    _tasks[task_id] = _tasks[task_id].model_copy(update=kwargs)


TASK_TTL_HOURS = 24


def cleanup_expired(ttl_hours: int = TASK_TTL_HOURS) -> int:
    """Remove tasks older than ttl_hours. Returns number of removed tasks."""
    cutoff = datetime.now(UTC) - timedelta(hours=ttl_hours)
    expired = [task_id for task_id, task in _tasks.items() if task.created_at < cutoff]
    for task_id in expired:
        del _tasks[task_id]
    return len(expired)
