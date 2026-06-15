# HQA Simulator Adapter Smoke Test

## Purpose

This smoke test verifies that optional simulator adapters can be inspected without making those simulator packages mandatory for HQA V2.

## Results

- Adapters checked: `4`
- Available: `4`
- Unavailable: `0`

| Adapter | Status | Boundary |
|---|---:|---|
| `qiskit` | AVAILABLE | Optional simulator adapter; no physical hardware control. |
| `cirq` | AVAILABLE | Optional simulator adapter; no physical hardware control. |
| `qutip` | AVAILABLE | Optional simulator adapter; no physical hardware control. |
| `dynamiqs` | AVAILABLE | Optional simulator adapter; no physical hardware control. |

## Boundary

This test checks adapter availability and import discipline only. It does not validate physical quantum hardware, production QEC performance, or live backend access.
