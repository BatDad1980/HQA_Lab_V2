# HQA Simulator Readiness

## Purpose

This report checks optional quantum simulator packages for HQA V2 integration work.

HQA remains runnable without these packages. Missing packages mean the corresponding simulator lane is unavailable, not that HQA is broken.

## Summary

- Optional packages checked: `7`
- Installed: `4`
- Missing: `3`

| Lane | Import | Status | Purpose |
|---|---|---:|---|
| IBM Quantum | `qiskit` | AVAILABLE | Qiskit circuit and backend integration |
| IBM Aer | `qiskit_aer` | AVAILABLE | Qiskit Aer simulator integration |
| Google Quantum AI | `cirq` | AVAILABLE | Cirq circuit integration |
| Google qsim | `qsimcirq` | AVAILABLE | qsim-backed Cirq simulation |
| Open systems | `qutip` | MISSING | QuTiP open-system experiments |
| Bosonic / cat-qubit | `dynamiqs` | MISSING | Dynamiqs/JAX solver experiments |
| JAX backend | `jax` | MISSING | JAX runtime used by Dynamiqs |

## Recommended Install Profiles

- Core simulator lane: `pip install -r hqa_v2/integrations/requirements-core.txt`
- Bosonic/cat-qubit lane: `pip install -r hqa_v2/integrations/requirements-bosonic.txt`
- IBM Aer GPU lane: `pip install -r hqa_v2/integrations/requirements-ibm-gpu.txt`

Use a dedicated virtual environment. Do not make these packages mandatory for the base HQA regression suite.

## Boundary

This readiness check validates Python package availability only. It does not validate physical quantum hardware, production QEC performance, or live backend access.
