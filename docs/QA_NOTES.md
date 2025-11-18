# QA Notes

> **Disclaimer:** QA logs are informational only. You assume full responsibility for verifying results and addressing any issues discovered during testing.

## Completed
- `pytest` suite (`tests/test_api_client.py`, `tests/test_coordinator.py`) - `2025-11-18 @ 14:20 SAST`, PASS (uses sanitized fixtures in `tests/fixtures` and includes permission-error coverage).
- `python -m script.hassfest --integration-path custom_components/sunsynk_sync` — `2025-11-18 @ 13:55 SAST`, PASS (no errors/warnings).
- Manual API harness run (`api-explore/test_routes.py --delay 0.3`) — confirmed all 48 routes succeed (see `api-explore/last-run-report.json`).

## Pending (requires Home Assistant dev tooling)
- `pytest --hass-core` (or `pytest-homeassistant-custom-component`).
- End-to-end HA validation (load integration, verify entities appear, trigger refresh button).

## Checklist Before Release
- [ ] Run HA tests above and record outputs here.
- [ ] Capture screenshots/diagnostics demonstrating entity states.
- [ ] Update CHANGELOG/README with any new findings.
