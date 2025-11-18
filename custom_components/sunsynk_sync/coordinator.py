"""DataUpdateCoordinator for Sunsynk Sync."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Optional

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
            flow_task = self._client.async_get_flow()
            input_task = self._client.async_get_inverter_realtime("input")
            output_task = self._client.async_get_inverter_realtime("output")
            grid_task = self._client.async_get_inverter_realtime("grid")
            battery_task = self._client.async_get_inverter_realtime("battery")
            load_task = self._client.async_get_inverter_realtime("load")
            plant_rt_task = self._client.async_get_plant_realtime()
            plant_summary_task = self._client.async_get_plant_summary()
            message_task = self._client.async_get_message_count()
            inverter_counts_task = self._client.async_get_inverter_counts()
            gen_use_task = self._client.async_get_generation_use()

            tasks = [
                flow_task,
                input_task,
                output_task,
                grid_task,
                battery_task,
                load_task,
                plant_rt_task,
                plant_summary_task,
                message_task,
                inverter_counts_task,
                gen_use_task,
            ]

            if self._include_weather and self._weather_lon_lat:
                weather_task = self._client.async_get_weather(self._weather_lon_lat)
                tasks.append(weather_task)
            else:
                weather_task = None

            results = await asyncio.gather(*tasks, return_exceptions=True)

            data = {
                "flow": results[0],
                "pv_input": results[1],
                "ac_output": results[2],
                "grid": results[3],
                "battery": results[4],
                "load": results[5],
                "plant_realtime": results[6],
                "plant_summary": results[7],
                "message_count": results[8],
                "inverter_counts": results[9],
                "generation_use": results[10],
            }

            if weather_task:
                weather_result = results[-1]
                if isinstance(weather_result, Exception):
                    _LOGGER.warning("Weather fetch failed: %s", weather_result)
                else:
                    data["weather"] = weather_result

            for key, value in data.items():
                if isinstance(value, Exception):
                    raise value

            self.last_success_at = asyncio.get_event_loop().time()
            self.last_error = None
            return data  # type: ignore[return-value]

        except SunsynkApiError as err:
            self.last_error = str(err)
            _LOGGER.error("Coordinator update failed: %s", err)
            raise UpdateFailed(f"Sunsynk API error: {err}") from err
        except Exception as err:  # pragma: no cover - safety net
            self.last_error = str(err)
            _LOGGER.exception("Unexpected error updating Sunsynk data")
            raise UpdateFailed(f"Unexpected error: {err}") from err
