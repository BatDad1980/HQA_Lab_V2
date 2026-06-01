# HQA Dual Vendor Test Matrix Gate

## Purpose

This gate verifies that HQA's dual vendor test matrix covers cat and non-cat lanes without granting authority or collapsing claims.

## Results

- Checks: `10`
- Passed: `10`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Matrix schema is V0. |
| planning_only | PASS | Mode: `planning_and_readiness_only`. |
| no_hardware_authority | PASS | Matrix grants no hardware authority. |
| all_lanes_present | PASS | Lanes: `['CAT-ALICE-BOB', 'GOOGLE-GRID', 'IBM-HEAVY-HEX', 'NEUTRAL-VENDOR-GRAPH']`. |
| all_topologies_present | PASS | Topologies: `['bosonic_cat', 'grid_lattice', 'heavy_hex', 'neutral_graph']`. |
| cat_lane_separated | PASS | Cat lane is separate. |
| ibm_lane_heavy_hex | PASS | IBM lane uses heavy_hex. |
| google_lane_grid | PASS | Google lane uses grid_lattice. |
| boundaries_avoid_overclaim | PASS | Lane boundaries preserve claim discipline. |
| all_lanes_have_next_evidence | PASS | Every lane lists required next evidence. |

## Boundary

This gate validates test-matrix readiness only. It does not validate physical quantum hardware, production QEC performance, live vendor access, or HAL execution.
