"""Binary sensor platform for PSA Car Controller."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    ICON_CHARGING,
    ICON_PLUGGED,
    ICON_DOOR,
    ICON_DOOR_LOCK,
    ICON_CLIMATE,
)
from .coordinator import PSACCDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PSACC binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = []
    for vin, vehicle_data in coordinator.data.items():
        entities.extend([
            PSACCChargingBinarySensor(coordinator, vin),
            PSACCPluggedBinarySensor(coordinator, vin),
            PSACCDoorsLockedBinarySensor(coordinator, vin),
            PSACCDoorDriverBinarySensor(coordinator, vin),
            PSACCDoorPassengerBinarySensor(coordinator, vin),
            PSACCDoorRearLeftBinarySensor(coordinator, vin),
            PSACCDoorRearRightBinarySensor(coordinator, vin),
            PSACCHoodBinarySensor(coordinator, vin),
            PSACCTrunkBinarySensor(coordinator, vin),
            PSACCClimateBinarySensor(coordinator, vin),
        ])
    
    async_add_entities(entities)


class PSACCBaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base class for PSACC binary sensors."""

    def __init__(
        self,
        coordinator: PSACCDataUpdateCoordinator,
        vin: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
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


class PSACCChargingBinarySensor(PSACCBaseBinarySensor):
    """Charging binary sensor."""

    _attr_name = "Charging"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_icon = ICON_CHARGING

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_charging"

    @property
    def is_on(self):
        """Return true if charging."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        return charging.get("status") == "InProgress"


class PSACCPluggedBinarySensor(PSACCBaseBinarySensor):
    """Plugged binary sensor."""

    _attr_name = "Plugged"
    _attr_device_class = BinarySensorDeviceClass.PLUG
    _attr_icon = ICON_PLUGGED

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_plugged"

    @property
    def is_on(self):
        """Return true if plugged."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        return charging.get("plugged", False)


class PSACCDoorsLockedBinarySensor(PSACCBaseBinarySensor):
    """Doors locked binary sensor."""

    _attr_name = "Doors locked"
    _attr_device_class = BinarySensorDeviceClass.LOCK
    _attr_icon = ICON_DOOR_LOCK

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_doors_locked"

    @property
    def is_on(self):
        """Return true if doors are locked."""
        precond = self.vehicle_data.get("preconditionning", {})
        return precond.get("airConditioning", {}).get("status") == "Enabled"


class PSACCDoorDriverBinarySensor(PSACCBaseBinarySensor):
    """Driver door binary sensor."""

    _attr_name = "Driver door"
    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_icon = ICON_DOOR

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_door_driver"

    @property
    def is_on(self):
        """Return true if door is open."""
        doors = self.vehicle_data.get("doors", {})
        return doors.get("driver") == "Open"


class PSACCDoorPassengerBinarySensor(PSACCBaseBinarySensor):
    """Passenger door binary sensor."""

    _attr_name = "Passenger door"
    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_icon = ICON_DOOR

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_door_passenger"

    @property
    def is_on(self):
        """Return true if door is open."""
        doors = self.vehicle_data.get("doors", {})
        return doors.get("passenger") == "Open"


class PSACCDoorRearLeftBinarySensor(PSACCBaseBinarySensor):
    """Rear left door binary sensor."""

    _attr_name = "Rear left door"
    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_icon = ICON_DOOR

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_door_rear_left"

    @property
    def is_on(self):
        """Return true if door is open."""
        doors = self.vehicle_data.get("doors", {})
        return doors.get("rear_left") == "Open"


class PSACCDoorRearRightBinarySensor(PSACCBaseBinarySensor):
    """Rear right door binary sensor."""

    _attr_name = "Rear right door"
    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_icon = ICON_DOOR

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_door_rear_right"

    @property
    def is_on(self):
        """Return true if door is open."""
        doors = self.vehicle_data.get("doors", {})
        return doors.get("rear_right") == "Open"


class PSACCHoodBinarySensor(PSACCBaseBinarySensor):
    """Hood binary sensor."""

    _attr_name = "Hood"
    _attr_device_class = BinarySensorDeviceClass.OPENING
    _attr_icon = ICON_DOOR

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_hood"

    @property
    def is_on(self):
        """Return true if hood is open."""
        doors = self.vehicle_data.get("doors", {})
        return doors.get("hood") == "Open"


class PSACCTrunkBinarySensor(PSACCBaseBinarySensor):
    """Trunk binary sensor."""

    _attr_name = "Trunk"
    _attr_device_class = BinarySensorDeviceClass.OPENING
    _attr_icon = ICON_DOOR

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_trunk"

    @property
    def is_on(self):
        """Return true if trunk is open."""
        doors = self.vehicle_data.get("doors", {})
        return doors.get("trunk") == "Open"


class PSACCClimateBinarySensor(PSACCBaseBinarySensor):
    """Climate binary sensor."""

    _attr_name = "Climate"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_icon = ICON_CLIMATE

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_climate"

    @property
    def is_on(self):
        """Return true if climate is active."""
        precond = self.vehicle_data.get("preconditionning", {})
        status = precond.get("airConditioning", {}).get("status")
        return status in ["Enabled", "InProgress"]
