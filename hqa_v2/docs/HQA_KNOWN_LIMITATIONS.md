# HQA Known Limitations

## Purpose

This document states the current limits of HQA V2 plainly.

HQA is being developed as a controlled proxy and shadow-advisory architecture for quantum-adjacent safety, routing, and evidence capture. The current evidence is useful, but it must be interpreted inside its actual test boundaries.

## Current Evidence Boundary

| Area | Current Status | Limitation |
|---|---|---|
| Local proxy stack | Demonstrated through repeatable local demos and regression gates. | Proxy behavior is not the same as deployed lab hardware control. |
| IBM backend telemetry | Calibration/topology snapshots and reported adjacent-lane validation outcomes have been captured. | Clean-lane IBM work defaults to metadata capture and replay; live execution requires explicit authorization and job evidence. |
| Noisy circuit comparison | Bell-state comparisons can be run under local simulator noise models informed by backend telemetry. | These are local noisy simulations unless a real QPU job ID is present. |
| Quarantine/reroute logic | Degraded-node avoidance and shadow reroute proposals are replayable. | Current routing evidence is advisory and shadow-mode, not live modification of provider routing tables. |
| Cat-qubit lane | Cat-qubit proxy and solver contracts exist; QuTiP/Dynamiqs are available locally. | Current cat-qubit evidence should be treated as proxy/analytical until full bosonic solver runs are integrated and documented. |
| HAL boundary | Dry-run and mock loopback boundary contracts are tested. | Mock loopback ACKs are transport evidence only; they are not physical cryostat control. |
| BACL policy | Entropy, one-time-use, and fail-closed authority contracts are documented. | Current BACL proofs are local policy proofs, not a production cryptographic certification. |
| LLM advisory | Cognitive advisory is bounded by deterministic gates. | LLM output is non-authoritative and must never override BACL, HAL, intervention gates, or safe holds. |
| Large-scale legacy simulations | Older stress tests explored very large simulated fabrics. | Older scale results are model outcomes under simplified assumptions, not physical billion-qubit validation. |

## Benchmark Limitations

The older large-scale benchmark language must be read carefully:

- The simulated fabric uses simplified local error assumptions.
- The traditional baseline is a simple reference baseline, not a state-of-the-art production decoder.
- The result is useful as a stress contrast, not as a universal decoder comparison.
- Any external benchmark comparison should state the baseline, error model, hardware, runtime, and assumptions.

Future benchmark work should include fair comparisons against stronger decoder baselines such as PyMatching-style MWPM workflows where appropriate.

## IBM Validation Language

Safe wording:

> HQA has captured real IBM calibration/topology telemetry and used that telemetry in local noisy-simulation and shadow-replay workflows.

Only use stronger wording when a report includes:

- backend name
- job ID
- circuit submitted
- shot count
- timestamp
- result counts
- queue/execution metadata
- exact HQA intervention mode used

Without those, the evidence should be described as real telemetry plus local simulator or replay evidence.

## Cat-Qubit Language

Safe wording:

> HQA includes a cat-qubit proxy lane and solver contract for asymmetric bit-flip/phase-flip reasoning.

Current limitation:

- Full bosonic dynamics are not yet the clean-lane default.
- Analytical alpha tuning is useful as a proxy, but it should not be described as vendor-grade cat-qubit validation.
- Dynamiqs/QuTiP integration should be documented before cat-qubit claims are expanded.

## HAL And Physical Control Boundary

Safe wording:

> HQA can model HAL manifests, dry-run safety gates, and mock loopback transport ACKs.

Current limitation:

- Mock loopback server responses do not equal physical cryostat execution.
- A TCP ACK is not authority.
- Physical endpoints must require explicit configuration, operator approval, and safety interlocks.
- Missing or invalid BACL authority must fail closed.

## LLM Advisory Boundary

The LLM advisory layer should remain:

- non-authoritative
- bounded
- explainability-focused
- telemetry-compression-aware
- unable to authorize hardware action

The deterministic control plane must make the safety decision. The LLM may explain or summarize that decision.

## Package Structure Limitation

The broader HQA workspace currently contains multiple development layers:

- root-level historical/storm-lab files
- `hqa/` active implementation files
- `hqa_v2/` clean proxy/evidence lane

For external review, the reviewer should be directed to the clean lane first:

- `hqa_v2/docs/HQA_REVIEWER_BRIEF.md`
- `hqa_v2/docs/HQA_TECHNICAL_INDEX.md`
- `hqa_v2/docs/HQA_KNOWN_LIMITATIONS.md`
- `hqa_v2/reports/HQA_V2_REGRESSION_SUMMARY.md`

The duplicate module structure is a maintainability concern and should be consolidated gradually after claim hygiene and evidence packaging are stable.

## Non-Claims

HQA V2 currently does not claim:

- deployed physical quantum hardware control
- production QEC performance
- vendor-certified cat-qubit validation
- broad artificial cognition
- unrestricted autonomous hardware action
- replacement for provider safety systems
- certification under any external security, safety, or regulatory framework

## Reviewer Principle

Evaluate HQA V2 as a local-control architecture with proxy evidence, safety contracts, replayable gates, and a credible path toward lab integration.

Do not evaluate it as a finished quantum hardware product.

