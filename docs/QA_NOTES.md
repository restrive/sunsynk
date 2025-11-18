# QA Notes

> **Disclaimer:** QA logs are informational only. You assume full responsibility for verifying results and addressing any issues discovered during testing.
## Completed
- `pytest` suite (API client + coordinator) – `2025-11-18`.
- Manual API harness run (`api-explore/test_routes.py --delay 0.3`) – confirmed all 48 routes succeed.

## Pending (requires Home Assistant dev tooling) � hassfest + HA pytest queued once HA env ready
- `python -m script.hassfest`
- `pytest --hass-core` (or `pytest-homeassistant-custom-component`)
- End-to-end HA validation (load integration, verify entities appear, trigger refresh button).

## Checklist Before Release
- [ ] Run HA tests above and record outputs here.
- [ ] Capture screenshots/diagnostics demonstrating entity states.
- [ ] Update CHANGELOG/README with any new findings.


