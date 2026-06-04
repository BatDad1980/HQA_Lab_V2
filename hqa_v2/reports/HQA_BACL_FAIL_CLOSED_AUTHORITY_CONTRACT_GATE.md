# HQA BACL Fail-Closed Authority Contract Gate

## Purpose

This gate verifies that BACL authority failures are locked or held instead of falling back to raw command execution.

## Results

- Checks: `15`
- Passed: `15`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Contract schema is V0. |
| local_policy_replay | PASS | Mode: `local_policy_replay`. |
| raw_fallback_globally_blocked | PASS | Global raw fallback is blocked. |
| no_hardware_authority | PASS | No hardware authority granted. |
| no_real_actuator_authority | PASS | No real actuator authority granted. |
| valid_manifest_dry_run_only | PASS | Only fresh signed manifest gets dry-run authorization. |
| missing_key_safe_hold | PASS | Missing signer fails closed. |
| unregistered_key_locked | PASS | Unregistered key is locked. |
| malformed_signature_locked | PASS | Malformed signature is locked. |
| key_reuse_locked | PASS | Lamport key reuse is locked. |
| revoked_key_locked | PASS | Revoked key is locked. |
| no_case_allows_raw_fallback | PASS | No case allows raw fallback. |
| all_failure_cases_blocked | PASS | All authority failures are blocked. |
| policy_rule_present | PASS | Policy rule blocks raw pump fallback. |
| boundary_blocks_live_authority | PASS | Boundary blocks live commands and HAL authority. |

## Boundary

This gate validates local policy only. It does not sign live commands, open sockets, read external secrets, or authorize HAL execution.
