# Testing & Validation Steps

> **Disclaimer:** Running these tests and interpreting their results is your responsibility. The maintainers are not liable for damages, downtime, or data loss that may occur while executing or acting on these procedures.

## Local Python Tests (already running in this repo)
```
cd projects/1408 Renovations/projects/smart-home/hacs-plugins/sunsynk/code
pytest
```
- Covers: API client unit tests (`test_api_client.py`) and coordinator aggregation (`test_coordinator.py`).
- Requirement: `pycryptodome`, `pytest`.

## Home Assistant Platform Tests (pending HA dev container)
1. Install HA dev env (or use `pip install homeassistant` + `pytest-homeassistant-custom-component`).
2. Run hassfest:
   ```
   python -m script.hassfest
   ```
3. Run HA pytest (requires `pytest-homeassistant-custom-component`):
   ```
   pytest tests --durations=10
   ```
4. Optional: `pytest --hass-core` for integration-style tests.

## Manual API Spot Check
When staging credentials are available:
```
cd .../api-explore
python test_routes.py --delay 0.3
```
Confirms remote endpoints remain stable after code changes.

## Notes
- HA-specific tests/hassfest not executed yet because the base Home Assistant tooling is not installed in this workspace. Follow the steps above once the HA dev container is available.
- Record results (pass/fail) in `docs/QA_NOTES.md` after each run.
