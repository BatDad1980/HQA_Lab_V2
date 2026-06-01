# HQA Legacy Autonomic Stress Regulator V0

## Purpose

This report records a clean-lab harvest of the legacy V1 vagus/autonomic control primitive.

Instead of commanding hardware, the regulator aggregates local patch stress and emits bounded advisory decisions.

## Summary

- Execution mode: `shadow_advisory`
- Hardware authority: `False`
- Patch count: `4`
- Highest stress patch: `PATCH_SE`
- System recommendation: `SAFE_HOLD`

## Patch Decisions

| Patch | Corrections | Max Drift | Mean Syndrome Confidence | Stress Score | Band | Advisory Action |
|---|---:|---:|---:|---:|---|---|
| `PATCH_NE` | `24` | `0.12` | `0.453333` | `0.424457` | `yellow_calibration_hold` | `PROPOSE_CALIBRATION_HOLD` |
| `PATCH_NW` | `5` | `0.03` | `0.11` | `0.095514` | `green_monitor` | `MONITOR_ONLY` |
| `PATCH_SE` | `48` | `0.34` | `0.93` | `1.0` | `red_hold` | `SAFE_HOLD` |
| `PATCH_SW` | `39` | `0.23` | `0.77` | `0.725743` | `orange_reroute_review` | `PROPOSE_REROUTE_REVIEW` |

## Harvested Pattern

- V1 correction counts become local patch pressure.
- V1 thermal/autonomic reflex becomes advisory state classification.
- V1 preemptive degradation tracking becomes drift-velocity pressure.
- Missing safe routes push the system toward `SAFE_HOLD`, not forced execution.

## Disallowed Outputs

| Output | Count |
|---|---:|
| `live_cooling_command` | `0` |
| `pulse_change` | `0` |
| `hal_dispatch` | `0` |
| `backend_job` | `0` |

## Boundary

This artifact converts legacy autonomic stress logic into advisory patch-state decisions only. It does not dispatch cooling, pulses, backend jobs, or HAL commands.
