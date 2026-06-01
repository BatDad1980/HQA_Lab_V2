# HQA Risk Field Gate

## Purpose

This gate verifies that HQA Risk Field V0 produces bounded, advisory-only risk rankings from HQA-native evidence.

## Results

- Checks: `10`
- Passed: `10`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Risk field schema version is V0. |
| shadow_advisory_mode | PASS | Risk field remains in shadow advisory mode. |
| no_hardware_authority | PASS | Risk field grants no hardware authority. |
| all_vendor_nodes_present | PASS | Node IDs found: `['Q_0', 'Q_1', 'Q_2', 'Q_3']`. |
| scores_bounded | PASS | Scores: `[0.954809, 0.500409, 0.195463, 0.188663]`. |
| q1_highest_risk | PASS | Highest-risk node: `Q_1`. |
| suspected_patch_matches | PASS | Suspected patch matches top-ranked node. |
| cascade_contrast_detected | PASS | Cascade contrast: `0.886718`. |
| advisory_action_only | PASS | Action: `ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL`. |
| risk_bands_known | PASS | Bands: `['critical', 'elevated', 'low']`. |

## Boundary

This gate checks risk-field structure and advisory boundaries only. It does not validate physical quantum hardware, production QEC performance, or live HAL execution.
