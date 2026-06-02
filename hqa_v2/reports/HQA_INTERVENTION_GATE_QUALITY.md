# HQA Intervention Gate Quality

## Purpose

This gate verifies that Intervention Gate V0 maps stress-run breakpoints to bounded policy decisions.

## Results

- Checks: `12`
- Passed: `12`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Schema is V0. |
| shadow_policy_mode | PASS | Mode: `shadow_policy_gate`. |
| no_hardware_authority | PASS | No intervention result grants hardware authority. |
| ten_scenarios | PASS | Results `10`, expected `10`. |
| expected_results_match | PASS | Every scenario reached the expected decision and breakpoint. |
| stand_down_present | PASS | Stable IBM rerun stands down. |
| shadow_remap_present | PASS | Noisy IBM style remains shadow remap candidate. |
| patch_routing_required | PASS | Decisions: `['ACCEPT_ANNOTATION', 'HARD_BLOCK', 'KEY_ROTATION_REQUIRED', 'MONITOR_WITH_SHADOW_OPTIMIZATION', 'NO_INTERVENTION', 'PATCH_ROUTING_REQUIRED', 'REQUIRE_SUMMARY_COMPRESSION', 'SAFE_HOLD', 'SHADOW_REMAP_CANDIDATE']`. |
| hard_block_present | PASS | BACL exhausted key hard-blocks. |
| compression_required | PASS | Cognitive overload requires compression. |
| safe_hold_breakpoints | PASS | Breakpoints: `['adapted_route_improves', 'adapted_route_underperforms', 'advisory_latency_over_budget', 'lamport_key_exhausted', 'lamport_reuse_risk', 'latency_near_budget', 'latency_over_budget', 'physics_error_proxy_exceeds_one', 'small_positive_delta', 'within_latency_budget']`. |
| boundary_present | PASS | Boundary rejects live authority. |

## Boundary

This gate validates shadow policy decisions only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.
