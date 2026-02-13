import logging

from fastapi import FastAPI

from app.api.routes import klines, symbols


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto History Collector",
    version="0.1.0",
    description="FastAPI application for collecting historical crypto exchange data.",
)

# Include API routes
app.include_router(symbols.router)
app.include_router(klines.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Crypto History Collector API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "/api/status",
    }
