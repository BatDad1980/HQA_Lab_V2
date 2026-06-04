# HQA BACL Fail-Closed Authority Contract V0

## Purpose

This contract formalizes a hard authority rule: BACL failure must never degrade into raw hardware command fallback.

## Summary

- Execution mode: `local_policy_replay`
- Raw fallback allowed: `False`
- Hardware authority: `False`
- Real actuator authority: `False`

| Case | Decision | Reason | Raw Fallback Allowed |
|---|---|---|---:|
| `valid_one_time_manifest` | `AUTHORIZED_DRY_RUN_ONLY` | `FRESH_SIGNED_MANIFEST` | `False` |
| `missing_private_key` | `SAFE_HOLD` | `MISSING_SIGNER_FAIL_CLOSED` | `False` |
| `unregistered_public_key` | `SKULL_LOCK` | `UNREGISTERED_PUBLIC_KEY` | `False` |
| `malformed_signature` | `SKULL_LOCK` | `SIGNATURE_INVALID` | `False` |
| `lamport_key_reuse` | `SKULL_LOCK` | `LAMPORT_ONE_TIME_KEY_REUSE` | `False` |
| `revoked_key` | `SKULL_LOCK` | `KEY_REVOKED` | `False` |

## Policy Rule

BACL absence or failure must fail closed. Missing credentials, invalid signatures, unregistered keys, revoked keys, and one-time-key reuse cannot fall back to raw pump activation.

## Boundary

This contract is a local authority-policy proof. It signs no live commands, opens no sockets, reads no external secrets, and grants no HAL or actuator authority.
