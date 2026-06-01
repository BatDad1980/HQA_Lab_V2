# HQA Vendor Shadow Packet V1

## Purpose

This packet demonstrates the HQA V2 shadow-mode data handoff shape.

It is not a live hardware integration package. It contains only example JSON payloads and hashes.

## Flow

1. Read-only topology snapshot.
2. Syndrome record from a simulator or shadow telemetry lane.
3. HQA quarantine decision.
4. HQA reroute proposal.
5. HAL dry-run manifest requiring human/vendor approval.

## Files

- `01_topology_snapshot.json`
- `02_syndrome_record.json`
- `03_quarantine_decision.json`
- `04_reroute_proposal.json`
- `05_hal_manifest.json`
- `MANIFEST_SHA256.txt`

## Boundary

This packet grants no live hardware authority and submits no backend jobs.
