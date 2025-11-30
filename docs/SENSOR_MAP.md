# Sensor Candidates (Derived from `api-explore/.cache` – run: 2025-11-18)

> Use this list to implement `SensorEntityDescription`s in `sensor.py`. No values below should be hard-coded; everything comes from runtime API responses.

## Plant-Level Metrics (`/api/v1/plant/{plant_id}` & `/realtime`)
- `plant_pac` – Instantaneous plant AC power (W) → `data.realtime.pac`
- `plant_efficiency` – Efficiency (%) → `data.realtime.efficiency`
- `plant_etoday` / `plant_emonth` / `plant_eyear` / `plant_etotal` – Energy production (kWh)
- `plant_total_power` – Installed capacity (kW) → `data.realtime.totalPower`
- `plant_income` – Monetary savings for the day (local currency) → `data.realtime.income`
- `plant_investment` – Configured investment cost → `data.realtime.invest`
- `plant_currency_code/text` – Attributes for currency display (ZAR/R)
- `plant_update_at` – ISO timestamp of last refresh

## Inverter Summary (`/api/v1/inverter/{sn}?lan=en`)
- `inverter_status` / `inverter_run_status` – Textual status (Normal/Fault)
- `inverter_pac` – Output power (W)
- `inverter_rate_power` – Rated capacity (W)
- `inverter_energy_today/month/year/total` – Inverter-side energy counters (kWh)
- Implemented: `Inverter Output Power`, `Inverter Rated Power`, `Inverter Energy Today/Month/Year/Total`, and `Inverter Run Status` (with firmware/installer attributes).
- `inverter_brand`, `model`, `alias` – Attributes
- `firmware_versions` – Attributes from `version.*` (master/soft/hmi/etc.)

## PV String Telemetry (`/api/v1/inverter/{sn}/realtime/input`)
For each `pvIV` entry:
- `pv{n}_voltage` (V) → `vpv`
- `pv{n}_current` (A) → `ipv`
- `pv{n}_power` (W) → `ppv`
- `pv{n}_today_energy` (kWh) → `todayPv`
- Implemented: `PV Array {n} Power` sensor exposes per-string watts with voltage/current attributes.
Global fields:
- `pv_pac` – `data.pac`
- `pv_etoday` / `pv_etotal`

## AC Output (`/api/v1/inverter/{sn}/realtime/output`)
- `output_voltage_{phase}` (V) → `vip[].volt`
- `output_current_{phase}` (A) → `vip[].current`
- `output_power_{phase}` (W) → `vip[].power`
- `output_power_total` (W) → `pac` or `pInv`
- `output_frequency` (Hz) → `fac`

## Grid Interface (`/api/v1/inverter/grid/{sn}/realtime`)
- `grid_voltage_{phase}` (V), `grid_current_{phase}` (A), `grid_power_{phase}` (W) → `vip[]`
- `grid_pac` (W)
- `grid_qac` (VAR)
- `grid_frequency` (Hz) → `fac`
- `grid_power_factor`
- `grid_status` (integer + attribute meaning)
- `grid_energy_from_today/total` (kWh) → `etodayFrom`, `etotalFrom`
- `grid_energy_to_today/total` (kWh) → `etodayTo`, `etotalTo`
- `grid_limiter_power_total` + `limiterPowerArr[]`
- Implemented: `pac`, `qac`, `pf`, `fac`, `status`, `acRealyStatus`, `etodayFrom/To`, `etotalFrom/To`, `limiterTotalPower`, `limiterPowerArr`, and `vip[0]` voltage/current/power sensors.

## Battery Telemetry (`/api/v1/inverter/battery/{sn}/realtime`)
- `battery_power` (W) – positive = charging, negative = discharging
- `battery_soc` (%) – `bmsSoc` / `soc`
- `battery_voltage` (V) – `bmsVolt` / `voltage`
- `battery_current` (A) – `bmsCurrent` / `current`
- `battery_temp` (°C) – `bmsTemp` / `temp`
- `battery_capacity` (Ah) – `capacity`
- `battery_charge_voltage`/`discharge_voltage`
- `battery_charge_current_limit` / `battery_discharge_current_limit`
- Energy counters: `etodayChg`, `etodayDischg`, `emonthChg`, `emonthDischg`, `eyearChg`, `eyearDischg`, `etotalChg`, `etotalDischg`
- Status fields (charging/discharging state, BMS version) as attributes

## Load Metrics (`/api/v1/inverter/load/{sn}/realtime`)
- `load_power_total` (W)
- `load_daily_energy` (kWh) → `dailyUsed`
- `load_total_energy` (kWh) → `totalUsed`
- `ups_power_total` / `ups_power_l1/2/3`
- `smart_load_status`
- `load_frequency`

## Flow Overview (`/api/v1/inverter/{sn}/flow` or `/plant/energy/{plant_id}/flow`)
- Mirrors `pvPower`, `battPower`, `gridOrMeterPower`, `loadOrEpsPower`, `upsLoadPower`, `homeLoadPower`, `smartLoadPower`, `chargePilePower`, plus SOC.
- Direction flags (`pvTo`, `toGrid`, `toBat`, `gridTo`, etc.) can drive binary sensors but can also be exposed as diagnostic text attributes.

## Generation vs Use (`/api/v1/plant/energy/{plant_id}/generation/use`)
- `load_consumption_kwh`
- `pv_generation_kwh`
- `battery_charge_kwh`
- `grid_export_kwh`

## Weather (`/api/v1/weather`)
- `weather_description`
- `weather_temp` / `weather_temp_min` / `weather_temp_max` (°C)
- `weather_wind_speed` (m/s) / `weather_wind_direction` (°)
- `sunrise` / `sunset` (strings)
- `icon_url` attribute for UI cards

## Counters & Meta
- `message_unread_count` → `/api/v1/message/count`
- `inverter_total_count`, `inverter_fault_count`, `inverter_warning_count`, etc. → `/api/v1/inverters/count`
- `event_total_count` → `/api/v1/plant/{id}/eventCount`
- `user_area_code` / `area_id` sensors if needed for admin dashboards (`/api/v1/user/area`)

## Diagnostics/Attributes (optional sensors or attributes)
- `permission_summary` – number of granted permissions from `/api/v1/permission`
- `device_presence_flags` – booleans from `/api/v1/plant/{id}/check/device` (inverter/meter/battery present)
- `plant_currency_code/text`, `timezone`, `installer` – attach to device info rather than sensors to avoid leaking PII.

Use this map to populate `SENSOR_DESCRIPTIONS` with:
- `key` (identifier),
- `name`,
- `unit_of_measurement` / `device_class` / `state_class`,
- `value_fn` (lambda reading the right nested dict),
- `available` logic (handle empty arrays or `"--"` placeholders).

*Note*: Some responses contain personal data (addresses, installer emails). Avoid exposing those fields as sensors; keep them as device attributes only when necessary and consider redaction.

