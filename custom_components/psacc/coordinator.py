"""DataUpdateCoordinator for PSA Car Controller.

Le JSON de /get_vehicleinfo est produit par Status.to_dict() de psacc :
les clés sont les noms d'attributs Python (snake_case), pas les clés de l'API
Stellantis. Exemple :
  energy[0].level / autonomy / charging.{plugged,status,charging_rate,remaining_time,charging_mode}
  timed_odometer.mileage
  last_position.geometry.coordinates = [lon, lat, alt]
  environment.air.temp
  doors_state.{locked_state: [..], opening: [{identifier, state}]}
  preconditionning.air_conditioning.status
"""
import logging
import re
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import PSACCApiClient, PSACCApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Nombre d'échecs consécutifs tolérés avant de passer les entités en indisponible
MAX_FAILURES_KEEP_DATA = 3


def _dig(data: Any, *keys, default=None):
    """Lecture sûre d'un chemin dans des dicts/listes."""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        elif isinstance(data, list) and isinstance(key, int):
            data = data[key] if -len(data) <= key < len(data) else None
        else:
            return default
        if data is None:
            return default
    return data


def _iso_duration_to_minutes(value: Optional[str]) -> Optional[int]:
    """'PT1H30M' -> 90."""
    if not value or not isinstance(value, str):
        return None
    match = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?", value)
    if not match:
        return None
    days, hours, minutes, _ = (float(x) if x else 0 for x in match.groups())
    return int(days * 1440 + hours * 60 + minutes)


def _parse_dt(value: Any):
    if not value:
        return None
    parsed = dt_util.parse_datetime(str(value))
    if parsed and parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt_util.UTC)
    return parsed


def normalize_status(raw: Dict[str, Any], charge_control: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Transforme le JSON psacc en dict plat lu par les entités."""
    energies = raw.get("energy") or []
    electric = next((e for e in energies if e.get("type") == "Electric"), energies[0] if energies else {})
    fuel = next((e for e in energies if e.get("type") == "Fuel"), {})
    charging = electric.get("charging") or {}

    coords = _dig(raw, "last_position", "geometry", "coordinates", default=[]) or []
    lon = coords[0] if len(coords) > 0 else None
    lat = coords[1] if len(coords) > 1 else None
    alt = coords[2] if len(coords) > 2 else None

    openings = {
        (o.get("identifier") or "").lower(): o.get("state")
        for o in (_dig(raw, "doors_state", "opening", default=[]) or [])
        if isinstance(o, dict)
    }
    locked_state = _dig(raw, "doors_state", "locked_state", default=[]) or []

    threshold = None
    stop_hour = None
    if charge_control:
        threshold = charge_control.get("percentage_threshold")
        stop_hour = charge_control.get("_stop_hour") or charge_control.get("stop_hour")

    return {
        "raw": raw,
        "battery_level": electric.get("level"),
        "range_electric": electric.get("autonomy"),
        "range_fuel": fuel.get("autonomy"),
        "consumption": electric.get("consumption"),
        "plugged": charging.get("plugged"),
        "charging_status": charging.get("status"),
        "charging": charging.get("status") == "InProgress",
        "charging_rate": charging.get("charging_rate"),
        "charging_mode": charging.get("charging_mode"),
        "charging_remaining_min": _iso_duration_to_minutes(charging.get("remaining_time")),
        "next_delayed_time": charging.get("next_delayed_time"),
        "energy_updated_at": _parse_dt(electric.get("updated_at")),
        "mileage": _dig(raw, "timed_odometer", "mileage"),
        "latitude": lat,
        "longitude": lon,
        "altitude": alt,
        "heading": _dig(raw, "last_position", "properties", "heading"),
        "position_updated_at": _parse_dt(_dig(raw, "last_position", "properties", "updated_at")),
        "temperature_exterior": _dig(raw, "environment", "air", "temp"),
        "battery_voltage": _dig(raw, "battery", "voltage"),
        "moving": _dig(raw, "kinetic", "moving"),
        "doors_locked": None if not locked_state else any(
            str(s).lower() in ("locked", "superlocked") for s in locked_state
        ),
        "doors": openings,
        "climate_status": _dig(raw, "preconditionning", "air_conditioning", "status"),
        "charge_threshold": threshold,
        "charge_stop_hour": stop_hour,
    }


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
        self._failures = 0
        self._force_remote = False
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval),
        )

    async def async_refresh_from_car(self) -> None:
        """Prochain rafraîchissement en interrogeant le cloud PSA (pas le cache)."""
        self._force_remote = True
        await self.async_request_refresh()

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via API."""
        from_cache = not self._force_remote
        self._force_remote = False
        try:
            raw = await self.api.get_vehicle_status(self.vin, from_cache=from_cache)
            try:
                charge_control = await self.api.get_charge_control(self.vin)
            except PSACCApiError as err:
                _LOGGER.debug("charge_control indisponible : %s", err)
                charge_control = None
        except PSACCApiError as err:
            self._failures += 1
            if self.data and self._failures <= MAX_FAILURES_KEEP_DATA:
                _LOGGER.warning(
                    "psacc injoignable (%s/%s), conservation des dernières valeurs : %s",
                    self._failures, MAX_FAILURES_KEEP_DATA, err,
                )
                return self.data
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        self._failures = 0
        return {self.vin: {"vin": self.vin, **normalize_status(raw, charge_control)}}

    def get_vehicle_data(self, vin: str) -> Dict[str, Any]:
        """Get data for a specific vehicle."""
        return (self.data or {}).get(vin, {})

    def get_all_vehicles(self) -> Dict[str, Any]:
        """Get all vehicles data."""
        return self.data
