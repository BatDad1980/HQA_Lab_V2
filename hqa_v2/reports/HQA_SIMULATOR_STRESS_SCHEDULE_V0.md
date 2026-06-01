# HQA Simulator Stress Schedule V0

## Purpose

This report runs deterministic local stress profiles through the HQA risk-field and shadow-proposal chain.

The schedule is intended to show control-flow behavior across multiple conditions. It does not submit backend jobs or authorize hardware action.

## Results

| Scenario | Suspected Patch | Cascade Contrast | Top Risk | Band | Advisory Action | Proposal Mode |
|---|---|---:|---:|---|---|---|
| `nominal` | `Q_1` | `0.015625` | `0.224212` | `low` | `MONITOR_ONLY` | `shadow_advisory` |
| `mild_stress` | `Q_1` | `0.253906` | `0.550903` | `elevated` | `MONITOR_WITH_ROUTE_REVIEW` | `shadow_advisory` |
| `correlated_stress` | `Q_1` | `0.886718` | `0.954809` | `critical` | `ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL` | `shadow_advisory` |
| `no_route_hold` | `Q_1` | `0.941406` | `1.0` | `critical` | `NO_ROUTE_HOLD_REVIEW` | `blocked` |

## Boundary

Simulator Stress Schedule V0 is a deterministic local evidence schedule. It does not validate physical quantum hardware, production QEC performance, or live HAL execution.
