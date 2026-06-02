# HQA Telemetry Compression Gate V0

## Purpose

This report verifies that large telemetry payloads can be compressed into bounded risk features before cognitive advisory review.

The gate checks that compression reduces payload size, preserves the intervention decision, and keeps estimated advisory latency within the feedback budget.

## Results

| Scenario | Raw Bytes | Compressed Bytes | Ratio | Raw Decision | Compressed Decision | Preserved | Estimated Latency | Under Budget |
|---|---:|---:|---:|---|---|---:|---:|---:|
| `TCG-001` Stable small packet | `10038` | `504` | `19.917` | `ACCEPT_ANNOTATION` | `ACCEPT_ANNOTATION` | `True` | `61.506` | `True` |
| `TCG-002` Moderate device drift | `39887` | `506` | `78.828` | `MONITOR_WITH_ROUTE_REVIEW` | `MONITOR_WITH_ROUTE_REVIEW` | `True` | `63.171` | `True` |
| `TCG-003` Cognitive overload monster payload | `154990` | `493` | `314.381` | `QUARANTINE_REMAP_REVIEW` | `QUARANTINE_REMAP_REVIEW` | `True` | `63.76` | `True` |
| `TCG-004` Collapse payload | `154990` | `498` | `311.225` | `SAFE_HOLD` | `SAFE_HOLD` | `True` | `64.081` | `True` |

## Boundary

Telemetry compression summarizes evidence for advisory review only. It does not authorize live hardware control, backend jobs, pulse changes, or HAL dispatch.
