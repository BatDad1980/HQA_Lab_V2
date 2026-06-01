# HQA Simulator Stress Schedule Gate

## Purpose

This gate verifies that Simulator Stress Schedule V0 produces bounded advisory outputs across multiple local stress profiles.

## Results

- Checks: `10`
- Passed: `10`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Schedule summary schema is V0. |
| four_scenarios_present | PASS | Scenarios found: `['correlated_stress', 'mild_stress', 'no_route_hold', 'nominal']`. |
| scenario_dirs_exist | PASS | All scenario evidence folders exist. |
| actions_match_profiles | PASS | Actions: `{'nominal': 'MONITOR_ONLY', 'mild_stress': 'MONITOR_WITH_ROUTE_REVIEW', 'correlated_stress': 'ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL', 'no_route_hold': 'NO_ROUTE_HOLD_REVIEW'}`. |
| risk_scores_bounded | PASS | Scores: `[0.224212, 0.550903, 0.954809, 1.0]`. |
| risk_increases_with_stress | PASS | Ordered scores: `[0.224212, 0.550903, 0.954809, 1.0]`. |
| no_hardware_authority | PASS | No schedule result grants hardware authority. |
| no_route_hold_blocks_proposal | PASS | Mode: `blocked`. |
| nominal_monitor_only | PASS | Nominal profile remains monitor-only. |
| manifest_valid | PASS | All schedule artifact hashes match. |

## Boundary

This gate checks deterministic local schedule behavior only. It does not validate physical quantum hardware, production QEC performance, or live HAL execution.
