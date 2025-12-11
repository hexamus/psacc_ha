"""Button platform for PSA Car Controller."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import PSACCApiClient
from .const import (
    DOMAIN,
    MANUFACTURER,
    ICON_DOOR_LOCK,
    ICON_DOOR_UNLOCK,
    ICON_HORN,
    ICON_LIGHTS,
)
from .coordinator import PSACCDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PSACC button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    
    entities = []
    for vin, vehicle_data in coordinator.data.items():
        entities.extend([
            PSACCLockDoorsButton(coordinator, api, vin),
            PSACCUnlockDoorsButton(coordinator, api, vin),
            PSACCHornButton(coordinator, api, vin),
            PSACCLightsButton(coordinator, api, vin),
            PSACCWakeupButton(coordinator, api, vin),
            PSACCRefreshButton(coordinator, api, vin),
        ])
    
    async_add_entities(entities)


class PSACCBaseButton(CoordinatorEntity, ButtonEntity):
    """Base class for PSACC buttons."""

    def __init__(
        self,
        coordinator: PSACCDataUpdateCoordinator,
        api: PSACCApiClient,
        vin: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._api = api
        self._vin = vin
        self._attr_has_entity_name = True

    @property
    def vehicle_data(self):
        """Return vehicle data."""
        return self.coordinator.get_vehicle_data(self._vin)

    @property
    def device_info(self):
        """Return device information."""
        vehicle = self.vehicle_data
        return {
            "identifiers": {(DOMAIN, self._vin)},
            "name": f"{vehicle.get('brand', 'PSA')} {vehicle.get('model', 'Car')}",
            "manufacturer": MANUFACTURER,
            "model": vehicle.get("model", "Connected Car"),
            "sw_version": vehicle.get("firmware_version"),
        }


class PSACCLockDoorsButton(PSACCBaseButton):
    """Lock doors button."""

    _attr_name = "Lock doors"
    _attr_icon = ICON_DOOR_LOCK

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_lock_doors"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.lock_doors(self._vin)
        await self.coordinator.async_request_refresh()


class PSACCUnlockDoorsButton(PSACCBaseButton):
    """Unlock doors button."""

    _attr_name = "Unlock doors"
    _attr_icon = ICON_DOOR_UNLOCK

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_unlock_doors"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.unlock_doors(self._vin)
        await self.coordinator.async_request_refresh()


class PSACCHornButton(PSACCBaseButton):
    """Horn button."""

    _attr_name = "Horn"
    _attr_icon = ICON_HORN

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_horn"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.horn(self._vin, 1)


class PSACCLightsButton(PSACCBaseButton):
    """Lights button."""

    _attr_name = "Flash lights"
    _attr_icon = ICON_LIGHTS

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_lights"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.flash_lights(self._vin, 1)


class PSACCWakeupButton(PSACCBaseButton):
    """Wakeup button."""

    _attr_name = "Wake up"
    _attr_icon = "mdi:alarm"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_wakeup"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.wakeup(self._vin)
        await self.coordinator.async_request_refresh()


class PSACCRefreshButton(PSACCBaseButton):
    """Refresh button."""

    _attr_name = "Refresh data"
    _attr_icon = "mdi:refresh"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_refresh"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()
