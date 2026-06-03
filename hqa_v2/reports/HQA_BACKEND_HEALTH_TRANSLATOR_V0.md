# HQA Backend Health Translator V0

## Purpose

This report verifies the translation layer that lets HQA read different backend conditions through one normalized health grammar.

The rule is simple: HQA adapts to the measured playing field, not the provider or backend name.

## Summary

- Execution mode: `shadow_translation_only`
- Backends translated: `2`
- Hardware authority: `False`
- Jobs submitted: `0`

| Backend | Health Score | Degraded Fraction | Pressure Class | Intervention Hint |
|---|---:|---:|---|---|
| `ibm_fez` | `0.6119` | `0.391026` | `HIGH_DEGRADATION` | `QUARANTINE_REMAP_SHADOW` |
| `ibm_kingston` | `0.748151` | `0.211538` | `MODERATE_DEGRADATION` | `MONITOR_WITH_SHADOW_OPTIMIZATION` |

## Comparison

- Healthiest backend by normalized score: `ibm_kingston`
- Roughest backend by normalized score: `ibm_fez`
- Health score delta: `0.136251`
- Degraded fraction delta: `0.179488`
- Translation rule: Select behavior from normalized health profile, not backend name.

## Current Limitation

The current IBM calibration snapshots preserve summary metrics. Spatial defect clustering requires a richer future snapshot that stores per-qubit classes and coupling-map adjacency.

## Boundary

Backend health translation normalizes local calibration evidence only. It does not submit jobs, run circuits, alter routing tables, change pulses, or authorize HAL execution.
