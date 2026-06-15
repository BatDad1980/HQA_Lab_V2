# HQA Evidence Dashboard V0

## Purpose

This report documents the generated read-only evidence dashboard.

The dashboard is backed by local HQA reports and JSON logs. It does not simulate live controls, read credentials, contact providers, or authorize hardware.

## Cards

| Card | Status | Metric | Artifact |
|---|---:|---:|---|
| Regression Spine | PASS | `78/78` | `hqa_v2/reports/HQA_V2_REGRESSION_SUMMARY.md` |
| Provider Normalization | PASS | `12/12` | `hqa_v2/reports/HQA_PROVIDER_NORMALIZATION_MATRIX_GATE.md` |
| Provider Replay | PASS | `14/14` | `hqa_v2/reports/HQA_PROVIDER_REPLAY_HARNESS_GATE.md` |
| Patch Routing | PASS | `11/11` | `hqa_v2/reports/HQA_PATCH_ROUTING_PROTOTYPE_QUALITY.md` |
| Telemetry Compression | PASS | `11/11` | `hqa_v2/reports/HQA_TELEMETRY_COMPRESSION_GATE_QUALITY.md` |

## Provider Rows

- Rows: `6`

## Output

- Dashboard: `outputs\evidence_dashboard_v0\HQA_EVIDENCE_DASHBOARD_V0.html`
- Manifest: `outputs\evidence_dashboard_v0\dashboard_manifest.json`

## Boundary

This dashboard is a local, read-only evidence surface. It does not claim physical quantum validation, production QEC performance, live provider access, or hardware control.
