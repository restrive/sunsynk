"""Diagnostics support for Sunsynk Sync."""

from __future__ import annotations

from typing import Any

try:  # pragma: no cover
    from homeassistant.components.diagnostics import async_redact_data
except ImportError:  # pragma: no cover
    def async_redact_data(data: Any, keys: set[str]) -> Any:
        return data

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_INVERTER_SN,
    DOMAIN,
)

REDACT_KEYS = {
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_INVERTER_SN,
    "access_token",
    "refresh_token",
    "address",
    "phone",
    "installer",
    "email",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    data = coordinator.data if coordinator else {}
    meta = {}
    if coordinator:
        meta = {
            "last_update_success": getattr(coordinator, "last_update_success", False),
            "last_success_at": getattr(coordinator, "last_success_at", None),
            "last_error": getattr(coordinator, "last_error", None),
        }
    payload = {
        "config": entry.as_dict(),
        "coordinator": {"meta": meta, "data": data},
    }
    return async_redact_data(payload, REDACT_KEYS)
