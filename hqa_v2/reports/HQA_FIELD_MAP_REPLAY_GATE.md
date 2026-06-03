# HQA Field Map Replay Gate

## Purpose

This gate verifies that field-map evidence becomes bounded shadow review artifacts without execution authority.

## Results

- Checks: `12`
- Passed: `12`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Replay schema is V0. |
| shadow_only | PASS | Mode: `shadow_replay_only`. |
| no_hardware_authority | PASS | No artifact grants hardware authority. |
| no_jobs_submitted | PASS | Replay submitted zero jobs. |
| candidates_ranked | PASS | Candidates: `5`. |
| targets_selected | PASS | Targets: `['Q_3', 'Q_1', 'Q_2']`. |
| edge_neighborhoods_present | PASS | Damaged edge neighborhoods are represented. |
| review_required | PASS | Operator review required for non-nominal field. |
| intervention_bounded | PASS | Mode: `QUARANTINE_REMAP_SHADOW`. |
| artifacts_present | PASS | All replay artifacts exist. |
| manifest_valid | PASS | All artifact hashes match. |
| boundary_present | PASS | Boundary blocks jobs and HAL authority. |

## Boundary

This gate validates shadow replay artifacts only. It does not validate live quantum performance, submit jobs, run circuits, alter routing tables, change pulses, or authorize HAL execution.
