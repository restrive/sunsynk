"""Binary sensors for Sunsynk Sync."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PLANT_ID, DOMAIN
from .coordinator import SunsynkCoordinator


@dataclass
class SunsynkBinarySensorDescription(BinarySensorEntityDescription):
    """Binary sensor description for Sunsynk."""

    value_fn: Callable[[dict[str, Any]], bool] = lambda _: False
    available_fn: Optional[Callable[[dict[str, Any]], bool]] = None


BINARY_SENSOR_DESCRIPTIONS: tuple[SunsynkBinarySensorDescription, ...] = (
    SunsynkBinarySensorDescription(
        key="grid_available",
        name="Grid Available",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: data["grid"]["status"] == 1,
    ),
    SunsynkBinarySensorDescription(
        key="battery_charging",
        name="Battery Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda data: data["battery"]["power"] > 0,
    ),
    SunsynkBinarySensorDescription(
        key="notification_pending",
        name="Notifications Pending",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data["message_count"] > 0,
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
    """Set up binary sensors from a config entry."""
    coordinator: SunsynkCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        SunsynkBinarySensor(coordinator, description, entry)
        for description in BINARY_SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class SunsynkBinarySensor(CoordinatorEntity[SunsynkCoordinator], BinarySensorEntity):
    """Representation of a Sunsynk binary sensor."""

    entity_description: SunsynkBinarySensorDescription

    def __init__(
        self,
        coordinator: SunsynkCoordinator,
        description: SunsynkBinarySensorDescription,
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
    def is_on(self) -> bool:
        return bool(self.entity_description.value_fn(self.coordinator.data or {}))

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        checker = self.entity_description.available_fn
        if checker is None:
            return True
        return bool(checker(self.coordinator.data or {}))
