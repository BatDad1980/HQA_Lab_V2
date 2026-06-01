# HQA Topology Compensation Profiles Gate

## Purpose

This gate verifies that topology compensation supports multiple chip families while keeping HQA interpretation-only.

## Results

- Checks: `10`
- Passed: `10`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Profile schema is V0. |
| interpretation_only | PASS | Mode: `interpretation_only`. |
| no_hardware_authority | PASS | No compensation artifact grants hardware authority. |
| all_families_present | PASS | Families: `['bosonic_cat', 'grid_lattice', 'heavy_hex', 'neutral_graph']`. |
| families_have_bounds | PASS | All families have bounded coupling floors and positive degree baselines. |
| normalized_trace_has_compensation | PASS | Normalized trace includes compensation metadata. |
| heavy_hex_selected | PASS | Normalized family: `heavy_hex`. |
| compensation_has_observed_degree | PASS | Observed degree: `1.333333`. |
| risk_bias_present | PASS | Compensation risk-bias note exists. |
| normalization_rule_present | PASS | Normalization rule preserves HQA API. |

## Boundary

This gate validates topology-compensation metadata only. It does not validate physical quantum hardware, production QEC performance, live vendor access, or HAL execution.
