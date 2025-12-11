"""Config flow for PSA Car Controller integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
import homeassistant.helpers.config_validation as cv

from .api import PSACCApiClient, PSACCApiConnectionError
from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    MAX_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class PSACCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PSA Car Controller."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_url = user_input[CONF_API_URL]
            
            # Test the connection
            session = aiohttp_client.async_get_clientsession(self.hass)
            api = PSACCApiClient(api_url, session)
            
            try:
                if await api.test_connection():
                    await self.async_set_unique_id(api_url)
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title="PSA Car Controller",
                        data={
                            CONF_API_URL: api_url,
                            CONF_UPDATE_INTERVAL: user_input.get(
                                CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                            ),
                        },
                    )
            except PSACCApiConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL, default="http://"): cv.string,
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=DEFAULT_UPDATE_INTERVAL,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return PSACCOptionsFlowHandler(config_entry)


class PSACCOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.data.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                    ),
                }
            ),
        )
