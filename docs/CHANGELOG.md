# Changelog

> **Disclaimer:** Release notes describe changes without implying warranties. Validate every build in your environment before production use.

## 0.0.1 (Scaffold)
- Added manifest, translations, and README.
- Implemented Sunsynk OAuth client (`api_client.py`) + coordinator (`coordinator.py`).
- Added sensor/binary sensor/button platforms with coordinator-backed entities.
- Added diagnostics export and config/options flows.
- Local pytest suite for client + coordinator; HA-specific tests pending (`docs/TESTING.md`).
