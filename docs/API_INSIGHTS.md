# API Insights (From `api-explore/` harness – 2025-11-18 run)

- **Auth flow**
  - Required sequence: `GET /anonymous/publicKey?nonce=<ts>&source=sunsynk&sign=MD5(nonce+source+"POWER_VIEW")` to fetch RSA key, then encrypt password for `POST /oauth/token/new`.
  - Tokens issued by `/oauth/token/new` work across `https://api.sunsynk.net/api/v1/*`.

- **Core resources**
  - `/api/v1/plant/{plant_id}` + `/realtime`/`/layout/day`/`/logical/layout/day` provide plant-level summaries. Current data set shows `plant_id=221135` valid.
  - `/api/v1/inverter/{sn}/realtime/input|output|grid|battery|load` surface PV input, AC output, grid import/export, SOC/voltage/current, and load demand in near real time.
  - `/api/v1/inverter/{sn}/flow` aggregates PV/Battery/Grid→Load flow values (`pvPower`, `battPower`, `gridOrMeterPower`, `loadOrEpsPower`, `soc`, etc.)—perfect for a single coordinator call feeding multiple sensors.
  - `/api/v1/inverter/{sn}/day|month` endpoints provide historical series by column (e.g., `ppv`, `pac`, `p_bms`).
  - `/api/v1/message/count` + `/api/v1/message/getLastUnReadNotice` allow notification sensors.
  - `/api/v1/ss/notices/views`, `/api/v1/plant/eventCount`, `/api/v1/plant/events` expose event/stat counters (can map to diagnostics or sensors).
  - `/api/v1/weather` returns ambient weather for plant coordinates (desc, temps, wind, sunrise/sunset).

- **Data points confirmed in cache**
  - `pvPower`, `mpptPower`, `battPower`, `gridOrMeterPower`, `loadOrEpsPower`, `soc`, `homeLoadPower`, etc. (inverter flow).
  - Battery snapshot includes SOC+voltage (ensure mapping once actual payloads populate—they currently return placeholders but API returns 200).
  - Plant metadata: `etoday`, `etotal`, `pac`, `status`, address, etc.
  - `inverters_count` differentiates `normal`, `fault`, `warning`.

- **Implementation notes**
  - Rate limit felt comfortable at ~0.2–0.3 s between requests; coordinator should choose a single refresh rather than per-platform calls.
  - All endpoints return JSON objects with `code/msg/data`. `code=0` indicates success; treat others as HA errors/retries.
  - Maintain redaction of access tokens/credentials—no comments or config files should contain actual email/password.

Map these insights into comments/TODOs across the skeleton files so future implementation can latch onto the right routes quickly.

