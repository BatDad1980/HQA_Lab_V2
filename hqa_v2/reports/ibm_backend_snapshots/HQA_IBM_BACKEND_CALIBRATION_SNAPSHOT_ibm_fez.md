# HQA IBM Backend Calibration Snapshot

## Purpose

This report captures current IBM Quantum backend calibration metadata for HQA shadow analysis.

Credentials are read only from environment variables. No credentials are printed, stored, committed, or packaged.

## Run Status

- `qiskit_ibm_runtime` installed: `True`
- `IBM_QUANTUM_TOKEN` present: `True`
- `IBM_QUANTUM_INSTANCE_CRN` present: `True`
- Snapshot performed: `True`
- Backend selected: `ibm_fez`
- Excluded backends: `ibm_marrakesh`
- Jobs submitted: `0`
- Hardware authority: `False`

## Operational Backends Seen

- `ibm_marrakesh`
- `ibm_kingston`
- `ibm_fez`

## Calibration Snapshot

- Backend: `ibm_fez`
- Timestamp UTC: `2026-06-03T19:31:33.897756+00:00`
- Qubits: `156`
- Coupling edges: `352`
- Mean T1: `152.633249` us
- Mean T2: `106.16227` us
- Mean readout error: `0.028097`
- Degraded qubits: `61`
- Degraded fraction: `0.391026`

Thresholds:

- T1 minimum: `100.0` us
- T2 minimum: `40.0` us
- Readout error maximum: `0.03`

## Boundary

This snapshot reads backend calibration metadata only. It does not submit jobs, run circuits, reserve hardware, validate production quantum behavior, or grant HQA live hardware authority.
