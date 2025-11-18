"""DataUpdateCoordinator for Sunsynk Sync."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

try:  # pragma: no cover - allow running tests without Home Assistant
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
except ImportError:  # pragma: no cover
    from typing import Any

    HomeAssistant = Any  # type: ignore[assignment]

    class DataUpdateCoordinator:  # type: ignore[override]
        def __init__(self, hass, logger, name, update_interval):
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval

    class UpdateFailed(Exception):
        """Fallback UpdateFailed."""

from .api_client import SunsynkApiClient, SunsynkApiError
from .const import DEFAULT_POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)
SCALAR_ROUTE_KEYS = {"message_count"}


class SunsynkCoordinator(DataUpdateCoordinator):  # type: ignore[misc]
    """Coordinator that aggregates Sunsynk API responses."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        client: SunsynkApiClient,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        include_weather: bool = False,
        weather_lon_lat: Optional[str] = None,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Sunsynk Sync Coordinator",
            update_interval=timedelta(seconds=poll_interval),
        )
        self._client = client
        self._include_weather = include_weather
        self._weather_lon_lat = weather_lon_lat
        self.last_success_at: Optional[float] = None
        self.last_error: Optional[str] = None

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            _LOGGER.debug("Refreshing Sunsynk data (weather=%s)", self._include_weather)
            task_defs: list[Tuple[str, bool, Any]] = [
                ("inverter_summary", False, self._client.async_get_inverter_summary()),
                ("flow", False, self._client.async_get_flow()),
                ("pv_input", False, self._client.async_get_inverter_realtime("input")),
                ("ac_output", False, self._client.async_get_inverter_realtime("output")),
                ("grid", False, self._client.async_get_inverter_realtime("grid")),
                ("battery", False, self._client.async_get_inverter_realtime("battery")),
                ("load", False, self._client.async_get_inverter_realtime("load")),
                ("plant_realtime", False, self._client.async_get_plant_realtime()),
                ("plant_summary", False, self._client.async_get_plant_summary()),
                ("message_count", False, self._client.async_get_message_count()),
                ("inverter_counts", False, self._client.async_get_inverter_counts()),
                ("generation_use", False, self._client.async_get_generation_use()),
            ]

            if self._include_weather and self._weather_lon_lat:
                task_defs.append(
                    ("weather", True, self._client.async_get_weather(self._weather_lon_lat))
                )

            results = await asyncio.gather(
                *(task for _, _, task in task_defs), return_exceptions=True
            )

            data: Dict[str, Any] = {}
            route_errors: Dict[str, str] = {}
            success_count = 0

            for (key, optional, _), result in zip(task_defs, results):
                if isinstance(result, Exception):
                    route_errors[key] = str(result)
                    if not optional:
                        data[key] = {} if key not in SCALAR_ROUTE_KEYS else None
                    continue
                data[key] = result
                if not optional:
                    success_count += 1

            if success_count == 0:
                error_msg = "; ".join(route_errors.values()) or "unknown error"
                self.last_error = error_msg
                raise UpdateFailed(f"Sunsynk API error: {error_msg}")

            if route_errors:
                data["route_errors"] = route_errors
                self.last_error = "; ".join(
                    f"{route}: {message}" for route, message in route_errors.items()
                )
                _LOGGER.warning("Partial Sunsynk update due to route errors: %s", route_errors)
            else:
                self.last_error = None

            self.last_success_at = asyncio.get_event_loop().time()
            return data  # type: ignore[return-value]

        except SunsynkApiError as err:
            self.last_error = str(err)
            _LOGGER.error("Coordinator update failed: %s", err)
            raise UpdateFailed(f"Sunsynk API error: {err}") from err
        except Exception as err:  # pragma: no cover - safety net
            self.last_error = str(err)
            _LOGGER.exception("Unexpected error updating Sunsynk data")
            raise UpdateFailed(f"Unexpected error: {err}") from err
