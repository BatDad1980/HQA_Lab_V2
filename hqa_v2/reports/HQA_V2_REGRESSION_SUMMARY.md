# HQA V2 Regression Summary

## Purpose

This report summarizes the safe HQA V2 proxy demo/regression set.

It verifies that the demos run from a clean repository root and that active text artifacts pass the claim-boundary smoke test.

## Results

- Commands run: `14`
- Passed: `14`
- Failed: `0`

| Check | Status | Seconds | Command |
|---|---:|---:|---|
| HAL safety | PASS | 0.084 | `python hqa_v2/demos/hqa_hal_safety_demo.py` |
| Topology routing | PASS | 0.087 | `python hqa_v2/demos/hqa_topology_routing_demo.py` |
| Live telemetry | PASS | 0.603 | `python hqa_v2/demos/hqa_live_control_loop_demo.py` |
| Predictive homeostasis | PASS | 0.586 | `python hqa_v2/demos/hqa_predictive_homeostasis_demo.py` |
| CR routing | PASS | 0.089 | `python hqa_v2/demos/hqa_cr_routing_demo.py` |
| Analog pulse shaping | PASS | 0.096 | `python hqa_v2/demos/hqa_analog_pulse_demo.py` |
| Cat-qubit proxy | PASS | 0.087 | `python hqa_v2/demos/alice_and_bob_cat_qubit_demo.py` |
| Simulator readiness | PASS | 0.062 | `python hqa_v2/integrations/simulator_readiness.py` |
| IBM runtime dry readiness | PASS | 0.070 | `python hqa_v2/integrations/ibm_runtime_readiness.py` |
| Simulator adapter smoke | PASS | 0.060 | `python hqa_v2/quality/simulator_adapter_smoke_test.py` |
| Stress harness | PASS | 0.061 | `python hqa_v2/demos/hqa_stress_harness.py` |
| Deterministic stress scenarios | PASS | 0.095 | `python hqa_v2/quality/hqa_v2_stress_scenarios.py` |
| Integrated loop | PASS | 0.671 | `python hqa_v2/demos/hqa_v2_integrated_control_loop.py` |
| Claim boundary smoke | PASS | 0.250 | `python hqa_v2/quality/claim_boundary_smoke_test.py` |

## Failure Details

No failures.

## Boundary

This regression suite validates proxy control-flow behavior only. It does not claim physical quantum validation, production QEC performance, or uncontrolled hardware execution.
