from datetime import datetime

from app.enums import ImportTaskStatusEnum, TimeframeEnum
from app.schemas.common import ExchangeMarketBase


class ImportTaskResponse(ExchangeMarketBase):
    id: str
    status: ImportTaskStatusEnum
    symbol: str
    timeframe: TimeframeEnum
    start_time: datetime
    end_time: datetime | None = None
    fetched: int | None = None
    inserted: int | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
