"""PSA Car Controller API Client."""
import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime

import aiohttp
from aiohttp import ClientError, ClientTimeout

from .const import (
    API_VEHICLES,
    API_STATUS,
    API_CHARGE_NOW,
    API_CHARGE_HOUR,
    API_CLIMATE_START,
    API_CLIMATE_STOP,
    API_WAKEUP,
    API_HORN,
    API_LIGHTS,
    API_LOCK,
    API_UNLOCK,
    API_PRECONDITIONING,
    API_CHARGE_THRESHOLD,
)

_LOGGER = logging.getLogger(__name__)

class PSACCApiError(Exception):
    """Base exception for PSACC API errors."""

class PSACCApiConnectionError(PSACCApiError):
    """Connection error exception."""

class PSACCApiAuthError(PSACCApiError):
    """Authentication error exception."""

class PSACCApiClient:
    """API client for PSA Car Controller."""

    def __init__(self, api_url: str, session: aiohttp.ClientSession):
        """Initialize the API client."""
        self._api_url = api_url.rstrip("/")
        self._session = session
        self._timeout = ClientTimeout(total=30)

    async def _request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the API."""
        url = f"{self._api_url}{endpoint}"
        
        try:
            _LOGGER.debug("Request %s %s with data: %s", method, url, data)
            
            async with self._session.request(
                method, url, json=data, timeout=self._timeout
            ) as response:
                response.raise_for_status()
                result = await response.json()
                _LOGGER.debug("Response: %s", result)
                return result
                
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout connecting to PSACC API: %s", err)
            raise PSACCApiConnectionError("Timeout connecting to API") from err
        except ClientError as err:
            _LOGGER.error("Error connecting to PSACC API: %s", err)
            raise PSACCApiConnectionError(f"Error connecting to API: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise PSACCApiError(f"Unexpected error: {err}") from err

    async def get_vehicles(self) -> list:
        """Get list of vehicles."""
        try:
            response = await self._request("GET", API_VEHICLES)
            return response if isinstance(response, list) else []
        except Exception as err:
            _LOGGER.error("Failed to get vehicles: %s", err)
            return []

    async def get_vehicle_status(self, vin: str) -> Dict[str, Any]:
        """Get vehicle status."""
        endpoint = API_STATUS.format(vin=vin)
        return await self._request("GET", endpoint)

    async def start_charge(self, vin: str) -> bool:
        """Start charging."""
        try:
            endpoint = API_CHARGE_NOW.format(vin=vin, charge="1")
            await self._request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error("Failed to start charge: %s", err)
            return False

    async def stop_charge(self, vin: str) -> bool:
        """Stop charging."""
        try:
            endpoint = API_CHARGE_NOW.format(vin=vin, charge="0")
            await self._request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error("Failed to stop charge: %s", err)
            return False

    async def set_charge_threshold(self, vin: str, threshold: int) -> bool:
        """Set charge threshold."""
        try:
            data = {
                "vin": vin,
                "percentage": threshold
            }
            await self._request("POST", API_CHARGE_THRESHOLD, data)
            return True
        except Exception as err:
            _LOGGER.error("Failed to set charge threshold: %s", err)
            return False

    async def set_charge_schedule(
        self, vin: str, start_time: str, end_time: str
    ) -> bool:
        """Set charge schedule."""
        try:
            data = {
                "vin": vin,
                "start": start_time,
                "end": end_time
            }
            await self._request("POST", API_CHARGE_HOUR, data)
            return True
        except Exception as err:
            _LOGGER.error("Failed to set charge schedule: %s", err)
            return False

    async def start_climate(self, vin: str, temperature: float = 21.0) -> bool:
        """Start climate control."""
        try:
            endpoint = API_CLIMATE_START.format(vin=vin, temperature=temperature)
            await self._request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error("Failed to start climate: %s", err)
            return False

    async def stop_climate(self, vin: str) -> bool:
        """Stop climate control."""
        try:
            endpoint = API_CLIMATE_STOP.format(vin=vin)
            await self._request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error("Failed to stop climate: %s", err)
            return False

    async def wakeup(self, vin: str) -> bool:
        """Wake up vehicle."""
        try:
            endpoint = API_WAKEUP.format(vin=vin)
            await self._request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error("Failed to wake up vehicle: %s", err)
            return False

    async def horn(self, vin: str, count: int = 1) -> bool:
        """Sound the horn."""
        try:
            endpoint = API_HORN.format(vin=vin, count=count)
            await self._request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error("Failed to sound horn: %s", err)
            return False

    async def flash_lights(self, vin: str, count: int = 1) -> bool:
        """Flash the lights."""
        try:
            endpoint = API_LIGHTS.format(vin=vin, count=count)
            await self._request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error("Failed to flash lights: %s", err)
            return False

    async def lock_doors(self, vin: str) -> bool:
        """Lock doors."""
        try:
            endpoint = API_LOCK.format(vin=vin)
            await self._request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error("Failed to lock doors: %s", err)
            return False

    async def unlock_doors(self, vin: str) -> bool:
        """Unlock doors."""
        try:
            endpoint = API_UNLOCK.format(vin=vin)
            await self._request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error("Failed to unlock doors: %s", err)
            return False

    async def test_connection(self) -> bool:
        """Test the API connection."""
        try:
            await self.get_vehicles()
            return True
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
