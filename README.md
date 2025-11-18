# Sunsynk Sync (HACS Scaffold)

## Status
- Version: 0.0.1 (skeleton)
- Purpose: Surface Sunsynk inverter + plant metrics inside Home Assistant using the new portal APIs.

> **Disclaimer:** This integration is provided "as is" without warranties of any kind. Use at your own risk; the maintainers are not liable for damages, data loss, or regulatory issues that may arise from installing or operating this code.

## Planned Features (see docs/SENSOR_MAP.md)
1. Plant KPIs (power, energy, revenue)
2. Inverter summary + per-string PV telemetry
3. Grid / Battery / Load metrics
4. Energy flow and generation vs use breakdowns
5. Weather, message counters, diagnostic sensors

## Roadmap / Status
- [x] OAuth client + coordinator
- [x] Sensor + binary sensor + button platforms (initial entities from `docs/SENSOR_MAP.md`)
- [x] Config + options flows
- [x] Diagnostics export (`custom_components/sunsynk_sync/diagnostics.py`)
- [x] Local pytest suite (`tests/test_api_client.py`, `tests/test_coordinator.py`)
- [ ] HA-specific validation (`hassfest`, `pytest-homeassistant-custom-component`) — see `docs/TESTING.md`
- [ ] Documentation polish + release packaging

## Development
- Code lives in custom_components/sunsynk_sync
- Supporting docs under docs/
- API exploration harness: ../api-explore
- Follow Task Builder plan (experts/task-builder/tasks/sunsynk-hacs-build-plan.20251118.v0.1.md)

## Debugging & Logging
- Each module uses `logging.getLogger(__name__)`; enabling debug level for `custom_components.sunsynk_sync` surfaces:
  - Auth lifecycle (masked email + plant ID).
  - Each REST request (`method endpoint params`).
  - Coordinator refresh start/end plus weather fetch status.
- Errors capture Sunsynk API messages and store `coordinator.last_error` for diagnostics export.
- Partial failures are tolerated: data["route_errors"] lists per-endpoint failures so other sensors keep updating while diagnostics show the issue.
- Diagnostics (`Settings → System → Repairs → Download Diagnostics`) now include `last_success_at` timestamps and the current coordinator payload (with sensitive fields redacted).
## PV Array Sensors
- `/api/v1/inverter/{sn}/realtime/input` responses often expose multiple `pvIV` strings; the integration now auto-creates `PV Array {n} Power` sensors for each string.
- Each sensor reports instantaneous power (W) and includes voltage/current attributes, giving immediate visibility into misbehaving arrays.
- Sensors are discovered dynamically after each coordinator refresh, so wiring up a new string in Sunsynk automatically surfaces a matching entity without reloading the integration.


## Security Notes
- Never commit real credentials or plant metadata.
- Use HA secrets for storing email/password.
- Diagnostics must redact tokens, serials, installer contact info.
