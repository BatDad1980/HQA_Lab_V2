# HQA Cat Solver Contract V0

## Purpose

This report defines the evidence contract a future cat-qubit solver adapter must satisfy before its output can feed HQA risk-field logic.

The contract is intentionally solver-agnostic. It supports QuTiP and Dynamiqs/JAX lanes without making either dependency mandatory for the base HQA regression.

## Contract Summary

- Schema version: `hqa.cat_solver_contract.v0`
- Execution mode: `contract_only`
- Hardware authority: `False`
- Accepted solvers: `qutip, dynamiqs_jax`

## Required Evidence Fields

| Field | Type | Required | Purpose |
|---|---|---:|---|
| `solver_name` | `string` | `True` | Identifies the bosonic/open-system solver used. |
| `solver_version` | `string` | `True` | Records solver version for replay and dependency review. |
| `trajectory_id` | `string` | `True` | Binds all observables to one simulated trajectory or ensemble. |
| `cycles` | `integer` | `True` | Correction-cycle count represented in the evidence. |
| `parity_history` | `array[number]` | `True` | Cycle-indexed parity expectation or parity measurement proxy. |
| `photon_loss_events` | `array[object]` | `True` | Trajectory-indexed photon-loss or jump records. |
| `logical_error_proxy` | `object` | `True` | Bit-flip and phase-flip proxy scores with confidence. |
| `wigner_metadata` | `object` | `True` | Compact phase-space metadata without storing heavy image arrays. |
| `cascade_indicator` | `string` | `True` | LOW_ACTIVITY, WATCHLIST, or CASCADE_LIKE classification. |
| `confidence` | `number[0,1]` | `True` | Confidence that the solver evidence supports the cascade classification. |

## HQA Mapping Rules

- `parity_history`: maps to syndrome persistence and cycle pressure
- `photon_loss_events`: maps to seed error and jump-density pressure
- `logical_error_proxy`: maps to risk-field syndrome pressure
- `wigner_metadata`: maps to phase-space stability notes only
- `cascade_indicator`: maps to LOW_ACTIVITY, WATCHLIST, or CASCADE_LIKE risk labels
- `confidence`: bounds the contribution of solver-derived evidence

## Rejection Rules

- Reject evidence with unknown solver_name.
- Reject evidence without solver_version.
- Reject evidence when parity_history length differs from cycles.
- Reject confidence outside [0, 1].
- Reject attempts to request live hardware, pulse changes, or HAL execution.
- Reject heavy binary/image arrays in the evidence packet; store metadata only.

## Boundary

Contract-only lane. It defines required solver evidence but does not run bosonic simulation, validate physical cat-qubit hardware, or grant live control authority.
