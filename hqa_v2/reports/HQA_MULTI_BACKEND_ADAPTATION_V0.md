# HQA Multi-Backend Hardware-Adaptive Demonstration V0

*Reads Qiskit-bundled snapshotted device calibration only. Zero jobs submitted,
no credentials, no hardware authority. Calibration-derived advisory analysis --
not a fidelity, control, or QEC claim.*

## What this shows

One HQA pipeline ingests several **different real device snapshots**, normalizes
each into the same health vocabulary, and produces a per-hardware quarantine and
routing decision. The chips differ, so the decisions differ -- with the same code.

Health thresholds (identical for every backend): T1 < 100.0 us, T2 < 40.0 us, readout > 0.03.

| Backend | Qubits | Edges | 2q gate | Mean T1 (us) | Mean T2 (us) | Mean readout | Quarantined | Healthy regions | Largest region | Longest healthy corridor |
|---|---:|---:|:--:|---:|---:|---:|---:|---:|---:|---:|
| `fake_fez` | 156 | 176 | cz | 145.26 | 90.46 | 0.01324 | 54 (34.6%) | 26 | 32 | 19 hops (9→36) |
| `fake_marrakesh` | 156 | 176 | cz | 207.13 | 147.0 | 0.02703 | 52 (33.3%) | 21 | 37 | 24 hops (95→47) |
| `fake_torino` | 133 | 150 | cz | 173.61 | 145.19 | 0.04674 | 70 (52.6%) | 48 | 4 | 2 hops (104→93) |
| `fake_sherbrooke` | 127 | 144 | ecr | 289.55 | 186.01 | 0.04148 | 53 (41.7%) | 20 | 12 | 11 hops (122→86) |
| `fake_brisbane` | 127 | 144 | ecr | 233.71 | 160.58 | 0.03114 | 41 (32.3%) | 18 | 17 | 15 hops (71→2) |
| `fake_osaka` | 127 | 144 | ecr | 281.0 | 162.54 | 0.04194 | 59 (46.5%) | 26 | 9 | 6 hops (101→73) |

## Reading the result

- **Quarantined** differs per chip because each device's real T1/T2/readout snapshot
  differs -- HQA adapts its degraded-region map to the hardware in front of it.
- **Largest healthy region** is the biggest contiguous all-healthy patch left after
  quarantine: a per-device answer to 'how much usable fabric remains, and where.'
- **Longest healthy corridor** is the longest all-healthy path HQA can offer on that
  chip (its diameter through healthy qubits) -- a route that actually exists, with
  different length and endpoints per device.

The point is not any single number; it is that the *same normalization and
adaptation logic* produces hardware-appropriate, materially different decisions
across real IBM device snapshots, at zero cost.

## Scope note

Real-data anchors here are IBM snapshots (the free real calibration available).
Non-IBM providers are covered as dialects in `HQA_PROVIDER_NORMALIZATION_MATRIX_V0`
using representative fixtures; live cross-vendor snapshots would require partner data.

## Boundary

Reads Qiskit-bundled snapshotted device calibration only. No live IBM access, no jobs submitted, no credentials, no hardware authority. Advisory calibration-derived analysis; not a fidelity or QEC claim.
