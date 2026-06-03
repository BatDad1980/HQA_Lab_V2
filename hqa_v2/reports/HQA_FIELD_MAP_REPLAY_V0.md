# HQA Field Map Replay V0

## Purpose

This report replays an IBM-style field map into bounded shadow quarantine and reroute review artifacts.

## Summary

- Source backend: `ibm_fixture_heavy_hex_patch`
- Source collection mode: `offline_fixture`
- Execution mode: `shadow_replay_only`
- Hardware authority: `False`
- Jobs submitted: `0`
- Intervention mode: `QUARANTINE_REMAP_SHADOW`
- Recommended targets: `Q_3, Q_1, Q_2`
- Avoided edge neighborhoods: `4`

## Top Candidates

| Rank | Qubit | Status | Reasons | Degraded Edges | Risk Score |
|---:|---|---|---|---:|---:|
| 1 | `Q_3` | `degraded` | `high_readout_error` | `2` | `0.51` |
| 2 | `Q_1` | `degraded` | `weak_t1` | `2` | `0.48` |
| 3 | `Q_2` | `degraded` | `weak_t2` | `2` | `0.48` |
| 4 | `Q_0` | `healthy` | `-` | `1` | `0.08` |
| 5 | `Q_4` | `healthy` | `-` | `1` | `0.08` |

## Artifacts

- `01_quarantine_candidates.json`
- `02_reroute_review.json`
- `03_intervention_hint.json`
- `MANIFEST_SHA256.txt`

## Boundary

Field Map Replay V0 produces review artifacts only. It submits zero jobs, runs zero circuits, changes no routing table or pulses, and grants no HAL authority.
