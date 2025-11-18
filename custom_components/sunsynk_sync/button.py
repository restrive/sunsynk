"""Buttons for Sunsynk Sync."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api_client import SunsynkApiClient
from .const import CONF_PLANT_ID, DOMAIN
from .coordinator import SunsynkCoordinator


@dataclass
class SunsynkButtonDescription(ButtonEntityDescription):
    """Description for Sunsynk buttons."""

    action: str = "refresh"


BUTTON_DESCRIPTIONS: tuple[SunsynkButtonDescription, ...] = (
    SunsynkButtonDescription(
        key="manual_refresh",
        name="Refresh Sunsynk Data",
        action="refresh",
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
    """Set up button entities for a config entry."""
    coordinator: SunsynkCoordinator = hass.data[DOMAIN][entry.entry_id]
    client: SunsynkApiClient = coordinator._client  # type: ignore[attr-defined]
    entities = [
        SunsynkButton(coordinator, client, description, entry)
        for description in BUTTON_DESCRIPTIONS
    ]
    async_add_entities(entities)


class SunsynkButton(CoordinatorEntity[SunsynkCoordinator], ButtonEntity):
    """Representation of a Sunsynk button."""

    entity_description: SunsynkButtonDescription

    def __init__(
        self,
        coordinator: SunsynkCoordinator,
        client: SunsynkApiClient,
        description: SunsynkButtonDescription,
        entry,
    ) -> None:
        super().__init__(coordinator)
        self._client = client
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        plant_id = entry.data.get(CONF_PLANT_ID, "Sunsynk")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Sunsynk Plant {plant_id}",
            manufacturer="Sunsynk",
        )

    async def async_press(self) -> None:
        """Handle button press actions."""
        if self.entity_description.action == "refresh":
            await self.coordinator.async_request_refresh()
