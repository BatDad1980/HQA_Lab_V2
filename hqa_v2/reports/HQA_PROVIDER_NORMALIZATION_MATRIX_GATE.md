# HQA Provider Normalization Matrix Gate

## Purpose

This gate verifies provider-dialect normalization coverage and boundary behavior.

## Results

- Checks: `12`
- Passed: `12`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Matrix schema is V0. |
| shadow_only | PASS | Mode: `shadow_normalization_only`. |
| no_hardware_authority | PASS | No packet grants hardware authority. |
| no_credential_access | PASS | No packet reads or requires credentials. |
| provider_coverage | PASS | Providers: `aws_braket, azure_quantum, cirq_qsim, ibm_qiskit_runtime, nvidia_cuda_q, qutip_dynamiqs`. |
| topology_family_coverage | PASS | Families: `bosonic_cat, grid_lattice, heavy_hex, neutral_graph`. |
| provider_count | PASS | Packets: `6`. |
| each_packet_hashed | PASS | Every packet has a source hash. |
| ibm_defect_density | PASS | IBM fixture maps degraded qubits to defect density. |
| cat_lane_present | PASS | Bosonic/cat solver lane exists. |
| neutral_aggregators_present | PASS | Aggregator/runtime lanes are represented. |
| boundary_words_present | PASS | Adapter boundaries block credentials, live jobs, and hardware control. |

## Boundary

This gate validates offline normalization only. It does not validate live vendor access, physical quantum performance, provider credentials, or HAL execution.
