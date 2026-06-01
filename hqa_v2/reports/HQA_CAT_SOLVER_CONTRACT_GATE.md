# HQA Cat Solver Contract Gate

## Purpose

This gate verifies that the cat-qubit solver contract is complete, bounded, and contract-only.

## Results

- Checks: `10`
- Passed: `10`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Contract schema is V0. |
| contract_only | PASS | Mode: `contract_only`. |
| no_hardware_authority | PASS | Contract grants no hardware authority. |
| accepted_solvers | PASS | Solvers: `['qutip', 'dynamiqs_jax']`. |
| required_fields_complete | PASS | Fields: `['cascade_indicator', 'confidence', 'cycles', 'logical_error_proxy', 'parity_history', 'photon_loss_events', 'solver_name', 'solver_version', 'trajectory_id', 'wigner_metadata']`. |
| all_fields_required | PASS | All evidence fields are required. |
| confidence_rule_present | PASS | Confidence rejection rule is present. |
| live_control_rejected | PASS | Live control rejection rule is present. |
| heavy_arrays_rejected | PASS | Heavy artifact rejection rule is present. |
| mapping_covers_cascade | PASS | Cascade and confidence mapping rules exist. |

## Boundary

This gate validates a solver evidence contract only. It does not validate physical cat-qubit hardware, production QEC performance, or live HAL execution.
