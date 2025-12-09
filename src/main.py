"""FastAPI application with embedded Streamlit."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template

from src.api.routes import base
from src.config import settings
from src.ui import StreamlitManager

logger = logging.getLogger(__name__)

# Initialize Streamlit manager
streamlit_manager = StreamlitManager(
    port=settings.STREAMLIT_PORT, host=settings.STREAMLIT_HOST
)

# Cache wrapper template to avoid repeated file reads
_wrapper_template: Template | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: startup and shutdown."""
    global _wrapper_template

    # Startup: start Streamlit subprocess
    logger.info("Starting Streamlit subprocess...")
    streamlit_manager.start()

    # Load and cache wrapper template
    logger.info("Loading wrapper template...")
    try:
        templates_path = Path(__file__).parent / "ui" / "templates"
        wrapper_file = templates_path / "streamlit_wrapper.html"

        if not wrapper_file.exists():
            raise FileNotFoundError(f"Template file not found: {wrapper_file}")

        template_content = wrapper_file.read_text(encoding="utf-8")
        _wrapper_template = Template(template_content)
        logger.info("Wrapper template loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load wrapper template: {e}")
        raise

    logger.info("Application startup complete")

    yield

    # Shutdown: gracefully stop Streamlit subprocess
    logger.info("Stopping Streamlit subprocess...")
    await streamlit_manager.stop()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Crypto History Collector",
    version="0.1.0",
    description="FastAPI application for collecting historical crypto exchange data.",
    lifespan=lifespan,
)

# Mount static files
static_path = Path(__file__).parent / "ui" / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include API routes
app.include_router(base.router)


@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root() -> HTMLResponse:
    """Root endpoint serving Streamlit iframe wrapper."""
    if _wrapper_template is None:
        logger.error("Wrapper template not loaded")
        raise RuntimeError("Wrapper template not loaded")

    rendered_html = _wrapper_template.render(streamlit_url=settings.streamlit_url)
    return HTMLResponse(content=rendered_html)
