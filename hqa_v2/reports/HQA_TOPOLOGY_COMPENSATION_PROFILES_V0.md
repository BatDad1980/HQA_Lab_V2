# HQA Topology Compensation Profiles V0

## Purpose

This report defines how HQA compensates for different chip/topology families without changing its core risk-field or proposal APIs.

The profile layer prevents vendor-specific geometry from becoming vendor-specific HQA logic.

## Profiles

| Family | Typical Vendor | Connectivity Model | Degree Baseline | Coupling Floor | Risk Bias |
|---|---|---|---:|---:|---|
| `heavy_hex` | `ibm` | `sparse_fixed_frequency_lattice` | `2.4` | `0.55` | watch correlated edge activity and readout-adjacent syndrome persistence |
| `grid_lattice` | `google` | `nearest_neighbor_planar_grid` | `3.2` | `0.5` | watch neighborhood clusters and local patch rupture |
| `bosonic_cat` | `alice_bob` | `oscillator_mode_with_ancilla_controls` | `1.8` | `0.45` | watch parity persistence, photon-loss events, and masked ancilla faults |
| `neutral_graph` | `neutral_vendor` | `vendor_supplied_graph` | `2.0` | `0.4` | use declared topology only; do not infer hardware physics |

## Rule

Every external topology must be normalized into the same HQA node/edge graph and accompanied by a topology-compensation profile.

This allows HQA to compare heavy-hex, grid/lattice, bosonic/cat, and neutral graph evidence without changing its evaluation angle for every company.

## Boundary

Topology compensation profiles normalize interpretation across chip families only. They do not authorize live backend access, calibration, pulse changes, or HAL execution.
