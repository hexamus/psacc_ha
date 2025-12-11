"""Number platform for PSA Car Controller."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import PSACCApiClient
from .const import (
    DOMAIN,
    MANUFACTURER,
    ICON_BATTERY,
    ICON_TEMPERATURE,
)
from .coordinator import PSACCDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PSACC number platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    
    entities = []
    for vin, vehicle_data in coordinator.data.items():
        entities.extend([
            PSACCChargeThresholdNumber(coordinator, api, vin),
            PSACCClimateTemperatureNumber(coordinator, api, vin),
        ])
    
    async_add_entities(entities)


class PSACCBaseNumber(CoordinatorEntity, NumberEntity):
    """Base class for PSACC numbers."""

    def __init__(
        self,
        coordinator: PSACCDataUpdateCoordinator,
        api: PSACCApiClient,
        vin: str,
    ) -> None:
        """Initialize the number."""
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


class PSACCChargeThresholdNumber(PSACCBaseNumber):
    """Charge threshold number."""

    _attr_name = "Charge threshold"
    _attr_icon = ICON_BATTERY
    _attr_native_min_value = 50
    _attr_native_max_value = 100
    _attr_native_step = 5
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_charge_threshold_number"

    @property
    def native_value(self):
        """Return the current value."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        return charging.get("charge_threshold", 100)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self._api.set_charge_threshold(self._vin, int(value))
        await self.coordinator.async_request_refresh()


class PSACCClimateTemperatureNumber(PSACCBaseNumber):
    """Climate temperature number."""

    _attr_name = "Climate temperature"
    _attr_icon = ICON_TEMPERATURE
    _attr_native_min_value = 16
    _attr_native_max_value = 28
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_climate_temperature"

    @property
    def native_value(self):
        """Return the current value."""
        precond = self.vehicle_data.get("preconditionning", {})
        return precond.get("airConditioning", {}).get("temperature", 21.0)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        # Start climate with new temperature
        await self._api.start_climate(self._vin, value)
        await self.coordinator.async_request_refresh()
