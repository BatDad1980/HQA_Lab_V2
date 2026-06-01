# HQA Qiskit Aer Cascade Gate

## Purpose

This gate verifies that the local Aer cascade probe separates a quiet nominal profile from an intentionally stressed profile.

## Results

- Checks: `7`
- Passed: `7`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| nominal_profile_present | PASS | Nominal profile summary exists. |
| stress_profile_present | PASS | Stress profile summary exists. |
| nominal_aer_ran | PASS | Nominal profile ran local Aer. |
| stress_aer_ran | PASS | Stress profile ran local Aer. |
| nominal_stays_quiet | PASS | Nominal cascade-like rate `0.027344` <= `0.10`. |
| stress_lights_up | PASS | Stress cascade-like rate `0.914062` >= `0.50`. |
| profile_separation | PASS | Stress minus nominal separation `0.886718` >= `0.40`. |

## Boundary

This gate evaluates local simulator-observation behavior only. It does not validate physical quantum hardware, production QEC performance, or live backend behavior.
