# HQA BACL Entropy Policy V0

## Purpose

This report captures a red-team finding: public telemetry must never be sufficient to derive manifest-signing authority.

## Legacy Finding

- Attacker key matched target: `True`
- Forged manifest decision: `AUTHORIZED`
- Finding: Legacy deterministic public-only seeding is insecure.

## Hardened Finding

- Private salt required: `True`
- Attacker key matched target: `False`
- Forged manifest decision: `SKULL_LOCK`
- Finding: Private salt prevents telemetry-only key recovery.

## Policy Rule

Reject any manifest-signing scheme where public telemetry alone can regenerate signing authority.

## Boundary

BACL Entropy Policy V0 is a local red-team policy proof. It signs no live commands, reads no external secrets, submits no jobs, and grants no HAL authority.
