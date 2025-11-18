"""Shared constants for Sunsynk Sync."""

from __future__ import annotations

DOMAIN = "sunsynk_sync"

# Config keys
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_PLANT_ID = "plant_id"
CONF_INVERTER_SN = "inverter_sn"
CONF_LAN = "lan"
CONF_POLL_INTERVAL = "poll_interval"
CONF_INCLUDE_WEATHER = "include_weather"
CONF_ENABLE_PV_DETAIL = "enable_pv_detail"
CONF_ENABLE_DEBUG = "enable_debug"
CONF_WEATHER_COORDS = "weather_lon_lat"

DATA_COORDINATOR = "coordinator"
DATA_CLIENT = "client"

DEFAULT_BASE_URL = "https://api.sunsynk.net"
DEFAULT_SOURCE = "sunsynk"
DEFAULT_LAN = "en"
DEFAULT_POLL_INTERVAL = 30  # seconds

FLOW_ENDPOINT = "/api/v1/inverter/{sn}/flow"
REALTIME_ENDPOINT = "/api/v1/inverter/{sn}/realtime/{category}"
PLANT_REALTIME_ENDPOINT = "/api/v1/plant/{plant_id}/realtime"
PLANT_SUMMARY_ENDPOINT = "/api/v1/plant/{plant_id}"
WEATHER_ENDPOINT = "/api/v1/weather"
MESSAGE_COUNT_ENDPOINT = "/api/v1/message/count"
INVERTER_COUNT_ENDPOINT = "/api/v1/inverters/count"
GEN_USE_ENDPOINT = "/api/v1/plant/energy/{plant_id}/generation/use"
