# HQA Qiskit Aer Cascade Noise Probe

## Purpose

This report demonstrates a local Aer simulator probe that preserves full syndrome-history bitstrings under a custom noise model.

The probe is intended to test cascade-observation plumbing, not physical quantum hardware behavior.

## Configuration

| Profile | Shots | Seed Injected | Measurement Flip | Single X Proxy | Correlated CX XX Proxy |
|---|---:|---:|---:|---:|---:|
| `nominal` | 512 | `False` | `0.003` | `0.0005` | `0.002` |
| `stress` | 512 | `True` | `0.015` | `0.002` | `0.025` |

## Results

| Profile | Local Aer | Unique Histories | Cascade-Like Shots | Cascade-Like Rate | Dominant History | HQA Action |
|---|---:|---:|---:|---:|---:|---|
| `nominal` | `True` | 16 | 14 | `0.027344` | `00000000` | MONITOR_ONLY |
| `stress` | `True` | 55 | 468 | `0.914062` | `11111111` | SENTINEL_REVIEW_RECOMMENDED |

## Top Syndrome Histories

| Rank | Profile | History | Count | Weight | Flagged Cycles | HQA Decoder Signal |
|---:|---|---:|---:|---:|---:|---|
| 1 | `nominal` | `00000000` | 474 | 0 | 0 | LOW_ACTIVITY_HISTORY |
| 2 | `nominal` | `01000000` | 7 | 1 | 1 | LOW_ACTIVITY_HISTORY |
| 3 | `nominal` | `10101000` | 5 | 3 | 3 | CASCADE_LIKE_HISTORY |
| 4 | `nominal` | `00000010` | 3 | 1 | 1 | LOW_ACTIVITY_HISTORY |
| 5 | `nominal` | `01010000` | 3 | 2 | 2 | WATCHLIST_HISTORY |
| 6 | `nominal` | `11111111` | 3 | 8 | 4 | CASCADE_LIKE_HISTORY |
| 7 | `nominal` | `00001000` | 2 | 1 | 1 | LOW_ACTIVITY_HISTORY |
| 8 | `nominal` | `00010000` | 2 | 1 | 1 | LOW_ACTIVITY_HISTORY |
| 9 | `nominal` | `00100000` | 2 | 1 | 1 | LOW_ACTIVITY_HISTORY |
| 10 | `nominal` | `10000000` | 2 | 1 | 1 | LOW_ACTIVITY_HISTORY |
| 11 | `nominal` | `11100000` | 2 | 3 | 2 | WATCHLIST_HISTORY |
| 12 | `nominal` | `11111000` | 2 | 5 | 3 | CASCADE_LIKE_HISTORY |
| 13 | `nominal` | `11111100` | 2 | 6 | 3 | CASCADE_LIKE_HISTORY |
| 14 | `nominal` | `01010100` | 1 | 3 | 3 | CASCADE_LIKE_HISTORY |
| 15 | `nominal` | `11000000` | 1 | 2 | 1 | LOW_ACTIVITY_HISTORY |
| 16 | `nominal` | `11111110` | 1 | 7 | 4 | CASCADE_LIKE_HISTORY |
| 17 | `stress` | `11111111` | 292 | 8 | 4 | CASCADE_LIKE_HISTORY |
| 18 | `stress` | `01111111` | 15 | 7 | 4 | CASCADE_LIKE_HISTORY |
| 19 | `stress` | `10111111` | 15 | 7 | 4 | CASCADE_LIKE_HISTORY |
| 20 | `stress` | `10101011` | 12 | 5 | 4 | CASCADE_LIKE_HISTORY |

## Interpretation

The nominal profile checks the quiet baseline. The stress profile injects a seed and correlated noise so the HQA cascade observer can verify that syndrome history, not only final-state counts, drives the decision.

## Boundary

This is a local simulator probe. It does not submit IBM jobs, validate physical quantum hardware, prove production QEC performance, or grant HQA hardware control authority.
