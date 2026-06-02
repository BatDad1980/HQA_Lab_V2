# HQA Provider Replay Harness V0

## Purpose

This report verifies that normalized provider packets can be replayed through one deterministic HQA response grammar.

The harness is shadow-only: it does not import cloud SDKs, read credentials, submit jobs, or authorize HAL actions.

## Results

- Providers replayed: `6`
- Execution mode: `shadow_replay_only`
- Hardware authority: `False`
- Credential access: `False`
- Live jobs submitted: `False`
- Decision set: `ACCEPT_SIMULATOR_REPLAY, METADATA_ONLY_REPLAY, MONITOR_WITH_SHADOW_OPTIMIZATION, NO_INTERVENTION, PATCH_ROUTING_REPLAY`

| Provider | Lane | Family | Replay Decision | Reviewer Required | Reason |
|---|---|---|---|---:|---|
| `ibm_qiskit_runtime` | `real_qpu_calibration` | `heavy_hex` | `NO_INTERVENTION` | `False` | Heavy-hex calibration is below readout instability threshold; HQA stands down. |
| `aws_braket` | `aggregated_device_metadata` | `neutral_graph` | `METADATA_ONLY_REPLAY` | `False` | Aggregator packet is provider metadata only; no intervention decision can be promoted. |
| `azure_quantum` | `aggregated_workspace_metadata` | `neutral_graph` | `METADATA_ONLY_REPLAY` | `False` | Aggregator packet is provider metadata only; no intervention decision can be promoted. |
| `nvidia_cuda_q` | `hybrid_runtime_simulation` | `neutral_graph` | `ACCEPT_SIMULATOR_REPLAY` | `False` | CUDA-Q packet is local simulator metadata inside the latency budget. |
| `cirq_qsim` | `grid_circuit_simulation` | `grid_lattice` | `PATCH_ROUTING_REPLAY` | `True` | Grid/lattice packet has enough local patch pressure to exercise patch-routing replay. |
| `qutip_dynamiqs` | `bosonic_solver_simulation` | `bosonic_cat` | `MONITOR_WITH_SHADOW_OPTIMIZATION` | `False` | Cat solver packet is stable enough for bounded shadow optimization monitoring. |

## Boundary

Provider replay validates deterministic shadow responses to normalized telemetry. It does not contact providers, submit jobs, prove provider performance, or authorize hardware control.
