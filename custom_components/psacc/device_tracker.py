"""Device tracker platform for PSA Car Controller."""
from __future__ import annotations

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    ICON_LOCATION,
)
from .coordinator import PSACCDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PSACC device tracker platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = []
    for vin, vehicle_data in coordinator.data.items():
        entities.append(PSACCDeviceTracker(coordinator, vin))
    
    async_add_entities(entities)


class PSACCDeviceTracker(CoordinatorEntity, TrackerEntity):
    """PSACC device tracker."""

    _attr_has_entity_name = True
    _attr_name = "Location"
    _attr_icon = ICON_LOCATION

    def __init__(
        self,
        coordinator: PSACCDataUpdateCoordinator,
        vin: str,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self._vin = vin

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_location"

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

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude."""
        return self.vehicle_data.get("latitude")

    @property
    def longitude(self) -> float | None:
        """Return longitude."""
        return self.vehicle_data.get("longitude")

    @property
    def location_accuracy(self) -> int:
        """Return location accuracy in meters."""
        return 50  # Approximate GPS accuracy

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        data = self.vehicle_data
        updated = data.get("position_updated_at")
        return {
            "altitude": data.get("altitude"),
            "heading": data.get("heading"),
            "updated_at": updated.isoformat() if updated else None,
        }
