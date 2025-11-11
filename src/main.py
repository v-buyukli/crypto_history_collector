from fastapi import FastAPI

from src.api.routes import base

app = FastAPI(
    title="Crypto History Collector",
    version="0.1.0",
    description="FastAPI application for collecting historical crypto exchange data.",
)

app.include_router(base.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint to verify that the API is running."""
    return {"message": "Crypto History Collector is running"}
