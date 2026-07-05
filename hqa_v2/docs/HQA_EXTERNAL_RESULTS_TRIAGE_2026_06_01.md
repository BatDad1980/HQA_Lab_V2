# HQA External Results Triage - 2026-06-01

## Purpose

This memo records a careful triage of two external-result documents supplied from the private Quantum Jedi lane:

- `HQA_IBM_QPU_RESULTS.md`
- `HQA_CAT_QUBIT_RESULTS.md`

The files were read as candidate evidence notes. They are not copied into the HQA Lab evidence chain as raw proof, because the clean lab must preserve source boundaries, provenance, and claim discipline.

## IBM Marrakesh Result

### What It Appears To Show

The IBM result contains:

- Target backend: `ibm_marrakesh`.
- Topology family: heavy-hex.
- Processor scale: 156 qubits.
- Calibration-derived metrics:
  - mean `T1`
  - mean `T2`
  - mean readout error
- Conservative defect thresholds.
- Defect/quarantine list: 55 of 156 qubits.
- Coupling-map pruning from 352 to 154 connections.
- Bell-state comparison:
  - unadapted route fidelity: `97.27%`
  - HQA quarantine-map route fidelity: `97.56%`
  - delta: `+0.29%`
  - transpile time also improved.

### Correct Evidence Label

This should be treated as:

```text
IBM heavy-hex calibration-derived quarantine and routing evidence,
with local noisy simulation comparison using live/device-derived parameters.
```

It should not be described as:

```text
Full physical QPU fidelity validation of HQA closed-loop control.
```

Reason:

The document states the physical backend/calibration was used, but the circuit comparison was run under a local noisy simulator matching the live device's physical error parameters.

### HQA Lab Relevance

This is highly relevant to the new intake lane:

- `source_vendor`: `ibm`
- `topology_family`: `heavy_hex`
- `collection_mode`: likely `hardware_export` or `vendor_shadow`, depending on provenance.
- HQA normalization target:
  - topology snapshot
  - syndrome/defect record
  - topology compensation metadata
  - risk field
  - shadow proposal

The key value is not the small 2-qubit Bell delta alone. The stronger value is the quarantine/routing evidence against a real heavy-hex calibration map.

## Cat-Qubit Result

### What It Appears To Show

The cat-qubit result contains:

- A modeled asymmetric noise trade-off:
  - bit-flip suppression as photon size increases
  - phase-flip exposure as photon size increases
- A grid/optimizer search over alpha.
- Static baseline at alpha `1.20`.
- HQA closed-loop adapted alpha `1.35`.

> **Correction (2026-07-05):** an earlier draft of this section reported a `+2.68%`
> combined-fidelity gain (baseline `93.82%` -> adapted `96.50%`). That number is
> **not reproduced by any run and is retired.** The only actual cat run on record
> (same alpha 1.20 -> 1.35) is a **null**: combined fidelity 95.15% -> 94.97%
> (delta -0.18%), because at that noise level the default alpha is already
> near-optimal and forcing alpha=1.35 slightly overshoots it. The reproducible,
> dynamiqs-validated result is in `reports/HQA_CAT_SETPOINT_HOMEOSTASIS_V0.md`:
> setpoint tracking helps only when the noise *asymmetry* drifts, and correctly
> does nothing when it does not. Do not cite `+2.68%`.

### Correct Evidence Label

This should be treated as:

```text
Cat-qubit asymmetric noise-model validation and alpha-optimization evidence.
```

It should not be described as:

```text
Physical Alice & Bob hardware validation.
```

Reason:

The document frames the model as characteristic of bosonic cat-qubit systems. It does not show an authorized physical cat-qubit hardware trace.

### HQA Lab Relevance

This is relevant to:

- `hqa_v2/integrations/cat_solver_contract_v0.py`
- `hqa_v2/reports/HQA_CAT_SOLVER_CONTRACT_V0.md`
- `topology_family`: `bosonic_cat`

Before entering the HQA Lab evidence chain, future cat results should emit the required contract fields:

- solver name/version
- trajectory ID
- cycles
- parity history
- photon-loss events
- logical error proxy
- Wigner metadata
- cascade indicator
- confidence

## Chip-Design Compensation

These results reinforce the need for the topology-compensation layer.

HQA should not change its core logic for every company. It should normalize different chip designs into one internal grammar:

```text
vendor topology
  -> topology family compensation
  -> HQA node/edge graph
  -> syndrome/risk/proposal chain
```

Current supported topology families:

- `heavy_hex`
- `grid_lattice`
- `bosonic_cat`
- `neutral_graph`

## Recommended Next Step

Create an authorized, redacted static trace packet from the IBM Marrakesh result using the external intake format:

- one topology snapshot
- one defect/quarantine record
- one routing/pruning summary
- one provenance block
- no API keys or account metadata

Then run:

```powershell
python hqa_v2/integrations/external_quantum_trace_intake_v0.py
python hqa_v2/quality/external_quantum_trace_intake_gate.py
```

The clean milestone is:

```text
real calibration-derived trace
  -> HQA intake accepted
  -> topology compensation attached
  -> risk/proposal chain replayed
  -> advisory-only report generated
```

## Boundary

These results are promising candidate evidence notes.

They do not yet convert HQA Lab V2 into a physically validated quantum controller, production QEC system, or live hardware control stack.
