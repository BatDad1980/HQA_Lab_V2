# HQA IBM Backend Field Map Gate

## Purpose

This gate verifies that IBM backend field-map evidence exposes qubit and edge neighborhoods without expanding authority.

## Results

- Checks: `11`
- Passed: `11`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Field-map schema is V0. |
| ibm_heavy_hex | PASS | IBM heavy-hex lane is declared. |
| no_hardware_authority | PASS | No HAL authority granted. |
| no_jobs_submitted | PASS | Zero provider jobs submitted. |
| qubit_fields_present | PASS | Every qubit has health fields. |
| edge_fields_present | PASS | Every edge has neighborhood fields. |
| degraded_reasons_present | PASS | Every degraded qubit has a reason. |
| degraded_edges_visible | PASS | Summary matches degraded edge count. |
| cluster_proxy_visible | PASS | Cluster proxy is available. |
| fixture_offline_by_default | PASS | Mode: `offline_fixture`. |
| boundary_present | PASS | Boundary blocks jobs and HAL authority. |

## Boundary

This gate validates field-map evidence shape only. It does not validate live quantum performance, submit jobs, run circuits, alter pulses, or authorize HAL execution.
