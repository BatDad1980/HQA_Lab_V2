# HQA Legacy Scar Router Gate

## Purpose

This gate verifies that the V1 scar-router harvest behaves as a bounded shadow replay artifact.

## Results

- Checks: `8`
- Passed: `8`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Schema is V0. |
| shadow_replay_only | PASS | Mode: `shadow_replay`. |
| no_hardware_authority | PASS | No hardware authority present. |
| scar_route_exists | PASS | Path: `['Q_0_1', 'Q_1_1', 'Q_2_1', 'Q_3_1', 'Q_3_2', 'Q_3_3', 'Q_4_3']`. |
| scar_route_avoids_blocked | PASS | Blocked nodes: `['Q_1_2', 'Q_2_2']`. |
| cat_phase_bias_applied | PASS | Phase cost `18.8`, generic cost `13.2`. |
| no_route_safe_hold | PASS | Action: `SAFE_HOLD`. |
| boundary_present | PASS | Boundary rejects physical validation claim. |

## Boundary

This gate validates deterministic route-selection behavior only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.
