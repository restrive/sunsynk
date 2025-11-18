# Enhanced Logging Research Plan

## Step 0: Topic Breakdown
- Focus: Improve debugging/logging inside Sunsynk Sync (HA custom component).
- Dimensions: token auth lifecycle, coordinator updates, entity update cycle, HA logging config, user-facing diagnostics.
- Hidden cognitive processes: introspection on failure cases, sensemaking of API responses.

## Step 1: Perspective Ledger
- Technological: aiohttp retries, coordinator errors.
- Operational: installer workflows.
- UX: actionable messages, HA notification hooks.
- Ethical/security: avoid logging secrets.

## Step 2: Source-Layer Map
- HA developer docs (logging, coordinator).
- Sunsynk community threads (common errors).
- Practitioner posts on HA logging best practices.

## Step 3: Prompt Set
1. "How does HA recommend structured logging in custom components?"
2. "What failure modes do Sunsynk users report (No Permissions, network) and how can logs help?"
3. "What minimal logging is necessary to trace aiohttp requests without leaking secrets?"
4. "How can diagnostics exports surface errors for HACS support?"

## Step 4: Minimal Viable Tests
- Simulate API auth failure and confirm log includes endpoint + masked email.
- Trigger coordinator UpdateFailed and check HA log output.
- Call diagnostics endpoint and ensure redacted payload still exposes error context.

## Step 5: Execution Plan
1. Review HA logging docs
2. Scan Sunsynk community posts
3. Draft logging scaffolding (logger per module).
4. Implement structured log calls around aiohttp requests, coordinator refresh, entity update.
5. Extend diagnostics to include last successful refresh timestamp + error codes.

## Step 6: Synthesis Outline
- Logging requirements vs current state matrix
- Proposed code changes (client/coordinator/entity/diagnostics)
- Testing plan (pytest + manual HA).

## Step 7: Deliverables
- Code updates with instrumentation
- Docs snippet describing new logging toggles
- QA checklist for future regressions.
