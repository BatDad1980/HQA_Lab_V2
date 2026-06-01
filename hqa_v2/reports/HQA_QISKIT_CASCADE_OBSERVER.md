# HQA Qiskit Cascade Observer

## Purpose

This report demonstrates a local Qiskit-facing cascade observation lane for HQA V2.

Instead of reducing the experiment to a final state, the observer emits a cycle-by-cycle syndrome history that HQA can treat as cascade evidence.

## Readiness

- Qiskit available: `True`
- Qiskit Aer available: `True`
- Dynamic `if_test` construction available: `True`
- Circuit qubits: `5`
- Circuit classical bits: `8`
- Circuit depth: `18`

## Noise Manifest

- Single-qubit bit-flip proxy rate: `0.004`
- Measurement-flip proxy rate: `0.01`
- Correlated-neighbor proxy rate: `0.035`
- Cascade seed: `data[1] photon-loss-proxy / bit-flip-proxy at cycle 1`

## Syndrome Trace

| Cycle | Syndrome | Seed Error | Correlated Error | Decoder Signal |
|---:|---:|---|---|---|
| 0 | `00` | - | - | BASELINE_CLEAR |
| 1 | `11` | data[1] | - | CASCADE_SEED_DETECTED |
| 2 | `10` | - | data[2] | CORRELATED_SPREAD_OBSERVED |
| 3 | `01` | - | data[0] | CORRELATED_SPREAD_OBSERVED |

## HQA Decision

- Cascade detected: `True`
- Quarantine target: `data[1]`
- HQA action: `SENTINEL_QUARANTINE_AND_REROUTE_PROPOSAL`

## Boundary

This observer is a local simulator-facing proxy. It does not submit live IBM jobs, validate physical quantum hardware, prove production QEC performance, or grant HQA hardware control authority.
