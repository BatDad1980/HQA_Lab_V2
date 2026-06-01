# HQA External Quantum Trace Intake V0

## Purpose

This report defines and exercises the front door for external quantum telemetry before it can enter HQA risk-field logic.

The intake layer validates provenance, redaction, topology bounds, syndrome bounds, and live-authority boundaries. It does not contact vendors or submit jobs.

## Contract Summary

- Schema version: `hqa.external_quantum_trace_intake.v0`
- Execution mode: `intake_validation_only`
- Hardware authority: `False`
- Allowed vendors: `alice_bob, google, ibm, local_simulator, neutral_vendor`
- Allowed topology families: `bosonic_cat, grid_lattice, heavy_hex, neutral_graph`

## Intake Decisions

| Trace | Vendor | Accepted | Normalized | Reasons | Output |
|---|---|---:|---:|---|---|
| `TRACE-IBM-SHADOW-001` | `ibm` | `True` | `True` | - | `outputs\external_trace_intake_v0\TRACE-IBM-SHADOW-001_normalized.json` |
| `TRACE-REJECT-SECRET-001` | `unknown_lab` | `False` | `False` | unknown source_vendor `unknown_lab`; unknown topology_family `unknown_shape`; missing provenance.permission_basis; secret-like content detected; invalid coherence_score for node `Q_0`; invalid syndrome_bits for record `BAD`; invalid confidence for record `BAD`; trace requested forbidden live authority | `-` |

## Boundary

External trace intake validates and normalizes data only. It does not contact vendors, submit jobs, validate physical quantum performance, or authorize hardware control.
