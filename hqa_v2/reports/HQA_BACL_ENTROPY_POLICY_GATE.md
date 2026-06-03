# HQA BACL Entropy Policy Gate

## Purpose

This gate verifies that the BACL entropy policy identifies public-only deterministic seeding as unsafe and blocks telemetry-only forgery under the hardened scheme.

## Results

- Checks: `11`
- Passed: `11`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Policy schema is V0. |
| local_policy_proof | PASS | Mode: `local_policy_proof`. |
| legacy_attack_reproduced | PASS | Legacy public-only seed reproduces signing key. |
| hardened_key_diverges | PASS | Attacker without private salt cannot reproduce key. |
| hardened_forgery_locked | PASS | Hardened forged manifest is locked. |
| private_salt_required | PASS | Private salt is required. |
| public_only_seed_rejected_rule | PASS | Decision rule rejects telemetry-only signing authority. |
| no_live_command_signed | PASS | No live command signed. |
| no_hardware_authority | PASS | No hardware authority granted. |
| no_jobs_submitted | PASS | Zero provider jobs submitted. |
| boundary_present | PASS | Boundary blocks external secrets and HAL authority. |

## Boundary

This gate validates local entropy policy only. It does not validate production cryptography, sign live commands, submit jobs, alter pulses, or authorize HAL execution.
