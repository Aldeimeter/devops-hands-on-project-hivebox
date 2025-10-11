"""Version endpoint router."""
from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/version")
def get_version():
    """Get the current application version."""
    return {"version": settings.app_version}
