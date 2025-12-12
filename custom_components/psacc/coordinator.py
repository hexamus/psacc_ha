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
        vin: str,
        update_interval: int,
    ) -> None:
        """Initialize."""
        self.api = api
        self.vin = vin
        self.vehicle_data = {}
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via API."""
        try:
            # Récupérer le statut du véhicule avec le VIN
            status = await self.api.get_vehicle_status(self.vin)
            
            # Stocker les données avec le VIN comme clé
            data = {
                self.vin: {
                    "vin": self.vin,
                    **status,
                }
            }
            
            return data

        except PSACCApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def get_vehicle_data(self, vin: str) -> Dict[str, Any]:
        """Get data for a specific vehicle."""
        return self.data.get(vin, {})

    def get_all_vehicles(self) -> Dict[str, Any]:
        """Get all vehicles data."""
        return self.data
