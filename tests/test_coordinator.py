import asyncio
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from custom_components.sunsynk_sync.api_client import SunsynkApiClient  # noqa: E402
from custom_components.sunsynk_sync.coordinator import (  # noqa: E402
    SunsynkCoordinator,
    UpdateFailed,
)


class FixtureClient(SunsynkApiClient):
    def __init__(self, fixture_dir: Path) -> None:
        self._fixture_dir = fixture_dir

    async def async_get_flow(self):
        return self._load("inverter_flow.json")

    async def async_get_inverter_realtime(self, category: str):
        mapping = {
            "input": "inverter_realtime_input.json",
            "output": "inverter_realtime_output.json",
            "grid": "inverter_realtime_grid.json",
            "battery": "inverter_realtime_battery.json",
            "load": "inverter_realtime_load.json",
        }
        return self._load(mapping[category])

    async def async_get_plant_realtime(self):
        return self._load("plant_realtime.json")

    async def async_get_plant_summary(self):
        return self._load("plant_summary.json")

    async def async_get_message_count(self):
        return self._load("message_count.json")

    async def async_get_inverter_counts(self):
        return self._load("inverters_count.json")

    async def async_get_generation_use(self):
        return self._load("plant_generation_use.json")

    async def async_get_weather(self, lon_lat: str):
        return self._load("weather_by_location.json")

    def _load(self, filename: str):
        path = self._fixture_dir / filename
        data = json.loads(path.read_text())
        return data.get("data", data)


async def _run_coordinator():
    fixture_dir = Path(__file__).resolve().parent / "fixtures"
    client = FixtureClient(fixture_dir)
    coordinator = SunsynkCoordinator(
        hass=None,  # type: ignore[arg-type]
        client=client,
        poll_interval=30,
        include_weather=True,
        weather_lon_lat="-25.980585973335,28.00603438051",
    )
    return await coordinator._async_update_data()


def test_coordinator_collects_all_payloads():
    data = asyncio.run(_run_coordinator())
    assert data["flow"]["pvPower"] == 0
    assert data["pv_input"]["pvIV"][0]["vpv"] == "207.7"
    assert data["battery"]["soc"] == "27.0"
    assert data["plant_realtime"]["pac"] == 1400
    assert data["weather"]["currWea"]["desc"] == "mist"


class PartialFailureClient(FixtureClient):
    async def async_get_inverter_realtime(self, category: str):
        if category == "battery":
            raise RuntimeError("battery permission error")
        return await super().async_get_inverter_realtime(category)


async def _run_partial_coordinator():
    fixture_dir = Path(__file__).resolve().parent / "fixtures"
    client = PartialFailureClient(fixture_dir)
    coordinator = SunsynkCoordinator(
        hass=None,  # type: ignore[arg-type]
        client=client,
        poll_interval=30,
        include_weather=False,
    )
    return await coordinator._async_update_data()


def test_coordinator_returns_partial_data_and_errors():
    data = asyncio.run(_run_partial_coordinator())
    assert data["plant_realtime"]["pac"] == 1400
    assert data["battery"] == {}
    assert "route_errors" in data
    assert "battery" in data["route_errors"]


class AllFailClient:
    async def async_get_flow(self):
        raise RuntimeError("flow boom")

    async def async_get_inverter_realtime(self, category: str):
        raise RuntimeError(f"{category} boom")

    async def async_get_plant_realtime(self):
        raise RuntimeError("plant boom")

    async def async_get_plant_summary(self):
        raise RuntimeError("summary boom")

    async def async_get_message_count(self):
        raise RuntimeError("msg boom")

    async def async_get_inverter_counts(self):
        raise RuntimeError("count boom")

    async def async_get_generation_use(self):
        raise RuntimeError("gen boom")


def test_coordinator_raises_when_all_routes_fail():
    client = AllFailClient()
    coordinator = SunsynkCoordinator(
        hass=None,  # type: ignore[arg-type]
        client=client,  # type: ignore[arg-type]
        poll_interval=30,
        include_weather=False,
    )
    with pytest.raises(UpdateFailed):
        asyncio.run(coordinator._async_update_data())
