"""Config and options flow for Sunsynk Sync."""

from __future__ import annotations

from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

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

DYNAMIC_HINTS = {
    CONF_EMAIL: "Email used on the Sunsynk portal",
    CONF_PASSWORD: "Portal password (stored securely)",
    CONF_PLANT_ID: "Example format: 221135 (numeric Plant ID from portal URL)",
    CONF_INVERTER_SN: "Example format: 2302100572 (inverter serial printed on device)",
    CONF_LAN: "Example: en (language code)",
    CONF_POLL_INTERVAL: "Refresh interval in seconds (e.g., 30)",
    CONF_WEATHER_COORDS: "Example format: -25.98,28.00 (lat,lon) or leave blank",
}

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL, description={"suggested_value": "", "description": DYNAMIC_HINTS[CONF_EMAIL]}): str,
        vol.Required(CONF_PASSWORD, description={"description": DYNAMIC_HINTS[CONF_PASSWORD]}): str,
        vol.Required(CONF_PLANT_ID, description={"description": DYNAMIC_HINTS[CONF_PLANT_ID]}): str,
        vol.Required(CONF_INVERTER_SN, description={"description": DYNAMIC_HINTS[CONF_INVERTER_SN]}): str,
        vol.Optional(CONF_LAN, default="en", description={"description": DYNAMIC_HINTS[CONF_LAN]}): str,
        vol.Optional(CONF_POLL_INTERVAL, default=30, description={"description": DYNAMIC_HINTS[CONF_POLL_INTERVAL]}): vol.All(int, vol.Range(min=10, max=600)),
        vol.Optional(CONF_INCLUDE_WEATHER, default=False, description={"description": "Toggle weather sensors"}): bool,
        vol.Optional(CONF_WEATHER_COORDS, default="", description={"description": DYNAMIC_HINTS[CONF_WEATHER_COORDS]}): str,
    }
)


class SunsynkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: Dict[str, Any] | None = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_PLANT_ID])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Sunsynk {user_input[CONF_PLANT_ID]}",
                data=user_input,
            )
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(entry: config_entries.ConfigEntry):
        return SunsynkOptionsFlow(entry)


class SunsynkOptionsFlow(config_entries.OptionsFlow):
    """Handle Sunsynk options."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input: Dict[str, Any] | None = None):
        defaults = {
            CONF_POLL_INTERVAL: self._entry.options.get(CONF_POLL_INTERVAL, self._entry.data.get(CONF_POLL_INTERVAL, 30)),
            CONF_INCLUDE_WEATHER: self._entry.options.get(CONF_INCLUDE_WEATHER, self._entry.data.get(CONF_INCLUDE_WEATHER, False)),
            CONF_WEATHER_COORDS: self._entry.options.get(CONF_WEATHER_COORDS, self._entry.data.get(CONF_WEATHER_COORDS, "")),
        }
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_POLL_INTERVAL, default=defaults[CONF_POLL_INTERVAL], description={"description": DYNAMIC_HINTS[CONF_POLL_INTERVAL]}): vol.All(int, vol.Range(min=10, max=600)),
                vol.Required(CONF_INCLUDE_WEATHER, default=defaults[CONF_INCLUDE_WEATHER]): bool,
                vol.Optional(CONF_WEATHER_COORDS, default=defaults[CONF_WEATHER_COORDS], description={"description": DYNAMIC_HINTS[CONF_WEATHER_COORDS]}): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
