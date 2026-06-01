# HQA Dual Vendor Test Matrix V0

## Purpose

This report defines HQA's dual testing strategy: cat-qubit evidence in one lane, and non-cat vendor topology/syndrome evidence in parallel lanes.

The goal is to test HQA against different chip designs without changing HQA's core evaluation angle for each company.

## Test Lanes

| Lane | Vendor Family | Topology Family | Current Status | HQA Entrypoint |
|---|---|---|---|---|
| `CAT-ALICE-BOB` | `alice_bob` | `bosonic_cat` | `contract_ready_model_evidence_present` | `cat_solver_contract_v0 -> external_trace_intake_v0 -> topology_compensation` |
| `IBM-HEAVY-HEX` | `ibm` | `heavy_hex` | `candidate_calibration_derived_result_present` | `external_trace_intake_v0 -> topology_compensation -> risk_field -> shadow_proposal` |
| `GOOGLE-GRID` | `google` | `grid_lattice` | `intake_ready_no_authorized_trace_yet` | `external_trace_intake_v0 -> topology_compensation -> risk_field -> shadow_proposal` |
| `NEUTRAL-VENDOR-GRAPH` | `neutral_vendor` | `neutral_graph` | `schema_ready` | `external_trace_intake_v0 -> topology_compensation -> risk_field -> shadow_proposal` |

## Required Next Evidence

### `CAT-ALICE-BOB`

- authorized cat-qubit solver output or hardware export
- parity history
- photon-loss events
- logical error proxy
- Wigner metadata summary
- confidence-bounded cascade indicator

Comparison goal: Compare static alpha/control parameters against HQA-adapted alpha/control proposals under asymmetric X/Z noise.

Boundary: Cat lane must not be described as Alice & Bob physical validation until authorized physical cat-qubit traces exist.

### `IBM-HEAVY-HEX`

- redacted backend calibration export
- defect/quarantine list
- coupling map before and after pruning
- routing comparison trace
- provenance and permission basis

Comparison goal: Compare default routing against HQA quarantine/reroute posture on heavy-hex calibration data.

Boundary: IBM lane should distinguish physical calibration access from local noisy simulation comparison.

### `GOOGLE-GRID`

- authorized grid/lattice topology export
- cycle-indexed syndrome or error proxy records
- coupling/edge health records
- provenance and permission basis

Comparison goal: Evaluate whether HQA risk ranking remains stable on planar grid/lattice neighborhood rupture patterns.

Boundary: Google lane remains schema-ready only until authorized trace data exists.

### `NEUTRAL-VENDOR-GRAPH`

- declared node/edge graph
- declared health metrics
- syndrome or error-history trace
- provenance and permission basis

Comparison goal: Test HQA without inferring undocumented hardware physics from the vendor graph.

Boundary: Neutral lane uses declared topology only and does not infer substrate physics.

## Boundary

The matrix coordinates evidence lanes only. It does not contact vendors, submit jobs, claim physical validation, or authorize live hardware action.
