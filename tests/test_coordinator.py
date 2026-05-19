import pytest
from unittest.mock import AsyncMock, patch, MagicMock, mock_open

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.entsoe_prijzen.const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_DOMAIN_ID,
)
from custom_components.entsoe_prijzen.coordinator import EntsoeCoordinator

# A realistic dummy XML payload to test the parser
VALID_XML_60M = """<?xml version="1.0" encoding="UTF-8"?>
<Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0">
    <TimeSeries>
        <Period>
            <resolution>PT60M</resolution>
            <timeInterval>
                <start>2026-05-19T10:00Z</start>
                <end>2026-05-19T12:00Z</end>
            </timeInterval>
            <Point>
                <position>1</position>
                <price.amount>100.00</price.amount>
            </Point>
            <Point>
                <position>2</position>
                <price.amount>150.00</price.amount>
            </Point>
        </Period>
    </TimeSeries>
</Publication_MarketDocument>"""


@pytest.fixture
def mock_entry():
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_TOKEN: "test_token", CONF_DOMAIN_ID: "10YNL----------L"},
        options={"scan_interval": 3600},
    )


@pytest.fixture
def mock_cache():
    cache = MagicMock()
    cache.save_cache = MagicMock()
    return cache


@pytest.mark.asyncio
async def test_coordinator_first_run_uses_cache(
    hass: HomeAssistant, mock_entry, mock_cache
):
    """Test that if it's the first run and cache exists, it skips the download."""
    coord = EntsoeCoordinator(hass, mock_entry, mock_cache)

    # Simulate data loaded from cache during setup
    coord.last_data = [{"price_kwh": 0.10}]
    coord._is_first_run = True

    result = await coord._async_update_data()

    assert result == [{"price_kwh": 0.10}]
    assert coord._is_first_run is False  # Flag should flip


@pytest.mark.asyncio
@patch("custom_components.entsoe_prijzen.coordinator.async_get_clientsession")
async def test_coordinator_successful_update(
    mock_get_session, hass: HomeAssistant, mock_entry, mock_cache
):
    """Test full successful XML download, parsing, and caching."""
    coord = EntsoeCoordinator(hass, mock_entry, mock_cache)
    coord._is_first_run = False  # Force HTTP pull

    # Mock the aiohttp response context manager
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = VALID_XML_60M

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    mock_session.get.return_value.__aexit__.return_value = None
    mock_get_session.return_value = mock_session

    # Prevent actually writing the debug txt file to disk during tests
    with patch("builtins.open", mock_open()):
        result = await coord._async_update_data()

    # The parser should convert 100.00 EUR/MWh -> 0.10000 EUR/kWh
    assert len(result) == 2
    assert result[0]["price_kwh"] == 0.1
    assert result[1]["price_kwh"] == 0.15
    assert coord.error_count == 0
    mock_cache.save_cache.assert_called_once()


@pytest.mark.asyncio
@patch("custom_components.entsoe_prijzen.coordinator.async_get_clientsession")
async def test_coordinator_http_error(
    mock_get_session, hass: HomeAssistant, mock_entry, mock_cache
):
    """Test how the coordinator handles a bad HTTP response (e.g., 500 Internal Error)."""
    coord = EntsoeCoordinator(hass, mock_entry, mock_cache)
    coord._is_first_run = False
    coord.last_data = [{"cached": "data"}]

    mock_response = AsyncMock()
    mock_response.status = 500

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    mock_session.get.return_value.__aexit__.return_value = None
    mock_get_session.return_value = mock_session

    result = await coord._async_update_data()

    assert coord.error_count == 1
    assert result == [{"cached": "data"}]  # Should return fallback data


@pytest.mark.asyncio
@patch("custom_components.entsoe_prijzen.coordinator.async_get_clientsession")
async def test_coordinator_parsing_exception(
    mock_get_session, hass: HomeAssistant, mock_entry, mock_cache
):
    """Test how the coordinator handles corrupted XML data."""
    coord = EntsoeCoordinator(hass, mock_entry, mock_cache)
    coord._is_first_run = False

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = "NOT VALID XML"

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    mock_session.get.return_value.__aexit__.return_value = None
    mock_get_session.return_value = mock_session

    result = await coord._async_update_data()

    assert coord.error_count == 1
    assert result == []


def test_write_debug_file_sync(hass: HomeAssistant, mock_entry, mock_cache):
    """Test the synchronous file writing method directly to ensure it catches exceptions."""
    coord = EntsoeCoordinator(hass, mock_entry, mock_cache)

    # Test successful write
    with patch("builtins.open", mock_open()) as m:
        coord._write_debug_file_sync("test_path.txt", "debug content")
        m.assert_called_once_with("test_path.txt", "w", encoding="utf-8")
        m().write.assert_called_once_with("debug content")

    # Test exception handling (e.g. permission denied)
    with patch("builtins.open", side_effect=PermissionError):
        # This shouldn't crash, it should just silently pass as coded
        coord._write_debug_file_sync("test_path.txt", "debug content")
