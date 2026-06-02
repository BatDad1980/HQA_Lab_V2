# HQA Patch Routing Prototype Quality

## Purpose

This gate verifies that patch routing reduces planning workload while preserving route/no-route decisions.

## Results

- Checks: `11`
- Passed: `11`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Schema is V0. |
| shadow_mode | PASS | Mode: `shadow_routing_prototype`. |
| no_hardware_authority | PASS | No patch routing result grants hardware authority. |
| four_scenarios | PASS | Results `4`, expected `4`. |
| expected_decisions_match | PASS | All route/no-route decisions match expected outcomes. |
| routes_have_paths | PASS | Every available route includes a patch path. |
| no_route_safe_hold | PASS | Patch wall triggers safe hold. |
| large_reductions | PASS | Reductions: `[244.565, 230.769, 405.862]`. |
| patch_latency_under_budget | PASS | Patch latencies: `[1.747, 5.419, 11.844]`. |
| global_latency_exposes_need | PASS | Global latencies: `[205.0, 820.0, 3280.0]`. |
| boundary_present | PASS | Boundary rejects physical validation claim. |

## Boundary

This gate validates shadow route-planning behavior only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.
