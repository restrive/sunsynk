# QA Notes

> **Disclaimer:** QA logs are informational only. You assume full responsibility for verifying results and addressing any issues discovered during testing.

## Completed
- `pytest` suite (`tests/test_api_client.py`, `tests/test_coordinator.py`) - `2025-11-18 @ 15:02 SAST`, PASS (uses sanitized fixtures in `tests/fixtures` and includes permission-error coverage).
- `pytest` suite (legacy realtime routing + partial-error coverage) - `2025-11-18 @ 16:20 SAST`, PASS (adds tests ensuring battery/load/grid use `/api/v1/inverter/{category}/{sn}/realtime` and coordinator surfaces `route_errors` when an endpoint fails).
- `pytest` suite (PV array sensors) - `2025-11-18 @ 17:30 SAST`, PASS (includes new `tests/test_sensor.py` verifying per-string power + attributes).
- `python -m script.hassfest --integration-path custom_components/sunsynk_sync` - `2025-11-18 @ 15:05 SAST`, PASS (no errors/warnings; libturbojpeg warning expected).
- Manual API harness run (`api-explore/test_routes.py --delay 0.3`) - confirmed all 48 routes succeed (see `api-explore/last-run-report.json`).
- Targeted HA-style realtime routes (`python test_routes.py --routes routes.ha_realtime.json --delay 0.3`) - `2025-11-18 @ 15:40 SAST`, **FAIL** (200 OK but payload lacks `data`; responses return `code=2` / `msg="No Permissions"` for `/api/v1/inverter/{sn}/realtime/{battery|load|grid}`; captured in `api-explore/last-run-report-ha-realtime.json`).
- Legacy realtime routes from manifest (`python test_routes.py --only inverter_realtime_battery inverter_realtime_load inverter_realtime_grid --delay 0.3`) - `2025-11-18 @ 16:55 SAST`, PASS (all endpoints return `code=0` with telemetry; see `api-explore/last-run-report-legacy-realtime.json`).

## Pending (requires Home Assistant dev tooling)
- `pytest --hass-core` (or `pytest-homeassistant-custom-component`).
- End-to-end HA validation (load integration, verify entities appear, trigger refresh button).

## Checklist Before Release
- [ ] Run HA tests above and record outputs here.
- [ ] Capture screenshots/diagnostics demonstrating entity states.
- [ ] Update CHANGELOG/README with any new findings.
