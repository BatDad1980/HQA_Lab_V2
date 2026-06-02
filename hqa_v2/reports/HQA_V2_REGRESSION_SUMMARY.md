# HQA V2 Regression Summary

## Purpose

This report summarizes the safe HQA V2 proxy demo/regression set.

It verifies that the demos run from a clean repository root and that active text artifacts pass the claim-boundary smoke test.

## Results

- Commands run: `54`
- Passed: `54`
- Failed: `0`

| Check | Status | Seconds | Command |
|---|---:|---:|---|
| HAL safety | PASS | 0.112 | `python hqa_v2/demos/hqa_hal_safety_demo.py` |
| Topology routing | PASS | 0.090 | `python hqa_v2/demos/hqa_topology_routing_demo.py` |
| Live telemetry | PASS | 0.617 | `python hqa_v2/demos/hqa_live_control_loop_demo.py` |
| Predictive homeostasis | PASS | 0.609 | `python hqa_v2/demos/hqa_predictive_homeostasis_demo.py` |
| CR routing | PASS | 0.097 | `python hqa_v2/demos/hqa_cr_routing_demo.py` |
| Analog pulse shaping | PASS | 0.109 | `python hqa_v2/demos/hqa_analog_pulse_demo.py` |
| Cat-qubit proxy | PASS | 0.113 | `python hqa_v2/demos/alice_and_bob_cat_qubit_demo.py` |
| Simulator readiness | PASS | 0.113 | `python hqa_v2/integrations/simulator_readiness.py` |
| IBM runtime dry readiness | PASS | 0.126 | `python hqa_v2/integrations/ibm_runtime_readiness.py` |
| Simulator adapter smoke | PASS | 0.099 | `python hqa_v2/quality/simulator_adapter_smoke_test.py` |
| Simulator facade smoke | PASS | 5.555 | `python hqa_v2/quality/simulator_facade_smoke_test.py` |
| Qiskit cascade observer | PASS | 0.895 | `python hqa_v2/integrations/qiskit_cascade_observer.py` |
| Qiskit Aer cascade noise probe | PASS | 2.474 | `python hqa_v2/integrations/qiskit_aer_cascade_noise_probe.py` |
| Qiskit Aer cascade gate | PASS | 0.111 | `python hqa_v2/quality/qiskit_aer_cascade_gate.py` |
| HQA risk field | PASS | 0.142 | `python hqa_v2/integrations/hqa_risk_field_v0.py` |
| HQA risk field gate | PASS | 0.096 | `python hqa_v2/quality/hqa_risk_field_gate.py` |
| Shadow adaptive proposal | PASS | 0.183 | `python hqa_v2/integrations/shadow_adaptive_proposal_v0.py` |
| Shadow adaptive proposal gate | PASS | 0.126 | `python hqa_v2/quality/shadow_adaptive_proposal_gate.py` |
| Simulator stress schedule | PASS | 0.491 | `python hqa_v2/integrations/simulator_stress_schedule_v0.py` |
| Simulator stress schedule gate | PASS | 0.167 | `python hqa_v2/quality/simulator_stress_schedule_gate.py` |
| Environment profile library | PASS | 0.119 | `python hqa_v2/integrations/environment_profile_library_v0.py` |
| Environment profile library gate | PASS | 0.141 | `python hqa_v2/quality/environment_profile_library_gate.py` |
| Cat cascade proxy | PASS | 0.125 | `python hqa_v2/integrations/cat_cascade_proxy.py` |
| Cat solver contract | PASS | 0.145 | `python hqa_v2/integrations/cat_solver_contract_v0.py` |
| Cat solver contract gate | PASS | 0.137 | `python hqa_v2/quality/cat_solver_contract_gate.py` |
| External quantum trace intake | PASS | 0.146 | `python hqa_v2/integrations/external_quantum_trace_intake_v0.py` |
| External quantum trace intake gate | PASS | 0.159 | `python hqa_v2/quality/external_quantum_trace_intake_gate.py` |
| Topology compensation profiles | PASS | 0.126 | `python hqa_v2/integrations/topology_compensation_profiles_v0.py` |
| Topology compensation profiles gate | PASS | 0.132 | `python hqa_v2/quality/topology_compensation_profiles_gate.py` |
| Dual vendor test matrix | PASS | 0.145 | `python hqa_v2/integrations/dual_vendor_test_matrix_v0.py` |
| Dual vendor test matrix gate | PASS | 0.156 | `python hqa_v2/quality/dual_vendor_test_matrix_gate.py` |
| Legacy scar router | PASS | 0.115 | `python hqa_v2/integrations/legacy_scar_router_v0.py` |
| Legacy scar router gate | PASS | 0.108 | `python hqa_v2/quality/legacy_scar_router_gate.py` |
| Legacy autonomic stress regulator | PASS | 0.127 | `python hqa_v2/integrations/legacy_autonomic_stress_regulator_v0.py` |
| Legacy autonomic stress regulator gate | PASS | 0.125 | `python hqa_v2/quality/legacy_autonomic_stress_regulator_gate.py` |
| HQA mud run | PASS | 0.200 | `python hqa_v2/integrations/hqa_mud_run_v0.py` |
| HQA mud run gate | PASS | 0.132 | `python hqa_v2/quality/hqa_mud_run_gate.py` |
| Cognitive advisory contract | PASS | 0.161 | `python hqa_v2/integrations/cognitive_advisory_contract_v0.py` |
| Cognitive advisory contract gate | PASS | 0.132 | `python hqa_v2/quality/cognitive_advisory_contract_gate.py` |
| HQA intervention gate | PASS | 0.126 | `python hqa_v2/integrations/hqa_intervention_gate_v0.py` |
| HQA intervention gate quality | PASS | 0.119 | `python hqa_v2/quality/hqa_intervention_gate_quality.py` |
| Telemetry compression gate | PASS | 0.133 | `python hqa_v2/integrations/telemetry_compression_gate_v0.py` |
| Telemetry compression gate quality | PASS | 0.115 | `python hqa_v2/quality/telemetry_compression_gate_quality.py` |
| Patch routing prototype | PASS | 0.131 | `python hqa_v2/integrations/patch_routing_prototype_v0.py` |
| Patch routing prototype quality | PASS | 0.147 | `python hqa_v2/quality/patch_routing_prototype_quality.py` |
| Provider normalization matrix | PASS | 0.124 | `python hqa_v2/integrations/provider_normalization_matrix_v0.py` |
| Provider normalization matrix gate | PASS | 0.098 | `python hqa_v2/quality/provider_normalization_matrix_gate.py` |
| Schema contract smoke | PASS | 0.188 | `python hqa_v2/quality/schema_contract_smoke_test.py` |
| Vendor shadow packet | PASS | 0.173 | `python hqa_v2/package/build_vendor_shadow_packet.py` |
| Vendor shadow packet validation | PASS | 0.117 | `python hqa_v2/quality/vendor_shadow_packet_validation.py` |
| Stress harness | PASS | 0.099 | `python hqa_v2/demos/hqa_stress_harness.py` |
| Deterministic stress scenarios | PASS | 0.174 | `python hqa_v2/quality/hqa_v2_stress_scenarios.py` |
| Integrated loop | PASS | 0.698 | `python hqa_v2/demos/hqa_v2_integrated_control_loop.py` |
| Claim boundary smoke | PASS | 0.327 | `python hqa_v2/quality/claim_boundary_smoke_test.py` |

## Failure Details

No failures.

## Boundary

This regression suite validates proxy control-flow behavior only. It does not claim physical quantum validation, production QEC performance, or uncontrolled hardware execution.
