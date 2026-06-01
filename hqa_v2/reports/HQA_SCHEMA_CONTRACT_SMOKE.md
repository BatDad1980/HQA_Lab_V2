# HQA Schema Contract Smoke Test

## Purpose

This smoke test verifies that HQA V2 vendor-interface schemas are present, parseable, and strict enough for shadow-mode integration review.

## Results

- Schemas checked: `5`
- Passed: `5`
- Failed: `0`

| Schema | Status | Detail |
|---|---:|---|
| `topology_snapshot.schema.json` | PASS | HQA Topology Snapshot |
| `syndrome_record.schema.json` | PASS | HQA Syndrome Record |
| `quarantine_decision.schema.json` | PASS | HQA Quarantine Decision |
| `reroute_proposal.schema.json` | PASS | HQA Reroute Proposal |
| `hal_manifest.schema.json` | PASS | HQA HAL Manifest |

## Boundary

These schemas define dry-run and shadow-advisory data contracts. They do not grant HQA physical hardware authority.
