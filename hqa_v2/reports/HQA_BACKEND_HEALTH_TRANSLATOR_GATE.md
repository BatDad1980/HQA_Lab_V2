# HQA Backend Health Translator Gate

## Purpose

This gate verifies that backend calibration evidence is translated into a provider-neutral HQA health grammar without granting hardware authority.

## Results

- Checks: `12`
- Passed: `12`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Translator schema is V0. |
| shadow_only | PASS | Mode: `shadow_translation_only`. |
| no_hardware_authority | PASS | No profile grants hardware authority. |
| no_jobs_submitted | PASS | Translation submitted zero jobs. |
| two_ibm_backends_present | PASS | Backends: `ibm_fez, ibm_kingston`. |
| normalized_health_scores | PASS | Every backend has a bounded health score. |
| kingston_healthier_than_fez | PASS | Kingston ranks healthier than Fez from captured telemetry. |
| fez_quarantine_hint | PASS | Fez maps to shadow quarantine/remap pressure. |
| kingston_monitor_hint | PASS | Kingston maps to monitor/shadow optimization. |
| backend_name_not_policy | PASS | Comparison states provider-neutral translation rule. |
| spatial_limitation_honest | PASS | Summary snapshots do not overclaim spatial clustering visibility. |
| boundary_present | PASS | Boundary blocks jobs and HAL execution. |

## Boundary

This gate validates shadow health translation only. It does not validate production QEC, submit provider jobs, run circuits, change pulses, or authorize HAL execution.
