"""Switch platform for PSA Car Controller."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import PSACCApiClient
from .const import (
    DOMAIN,
    MANUFACTURER,
    ICON_CHARGING,
    ICON_CLIMATE,
)
from .coordinator import PSACCDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PSACC switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    
    entities = []
    for vin, vehicle_data in coordinator.data.items():
        entities.extend([
            PSACCChargingSwitch(coordinator, api, vin),
            PSACCClimateSwitch(coordinator, api, vin),
        ])
    
    async_add_entities(entities)


class PSACCBaseSwitch(CoordinatorEntity, SwitchEntity):
    """Base class for PSACC switches."""

    def __init__(
        self,
        coordinator: PSACCDataUpdateCoordinator,
        api: PSACCApiClient,
        vin: str,
    ) -> None:
        """Initialize the switch."""
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


class PSACCChargingSwitch(PSACCBaseSwitch):
    """Charging switch."""

    _attr_name = "Charging"
    _attr_icon = ICON_CHARGING

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_charging_switch"

    @property
    def is_on(self):
        """Return true if charging."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        return charging.get("status") == "InProgress"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on charging."""
        await self._api.start_charge(self._vin)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off charging."""
        await self._api.stop_charge(self._vin)
        await self.coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        return charging.get("plugged", False)


class PSACCClimateSwitch(PSACCBaseSwitch):
    """Climate switch."""

    _attr_name = "Climate"
    _attr_icon = ICON_CLIMATE

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_climate_switch"

    @property
    def is_on(self):
        """Return true if climate is on."""
        precond = self.vehicle_data.get("preconditionning", {})
        status = precond.get("airConditioning", {}).get("status")
        return status in ["Enabled", "InProgress"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on climate."""
        await self._api.start_climate(self._vin, 21.0)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off climate."""
        await self._api.stop_climate(self._vin)
        await self.coordinator.async_request_refresh()
