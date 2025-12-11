"""Sensor platform for PSA Car Controller."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    ICON_BATTERY,
    ICON_RANGE,
    ICON_MILEAGE,
    ICON_CONSUMPTION,
    ICON_CHARGING,
    ICON_TEMPERATURE,
)
from .coordinator import PSACCDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PSACC sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = []
    for vin, vehicle_data in coordinator.data.items():
        entities.extend([
            PSACCBatteryLevelSensor(coordinator, vin),
            PSACCRangeElectricSensor(coordinator, vin),
            PSACCRangeTotalSensor(coordinator, vin),
            PSACCMileageSensor(coordinator, vin),
            PSACCChargingPowerSensor(coordinator, vin),
            PSACCChargingTimeSensor(coordinator, vin),
            PSACCConsumptionSensor(coordinator, vin),
            PSACCTemperatureExteriorSensor(coordinator, vin),
            PSACCChargeThresholdSensor(coordinator, vin),
            PSACCLastUpdateSensor(coordinator, vin),
        ])
    
    async_add_entities(entities)


class PSACCBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for PSACC sensors."""

    def __init__(
        self,
        coordinator: PSACCDataUpdateCoordinator,
        vin: str,
    ) -> None:
        """Initialize the sensor."""
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


class PSACCBatteryLevelSensor(PSACCBaseSensor):
    """Battery level sensor."""

    _attr_name = "Battery level"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = ICON_BATTERY

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_battery_level"

    @property
    def native_value(self):
        """Return the state."""
        return self.vehicle_data.get("energy", [{}])[0].get("level")


class PSACCRangeElectricSensor(PSACCBaseSensor):
    """Electric range sensor."""

    _attr_name = "Range electric"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = ICON_RANGE

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_range_electric"

    @property
    def native_value(self):
        """Return the state."""
        return self.vehicle_data.get("energy", [{}])[0].get("autonomy")


class PSACCRangeTotalSensor(PSACCBaseSensor):
    """Total range sensor."""

    _attr_name = "Range total"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = ICON_RANGE

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_range_total"

    @property
    def native_value(self):
        """Return the state."""
        # Sum electric and fuel range if available
        electric = self.vehicle_data.get("energy", [{}])[0].get("autonomy", 0) or 0
        fuel = self.vehicle_data.get("energy", [{}])[1].get("autonomy", 0) if len(
            self.vehicle_data.get("energy", [])
        ) > 1 else 0
        return electric + fuel if electric or fuel else None


class PSACCMileageSensor(PSACCBaseSensor):
    """Mileage sensor."""

    _attr_name = "Mileage"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = ICON_MILEAGE

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_mileage"

    @property
    def native_value(self):
        """Return the state."""
        return self.vehicle_data.get("odometer", {}).get("mileage")


class PSACCChargingPowerSensor(PSACCBaseSensor):
    """Charging power sensor."""

    _attr_name = "Charging power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_icon = ICON_CHARGING

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_charging_power"

    @property
    def native_value(self):
        """Return the state."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        if charging.get("status") == "InProgress":
            return charging.get("rate")
        return 0


class PSACCChargingTimeSensor(PSACCBaseSensor):
    """Charging time remaining sensor."""

    _attr_name = "Charging time remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = ICON_CHARGING

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_charging_time"

    @property
    def native_value(self):
        """Return the state."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        if charging.get("status") == "InProgress":
            return charging.get("remaining_time")
        return None


class PSACCConsumptionSensor(PSACCBaseSensor):
    """Average consumption sensor."""

    _attr_name = "Average consumption"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "kWh/100km"
    _attr_icon = ICON_CONSUMPTION

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_consumption"

    @property
    def native_value(self):
        """Return the state."""
        return self.vehicle_data.get("environment", {}).get("consumption")


class PSACCTemperatureExteriorSensor(PSACCBaseSensor):
    """Exterior temperature sensor."""

    _attr_name = "Exterior temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = ICON_TEMPERATURE

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_temperature_exterior"

    @property
    def native_value(self):
        """Return the state."""
        return self.vehicle_data.get("environment", {}).get("temperature")


class PSACCChargeThresholdSensor(PSACCBaseSensor):
    """Charge threshold sensor."""

    _attr_name = "Charge threshold"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = ICON_BATTERY

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_charge_threshold"

    @property
    def native_value(self):
        """Return the state."""
        charging = self.vehicle_data.get("energy", [{}])[0].get("charging", {})
        return charging.get("charge_threshold", 100)


class PSACCLastUpdateSensor(PSACCBaseSensor):
    """Last update sensor."""

    _attr_name = "Last update"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._vin}_last_update"

    @property
    def native_value(self):
        """Return the state."""
        return self.vehicle_data.get("updatedAt")
