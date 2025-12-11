"""DataUpdateCoordinator for PSA Car Controller."""
import logging
from datetime import timedelta
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PSACCApiClient, PSACCApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PSACCDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching PSACC data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: PSACCApiClient,
        update_interval: int,
    ) -> None:
        """Initialize."""
        self.api = api
        self.vehicles = {}
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via API."""
        try:
            # Get list of vehicles if not cached
            if not self.vehicles:
                vehicles = await self.api.get_vehicles()
                for vehicle in vehicles:
                    vin = vehicle.get("vin")
                    if vin:
                        self.vehicles[vin] = vehicle

            # Update status for each vehicle
            data = {}
            for vin in self.vehicles:
                try:
                    status = await self.api.get_vehicle_status(vin)
                    data[vin] = {
                        **self.vehicles[vin],
                        **status,
                    }
                except PSACCApiError as err:
                    _LOGGER.warning("Failed to update vehicle %s: %s", vin, err)
                    # Keep previous data if update fails
                    if vin in self.data:
                        data[vin] = self.data[vin]

            return data

        except PSACCApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def get_vehicle_data(self, vin: str) -> Dict[str, Any]:
        """Get data for a specific vehicle."""
        return self.data.get(vin, {})

    def get_all_vehicles(self) -> Dict[str, Any]:
        """Get all vehicles data."""
        return self.data
