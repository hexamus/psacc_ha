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
        position = self.vehicle_data.get("position", {})
        coordinates = position.get("geometry", {}).get("coordinates", [])
        return coordinates[1] if len(coordinates) >= 2 else None

    @property
    def longitude(self) -> float | None:
        """Return longitude."""
        position = self.vehicle_data.get("position", {})
        coordinates = position.get("geometry", {}).get("coordinates", [])
        return coordinates[0] if len(coordinates) >= 2 else None

    @property
    def location_accuracy(self) -> int:
        """Return location accuracy in meters."""
        return 50  # Approximate GPS accuracy

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        position = self.vehicle_data.get("position", {})
        properties = position.get("properties", {})
        
        return {
            "altitude": properties.get("altitude"),
            "heading": properties.get("heading"),
            "updated_at": properties.get("updatedAt"),
            "signal_quality": properties.get("signalQuality"),
        }
