# HQA Provider Replay Harness Gate

## Purpose

This gate verifies that all normalized provider lanes replay through bounded deterministic HQA responses.

## Results

- Checks: `14`
- Passed: `14`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Replay schema is V0. |
| shadow_only | PASS | Mode: `shadow_replay_only`. |
| no_hardware_authority | PASS | Replay grants no hardware authority. |
| no_credentials | PASS | Replay reads no credentials. |
| no_live_jobs | PASS | Replay submits no jobs. |
| provider_coverage | PASS | Providers: `aws_braket, azure_quantum, cirq_qsim, ibm_qiskit_runtime, nvidia_cuda_q, qutip_dynamiqs`. |
| provider_count | PASS | Results: `6`. |
| ibm_stands_down | PASS | IBM stable calibration replays as stand-down. |
| cuda_replay | PASS | CUDA-Q metadata replays as simulator replay. |
| cat_shadow_optimization | PASS | Cat solver lane replays as shadow optimization monitor. |
| grid_patch_replay | PASS | Grid/lattice lane exercises patch-routing replay. |
| aggregators_metadata_only | PASS | Aggregator lanes remain metadata-only. |
| decision_diversity | PASS | Decision set size: `5`. |
| features_used | PASS | Every replay declares normalized feature classes used. |

## Boundary

This gate validates shadow replay only. It does not validate live provider access, physical quantum performance, production QEC, credentials, or HAL execution.
