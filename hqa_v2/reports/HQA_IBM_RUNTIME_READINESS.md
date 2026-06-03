# HQA IBM Runtime Readiness

## Purpose

This report checks whether HQA V2 can reach the optional IBM Quantum runtime lane.

Credentials are never read from files, printed, committed, or packaged. This check only uses environment variables explicitly set in the active shell.

## Status

- `qiskit_ibm_runtime` installed: `True`
- `IBM_QUANTUM_TOKEN` present: `True`
- `IBM_QUANTUM_INSTANCE_CRN` present: `True`
- Live check requested: `True`
- Live check performed: `True`
- Operational backends returned: `3`

## Backends

- `ibm_marrakesh`
- `ibm_kingston`
- `ibm_fez`

## Usage

```powershell
$env:IBM_QUANTUM_TOKEN = "<token>"
$env:IBM_QUANTUM_INSTANCE_CRN = "<instance-crn>"
python hqa_v2/integrations/ibm_runtime_readiness.py --live
```

## Boundary

This readiness check validates optional runtime access only. It does not submit jobs, reserve hardware, validate production quantum behavior, or grant HQA live hardware authority.
