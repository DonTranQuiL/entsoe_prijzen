import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_DOMAIN_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAINS,
)

_LOGGER = logging.getLogger(__name__)


class EntsoeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            token = user_input.get(CONF_API_TOKEN)
            domain_id = user_input.get(CONF_DOMAIN_ID)

            if not token:
                errors[CONF_API_TOKEN] = "required"

            if not errors:
                country_name = DOMAINS.get(domain_id, "Onbekend").split(" - ")[0]
                return self.async_create_entry(
                    title=f"ENTSO-E Prijzen ({country_name})",
                    data={CONF_API_TOKEN: token, CONF_DOMAIN_ID: domain_id},
                    options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_TOKEN): str,
                vol.Required(CONF_DOMAIN_ID, default="10YNL----------L"): vol.In(
                    DOMAINS
                ),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=options_schema)
