# HQA Shadow Adaptive Proposal Gate

## Purpose

This gate verifies that Shadow Adaptive Proposal V0 emits reviewable artifacts without live authority.

## Results

- Checks: `10`
- Passed: `10`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| quarantine_schema | PASS | Quarantine payload uses vendor schema. |
| quarantine_shadow_only | PASS | Authority: `shadow_advisory`. |
| quarantine_target_q1 | PASS | Target: `Q_1`. |
| reroute_shadow_only | PASS | Mode: `shadow_advisory`. |
| reroute_requires_review | PASS | Vendor review is required. |
| reroute_avoids_q1 | PASS | Avoided targets: `['Q_1']`. |
| hal_schema | PASS | HAL payload uses vendor schema. |
| hal_dry_run_only | PASS | Mode: `dry_run`. |
| hal_requires_human_approval | PASS | Human approval is required. |
| manifest_valid | PASS | All artifact hashes match. |

## Boundary

This gate checks shadow-review packet structure only. It does not validate physical quantum hardware, production QEC performance, or live HAL execution.
