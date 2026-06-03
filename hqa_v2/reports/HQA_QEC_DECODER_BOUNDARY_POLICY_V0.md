# HQA QEC Decoder Boundary Policy V0

## Purpose

This report formalizes the decoder rule that odd syndrome sets must resolve through a virtual boundary partner instead of crashing.

## Policy Rule

Odd active syndrome cardinality must map the unpaired syndrome to a virtual boundary partner.

## Results

| Case | Active Count | Cardinality | Status | Boundary Used | Dropped | Crashed |
|---|---:|---|---|---:|---:|---:|
| `QEC-EVEN-002` | `2` | `even` | `RESOLVED_DIRECTLY` | `False` | `0` | `False` |
| `QEC-ODD-003` | `3` | `odd` | `RESOLVED_WITH_BOUNDARY` | `True` | `0` | `False` |
| `QEC-ODD-001` | `1` | `odd` | `RESOLVED_WITH_BOUNDARY` | `True` | `0` | `False` |
| `QEC-CLEAR-000` | `0` | `even` | `RESOLVED_DIRECTLY` | `False` | `0` | `False` |

## Boundary

QEC Decoder Boundary Policy V0 is local decoder policy replay only. It does not validate production decoding, submit backend jobs, run circuits, change pulses, or authorize HAL execution.
