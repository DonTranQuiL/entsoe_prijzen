import pytest
from unittest.mock import patch
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.entsoe_prijzen.const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_DOMAIN_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom components during testing."""
    yield


@pytest.mark.asyncio
async def test_form_user_success(hass):
    """Test we can create an entry through the user step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch("custom_components.entsoe_prijzen.async_setup_entry", return_value=True):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_API_TOKEN: "test_token_123",
                CONF_DOMAIN_ID: "10YNL----------L",
            },
        )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "ENTSO-E Prijzen (NL)"
    assert result2["data"][CONF_API_TOKEN] == "test_token_123"
    assert result2["data"][CONF_DOMAIN_ID] == "10YNL----------L"
    assert result2["options"][CONF_SCAN_INTERVAL] == DEFAULT_SCAN_INTERVAL


@pytest.mark.asyncio
async def test_options_flow(hass):
    """Test the options flow for changing the scan interval."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_TOKEN: "token", CONF_DOMAIN_ID: "10YNL----------L"},
        options={CONF_SCAN_INTERVAL: 3600},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_SCAN_INTERVAL: 7200,
        },
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_SCAN_INTERVAL] == 7200
