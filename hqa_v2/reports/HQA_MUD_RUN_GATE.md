# HQA Mud Run Gate

## Purpose

This gate verifies that Mud Run V0 reaches the expected fail-closed breakpoints.

## Results

- Checks: `10`
- Passed: `10`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Mud-run schema is V0. |
| adversarial_shadow_mode | PASS | Mode: `adversarial_shadow_harness`. |
| no_hardware_authority | PASS | No mud-run result grants hardware authority. |
| eight_scenarios | PASS | Results `8`, expected `8`. |
| expected_breakpoints_match | PASS | Every scenario reached its expected disposition and breakpoint. |
| fail_closed_modes_present | PASS | Dispositions: `['ACCEPT_SHADOW', 'QUARANTINE', 'REJECT', 'REVIEW_LOCK', 'SAFE_HOLD']`. |
| accept_shadow_still_possible | PASS | A harsh but bounded payload can still enter shadow evaluation. |
| breakpoint_variety | PASS | Breakpoints: `['conflicting_calibration', 'extreme_cat_noise', 'hardware_authority_boundary', 'no_route_available', 'none', 'schema_bounds', 'secret_containment', 'topology_compensation_gap']`. |
| manifest_valid | PASS | All mud-run hashes match. |
| boundary_present | PASS | Boundary rejects live authority. |

## Boundary

This gate validates local adversarial intake behavior only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.
