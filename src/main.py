from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import base

app = FastAPI(
    title="Crypto History Collector",
    version="0.1.0",
    description="FastAPI application for collecting historical crypto exchange data.",
)

# Mount static files
static_path = Path(__file__).parent / "static"
templates_path = Path(__file__).parent / "templates"

app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

app.include_router(base.router)


@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    """Root endpoint serving the main HTML page."""
    index_file = templates_path / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
