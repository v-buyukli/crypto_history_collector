import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app import task_store
from app.api.routes import klines, symbols


logger = logging.getLogger(__name__)

CLEANUP_INTERVAL_SECONDS = 3600  # run cleanup every hour


async def _cleanup_loop() -> None:
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
        removed = task_store.cleanup_expired()
        if removed:
            logger.info("Task cleanup: removed %d expired tasks", removed)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_cleanup_loop())
    yield
    task.cancel()


app = FastAPI(
    title="Crypto History Collector",
    version="0.1.0",
    description="FastAPI application for collecting historical crypto exchange data.",
    lifespan=lifespan,
)

# Include API routes
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(symbols.router)
api_router.include_router(klines.router)
app.include_router(api_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Crypto History Collector API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
