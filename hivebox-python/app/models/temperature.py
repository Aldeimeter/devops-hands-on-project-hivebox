from pydantic import BaseModel


class ExcludedReason(BaseModel):
    """Model for excluded box reasoning"""

    box_id: str
    reason: str
    last_measurement: str | None = None


class Statistics(BaseModel):
    """Statistics about temperature data collection"""

    boxes_checked: int
    valid_readings: int
    excluded_boxes: int


class TemperatureResponse(BaseModel):
    """Response model for /temperature endpoint"""

    average_temperature: float | None
    unit: str = "°C"
    timestamp: str
    statistics: Statistics
    excluded_reasons: list[ExcludedReason]
