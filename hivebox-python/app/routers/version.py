from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/version")
def get_version():
    return {"version": settings.app_version}
