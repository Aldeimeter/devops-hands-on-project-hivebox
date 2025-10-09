from datetime import datetime, timedelta, timezone

import httpx

from app.models.temperature import ExcludedReason, Statistics, TemperatureResponse


class OpenSenseMapService:
    """Service for interacting with OpenSenseMap API"""

    BASE_URL = "https://api.opensensemap.org"

    def __init__(self, box_ids: list[str]):
        self.box_ids = box_ids

    def get_average_temperature(self) -> TemperatureResponse:
        """
        Fetch temperature data from all boxes and calculate average.
        Only includes data from the last hour.
        """
        valid_temps: list[float] = []
        excluded: list[ExcludedReason] = []
        boxes_checked = len(self.box_ids)

        for box_id in self.box_ids:
            result = self._fetch_box_temperature(box_id)

            if result["status"] == "valid":
                valid_temps.append(result["temperature"])
            else:
                excluded.append(
                    ExcludedReason(
                        box_id=box_id,
                        reason=result["reason"],
                        last_measurement=result.get("last_measurement"),
                    )
                )

        # Calculate average
        avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else None

        return TemperatureResponse(
            average_temperature=avg_temp,
            unit="°C",
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            statistics=Statistics(
                boxes_checked=boxes_checked,
                valid_readings=len(valid_temps),
                excluded_boxes=len(excluded),
            ),
            excluded_reasons=excluded,
        )

    def _fetch_box_temperature(self, box_id: str) -> dict:
        """
        Fetch temperature for a single box.
        Returns dict with status and data.
        """
        try:
            response = httpx.get(f"{self.BASE_URL}/boxes/{box_id}", timeout=10.0)

            if response.status_code == 404:
                return {"status": "excluded", "reason": "box_not_found"}

            if response.status_code != 200:
                return {"status": "excluded", "reason": "api_failure"}

            data = response.json()
            return self._extract_temperature(data, box_id)

        except Exception:
            return {"status": "excluded", "reason": "api_failure"}

    def _extract_temperature(self, box_data: dict, box_id: str) -> dict:
        """Extract temperature from box data"""
        sensors = box_data.get("sensors", [])

        # Find temperature sensor
        temp_sensor = None
        for sensor in sensors:
            if sensor.get("title") == "Temperatur":
                temp_sensor = sensor
                break

        if not temp_sensor:
            return {"status": "excluded", "reason": "no_temperature_sensor"}

        # Check if measurement exists
        last_measurement = temp_sensor.get("lastMeasurement")
        if not last_measurement:
            return {"status": "excluded", "reason": "no_measurement"}

        # Check if value is null
        value = last_measurement.get("value")
        if value is None:
            return {
                "status": "excluded",
                "reason": "null_value",
                "last_measurement": last_measurement.get("createdAt"),
            }

        # Check data freshness (within 1 hour)
        created_at = last_measurement.get("createdAt")
        if not self._is_data_fresh(created_at):
            return {
                "status": "excluded",
                "reason": "data_too_old",
                "last_measurement": created_at,
            }

        # Valid temperature reading
        return {"status": "valid", "temperature": float(value)}

    def _is_data_fresh(self, timestamp_str: str) -> bool:
        """Check if data is less than 1 hour old"""
        try:
            # Parse ISO 8601 timestamp
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age = now - timestamp

            return age <= timedelta(hours=1)
        except Exception:
            return False
