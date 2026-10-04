"""PSA Car Controller API Client.

Toutes les routes de psa_car_controller (flobz) sont en GET.
Référence : psa_car_controller/web/view/api.py
"""
import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp
from aiohttp import ClientError, ClientTimeout

from .const import (
    API_STATUS,
    API_CHARGE_NOW,
    API_CHARGE_HOUR,
    API_CHARGE_CONTROL,
    API_PRECONDITIONING,
    API_WAKEUP,
    API_HORN,
    API_LIGHTS,
    API_LOCK,
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
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """GET request to the API, returns decoded JSON."""
        url = f"{self._api_url}{endpoint}"
        try:
            _LOGGER.debug("GET %s params=%s", url, params)
            async with self._session.get(
                url, params=params, timeout=self._timeout
            ) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                if "application/json" not in content_type:
                    text = await response.text()
                    raise PSACCApiError(
                        f"Réponse non JSON ({content_type}) pour {endpoint}: {text[:200]}"
                    )
                result = await response.json()
                _LOGGER.debug("Response: %s", result)
                if isinstance(result, dict) and "error" in result:
                    raise PSACCApiError(f"{endpoint}: {result['error']}")
                return result
        except asyncio.TimeoutError as err:
            raise PSACCApiConnectionError("Timeout connecting to API") from err
        except ClientError as err:
            raise PSACCApiConnectionError(f"Error connecting to API: {err}") from err

    # ---------- Lecture ----------

    async def get_vehicle_status(self, vin: str, from_cache: bool = True) -> Dict[str, Any]:
        """Statut du véhicule.

        from_cache=True : dernier état connu de psacc (local, sans appel au cloud PSA).
        from_cache=False : psacc interroge l'API Stellantis (plus lent, quota).
        """
        return await self._request(
            API_STATUS.format(vin=vin), {"from_cache": 1 if from_cache else 0}
        )

    async def get_charge_control(self, vin: str) -> Dict[str, Any]:
        """Seuil de charge et heure d'arrêt gérés par psacc."""
        return await self._request(API_CHARGE_CONTROL, {"vin": vin})

    # ---------- Actions ----------

    async def _action(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            await self._request(endpoint, params)
            return True
        except PSACCApiError as err:
            _LOGGER.error("Action %s en échec : %s", endpoint, err)
            return False

    async def start_charge(self, vin: str) -> bool:
        return await self._action(API_CHARGE_NOW.format(vin=vin, charge=1))

    async def stop_charge(self, vin: str) -> bool:
        return await self._action(API_CHARGE_NOW.format(vin=vin, charge=0))

    async def set_charge_threshold(self, vin: str, threshold: int) -> bool:
        return await self._action(API_CHARGE_CONTROL, {"vin": vin, "percentage": int(threshold)})

    async def set_charge_stop_hour(self, vin: str, hour: int, minute: int) -> bool:
        return await self._action(API_CHARGE_CONTROL, {"vin": vin, "hour": hour, "minute": minute})

    async def set_charge_start_hour(self, vin: str, hour: int, minute: int) -> bool:
        """Heure de début de la charge différée (programmée dans la voiture)."""
        return await self._action(API_CHARGE_HOUR, {"vin": vin, "hour": hour, "minute": minute})

    async def set_charge_schedule(self, vin: str, start_time: str, end_time: str) -> bool:
        sh, sm = (int(x) for x in start_time.split(":")[:2])
        eh, em = (int(x) for x in end_time.split(":")[:2])
        ok_start = await self.set_charge_start_hour(vin, sh, sm)
        ok_stop = await self.set_charge_stop_hour(vin, eh, em)
        return ok_start and ok_stop

    async def start_climate(self, vin: str, temperature: float = 21.0) -> bool:
        """Préconditionnement (la température est celle réglée dans la voiture)."""
        return await self._action(API_PRECONDITIONING.format(vin=vin, activate=1))

    async def stop_climate(self, vin: str) -> bool:
        return await self._action(API_PRECONDITIONING.format(vin=vin, activate=0))

    async def wakeup(self, vin: str) -> bool:
        return await self._action(API_WAKEUP.format(vin=vin))

    async def horn(self, vin: str, count: int = 1) -> bool:
        return await self._action(API_HORN.format(vin=vin, count=count))

    async def flash_lights(self, vin: str, duration: int = 10) -> bool:
        return await self._action(API_LIGHTS.format(vin=vin, duration=duration))

    async def lock_doors(self, vin: str) -> bool:
        return await self._action(API_LOCK.format(vin=vin, lock=1))

    async def unlock_doors(self, vin: str) -> bool:
        return await self._action(API_LOCK.format(vin=vin, lock=0))
