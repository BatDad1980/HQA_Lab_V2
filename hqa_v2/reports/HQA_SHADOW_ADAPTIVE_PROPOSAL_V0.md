# HQA Shadow Adaptive Proposal V0

## Purpose

This report translates HQA Risk Field V0 into reviewable shadow-mode control artifacts.

The output is intentionally non-executing. It proposes what a vendor/operator should review next; it does not modify hardware, backend topology, pulse schedules, or routing tables.

## Generated Artifacts

| Artifact | Purpose | Authority |
|---|---|---|
| `01_quarantine_decision.json` | Review whether the suspected patch should be quarantined or monitored. | `shadow_advisory` |
| `02_reroute_review.json` | Review route avoidance around the suspected patch. | `shadow_advisory` |
| `03_hal_dry_run_manifest.json` | Review the HAL-facing dry-run request boundary. | `dry_run` |
| `MANIFEST_SHA256.txt` | Tamper-evident hashes for the generated artifacts. | n/a |

## Summary

- Suspected patch: `Q_1`
- Quarantine decision: `quarantine`
- HAL requested action: `dry_run_review_route_review_and_quarantine_proposal`
- Manifest: `outputs\shadow_adaptive_proposal_v0\MANIFEST_SHA256.txt`

## Boundary

Shadow Adaptive Proposal V0 is a review packet only. It does not authorize live quantum hardware actions, live backend jobs, live pulse changes, or physical HAL execution.
