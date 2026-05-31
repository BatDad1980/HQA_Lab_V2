# HQA V2 Stress Scenario Report

## Purpose

This report runs deterministic proxy stress scenarios against the HQA V2 control stack.

The goal is to test bounded behavior under faults, degraded nodes, no-route conditions, CUDA unavailability, and HAL policy blocks.

## Summary

- Scenarios: `5`
- Passed: `5`
- Failed: `0`

| Scenario | Status | Expected | Observed |
|---|---:|---|---|
| single_fault_reroute | PASS | Route exists and avoids quarantined Q_2_2. | `path=['Q_0_0', 'Q_1_1', 'Q_0_2', 'Q_1_3', 'Q_2_4', 'Q_3_3', 'Q_4_4']` |
| degraded_node_avoidance | PASS | Route exists and prefers stable alternate path over degraded Q_2_2. | `path=['Q_0_0', 'Q_1_1', 'Q_0_2', 'Q_1_3', 'Q_2_4', 'Q_3_3', 'Q_4_4']` |
| no_route_safe_hold | PASS | No route exists after isolating the only first-hop node; no downstream hardware path should be generated. | `isolated=['Q_1_1']; path=None` |
| cuda_unavailable_fallback | PASS | CUDA edge interface reports fallback while HAL remains dry-run bounded. | `cuda_success=False; hal_success=True; path=['Q_0_0', 'Q_1_1', 'Q_0_2', 'Q_1_3', 'Q_2_4', 'Q_3_3', 'Q_4_4']` |
| hal_forbidden_action_block | PASS | Forbidden HAL command is blocked by governor. | `hal_success=False; path=['Q_0_0', 'Q_1_1', 'Q_0_2', 'Q_1_3', 'Q_2_4', 'Q_3_3', 'Q_4_4']` |

## Boundary

These are proxy control-plane scenarios. They do not validate physical quantum hardware, production QEC performance, or uncontrolled hardware execution.

JSON result file: `stress_scenarios_results.json`
