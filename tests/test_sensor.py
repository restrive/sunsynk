from types import SimpleNamespace

from custom_components.sunsynk_sync.coordinator import SunsynkCoordinator
from custom_components.sunsynk_sync.sensor import SunsynkPvArraySensor


def _build_coordinator(payload):
    coordinator = SunsynkCoordinator(
        hass=None,  # type: ignore[arg-type]
        client=object(),  # client not used for these tests
        poll_interval=30,
        include_weather=False,
        weather_lon_lat=None,
    )
    coordinator.data = payload
    coordinator.last_update_success = True
    return coordinator


def _entry():
    return SimpleNamespace(entry_id="entry123", data={"plant_id": "221135"})


def test_pv_array_sensor_reports_power_and_attributes():
    payload = {
        "pv_input": {
            "pvIV": [
                {"vpv": "207.7", "ipv": "5.5", "ppv": "1142.4"},
                {"vpv": "210.3", "ipv": "5.2", "ppv": "1093.6"},
            ]
        }
    }
    coordinator = _build_coordinator(payload)
    sensor = SunsynkPvArraySensor(coordinator, _entry(), 0)
    assert sensor.native_value == 1142.4
    assert sensor.extra_state_attributes["voltage"] == 207.7
    assert sensor.extra_state_attributes["current"] == 5.5
    assert sensor.available is True


def test_pv_array_sensor_handles_missing_array():
    coordinator = _build_coordinator({"pv_input": {"pvIV": []}})
    sensor = SunsynkPvArraySensor(coordinator, _entry(), 1)
    assert sensor.native_value is None
    assert sensor.available is False
