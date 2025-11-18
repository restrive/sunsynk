"""Sensor platform for Sunsynk Sync."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfPower, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PLANT_ID, DOMAIN
from .coordinator import SunsynkCoordinator


def _safe(fn: Callable[[dict[str, Any]], Any]) -> Callable[[dict[str, Any]], Any]:
    def wrapper(data: dict[str, Any]) -> Any:
        try:
            return fn(data)
        except (KeyError, TypeError, IndexError, ValueError):
            return None

    return wrapper


@dataclass
class SunsynkSensorDescription(SensorEntityDescription):
    """Description for Sunsynk sensors."""

    value_fn: Callable[[dict[str, Any]], Any] = lambda _: None
    available_fn: Optional[Callable[[dict[str, Any]], bool]] = None


SENSOR_DESCRIPTIONS: tuple[SunsynkSensorDescription, ...] = (
    SunsynkSensorDescription(
        key="plant_pac",
        name="Plant Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=_safe(lambda data: data["plant_realtime"]["pac"]),
    ),
    SunsynkSensorDescription(
        key="plant_etoday",
        name="Plant Energy Today",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=_safe(lambda data: data["plant_realtime"]["etoday"]),
    ),
    SunsynkSensorDescription(
        key="plant_etotal",
        name="Plant Energy Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=_safe(lambda data: data["plant_realtime"]["etotal"]),
    ),
    SunsynkSensorDescription(
        key="plant_income",
        name="Plant Income Today",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_safe(lambda data: data["plant_realtime"]["income"]),
    ),
    SunsynkSensorDescription(
        key="pv_power",
        name="PV Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=_safe(lambda data: sum(float(pv["ppv"]) for pv in data["pv_input"].get("pvIV", []))),
        available_fn=lambda data: bool(data["pv_input"].get("pvIV")),
    ),
    SunsynkSensorDescription(
        key="grid_power",
        name="Grid Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=_safe(lambda data: data["grid"]["pac"]),
    ),
    SunsynkSensorDescription(
        key="grid_frequency",
        name="Grid Frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="Hz",
        value_fn=_safe(lambda data: data["grid"]["fac"]),
    ),
    SunsynkSensorDescription(
        key="battery_soc",
        name="Battery State of Charge",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        value_fn=_safe(lambda data: data["battery"].get("bmsSoc") or float(data["battery"]["soc"])),
    ),
    SunsynkSensorDescription(
        key="battery_power",
        name="Battery Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=_safe(lambda data: data["battery"]["power"]),
    ),
    SunsynkSensorDescription(
        key="load_power",
        name="Load Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=_safe(lambda data: data["load"]["totalPower"]),
    ),
    SunsynkSensorDescription(
        key="load_daily_energy",
        name="Load Energy Today",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=_safe(lambda data: data["load"]["dailyUsed"]),
    ),
    SunsynkSensorDescription(
        key="weather_temperature",
        name="Outdoor Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_safe(lambda data: float(data["weather"]["currWea"]["currTemp"])),
        available_fn=lambda data: "weather" in data,
    ),
    SunsynkSensorDescription(
        key="weather_wind_speed",
        name="Wind Speed",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="m/s",
        value_fn=_safe(lambda data: float(data["weather"]["currWea"]["windSpeed"])),
        available_fn=lambda data: "weather" in data,
    ),
    SunsynkSensorDescription(
        key="message_unread",
        name="Unread Notifications",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_safe(lambda data: data["message_count"]),
    ),
    SunsynkSensorDescription(
        key="inverter_faults",
        name="Inverters in Fault",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_safe(lambda data: data["inverter_counts"]["fault"]),
    ),
    SunsynkSensorDescription(
        key="flow_soc",
        name="Flow SOC",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        value_fn=_safe(lambda data: data["flow"]["soc"]),
    ),
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Deprecated platform setup."""


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities for config entry."""
    coordinator: SunsynkCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        SunsynkSensor(coordinator, description, entry)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class SunsynkSensor(CoordinatorEntity[SunsynkCoordinator], SensorEntity):
    """Representation of a Sunsynk sensor."""

    entity_description: SunsynkSensorDescription

    def __init__(
        self,
        coordinator: SunsynkCoordinator,
        description: SunsynkSensorDescription,
        entry,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        plant_id = entry.data.get(CONF_PLANT_ID, "Sunsynk")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Sunsynk Plant {plant_id}",
            manufacturer="Sunsynk",
        )

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return self.entity_description.value_fn(data)

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        checker = self.entity_description.available_fn
        if checker is None:
            return True
        return bool(checker(self.coordinator.data or {}))
