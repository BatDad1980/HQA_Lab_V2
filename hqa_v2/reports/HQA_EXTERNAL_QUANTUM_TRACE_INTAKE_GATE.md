# HQA External Quantum Trace Intake Gate

## Purpose

This gate verifies that external trace intake accepts only bounded, provenance-bearing traces and rejects unsafe inputs.

## Results

- Checks: `10`
- Passed: `10`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| contract_schema | PASS | Contract schema is V0. |
| intake_only | PASS | Mode: `intake_validation_only`. |
| no_hardware_authority | PASS | No intake artifact grants hardware authority. |
| accepted_one_trace | PASS | Accepted traces: `1`. |
| rejected_one_trace | PASS | Rejected traces: `1`. |
| normalized_only_accepted | PASS | Normalized files: `1`. |
| secret_rejected | PASS | Secret-like trace was rejected. |
| live_authority_rejected | PASS | Live-authority request was rejected. |
| manifest_valid | PASS | All normalized trace hashes match. |
| normalization_target_present | PASS | Topology normalization target exists. |

## Boundary

This gate validates intake behavior only. It does not validate physical quantum hardware, production QEC performance, live vendor access, or HAL execution.
