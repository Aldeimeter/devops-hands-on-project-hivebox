from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models.temperature import TemperatureResponse
from app.services.opensensemap import OpenSenseMapService

router = APIRouter()


@router.get("/temperature", response_model=TemperatureResponse)
def get_temperature():
    """
    Get average temperature from all configured senseBoxes.
    Only includes data from the last hour.
    """
    # Check if boxes are configured
    if not settings.sensebox_ids:
        raise HTTPException(
            status_code=503,
            detail="No senseBox IDs configured. Please check sensebox_ids.txt file.",
        )

    # Fetch and calculate average temperature
    service = OpenSenseMapService(settings.sensebox_ids)
    return service.get_average_temperature()
