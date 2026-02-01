import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.routes import base


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto History Collector",
    version="0.1.0",
    description="FastAPI application for collecting historical crypto exchange data.",
)

# Mount static files
static_path = Path(__file__).parent / "ui" / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include API routes
app.include_router(base.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Crypto History Collector API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "/api/status",
    }
