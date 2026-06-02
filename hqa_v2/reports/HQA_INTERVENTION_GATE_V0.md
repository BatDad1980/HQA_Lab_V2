# HQA Intervention Gate V0

## Purpose

This report converts recent stress-run breakpoints into explicit intervention policy.

The gate decides when HQA should stand down, monitor, shadow-test, require patch routing, rotate keys, compress advisory payloads, or enter safe hold.

## Results

| Scenario | Vector | Decision | Breakpoint | Reviewer Required | Hardware Authority |
|---|---|---|---|---:|---:|
| `INT-001` IBM stable calibration rerun | `real_device_calibration` | `NO_INTERVENTION` | `adapted_route_underperforms` | `False` | `False` |
| `INT-002` IBM unstable calibration style | `real_device_calibration` | `SHADOW_REMAP_CANDIDATE` | `adapted_route_improves` | `True` | `False` |
| `INT-003` A-star routing latency ceiling | `algorithmic_routing` | `PATCH_ROUTING_REQUIRED` | `latency_near_budget` | `True` | `False` |
| `INT-004` A-star routing over budget | `algorithmic_routing` | `SAFE_HOLD` | `latency_over_budget` | `True` | `False` |
| `INT-005` BACL Lamport key overuse | `cryptographic_boundary` | `KEY_ROTATION_REQUIRED` | `lamport_reuse_risk` | `True` | `False` |
| `INT-006` BACL Lamport key exhausted | `cryptographic_boundary` | `HARD_BLOCK` | `lamport_key_exhausted` | `True` | `False` |
| `INT-007` Cat optimizer modest gain | `cat_qubit_noise` | `MONITOR_WITH_SHADOW_OPTIMIZATION` | `small_positive_delta` | `False` | `False` |
| `INT-008` Cat physics unrecoverable | `cat_qubit_noise` | `SAFE_HOLD` | `physics_error_proxy_exceeds_one` | `True` | `False` |
| `INT-009` Cognitive advisor under budget | `cognitive_advisory` | `ACCEPT_ANNOTATION` | `within_latency_budget` | `False` | `False` |
| `INT-010` Cognitive advisor overload | `cognitive_advisory` | `REQUIRE_SUMMARY_COMPRESSION` | `advisory_latency_over_budget` | `True` | `False` |

## Reasons

### `INT-001`

Default compiler route outperformed HQA remap on current calibration. HQA should stand down.

### `INT-002`

Calibration is noisy enough and adapted route improved in local shadow comparison.

### `INT-003`

Global pathfinding is near feedback budget and should move to patch/local routing.

### `INT-004`

Global pathfinding exceeded the feedback budget.

### `INT-005`

Lamport key reuse risk is too high; rotate before further signing.

### `INT-006`

Lamport one-time key material is exhausted and must not sign another command.

### `INT-007`

Cat optimization is bounded and mildly positive; keep it in shadow/monitor mode.

### `INT-008`

Noise model exceeded recoverable probability bounds; optimization cannot preserve useful state.

### `INT-009`

Cognitive advisory completed inside the feedback budget and remains annotation-only.

### `INT-010`

Cognitive advisory exceeded the feedback budget; summarize telemetry before model intake.

## Thresholds

| Threshold | Value |
|---|---:|
| `feedback_budget_ms` | `250.0` |
| `routing_patch_required_fraction` | `0.75` |
| `mean_readout_instability_threshold` | `0.03` |
| `lamport_rotation_after_any_reuse` | `True` |
| `cat_error_proxy_safe_hold` | `1.0` |

## Boundary

The intervention gate chooses shadow policy only. It does not authorize live hardware control, backend jobs, pulse changes, or cryptographic signing.
