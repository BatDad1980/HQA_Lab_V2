# HQA Evidence Dashboard Gate

## Purpose

This gate verifies the read-only evidence dashboard is backed by local proof artifacts and keeps clean boundaries.

## Results

- Checks: `10`
- Passed: `10`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| manifest_schema | PASS | Manifest schema is V0. |
| read_only_mode | PASS | Mode: `read_only_static_dashboard`. |
| no_authority | PASS | Manifest grants no authority or access. |
| card_count | PASS | Cards: `5`. |
| provider_rows | PASS | Provider rows: `6`. |
| regression_visible | PASS | Full regression count is visible: `78/78`. |
| provider_replay_visible | PASS | Provider replay decisions are visible. |
| boundary_visible | PASS | Boundary banner is visible. |
| no_interactive_live_controls | PASS | No buttons, onclick handlers, fetch calls, or sockets. |
| forbidden_claims_absent | PASS | Forbidden hits: `-`; nonclaims ok: `True`. |

## Boundary

This gate validates a local static dashboard only. It does not validate live provider access, credentials, hardware control, physical quantum performance, or production QEC.
