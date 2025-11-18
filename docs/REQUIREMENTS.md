# Sunsynk Sync – Consolidated Requirements

> **Disclaimer:** All requirements and implementation guidance are provided without warranty. Integrators assume full responsibility for ensuring compliance, data safety, and operational correctness.

Derived from:
- `STRUCTURE_NOTES.md` (cross-project conventions)
- `API_INSIGHTS.md`
- `SENSOR_MAP.md`
- `api-explore` cache (2025-11-18 run)

## Goal & Scope
Deliver a HACS-ready Home Assistant integration that exposes Sunsynk inverter + plant telemetry, weather, and system counters while following HA config/diagnostics conventions. All tokens handled securely via Sunsynk’s new OAuth flow (`/anonymous/publicKey` ➜ `/oauth/token/new`).

## MVP Entity Coverage
1. **Plant KPIs**: pac, efficiency, energy today/month/year/total, totalPower, investment, income.
2. **Inverter Summary**: pac, status/runStatus, ratePower, version info (attributes), energy counters.
3. **PV Strings**: per-string voltage/current/power/today energy.
4. **AC Output**: phase voltage/current/power, total pac, frequency.
5. **Grid**: pac/qac/pf, per-phase metrics, energy to/from grid, limiter power array.
6. **Battery**: power direction, SOC, voltage, current, temperature, capacity, charge/discharge kWh.
7. **Load**: instantaneous load power, daily/total consumption, UPS loads, smart load status/frequency.
8. **Flow Snapshot**: pvPower, battPower, gridOrMeterPower, load/UPS/home/smart load powers, direction flags.
9. **Generation vs Use**: pv, load, battery charge, grid export kWh.
10. **Weather**: description, temps, wind speed/direction, sunrise/sunset, icon.
11. **Counters / Diagnostics**: message unread count, inverter counts (normal/fault/warning), plant event count, device presence flags, user area metadata.
12. **Binary Sensors**: grid availability, battery charging/discharging, pending notifications.
13. **Buttons/Services** (stretch): manual refresh, notification ack (pending API confirmation).

## Configuration Requirements
- Config Flow collects: email, password, plant ID(s), inverter serial, locale (lan), optional weather toggle, polling interval.
- Options Flow: enable/disable weather, PV string detail, verbose diagnostics, toggles for high-frequency endpoints.
- Secrets stored securely; no plaintext credentials after token acquisition.

## Data & API Requirements
- Use Sunsynk new auth flow; support token refresh, error handling (`code != 0`).
- Coordinator batches calls once per interval; reuse data for all platforms.
- Respect rate limits (default ~30–60s between refreshes).
- Diagnostics export must redact tokens, serial numbers, installer contact info.

## Quality & Testing
- Unit tests for API client (auth, failures, refresh).
- Coordinator tests using sanitized cache fixtures.
- Platform tests verifying sensor states/attributes & registry entries.
- HA tooling: `hassfest`, `pytest`, linting.
- Manual validation using `api-explore` or staging HA instance.

This document anchors the build plan: future tasks should reference these requirements when implementing manifest, client, coordinator, platforms, and tests.
