# Skeptical Validation Report (2025-11-18)

## Critical Findings
- **HA runtime not yet validated**: No hassfest/HA pytest run due to missing HA tooling. Risk: schema or setup issues might surface only inside Home Assistant.
- **Sensor/Binary/Button mappings untested in HA**: Entity descriptions look correct but remain unverified in a real ConfigEntry.
- **API structure assumptions**: Parsing assumes Sunsynk payload shapes remain stable; missing keys currently return `None` without logging.
- **Credentials & rate limiting**: Token refresh has no exponential backoff; repeated failures could spam logs.

## Recommended Quick Tests (ROI-ordered)
1. `python -m script.hassfest` — catches manifest/translation/schema issues.
2. HA pytest via `pytest-homeassistant-custom-component` — verifies entry setup + entity states.
3. Manual HA smoke test with staging credentials — ensures coordinator + entities behave against the live API.
4. CI guard to keep `.cache/` sanitized — avoids reintroducing installer contact details.

## Edge Cases to Probe
- Plants with multiple inverters or missing PV strings (empty arrays).
- Weather disabled but coordinates blank (ensure coordinator skips fetch cleanly).
- Token expiry under concurrent refresh requests (lock contention).

## Confidence Adjustment
- **API client/coordinator correctness**: Medium confidence (unit-tested with fixtures).
- **HA entity registration**: Low/medium confidence until hassfest/HA pytest run.
- **Sensitive data hygiene**: Medium confidence; `.cache/` cleared, but enforce via git ignore or CI.

Use this report as a skeptical checklist before promoting the integration beyond scaffold status.

