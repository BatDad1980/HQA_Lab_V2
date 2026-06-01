# HQA Risk Field V0

## Purpose

This report converts HQA-native evidence into a bounded cascade-risk field.

The field is designed to rank local risk and recommend shadow-mode review actions. It does not authorize physical hardware control.

## Inputs

- Topology source: `outputs\vendor_shadow_packet_v1\01_topology_snapshot.json`
- Syndrome source: `outputs\vendor_shadow_packet_v1\02_syndrome_record.json`
- Cascade source: `logs/qiskit_aer_cascade_noise_probe.json`

## Field Summary

- Execution mode: `shadow_advisory`
- Hardware authority: `False`
- Cascade contrast: `0.886718`
- Suspected patch: `Q_1`
- Recommended advisory action: `ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL`

## Node Risk Ranking

| Rank | Node | Role | Status | Coherence | Coupling Fragility | Syndrome Pressure | Cascade Pressure | Risk Score | Band |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | `Q_1` | `data` | `degraded` | `0.42` | `0.19` | `0.4276` | `0.159609` | `0.954809` | `critical` |
| 2 | `Q_0` | `data` | `healthy` | `0.97` | `0.19` | `0.3002` | `0.159609` | `0.500409` | `elevated` |
| 3 | `Q_3` | `readout` | `healthy` | `0.94` | `0.12` | `0.1` | `0.055863` | `0.195463` | `low` |
| 4 | `Q_2` | `ancilla` | `healthy` | `0.96` | `0.12` | `0.1` | `0.055863` | `0.188663` | `low` |

## Evidence Notes

### `Q_1`

- coherence: `0.42`
- status: `degraded`
- cascade contrast: stress `0.914062` minus nominal `0.027344`
- topology: weakest coupling `0.81`
- syndrome: seed_error at `Q_1` confidence `0.91`
- syndrome: cascade-like decoder signal

### `Q_0`

- coherence: `0.97`
- status: `healthy`
- cascade contrast: stress `0.914062` minus nominal `0.027344`
- topology: weakest coupling `0.81`
- syndrome: correlated_error at `Q_0` confidence `0.91`
- syndrome: cascade-like decoder signal

### `Q_3`

- coherence: `0.94`
- status: `healthy`
- cascade contrast: stress `0.914062` minus nominal `0.027344`
- topology: weakest coupling `0.88`
- syndrome: cascade-like decoder signal

### `Q_2`

- coherence: `0.96`
- status: `healthy`
- cascade contrast: stress `0.914062` minus nominal `0.027344`
- topology: weakest coupling `0.88`
- syndrome: cascade-like decoder signal

## Boundary

Advisory risk ranking only; no live backend job, pulse change, quarantine command, or HAL execution is authorized.
