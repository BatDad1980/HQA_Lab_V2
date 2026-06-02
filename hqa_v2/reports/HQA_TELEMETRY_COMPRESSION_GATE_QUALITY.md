# HQA Telemetry Compression Gate Quality

## Purpose

This gate verifies that telemetry compression preserves HQA intervention decisions and keeps advisory payloads inside the latency budget.

## Results

- Checks: `11`
- Passed: `11`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Schema is V0. |
| shadow_mode | PASS | Mode: `shadow_compression_gate`. |
| no_hardware_authority | PASS | No compression result grants hardware authority. |
| four_scenarios | PASS | Results: `4`. |
| all_decisions_preserved | PASS | Every compressed summary preserved the raw intervention decision. |
| all_under_budget | PASS | Budget: `250.0` ms. |
| monster_compressed_enough | PASS | Monster ratio: `314.381`. |
| collapse_still_safe_hold | PASS | Collapse decision: `SAFE_HOLD`. |
| decision_variety | PASS | Decisions: `['ACCEPT_ANNOTATION', 'MONITOR_WITH_ROUTE_REVIEW', 'QUARANTINE_REMAP_REVIEW', 'SAFE_HOLD']`. |
| compression_positive | PASS | Ratios: `[19.917, 78.828, 314.381, 311.225]`. |
| boundary_present | PASS | Boundary rejects live authority. |

## Boundary

This gate validates telemetry summarization only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.
