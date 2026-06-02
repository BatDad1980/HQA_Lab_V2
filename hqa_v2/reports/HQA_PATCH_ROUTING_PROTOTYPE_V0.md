# HQA Patch Routing Prototype V0

## Purpose

This report tests a patch-level routing prototype for fabrics where global node-level A* approaches the feedback budget.

The prototype routes across coarse regions first and preserves safe-hold behavior when a patch wall blocks the fabric.

## Results

| Scenario | Grid Nodes | Patch Nodes | Workload Reduction | Global Latency Est. | Patch Latency Est. | Decision |
|---|---:|---:|---:|---:|---:|---|
| `PR-001` 150x150 rupture-threshold grid | `22500` | `100` | `244.565` | `205.0` | `1.747` | `PATCH_ROUTE_AVAILABLE` |
| `PR-002` 300x300 large fabric | `90000` | `400` | `230.769` | `820.0` | `5.419` | `PATCH_ROUTE_AVAILABLE` |
| `PR-003` 600x600 coarse fabric | `360000` | `900` | `405.862` | `3280.0` | `11.844` | `PATCH_ROUTE_AVAILABLE` |
| `PR-004` Patch wall no-route hold | `90000` | `400` | `450.0` | `820.0` | `1.822` | `SAFE_HOLD` |

## Boundary

Patch routing is a shadow planning prototype only. It does not validate physical quantum hardware, alter topology, change pulses, or dispatch HAL actions.
