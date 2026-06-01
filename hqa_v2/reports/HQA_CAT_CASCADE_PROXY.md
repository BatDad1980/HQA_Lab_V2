# HQA Cat Cascade Proxy

## Purpose

This report defines the cat-qubit cascade evidence lane for HQA V2.

Gate-level simulators are useful for control-plane plumbing, but cat-qubit cascade work requires bosonic/open-system solvers. This proxy captures the intended model and evidence stream without pretending unavailable solvers have run.

## Solver Readiness

- QuTiP available: `False`
- Dynamiqs available: `False`
- JAX available: `False`
- Selected lane: `spec_only`

| Solver | Status | Intended Use | Missing Reason |
|---|---:|---|---|
| Dynamiqs/JAX | unavailable | GPU/JAX Monte Carlo trajectories and Lindblad dynamics for photon-loss cascade studies. | dynamiqs and jax must both be installed. |
| QuTiP | unavailable | Academic-reference open-system master equation and trajectory checks. | qutip is not installed. |

## Cascade Model

- Primary seed: `single-photon-loss event in oscillator mode`
- Secondary seed: `ancilla/readout fault that masks parity change`
- State space: `truncated bosonic Hilbert space / oscillator phase-space proxy`
- Sentinel trigger: `parity anomaly persists or repeats across correction cycles`
- Quarantine target: `oscillator_mode_or_patch_id`
- HQA action: `SENTINEL_QUARANTINE_AND_ROUTE_AROUND_PATCH_PROPOSAL`

## Required Observables

- parity expectation over correction cycles
- photon-number drift
- logical bit-flip proxy
- phase-flip proxy
- Wigner negativity / lobe separation proxy

## Required Evidence Streams

- cycle-indexed parity measurements
- trajectory-indexed jump records
- Wigner snapshot metadata
- sentinel trigger timestamp
- quarantine/reroute decision manifest

## Boundary

This is a solver-ready proxy specification. It does not run a bosonic simulation unless QuTiP or Dynamiqs/JAX is installed, and it does not validate physical cat-qubit hardware, production QEC performance, or live control authority.
