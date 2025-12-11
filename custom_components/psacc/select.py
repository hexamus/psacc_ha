"""Select platform for PSA Car Controller."""
from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import PSACCApiClient
from .const import (
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import PSACCDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PSACC select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    
    entities = []
    for vin, vehicle_data in coordinator.data.items():
        entities.append(PSACCChargeModeSelect(coordinator, api, vin))
    
    async_add_entities(entities)


class PSACCBaseSelect(CoordinatorEntity, SelectEntity):
    """Base class for PSACC selects."""

    def __init__(
        self,
        coordinator: PSACCDataUpdateCoordinator,
        api: PSACCApiClient,
        vin: str,
    ) -> None:
        """Initialize the select."""
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


class PSACCChargeModeSelect(PSACCBaseSelect):
    """Charge mode select."""

    _attr_name = "Charge mode"
    _attr_icon = "mdi:ev-station"
    _attr_options = ["immediate", "scheduled", "economic"]

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_charge_mode"

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        mode = charging.get("mode", "immediate")
        
        # Map API mode to our options
        mode_mapping = {
            "now": "immediate",
            "schedule": "scheduled",
            "eco": "economic",
            "immediate": "immediate",
            "scheduled": "scheduled",
            "economic": "economic",
        }
        
        return mode_mapping.get(mode, "immediate")

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Map our options to API modes
        mode_mapping = {
            "immediate": "now",
            "scheduled": "schedule",
            "economic": "eco",
        }
        
        api_mode = mode_mapping.get(option, "now")
        
        # This would need to be implemented in the API client
        # For now, we'll just log it
        # await self._api.set_charge_mode(self._vin, api_mode)
        
        await self.coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        return charging.get("plugged", False)
