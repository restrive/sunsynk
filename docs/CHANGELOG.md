# Changelog

> **Disclaimer:** Release notes describe changes without implying warranties. Validate every build in your environment before production use.

## 0.1.1 (2025-11-30)
- **Fixed:** Authentication failure with Sunsynk API (`Internal Server Error` on `/oauth/token/new`).
- Updated token request to include required `sign` and `nonce` parameters per Sunsynk's updated API spec.
- Token sign now uses first 10 characters of the public key as salt instead of `POWER_VIEW`.

## 0.1.0 (2025-11-18)
- Added legacy-route fallbacks plus route-error diagnostics so permission failures no longer block refreshes.
- Introduced dynamic PV Array sensors with voltage/current attributes and runtime discovery.
- Added inverter summary polling with power/energy sensors and an `Inverter Run Status` entity exposing firmware + installer metadata.
- Expanded README, SENSOR_MAP, and QA notes to cover the new sensors and documented pytest/API harness runs.
- Added `tests/test_sensor.py` coverage for PV arrays and inverter summary/status sensors; full pytest suite now covers 11 tests.

## 0.0.1 (Scaffold)
- Added manifest, translations, and README.
- Implemented Sunsynk OAuth client (`api_client.py`) + coordinator (`coordinator.py`).
- Added sensor/binary sensor/button platforms with coordinator-backed entities.
- Added diagnostics export and config/options flows.
- Local pytest suite for client + coordinator; HA-specific tests pending (`docs/TESTING.md`).
