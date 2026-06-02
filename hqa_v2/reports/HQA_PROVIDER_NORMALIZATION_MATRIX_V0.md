# HQA Provider Normalization Matrix V0

## Purpose

This report verifies that HQA can receive major quantum-provider telemetry dialects through one shadow adapter grammar.

The adapter matrix is deliberately offline. It uses representative fixtures only, reads no credentials, submits no jobs, and grants no hardware authority.

## Coverage

- Providers covered: `6`
- Topology families covered: `bosonic_cat, grid_lattice, heavy_hex, neutral_graph`
- Execution mode: `shadow_normalization_only`
- Hardware authority: `False`
- Credential access: `False`

| Provider | Lane | Topology Family | HQA Interpretation |
|---|---|---|---|
| `ibm_qiskit_runtime` | `real_qpu_calibration` | `heavy_hex` | IBM-style sparse heavy-hex calibration is interpreted as node health plus coupling risk. |
| `aws_braket` | `aggregated_device_metadata` | `neutral_graph` | Aggregator or runtime metadata is interpreted only from declared graph and result fields. |
| `azure_quantum` | `aggregated_workspace_metadata` | `neutral_graph` | Aggregator or runtime metadata is interpreted only from declared graph and result fields. |
| `nvidia_cuda_q` | `hybrid_runtime_simulation` | `neutral_graph` | Aggregator or runtime metadata is interpreted only from declared graph and result fields. |
| `cirq_qsim` | `grid_circuit_simulation` | `grid_lattice` | Planar grid/lattice data is interpreted as local patch health plus neighborhood rupture risk. |
| `qutip_dynamiqs` | `bosonic_solver_simulation` | `bosonic_cat` | Cat-qubit solver data is interpreted as oscillator/parity health plus photon-loss or phase-bias risk. |

## Boundary

This matrix validates provider-dialect normalization only. It does not prove provider performance, physical quantum control, live cloud access, or production QEC.
