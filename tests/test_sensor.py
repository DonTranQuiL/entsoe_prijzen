import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from homeassistant.const import EntityCategory
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.entsoe_prijzen.const import DOMAIN
from custom_components.entsoe_prijzen.sensor import (
    EntsoeCurrentPriceSensor,
    EntsoeLastUpdateSensor,
    EntsoeLastUpdateStatusSensor,
    EntsoeConsecutiveErrorsSensor,
)


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()

    # We will simulate the current time as 2026-05-19 12:30:00 UTC
    coordinator.data = [
        {"timestamp_utc": "2026-05-19T11:00:00+00:00", "price_kwh": 0.15000},
        {
            "timestamp_utc": "2026-05-19T12:00:00+00:00",
            "price_kwh": 0.18000,
        },  # Current block
        {"timestamp_utc": "2026-05-19T13:00:00+00:00", "price_kwh": 0.20000},
    ]
    coordinator.last_update_success_timestamp = "2026-05-19T12:05:00+00:00"
    coordinator.error_count = 0
    return coordinator


@pytest.fixture
def mock_entry():
    return MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry_id",
        data={"domain_id": "10YNL----------L"},
    )


def test_current_price_sensor(mock_coordinator, mock_entry):
    """Test the current price sensor logic correctly picks the active time block."""
    sensor = EntsoeCurrentPriceSensor(mock_coordinator, "10YNL----------L", "NL")

    assert sensor.unique_id == "entsoe_10ynl----------l_current_price"
    assert sensor.icon == "mdi:flash"
    assert sensor.native_unit_of_measurement == "EUR/kWh"

    # Mock time so it falls exactly in the middle of our 12:00 block
    mock_now = datetime(2026, 5, 19, 12, 30, tzinfo=timezone.utc)

    with patch(
        "custom_components.entsoe_prijzen.sensor.dt_util.utcnow", return_value=mock_now
    ):
        # Should pick the 12:00 block (0.18000)
        assert sensor.state == 0.18000

    # Ensure attributes output the full data structure for markdown graphs
    assert "all_prices" in sensor.extra_state_attributes
    assert len(sensor.extra_state_attributes["all_prices"]) == 3


def test_current_price_sensor_no_data(mock_coordinator, mock_entry):
    """Test current price sensor gracefully handles empty API responses."""
    mock_coordinator.data = []
    sensor = EntsoeCurrentPriceSensor(mock_coordinator, "10YNL----------L", "NL")

    assert sensor.state is None
    assert sensor.extra_state_attributes == {}


def test_last_update_sensor(mock_coordinator, mock_entry):
    """Test diagnostic sensor outputting the timestamp of last successful API pull."""
    sensor = EntsoeLastUpdateSensor(mock_coordinator, "10YNL----------L", "NL")

    assert sensor.unique_id == "entsoe_10ynl----------l_last_update"
    assert sensor.entity_category == EntityCategory.DIAGNOSTIC
    assert sensor.state == "2026-05-19T12:05:00+00:00"


def test_status_sensor(mock_coordinator, mock_entry):
    """Test diagnostic sensor reporting OK vs Error states."""
    sensor = EntsoeLastUpdateStatusSensor(mock_coordinator, "10YNL----------L", "NL")
    assert sensor.state == "Success"

    mock_coordinator.error_count = 2
    assert sensor.state == "Error"


def test_error_count_sensor(mock_coordinator, mock_entry):
    """Test diagnostic sensor reporting raw error integer."""
    sensor = EntsoeConsecutiveErrorsSensor(mock_coordinator, "10YNL----------L", "NL")
    assert sensor.state == 0

    mock_coordinator.error_count = 5
    assert sensor.state == 5
