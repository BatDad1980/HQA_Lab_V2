# HQA IBM Live Validation Abstention Replay Gate

## Purpose

This gate verifies that reported IBM validation outcomes are translated into bounded intervention policy without turning into a live authority claim.

## Results

- Checks: `12`
- Passed: `12`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Replay schema is V0. |
| reported_fixture_mode | PASS | Mode: `reported_fixture_policy_replay`. |
| adjacent_source_labeled | PASS | Source is labeled as adjacent-lane report, not clean-lane proof. |
| no_clean_lane_jobs | PASS | Clean lane submitted zero IBM jobs. |
| no_hardware_authority | PASS | No decision grants hardware authority. |
| both_backends_present | PASS | Fez and Kingston are both replayed. |
| fez_positive_delta | PASS | Fez fixture shows quarantine-remap improvement. |
| fez_intervenes | PASS | Fez decision: `INTERVENE_WITH_QUARANTINE_REMAP_SHADOW`. |
| kingston_negative_delta | PASS | Kingston fixture shows forced-remap underperformance. |
| kingston_abstains | PASS | Kingston decision: `ABSTAIN_AND_MONITOR`. |
| core_rule_condition_aware | PASS | Core rule encodes condition-aware intervention. |
| boundary_blocks_overclaim | PASS | Boundary blocks live-job and production-performance claims. |

## Boundary

This gate validates policy replay only. It does not validate production QEC performance, submit IBM jobs, execute circuits, alter hardware routing, or authorize HAL execution.
