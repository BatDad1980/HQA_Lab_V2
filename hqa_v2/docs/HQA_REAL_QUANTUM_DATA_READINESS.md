# HQA Real Quantum Data Readiness

## Purpose

This memo defines the path from local proxy evidence to authorized external quantum telemetry.

The goal is not to claim physical validation before it exists. The goal is to make HQA ready to ingest real traces from an authorized source, normalize them safely, and replay the risk/proposal chain against those traces.

## Current Readiness

HQA V2 now has:

- Local simulator observation lanes.
- Vendor-neutral topology and syndrome schemas.
- Risk-field ranking.
- Shadow adaptive proposal packets.
- Deterministic stress schedule replay.
- Cat-qubit solver evidence contract.
- External quantum trace intake contract.

The external intake lane is implemented as:

- `hqa_v2/integrations/external_quantum_trace_intake_v0.py`
- `hqa_v2/quality/external_quantum_trace_intake_gate.py`
- `hqa_v2/reports/HQA_EXTERNAL_QUANTUM_TRACE_INTAKE_V0.md`
- `hqa_v2/reports/HQA_EXTERNAL_QUANTUM_TRACE_INTAKE_GATE.md`

## What Real Data Must Provide

Before external quantum-company data can enter HQA, it must include:

- Permission basis.
- Source vendor/backend label.
- Topology family label such as `heavy_hex`, `grid_lattice`, `bosonic_cat`, or `neutral_graph`.
- Redaction status.
- Topology nodes with bounded health/coherence scores.
- Topology edges with bounded coupling scores.
- Cycle-indexed syndrome records.
- Confidence values bounded to `[0, 1]`.
- No secrets, tokens, account identifiers, or credential material.
- No request for live backend execution, pulse changes, or HAL action.

## First Real-Data Milestone

The first real-data milestone should be a static export, not live access.

Preferred first packet:

```text
authorized vendor/sample trace
  -> external trace intake
  -> normalized topology/syndrome packet
  -> HQA risk field
  -> shadow adaptive proposal
  -> replayable report
```

## What Counts As Progress

A valid real-data proof would show:

- Intake accepts the authorized trace.
- Unsafe fields are absent or redacted.
- Normalized topology and syndrome records are produced.
- The risk field ranks a patch or reports low activity.
- Topology compensation metadata is attached so HQA does not change core logic per vendor chip family.
- The proposal layer remains advisory-only.
- The result is replayable from disk.

## What Does Not Count

The following do not count as physical validation:

- A screenshot of a vendor dashboard.
- A private API token existing on disk.
- A local simulator trace shaped like a vendor trace.
- A live backend connection that does not produce replayable syndrome/topology evidence.
- Any packet that cannot be shared under permission or MNDA.

## Boundary

HQA is ready for authorized external trace intake.

It is not yet validated against physical quantum hardware, production QEC performance, or live vendor control systems.

## Topology Compensation

Different quantum companies use different chip and substrate designs. HQA should not change its core evaluation angle for each company.

Instead, each external trace must declare a topology family. HQA then attaches interpretation-only compensation metadata:

- `heavy_hex` for sparse heavy-hex style superconducting layouts.
- `grid_lattice` for planar grid/lattice style layouts.
- `bosonic_cat` for oscillator/cat-qubit style evidence.
- `neutral_graph` for vendor-declared graph layouts that should not infer hardware physics.

This keeps HQA's internal grammar stable:

```text
vendor topology
  -> topology family compensation
  -> HQA node/edge graph
  -> syndrome/risk/proposal chain
```

The compensation layer changes interpretation thresholds and risk notes only. It does not authorize calibration, live pulse changes, or topology edits.
