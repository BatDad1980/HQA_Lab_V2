# HQA Simulator Facade Smoke Test

## Purpose

This smoke test verifies the unified optional simulator facade for local Qiskit Aer and Cirq/qsim lanes.

## Results

- Backends checked: `2`
- Ran successfully: `2`

| Backend | Available | Ran | Runtime Seconds | Counts | Boundary |
|---|---:|---:|---:|---|---|
| `qiskit_aer` | `True` | `True` | `1.12804` | `{'11': 127, '00': 129}` | Local Aer simulation only; no live backend job submitted. |
| `cirq` | `True` | `True` | `0.000979` | `{'00': 141, '11': 115}` | Local Cirq/qsim simulation only; no live backend job submitted. |

## Boundary

This facade runs local simulator checks only. It does not submit live backend jobs or grant HQA hardware control authority.
