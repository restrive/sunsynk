# Structure & Process Learnings (from Cudy Scanner, Ding Scanner, Kmonitor)

- **Custom components layout**
  - All integrations use `custom_components/<domain>/` with:
    - `__init__.py` / entry setup + unload.
    - `const.py` for domain name, config keys, default intervals.
    - `config_flow.py` (and sometimes `options_flow.py`) for UI setup, using HA’s `ConfigFlow`.
    - Feature platforms (`sensor.py`, `binary_sensor.py`, `button.py`, etc.) each referencing a shared `DataUpdateCoordinator`.
    - `coordinator.py` (or `client.py`) to isolate network calls.
    - `diagnostics.py` for redacted exports.
    - `manifest.json`, `strings.json`, and `translations/` folder.
  - `ding-scanner` already stubs folders for providers/passive scanners, hinting that feature-specific subpackages are acceptable when the domain grows.

- **Supporting folders**
  - `docs/` includes scope/backlog/validation notes (`MISSING_ITEMS.md`, `VALIDATION_REPORT.md`) to keep work visible without bloating README.
  - `research/` stores vendor/developer notes, Task Builder plans, and API raw captures.
  - `tests/` (present in `cudy-scanner`) mirror HA expectations using pytest fixtures with recorded payloads.

- **Process artifacts**
  - Each project references a Task Builder plan stored under `experts/task-builder/tasks/*.md`; our TASKLIST piggybacks this habit.
  - CHANGELOG + version bumping even for scaffolds (v0.0.1/v0.1.0) are standard.
  - Debug logging/diagnostics are prioritized even before feature-complete (see `kmonitor`).

These patterns drive the Sunsynk skeleton: follow the same folder layout, pre-create docs for backlog/API, and rely on coordinator-driven refreshes feeding multiple platforms.

