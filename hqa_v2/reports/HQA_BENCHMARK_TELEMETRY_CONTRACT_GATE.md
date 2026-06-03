# HQA Benchmark Telemetry Contract Gate

## Purpose

This gate verifies that benchmark telemetry can observe, record, hash, and report without becoming a command or authority surface.

## Results

- Checks: `12`
- Passed: `12`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Contract schema is V0. |
| commands_present | PASS | Commands: `benchmark-qec, run-telemetry`. |
| benchmark_distances | PASS | Distances: `[3, 5, 7]`. |
| records_hashed | PASS | Every benchmark record has a hash. |
| observe_record_hash_allowed | PASS | Observation, recording, and hashing are allowed. |
| no_authorize_or_actuate | PASS | Authorization and actuation are denied. |
| no_credential_storage | PASS | Credential storage is denied. |
| no_remote_dispatch | PASS | Remote command dispatch is denied. |
| no_hal_authority | PASS | HAL and hardware authority are denied. |
| no_jobs_submitted | PASS | Zero provider jobs submitted. |
| payload_limits_present | PASS | Credential-like payloads are rejected. |
| boundary_present | PASS | Boundary blocks credentials, command dispatch, and HAL authority. |

## Boundary

This gate validates telemetry contract shape only. It does not start a server, submit jobs, run live hardware, authorize interventions, or validate production QEC.
