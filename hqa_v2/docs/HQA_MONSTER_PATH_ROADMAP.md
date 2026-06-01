# HQA Monster Path Roadmap

## Purpose

This roadmap defines the path for the HQA Lab V1 branch from a safe proxy stack toward a lab-facing quantum-control integration candidate.

The goal is not to claim physical validation before it exists. The goal is to keep turning the architecture into something a technical reviewer can plug into increasingly serious environments without losing the safety boundary.

## Current Position

HQA V2 currently demonstrates a dry-run control plane:

- Synthetic quantum fabric fault injection
- Local sentinel reflex decisions
- Quarantine of degraded nodes
- Topology-aware rerouting
- OpenQASM emission proxy
- CUDA-style edge-kernel proxy with bounded fallback behavior
- HAL dry-run hardware boundary
- Deterministic stress scenarios
- Claim-boundary smoke testing
- Optional simulator readiness checks

This is the garage simulator stage. It is useful because it shows control logic, auditability, and safety behavior without pretending to be a validated quantum hardware controller.

## Phase 1: Simulator Bridge

Turn the proxy stack into a simulator-facing stack.

Primary targets:

- Qiskit and Aer for IBM-style circuit simulation.
- Cirq and qsim for Google-style circuit simulation.
- QuTiP for open-system dynamics.
- Dynamiqs/JAX for bosonic and cat-qubit experiments when that environment is installed.

Deliverables:

- Optional adapter modules that never break the base HQA regression when packages are missing.
- Readiness reports showing which simulator lanes are available.
- Adapter smoke tests proving import discipline.
- Trace conversion from HQA route decisions into simulator inputs.
- Simulator result ingestion back into HQA audit logs.
- Syndrome-history capture for cascade observation instead of final-state-only summaries.
- Custom correlated-noise manifests for local simulator probes.
- Decoder hooks that allow HQA cascade policies to be compared against standard decoder families later.

Acceptance target:

HQA can take one synthetic fault scenario, emit a simulator-ready circuit or model, run it in an available simulator lane, and attach the result to the existing audit chain.

First cascade target:

- Qiskit/Aer lane for dynamic-circuit and syndrome-record plumbing.
- Dynamiqs/QuTiP lane for cat-qubit physics once installed.
- Photon-loss cascade first, gate-induced cascade second.

Compatibility note:

- CUDA-Q is parked until the local CUDA/toolchain versions line up.
- HQA keeps GPU/CUDA language limited to implemented local proxy and fallback behavior.

## Phase 2: Digital Twin Replay

Turn simulator results into repeatable digital-twin evidence.

Primary targets:

- Deterministic scenario packs.
- Replayable JSONL traces.
- Before/after route comparison.
- Quarantine effect measurement.
- Cooling and HAL command dry-run manifests.

Deliverables:

- Scenario manifest format.
- Replay runner.
- Cross-simulator comparison report when multiple backends are installed.
- Failure catalog for no-route, degraded-route, backend-missing, and HAL-block cases.

Acceptance target:

A reviewer can run one command and reproduce the full HQA decision path from fault injection to route decision to simulator trace to HAL dry-run boundary.

## Phase 3: Shadow Hardware Interface

Prepare for a real lab without touching live control authority.

Primary targets:

- Vendor-neutral telemetry schemas.
- Read-only ingestion of calibration snapshots.
- Read-only ingestion of coherence, error, timing, and topology metadata.
- Manifest-only action proposals.
- Human approval hooks.

Deliverables:

- Hardware telemetry schema.
- Lab adapter boundary document.
- Shadow-mode controller that proposes actions but cannot execute them.
- Red-team tests for forbidden live actions.
- Hash-bound audit bundle for every proposed intervention.

Acceptance target:

HQA can sit beside a real system in shadow mode, read approved telemetry, generate an advisory reroute/quench manifest, and prove it executed no physical action.

## Phase 4: Controlled Integration Candidate

Only after simulator and shadow-mode evidence mature, prepare a narrow integration candidate.

Primary targets:

- Single sandboxed testbed.
- One limited fault class.
- One approved advisory output type.
- External controller retains authority.
- Immediate rollback.
- Full audit logging.

Deliverables:

- Integration safety checklist.
- Testbed constraints.
- Rollback protocol.
- Operator approval model.
- Evidence binder.

Acceptance target:

HQA is ready for a technical team to evaluate as a constrained advisory controller, not as an autonomous quantum hardware controller.

## Non-Claims

This roadmap does not claim:

- Physical quantum hardware validation.
- Production quantum error correction.
- Live cryostat control.
- Guaranteed decoherence prevention.
- Quantum advantage.
- Autonomous hardware authority.

## North Star

The monster version of HQA is not louder. It is stricter.

It earns trust by making every step replayable, every boundary visible, every simulator lane optional, and every hardware-facing action constrained until an external lab grants authority.
