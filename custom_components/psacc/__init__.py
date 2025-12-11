"""The PSA Car Controller integration."""
import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import aiohttp_client
import voluptuous as vol

from .api import PSACCApiClient
from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    SERVICE_SET_CHARGE_THRESHOLD,
    SERVICE_SET_CHARGE_SCHEDULE,
    SERVICE_START_CLIMATE,
    SERVICE_STOP_CLIMATE,
    SERVICE_HORN,
    SERVICE_LIGHTS,
    SERVICE_WAKEUP,
    ATTR_THRESHOLD,
    ATTR_START_TIME,
    ATTR_END_TIME,
    ATTR_TEMPERATURE,
    ATTR_COUNT,
    ATTR_VIN,
)
from .coordinator import PSACCDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
]

# Service schemas
SERVICE_SET_CHARGE_THRESHOLD_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_VIN): str,
        vol.Required(ATTR_THRESHOLD): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
    }
)

SERVICE_SET_CHARGE_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_VIN): str,
        vol.Required(ATTR_START_TIME): str,
        vol.Required(ATTR_END_TIME): str,
    }
)

SERVICE_CLIMATE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_VIN): str,
        vol.Optional(ATTR_TEMPERATURE, default=21): vol.All(
            vol.Coerce(float), vol.Range(min=16, max=28)
        ),
    }
)

SERVICE_HORN_LIGHTS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_VIN): str,
        vol.Optional(ATTR_COUNT, default=1): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=5)
        ),
    }
)

SERVICE_WAKEUP_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_VIN): str,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PSA Car Controller from a config entry."""
    api_url = entry.data[CONF_API_URL]
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

    session = aiohttp_client.async_get_clientsession(hass)
    api = PSACCApiClient(api_url, session)

    coordinator = PSACCDataUpdateCoordinator(hass, api, update_interval)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    # Register services
    async def handle_set_charge_threshold(call: ServiceCall) -> None:
        """Handle set charge threshold service."""
        vin = call.data[ATTR_VIN]
        threshold = call.data[ATTR_THRESHOLD]
        await api.set_charge_threshold(vin, threshold)
        await coordinator.async_request_refresh()

    async def handle_set_charge_schedule(call: ServiceCall) -> None:
        """Handle set charge schedule service."""
        vin = call.data[ATTR_VIN]
        start_time = call.data[ATTR_START_TIME]
        end_time = call.data[ATTR_END_TIME]
        await api.set_charge_schedule(vin, start_time, end_time)
        await coordinator.async_request_refresh()

    async def handle_start_climate(call: ServiceCall) -> None:
        """Handle start climate service."""
        vin = call.data[ATTR_VIN]
        temperature = call.data.get(ATTR_TEMPERATURE, 21)
        await api.start_climate(vin, temperature)
        await coordinator.async_request_refresh()

    async def handle_stop_climate(call: ServiceCall) -> None:
        """Handle stop climate service."""
        vin = call.data[ATTR_VIN]
        await api.stop_climate(vin)
        await coordinator.async_request_refresh()

    async def handle_horn(call: ServiceCall) -> None:
        """Handle horn service."""
        vin = call.data[ATTR_VIN]
        count = call.data.get(ATTR_COUNT, 1)
        await api.horn(vin, count)

    async def handle_lights(call: ServiceCall) -> None:
        """Handle lights service."""
        vin = call.data[ATTR_VIN]
        count = call.data.get(ATTR_COUNT, 1)
        await api.flash_lights(vin, count)

    async def handle_wakeup(call: ServiceCall) -> None:
        """Handle wakeup service."""
        vin = call.data[ATTR_VIN]
        await api.wakeup(vin)
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_CHARGE_THRESHOLD,
        handle_set_charge_threshold,
        schema=SERVICE_SET_CHARGE_THRESHOLD_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_CHARGE_SCHEDULE,
        handle_set_charge_schedule,
        schema=SERVICE_SET_CHARGE_SCHEDULE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_START_CLIMATE,
        handle_start_climate,
        schema=SERVICE_CLIMATE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_CLIMATE,
        handle_stop_climate,
        schema=SERVICE_WAKEUP_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_HORN, handle_horn, schema=SERVICE_HORN_LIGHTS_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_LIGHTS, handle_lights, schema=SERVICE_HORN_LIGHTS_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_WAKEUP, handle_wakeup, schema=SERVICE_WAKEUP_SCHEMA
    )

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
