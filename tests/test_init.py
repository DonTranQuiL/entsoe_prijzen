import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.entsoe_prijzen.const import DOMAIN, PLATFORMS
from custom_components.entsoe_prijzen import (
    async_setup_entry,
    async_unload_entry,
    update_listener,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom components during testing."""
    yield


@pytest.fixture
def mock_cache_and_coordinator():
    """Fixture to mock the cache and coordinator."""
    with (
        patch("custom_components.entsoe_prijzen.EntsoeCache") as mock_cache_cls,
        patch("custom_components.entsoe_prijzen.EntsoeCoordinator") as mock_coord_cls,
    ):
        mock_cache = MagicMock()
        mock_cache.load_cache = MagicMock(return_value=[])
        mock_cache.clear_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache

        mock_coord = MagicMock()
        mock_coord.last_data = []
        mock_coord.data = []
        mock_coord.domain_id = "10YNL----------L"
        mock_coord.cache = mock_cache
        mock_coord.async_config_entry_first_refresh = AsyncMock()
        mock_coord.async_request_refresh = AsyncMock()
        mock_coord_cls.return_value = mock_coord

        yield mock_cache, mock_coord


@pytest.mark.asyncio
async def test_async_setup_entry_no_cache(
    hass: HomeAssistant, mock_cache_and_coordinator
):
    """Test setup when cache is empty (triggers first_refresh)."""
    mock_cache, mock_coord = mock_cache_and_coordinator

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"api_token": "token", "domain_id": "10YNL----------L"},
    )
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
        return_value=True,
    ):
        assert await async_setup_entry(hass, entry) is True
        mock_coord.async_config_entry_first_refresh.assert_called_once()
        assert DOMAIN in hass.data


@pytest.mark.asyncio
async def test_async_setup_entry_with_cache(
    hass: HomeAssistant, mock_cache_and_coordinator
):
    """Test setup when cache exists (triggers background refresh)."""
    mock_cache, mock_coord = mock_cache_and_coordinator

    # Simulate existing cache data
    mock_cache.load_cache.return_value = [{"price": 0.10}]

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"api_token": "token", "domain_id": "10YNL----------L"},
    )
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
        return_value=True,
    ):
        assert await async_setup_entry(hass, entry) is True
        # Since cache exists, it shouldn't block startup with first_refresh
        mock_coord.async_config_entry_first_refresh.assert_not_called()


@pytest.mark.asyncio
async def test_async_unload_entry(hass: HomeAssistant, mock_cache_and_coordinator):
    """Test successful unload of the integration."""
    mock_cache, mock_coord = mock_cache_and_coordinator
    entry = MockConfigEntry(domain=DOMAIN, data={"domain_id": "10YNL----------L"})

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = mock_coord

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
        return_value=True,
    ) as mock_unload:
        assert await async_unload_entry(hass, entry) is True
        assert entry.entry_id not in hass.data[DOMAIN]
        mock_unload.assert_called_once_with(entry, PLATFORMS)


@pytest.mark.asyncio
async def test_services_and_update_listener(
    hass: HomeAssistant, mock_cache_and_coordinator
):
    """Test custom services and the update listener."""
    mock_cache, mock_coord = mock_cache_and_coordinator
    entry = MockConfigEntry(domain=DOMAIN, data={"domain_id": "10YNL----------L"})

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = mock_coord
    hass.services.async_register(DOMAIN, "refresh", MagicMock())
    hass.services.async_register(DOMAIN, "clear_files", MagicMock())

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
        return_value=True,
    ):
        await async_setup_entry(hass, entry)

    # Test Reload Listener
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_reload"
    ) as mock_reload:
        await update_listener(hass, entry)
        mock_reload.assert_called_once_with(entry.entry_id)

    # Test Refresh Service
    await hass.services.async_call(DOMAIN, "refresh", blocking=True)
    mock_coord.async_request_refresh.assert_called()

    # Test Clear Files Service
    with patch("os.path.exists", return_value=True), patch("os.remove") as mock_remove:
        await hass.services.async_call(DOMAIN, "clear_files", blocking=True)
        mock_cache.clear_cache.assert_called()
        mock_remove.assert_called_once()
