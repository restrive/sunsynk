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
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
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

    known_arrays: set[int] = set()

    def _discover_pv_arrays() -> None:
        data = coordinator.data or {}
        pv_rows = data.get("pv_input", {}).get("pvIV") or []
        new_entities: list[SunsynkPvArraySensor] = []
        for index in range(len(pv_rows)):
            if index in known_arrays:
                continue
            known_arrays.add(index)
            new_entities.append(SunsynkPvArraySensor(coordinator, entry, index))
        if new_entities:
            async_add_entities(new_entities)

    _discover_pv_arrays()
    remove_listener = coordinator.async_add_listener(_discover_pv_arrays)
    entry.async_on_unload(remove_listener)


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


class SunsynkPvArraySensor(CoordinatorEntity[SunsynkCoordinator], SensorEntity):
    """Sensor for a specific PV array/string."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(
        self,
        coordinator: SunsynkCoordinator,
        entry,
        index: int,
    ) -> None:
        super().__init__(coordinator)
        self._index = index
        self._attr_name = f"PV Array {index + 1} Power"
        self._attr_unique_id = f"{entry.entry_id}_pv_array_{index + 1}"
        plant_id = entry.data.get(CONF_PLANT_ID, "Sunsynk")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Sunsynk Plant {plant_id}",
            manufacturer="Sunsynk",
        )

    def _array_data(self) -> Optional[dict[str, Any]]:
        data = self.coordinator.data or {}
        pv_rows = data.get("pv_input", {}).get("pvIV") or []
        if self._index < len(pv_rows):
            return pv_rows[self._index]
        return None

    @property
    def native_value(self) -> Optional[float]:
        row = self._array_data()
        if not row:
            return None
        try:
            return float(row.get("ppv"))
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        row = self._array_data() or {}
        attrs: dict[str, Any] = {}
        voltage = row.get("vpv")
        current = row.get("ipv")
        if voltage is not None:
            try:
                attrs["voltage"] = float(voltage)
            except (TypeError, ValueError):
                attrs["voltage"] = voltage
        if current is not None:
            try:
                attrs["current"] = float(current)
            except (TypeError, ValueError):
                attrs["current"] = current
        return attrs

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        return self._array_data() is not None
