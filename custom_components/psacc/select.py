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
    _attr_options = ["immediate", "delayed"]

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_charge_mode"

    @property
    def current_option(self) -> str | None:
        """Mode de charge remonté par la voiture (charging_mode)."""
        mode = (self.vehicle_data.get("charging_mode") or "").lower()
        if mode in ("immediate", "delayed"):
            return mode
        return None

    async def async_select_option(self, option: str) -> None:
        """immediate = lancer la charge maintenant, delayed = revenir à la charge programmée."""
        if option == "immediate":
            await self._api.start_charge(self._vin)
        else:
            await self._api.stop_charge(self._vin)
        await self.coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return bool(self.vehicle_data.get("plugged"))
