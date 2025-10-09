from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    from main import app

    return TestClient(app)


@pytest.fixture
def mock_sensebox_response():
    """Factory fixture to create mock senseBox API responses"""

    def _create_response(
        box_id: str,
        temperature_value: float | None,
        timestamp: datetime | None = None,
        sensor_title: str = "Temperatur",
    ):
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        sensors = []
        if sensor_title:
            sensors.append(
                {
                    "title": sensor_title,
                    "unit": "°C",
                    "sensorType": "BME280",
                    "icon": "osem-thermometer",
                    "_id": f"{box_id}_sensor",
                    "lastMeasurement": {
                        "createdAt": timestamp.isoformat(),
                        "value": str(temperature_value) if temperature_value is not None else None,
                    }
                    if temperature_value is not None or timestamp
                    else None,
                }
            )

        return {
            "_id": box_id,
            "name": f"TestBox {box_id}",
            "sensors": sensors,
        }

    return _create_response


# =============================================================================
# 1. Happy Path Tests
# =============================================================================


class TestTemperatureEndpointHappyPath:
    """Test cases for successful temperature endpoint responses"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_endpoint_returns_200_with_valid_data(
        self, mock_get, client, mock_sensebox_response
    ):
        """All boxes have valid temperature readings within 1 hour"""
        # Mock config with 3 boxes
        with patch("app.config.settings.sensebox_ids", ["box1", "box2", "box3"]):
            # Mock API responses
            mock_get.side_effect = [
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box1", 20.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box2", 22.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box3", 24.0),
                ),
            ]

            response = client.get("/temperature")

            assert response.status_code == 200
            assert "average_temperature" in response.json()
            assert response.json()["average_temperature"] == 22.0

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_response_structure(
        self, mock_get, client, mock_sensebox_response
    ):
        """Validates response has all required fields"""
        with patch("app.config.settings.sensebox_ids", ["box1"]):
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_sensebox_response("box1", 23.5),
            )

            response = client.get("/temperature")
            data = response.json()

            # Check all required fields exist
            assert "average_temperature" in data
            assert "unit" in data
            assert "timestamp" in data
            assert "statistics" in data
            assert "excluded_reasons" in data

            # Validate field types and values
            assert data["unit"] == "°C"
            assert isinstance(data["timestamp"], str)
            assert "statistics" in data
            assert "boxes_checked" in data["statistics"]
            assert "valid_readings" in data["statistics"]
            assert "excluded_boxes" in data["statistics"]


# =============================================================================
# 2. Data Freshness Tests
# =============================================================================


class TestTemperatureDataFreshness:
    """Test cases for 1-hour data freshness validation"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_excludes_data_older_than_1_hour(
        self, mock_get, client, mock_sensebox_response
    ):
        """Data from 2 hours ago should be excluded"""
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=2)

        with patch("app.config.settings.sensebox_ids", ["box1", "box2"]):
            mock_get.side_effect = [
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box1", 20.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response(
                        "box2", 25.0, timestamp=old_timestamp
                    ),
                ),
            ]

            response = client.get("/temperature")
            data = response.json()

            # Should only include box1
            assert data["average_temperature"] == 20.0
            assert data["statistics"]["valid_readings"] == 1
            assert data["statistics"]["excluded_boxes"] == 1
            assert len(data["excluded_reasons"]) == 1
            assert data["excluded_reasons"][0]["reason"] == "data_too_old"

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_includes_data_at_boundary(
        self, mock_get, client, mock_sensebox_response
    ):
        """Data exactly 59 minutes old should be included"""
        boundary_timestamp = datetime.now(timezone.utc) - timedelta(minutes=59)

        with patch("app.config.settings.sensebox_ids", ["box1"]):
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_sensebox_response(
                    "box1", 21.5, timestamp=boundary_timestamp
                ),
            )

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] == 21.5
            assert data["statistics"]["valid_readings"] == 1
            assert data["statistics"]["excluded_boxes"] == 0

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_excludes_data_just_over_boundary(
        self, mock_get, client, mock_sensebox_response
    ):
        """Data 61 minutes old should be excluded"""
        over_boundary = datetime.now(timezone.utc) - timedelta(minutes=61)

        with patch("app.config.settings.sensebox_ids", ["box1"]):
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_sensebox_response(
                    "box1", 21.5, timestamp=over_boundary
                ),
            )

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] is None
            assert data["statistics"]["valid_readings"] == 0
            assert data["statistics"]["excluded_boxes"] == 1


# =============================================================================
# 3. Sensor Identification Tests
# =============================================================================


class TestTemperatureSensorIdentification:
    """Test cases for identifying temperature sensors"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_sensor_identified_by_temperatur_title(
        self, mock_get, client, mock_sensebox_response
    ):
        """Sensor with title 'Temperatur' should be identified"""
        with patch("app.config.settings.sensebox_ids", ["box1"]):
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_sensebox_response(
                    "box1", 22.5, sensor_title="Temperatur"
                ),
            )

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] == 22.5
            assert data["statistics"]["valid_readings"] == 1

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_no_sensor_found(
        self, mock_get, client, mock_sensebox_response
    ):
        """Box with no temperature sensor should be excluded"""
        with patch("app.config.settings.sensebox_ids", ["box1"]):
            # Create response with no Temperatur sensor
            mock_response = {
                "_id": "box1",
                "name": "TestBox box1",
                "sensors": [
                    {
                        "title": "Luftfeuchte",
                        "unit": "%",
                        "sensorType": "BME280",
                        "_id": "box1_sensor",
                        "lastMeasurement": {
                            "createdAt": datetime.now(timezone.utc).isoformat(),
                            "value": "65",
                        },
                    }
                ],
            }
            mock_get.return_value = Mock(status_code=200, json=lambda: mock_response)

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] is None
            assert data["statistics"]["valid_readings"] == 0
            assert data["statistics"]["excluded_boxes"] == 1
            assert data["excluded_reasons"][0]["reason"] == "no_temperature_sensor"


# =============================================================================
# 4. Data Validation Tests
# =============================================================================


class TestTemperatureDataValidation:
    """Test cases for validating temperature data"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_excludes_null_values(
        self, mock_get, client, mock_sensebox_response
    ):
        """Sensor with null temperature value should be excluded"""
        with patch("app.config.settings.sensebox_ids", ["box1"]):
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_sensebox_response("box1", None),
            )

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] is None
            assert data["statistics"]["valid_readings"] == 0
            assert data["statistics"]["excluded_boxes"] == 1
            assert data["excluded_reasons"][0]["reason"] == "null_value"

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_excludes_missing_measurement(self, mock_get, client):
        """Box with no lastMeasurement field should be excluded"""
        with patch("app.config.settings.sensebox_ids", ["box1"]):
            mock_response = {
                "_id": "box1",
                "name": "TestBox box1",
                "sensors": [
                    {
                        "title": "Temperatur",
                        "unit": "°C",
                        "sensorType": "BME280",
                        "_id": "box1_sensor",
                        # No lastMeasurement field
                    }
                ],
            }
            mock_get.return_value = Mock(status_code=200, json=lambda: mock_response)

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] is None
            assert data["statistics"]["valid_readings"] == 0
            assert data["statistics"]["excluded_boxes"] == 1
            assert data["excluded_reasons"][0]["reason"] == "no_measurement"


# =============================================================================
# 5. Multiple Boxes Scenarios
# =============================================================================


class TestTemperatureMultipleBoxes:
    """Test cases for handling multiple senseBoxes"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_calculates_average_from_multiple_boxes(
        self, mock_get, client, mock_sensebox_response
    ):
        """Calculate average from 3 valid boxes"""
        with patch("app.config.settings.sensebox_ids", ["box1", "box2", "box3"]):
            mock_get.side_effect = [
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box1", 20.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box2", 22.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box3", 24.0),
                ),
            ]

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] == 22.0
            assert data["statistics"]["boxes_checked"] == 3
            assert data["statistics"]["valid_readings"] == 3
            assert data["statistics"]["excluded_boxes"] == 0

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_partial_valid_readings(
        self, mock_get, client, mock_sensebox_response
    ):
        """2 valid boxes, 1 with old data"""
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=2)

        with patch("app.config.settings.sensebox_ids", ["box1", "box2", "box3"]):
            mock_get.side_effect = [
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box1", 20.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box2", 24.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response(
                        "box3", 30.0, timestamp=old_timestamp
                    ),
                ),
            ]

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] == 22.0
            assert data["statistics"]["boxes_checked"] == 3
            assert data["statistics"]["valid_readings"] == 2
            assert data["statistics"]["excluded_boxes"] == 1


# =============================================================================
# 6. Edge Cases
# =============================================================================


class TestTemperatureEdgeCases:
    """Test cases for edge scenarios"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_single_valid_reading(
        self, mock_get, client, mock_sensebox_response
    ):
        """Only 1 box has valid data"""
        with patch("app.config.settings.sensebox_ids", ["box1"]):
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_sensebox_response("box1", 25.5),
            )

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] == 25.5
            assert data["statistics"]["valid_readings"] == 1

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_no_valid_readings(
        self, mock_get, client, mock_sensebox_response
    ):
        """All boxes have stale data"""
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=3)

        with patch("app.config.settings.sensebox_ids", ["box1", "box2"]):
            mock_get.side_effect = [
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response(
                        "box1", 20.0, timestamp=old_timestamp
                    ),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response(
                        "box2", 22.0, timestamp=old_timestamp
                    ),
                ),
            ]

            response = client.get("/temperature")
            data = response.json()

            assert response.status_code == 200
            assert data["average_temperature"] is None
            assert data["statistics"]["valid_readings"] == 0
            assert data["statistics"]["excluded_boxes"] == 2

    def test_temperature_empty_sensebox_ids_file(self, client):
        """No boxes configured"""
        with patch("app.config.settings.sensebox_ids", []):
            response = client.get("/temperature")

            assert response.status_code == 503


# =============================================================================
# 7. API Failure Handling Tests
# =============================================================================


class TestTemperatureAPIFailures:
    """Test cases for handling OpenSenseMap API failures"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_handles_api_request_failure(
        self, mock_get, client, mock_sensebox_response
    ):
        """One box API call fails, others still processed"""
        with patch("app.config.settings.sensebox_ids", ["box1", "box2"]):
            mock_get.side_effect = [
                Mock(status_code=500),  # API failure
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box2", 22.0),
                ),
            ]

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] == 22.0
            assert data["statistics"]["valid_readings"] == 1
            assert data["statistics"]["excluded_boxes"] == 1
            assert data["excluded_reasons"][0]["reason"] == "api_failure"

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_handles_invalid_box_id(
        self, mock_get, client, mock_sensebox_response
    ):
        """API returns 404 for invalid box ID"""
        with patch("app.config.settings.sensebox_ids", ["invalid_box", "box2"]):
            mock_get.side_effect = [
                Mock(status_code=404),  # Box not found
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box2", 23.0),
                ),
            ]

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] == 23.0
            assert data["statistics"]["valid_readings"] == 1
            assert data["statistics"]["excluded_boxes"] == 1
            assert data["excluded_reasons"][0]["reason"] == "box_not_found"

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_all_api_calls_fail(self, mock_get, client):
        """All box API calls fail"""
        with patch("app.config.settings.sensebox_ids", ["box1", "box2"]):
            mock_get.side_effect = [
                Mock(status_code=500),
                Mock(status_code=500),
            ]

            response = client.get("/temperature")
            data = response.json()

            assert response.status_code == 200
            assert data["average_temperature"] is None
            assert data["statistics"]["valid_readings"] == 0
            assert data["statistics"]["excluded_boxes"] == 2


# =============================================================================
# 8. Calculation Precision Tests
# =============================================================================


class TestTemperatureCalculations:
    """Test cases for temperature calculation precision"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_average_rounding(
        self, mock_get, client, mock_sensebox_response
    ):
        """Test decimal precision in average calculation"""
        with patch("app.config.settings.sensebox_ids", ["box1", "box2", "box3"]):
            mock_get.side_effect = [
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box1", 20.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box2", 21.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box3", 22.0),
                ),
            ]

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] == 21.0

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_handles_extreme_values(
        self, mock_get, client, mock_sensebox_response
    ):
        """Test with extreme temperature values"""
        with patch("app.config.settings.sensebox_ids", ["box1", "box2"]):
            mock_get.side_effect = [
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box1", -40.0),
                ),
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box2", 50.0),
                ),
            ]

            response = client.get("/temperature")
            data = response.json()

            assert data["average_temperature"] == 5.0


# =============================================================================
# 9. Statistics Accuracy Tests
# =============================================================================


class TestTemperatureStatistics:
    """Test cases for statistics accuracy"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_statistics_counts_accurate(
        self, mock_get, client, mock_sensebox_response
    ):
        """Verify statistics counts match reality"""
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=2)

        with patch("app.config.settings.sensebox_ids", ["box1", "box2", "box3"]):
            mock_get.side_effect = [
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response("box1", 20.0),
                ),
                Mock(status_code=404),  # Invalid box
                Mock(
                    status_code=200,
                    json=lambda: mock_sensebox_response(
                        "box3", 22.0, timestamp=old_timestamp
                    ),
                ),
            ]

            response = client.get("/temperature")
            data = response.json()

            stats = data["statistics"]
            assert stats["boxes_checked"] == 3
            assert stats["valid_readings"] == 1
            assert stats["excluded_boxes"] == 2
            assert (
                stats["valid_readings"] + stats["excluded_boxes"]
                == stats["boxes_checked"]
            )
            assert len(data["excluded_reasons"]) == stats["excluded_boxes"]


# =============================================================================
# 10. Timestamp Tests
# =============================================================================


class TestTemperatureTimestamp:
    """Test cases for response timestamp validation"""

    @patch("app.services.opensensemap.httpx.get")
    def test_temperature_timestamp_is_current(
        self, mock_get, client, mock_sensebox_response
    ):
        """Verify response timestamp is current server time"""
        with patch("app.config.settings.sensebox_ids", ["box1"]):
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_sensebox_response("box1", 21.0),
            )

            before = datetime.now(timezone.utc)
            response = client.get("/temperature")
            after = datetime.now(timezone.utc)

            data = response.json()
            timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

            # Timestamp should be between before and after request
            assert before <= timestamp <= after

            # Verify ISO 8601 format with timezone
            assert "T" in data["timestamp"]
            assert data["timestamp"].endswith("Z") or "+" in data["timestamp"]
