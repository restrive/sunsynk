from types import SimpleNamespace

from custom_components.sunsynk_sync.coordinator import SunsynkCoordinator
from custom_components.sunsynk_sync.sensor import (
    SENSOR_DESCRIPTIONS,
    SunsynkInverterStatusSensor,
    SunsynkPvArraySensor,
    SunsynkSensor,
)


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


def _summary_payload():
    return {
        "inverter_summary": {
            "pac": 1246,
            "ratePower": 8000,
            "etoday": 26.2,
            "emonth": 408.0,
            "eyear": 7230.8,
            "etotal": 20582.0,
            "runStatus": "Normal",
            "status": 1,
            "alias": "Gericke",
            "brand": "Deye",
            "model": "",
            "sn": "2302100572",
            "updateAt": "2025-11-18T15:16:14Z",
            "plant": {
                "installer": "Set-the-bar Installers",
                "email": "setthebarinstallers@gmail.com",
                "phone": "(072) 2382241",
            },
            "version": {
                "masterVer": "6.0.2.7",
                "softVer": "1.7.2.4",
                "hmiVer": "E.4.3.D",
            },
        }
    }


def _get_description(key: str):
    return next(desc for desc in SENSOR_DESCRIPTIONS if desc.key == key)


def test_inverter_energy_sensors_use_summary_payload():
    coordinator = _build_coordinator(_summary_payload())
    entry = _entry()
    desc = _get_description("inverter_energy_today")
    sensor = SunsynkSensor(coordinator, desc, entry)
    assert sensor.native_value == 26.2
    assert sensor.available

    power_desc = _get_description("inverter_power")
    power_sensor = SunsynkSensor(coordinator, power_desc, entry)
    assert power_sensor.native_value == 1246.0


def test_inverter_status_sensor_exposes_attributes():
    coordinator = _build_coordinator(_summary_payload())
    sensor = SunsynkInverterStatusSensor(coordinator, _entry())
    assert sensor.native_value == "Normal"
    attrs = sensor.extra_state_attributes
    assert attrs["alias"] == "Gericke"
    assert attrs["status_code"] == 1
    assert attrs["installer"] == "Set-the-bar Installers"
    assert sensor.available is True
