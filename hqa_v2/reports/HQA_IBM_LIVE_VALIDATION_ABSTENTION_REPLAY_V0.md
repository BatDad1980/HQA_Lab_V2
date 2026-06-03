# HQA IBM Live Validation Abstention Replay V0

## Purpose

This replay captures the policy lesson from reported IBM live-validation outcomes: HQA is not an always-remap system. It is a condition-aware intervention layer.

The fixtures below came from an adjacent HQA lane and are treated as replay inputs, not clean-lane proof until independently reproduced here.

## Summary

- Execution mode: `reported_fixture_policy_replay`
- Source class: `adjacent_lane_reported_live_validation`
- Clean-lane jobs submitted: `0`
- Hardware authority: `False`

| Backend | Defect Density | Default Qiskit | HQA Quarantine | Delta | Policy Decision |
|---|---:|---:|---:|---:|---|
| `ibm_fez` | `0.352564` | `0.9404` | `0.9648` | `+0.024400` | `INTERVENE_WITH_QUARANTINE_REMAP_SHADOW` |
| `ibm_kingston` | `0.211538` | `0.9824` | `0.9648` | `-0.017600` | `ABSTAIN_AND_MONITOR` |

## Lessons

- `ibm_fez`: Degraded field improved when HQA steered around defect pressure.
- `ibm_kingston`: Forced remap under healthier conditions underperformed default routing; stand down and shadow-optimize.

## Core Rule

HQA should intervene only when measured field conditions justify it; otherwise it should abstain, monitor, or shadow-optimize.

## Boundary

This replay formalizes a policy lesson from reported adjacent-lane results. It does not submit IBM jobs, run circuits, reserve hardware, alter pulses, or claim production quantum performance.
