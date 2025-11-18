"""Sunsynk Sync integration entry-points."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

try:
    from homeassistant.helpers import config_validation as cv
except ImportError:  # pragma: no cover - fallback when HA not installed in tests
    class _DummyCV:  # type: ignore[too-many-ancestors]
        @staticmethod
        def config_entry_only_config_schema(domain: str):
            return {}

    cv = _DummyCV()  # type: ignore[assignment]

from .api_client import SunsynkApiClient
from .const import (
    CONF_EMAIL,
    CONF_INCLUDE_WEATHER,
    CONF_INVERTER_SN,
    CONF_LAN,
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_POLL_INTERVAL,
    CONF_WEATHER_COORDS,
    DOMAIN,
)
from .coordinator import SunsynkCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up via YAML (not used)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sunsynk Sync from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    data: Mapping[str, Any] = entry.data
    options: Mapping[str, Any] = entry.options or {}

    client = SunsynkApiClient(
        session,
        email=data[CONF_EMAIL],
        password=data[CONF_PASSWORD],
        plant_id=data[CONF_PLANT_ID],
        inverter_sn=data[CONF_INVERTER_SN],
        lan=data.get(CONF_LAN, "en"),
    )

    poll_interval = options.get(CONF_POLL_INTERVAL, data.get(CONF_POLL_INTERVAL, 30))
    include_weather = options.get(CONF_INCLUDE_WEATHER, data.get(CONF_INCLUDE_WEATHER, False))
    weather_lon_lat = options.get(CONF_WEATHER_COORDS) or data.get(CONF_WEATHER_COORDS)

    coordinator = SunsynkCoordinator(
        hass,
        client=client,
        poll_interval=poll_interval,
        include_weather=include_weather,
        weather_lon_lat=weather_lon_lat,
    )
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
