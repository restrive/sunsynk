# Sunsynk HACS Integration Task List

> Checklist stitches together structure/learnings from existing plugins (`cudy-scanner`, `ding-scanner`, `kmonitor`) plus the new Sunsynk API explore harness. Items marked ✅ are already handled in this iteration; unchecked boxes should be executed in order.

1. ✅ **Scan existing HACS plugins for structure conventions**
   - Confirm every mature integration keeps `custom_components/<domain>/` with `config_flow.py`, `const.py`, `coordinator.py`, feature platforms (sensor/binary_sensor/button), diagnostics, translations, and docs/tests subfolders.
   - Note supporting docs/backlog patterns (`docs/*`, `research/*`, `MISSING_ITEMS.md`, Task Builder references) from `cudy-scanner`.
2. ✅ **Document learnings + constraints**
   - Capture cross-project requirements (local README, docs for scopes/backlog) under `code/docs/STRUCTURE_NOTES.md`.
   - Record API coverage & sensor candidates extracted via `api-explore` in `code/docs/API_INSIGHTS.md`.
3. ✅ **Lay down integration skeleton under `code/custom_components/sunsynk_sync/`**
   - Create placeholder modules (`__init__.py`, `const.py`, `config_flow.py`, `coordinator.py`, `sensor.py`, `binary_sensor.py`, `button.py`, `diagnostics.py`, `api_client.py`) containing comments only.
   - Include TODO comments referencing the specific Sunsynk API endpoints/data fields that will feed each platform, highlighting token flow via `/anonymous/publicKey` + `/oauth/token/new`.
4. ✅ **Protect sensitive data**
   - Ensure placeholders never hardcode emails/passwords; rely on comments referencing secrets stored in HA `secrets.yaml`.
5. ✅ **Embed API explorer insights as inline comments**
   - For each platform/comment block, point to the relevant route (e.g., `/api/v1/inverter/{sn}/realtime/input` provides `pvPower`, `/api/v1/inverter/battery/{sn}/realtime` provides SOC/voltage, `/api/v1/message/count` for sensors).
6. ☐ **Implement `manifest.json` & localization**
   - Populate manifest metadata (name, version, requirements), referencing dependencies discovered in other plugins.
   - Create `strings.json` translations (en) and map config/options forms.
7. ☐ **Build dedicated client + coordinator**
   - Implement authenticated session (reuse logic from `api_client.py` comments), caching tokens, respecting rate limits noted in `api-explore`.
   - Coordinator should bundle plant + inverter snapshots so multiple platforms reuse a single refresh.
8. ☐ **Implement platforms**
   - Sensors: PV/Load/Grid/Battery power, SOC, weather, message counts.
   - Binary sensors: grid availability, battery charge/discharge state.
   - Buttons/Services: e.g., planned “refresh now” or “acknowledge message” once API write support is scoped.
9. ☐ **Diagnostics/logging/test scaffolding**
   - Mirror `cudy-scanner`’s diagnostics export plus targeted pytest fixtures for mocked API responses.
10. ☐ **Docs & Release Prep**
    - Write README/install guide, backlog, validation checklist, and ensure no sensitive info in committed files before tagging initial version.

