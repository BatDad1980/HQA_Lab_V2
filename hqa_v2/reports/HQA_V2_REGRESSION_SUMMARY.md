# HQA V2 Regression Summary

## Purpose

This report summarizes the safe HQA V2 proxy demo/regression set.

It verifies that the demos run from a clean repository root and that active text artifacts pass the claim-boundary smoke test.

## Results

- Commands run: `32`
- Passed: `32`
- Failed: `0`

| Check | Status | Seconds | Command |
|---|---:|---:|---|
| HAL safety | PASS | 0.099 | `python hqa_v2/demos/hqa_hal_safety_demo.py` |
| Topology routing | PASS | 0.088 | `python hqa_v2/demos/hqa_topology_routing_demo.py` |
| Live telemetry | PASS | 0.596 | `python hqa_v2/demos/hqa_live_control_loop_demo.py` |
| Predictive homeostasis | PASS | 0.609 | `python hqa_v2/demos/hqa_predictive_homeostasis_demo.py` |
| CR routing | PASS | 0.082 | `python hqa_v2/demos/hqa_cr_routing_demo.py` |
| Analog pulse shaping | PASS | 0.091 | `python hqa_v2/demos/hqa_analog_pulse_demo.py` |
| Cat-qubit proxy | PASS | 0.083 | `python hqa_v2/demos/alice_and_bob_cat_qubit_demo.py` |
| Simulator readiness | PASS | 0.079 | `python hqa_v2/integrations/simulator_readiness.py` |
| IBM runtime dry readiness | PASS | 0.082 | `python hqa_v2/integrations/ibm_runtime_readiness.py` |
| Simulator adapter smoke | PASS | 0.095 | `python hqa_v2/quality/simulator_adapter_smoke_test.py` |
| Simulator facade smoke | PASS | 5.269 | `python hqa_v2/quality/simulator_facade_smoke_test.py` |
| Qiskit cascade observer | PASS | 0.775 | `python hqa_v2/integrations/qiskit_cascade_observer.py` |
| Qiskit Aer cascade noise probe | PASS | 2.057 | `python hqa_v2/integrations/qiskit_aer_cascade_noise_probe.py` |
| Qiskit Aer cascade gate | PASS | 0.065 | `python hqa_v2/quality/qiskit_aer_cascade_gate.py` |
| HQA risk field | PASS | 0.080 | `python hqa_v2/integrations/hqa_risk_field_v0.py` |
| HQA risk field gate | PASS | 0.067 | `python hqa_v2/quality/hqa_risk_field_gate.py` |
| Shadow adaptive proposal | PASS | 0.110 | `python hqa_v2/integrations/shadow_adaptive_proposal_v0.py` |
| Shadow adaptive proposal gate | PASS | 0.068 | `python hqa_v2/quality/shadow_adaptive_proposal_gate.py` |
| Simulator stress schedule | PASS | 0.180 | `python hqa_v2/integrations/simulator_stress_schedule_v0.py` |
| Simulator stress schedule gate | PASS | 0.082 | `python hqa_v2/quality/simulator_stress_schedule_gate.py` |
| Environment profile library | PASS | 0.078 | `python hqa_v2/integrations/environment_profile_library_v0.py` |
| Environment profile library gate | PASS | 0.060 | `python hqa_v2/quality/environment_profile_library_gate.py` |
| Cat cascade proxy | PASS | 0.074 | `python hqa_v2/integrations/cat_cascade_proxy.py` |
| Cat solver contract | PASS | 0.075 | `python hqa_v2/integrations/cat_solver_contract_v0.py` |
| Cat solver contract gate | PASS | 0.059 | `python hqa_v2/quality/cat_solver_contract_gate.py` |
| Schema contract smoke | PASS | 0.055 | `python hqa_v2/quality/schema_contract_smoke_test.py` |
| Vendor shadow packet | PASS | 0.137 | `python hqa_v2/package/build_vendor_shadow_packet.py` |
| Vendor shadow packet validation | PASS | 0.069 | `python hqa_v2/quality/vendor_shadow_packet_validation.py` |
| Stress harness | PASS | 0.073 | `python hqa_v2/demos/hqa_stress_harness.py` |
| Deterministic stress scenarios | PASS | 0.123 | `python hqa_v2/quality/hqa_v2_stress_scenarios.py` |
| Integrated loop | PASS | 0.689 | `python hqa_v2/demos/hqa_v2_integrated_control_loop.py` |
| Claim boundary smoke | PASS | 0.369 | `python hqa_v2/quality/claim_boundary_smoke_test.py` |

## Failure Details

No failures.

## Boundary

This regression suite validates proxy control-flow behavior only. It does not claim physical quantum validation, production QEC performance, or uncontrolled hardware execution.
