# HQA Lab First Pass - 2026-05-31

## Purpose

This pass converts the HQA V2 branch from a collection of promising proxy modules into a cleaner lab workflow that can be run from a fresh clone.

The goal was not to expand claims.

The goal was to make the existing architecture easier to execute, audit, and keep inside a disciplined evidence boundary.

## What Changed

### Demo Bootstrap

Added:

- `hqa_v2/demos/_bootstrap.py`

The bootstrap lets demos run directly from the repository root without manually setting `PYTHONPATH`.

Example:

```bash
python hqa_v2/demos/hqa_stress_harness.py
python hqa_v2/demos/hqa_hal_safety_demo.py
python hqa_v2/demos/hqa_topology_routing_demo.py
```

### Stress Harness Repair

Fixed:

- `hqa_v2/core/fabric_simulator.py`

`inject_stress()` now logs and returns the injected fault list. The stress harness previously expected this list but received `None`.

### Integrated Control Loop Repair

Updated:

- `hqa_v2/demos/hqa_v2_integrated_control_loop.py`

The integrated demo now uses the current HQA V2 APIs:

- `AuditLogger`
- `FabricSimulator(logger, width, height)`
- `inject_targeted_fault()`
- `LocalSentinelReflex.evaluate_faults()`
- `QuarantineManager.execute_quarantines()`
- `TopologyRouter.reroute_circuit()`
- `PulseTranslator.generate_hardware_instructions()`
- `HALCryostatBridge.dispatch_hardware_commands()`

The demo remains dry-run bounded.

### Output Path Discipline

Demos now write generated logs into:

- `hqa_v2/logs/`

And generated reports into:

- `hqa_v2/reports/`

This keeps root-level report clutter out of the repo.

### Claim Boundary Smoke Test

Added:

- `hqa_v2/quality/claim_boundary_smoke_test.py`

The scanner checks active demos and reports for overclaim language categories such as:

- absolute proof phrasing
- claims of achieved physical homeostasis
- mythic protocol labels
- unbounded scalability claims
- impossible assurance language

Explicit non-claim lines are allowed so boundary memos can still say what HQA is not.

## Verification

The following demos were run from the repository root:

- `hqa_v2/demos/hqa_hal_safety_demo.py`
- `hqa_v2/demos/hqa_topology_routing_demo.py`
- `hqa_v2/demos/hqa_live_control_loop_demo.py`
- `hqa_v2/demos/hqa_predictive_homeostasis_demo.py`
- `hqa_v2/demos/hqa_cr_routing_demo.py`
- `hqa_v2/demos/hqa_analog_pulse_demo.py`
- `hqa_v2/demos/alice_and_bob_cat_qubit_demo.py`
- `hqa_v2/demos/hqa_stress_harness.py`
- `hqa_v2/demos/hqa_v2_integrated_control_loop.py`

Claim-boundary smoke test:

```text
CLAIM BOUNDARY SMOKE TEST: PASS
Scanned 19 text files.
```

## Current Boundary

HQA V2 should be described as:

> A modular quantum-control proxy stack for topology-aware routing, localized fault response, dry-run HAL safety, and replayable audit evidence.

HQA V2 should not be described as:

- physical quantum validation
- a solved QEC system
- quantum supremacy
- unbounded scalability
- unbounded hardware execution

## Next Recommended Phase

Build a unified V2 regression runner that executes the safe demos, runs the claim-boundary smoke test, and emits one top-level markdown summary.

Suggested artifact:

- `hqa_v2/quality/hqa_v2_regression_runner.py`
- `hqa_v2/reports/HQA_V2_REGRESSION_SUMMARY.md`
