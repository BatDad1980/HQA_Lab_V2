# HQA Legacy Autonomic Stress Regulator Gate

## Purpose

This gate verifies that the legacy autonomic stress harvest emits bounded patch-state decisions only.

## Results

- Checks: `12`
- Passed: `12`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Schema is V0. |
| shadow_advisory_mode | PASS | Mode: `shadow_advisory`. |
| no_hardware_authority | PASS | No hardware authority present. |
| all_patches_present | PASS | Patches: `['PATCH_NE', 'PATCH_NW', 'PATCH_SE', 'PATCH_SW']`. |
| scores_bounded | PASS | Scores: `[0.424457, 0.095514, 1.0, 0.725743]`. |
| green_patch_monitors | PASS | NW action: `MONITOR_ONLY`. |
| calibration_hold_present | PASS | NE action: `PROPOSE_CALIBRATION_HOLD`. |
| reroute_review_present | PASS | SW action: `PROPOSE_REROUTE_REVIEW`. |
| safe_hold_on_no_route | PASS | SE action: `SAFE_HOLD`. |
| highest_stress_patch | PASS | Highest: `PATCH_SE`. |
| no_disallowed_outputs | PASS | Disallowed outputs: `{'live_cooling_command': 0, 'pulse_change': 0, 'hal_dispatch': 0, 'backend_job': 0}`. |
| boundary_present | PASS | Boundary rejects live dispatch. |

## Boundary

This gate validates advisory stress classification only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.
