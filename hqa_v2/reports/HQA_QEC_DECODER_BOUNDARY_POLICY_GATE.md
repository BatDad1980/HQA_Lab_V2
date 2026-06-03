# HQA QEC Decoder Boundary Policy Gate

## Purpose

This gate verifies that odd syndrome cardinality resolves through a virtual boundary partner without crash or silent loss.

## Results

- Checks: `12`
- Passed: `12`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Policy schema is V0. |
| local_policy_replay | PASS | Mode: `local_policy_replay`. |
| odd_cases_present | PASS | Odd cases: `2`. |
| odd_uses_boundary | PASS | Every odd case uses a virtual boundary partner. |
| even_no_boundary | PASS | Even nonzero cases resolve directly. |
| no_crashes | PASS | No case crashed. |
| no_silent_drops | PASS | No syndrome was silently dropped. |
| boundary_partner_recorded | PASS | Boundary partner appears in pair list. |
| policy_rule_present | PASS | Policy rule names the virtual boundary partner. |
| no_hardware_authority | PASS | No hardware authority granted. |
| no_jobs_submitted | PASS | Zero provider jobs submitted. |
| boundary_present | PASS | Boundary blocks production and HAL claims. |

## Boundary

This gate validates local decoder policy only. It does not validate production decoding, submit jobs, run circuits, alter pulses, or authorize HAL execution.
