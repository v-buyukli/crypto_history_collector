from fastapi import APIRouter


router = APIRouter(prefix="/api", tags=["Base"])


@router.get("/status")
async def get_status():
    """Return basic service health information."""
    return {"status": "ok"}
