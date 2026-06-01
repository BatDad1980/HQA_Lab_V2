# HQA Vendor Interface Contract

## Purpose

This document defines the first vendor-neutral interface contract for HQA V2.

The goal is to make HQA easy to evaluate beside IBM, Alice & Bob, Google, or another lab without granting HQA live hardware authority.

## Contract Files

| Schema | Purpose |
|---|---|
| `hqa_v2/schemas/topology_snapshot.schema.json` | Read-only map of nodes, health, roles, and coupling. |
| `hqa_v2/schemas/syndrome_record.schema.json` | Cycle-indexed syndrome observations from simulator or shadow hardware lanes. |
| `hqa_v2/schemas/quarantine_decision.schema.json` | HQA Sentinel decision to quarantine, hold, monitor, or propose release. |
| `hqa_v2/schemas/reroute_proposal.schema.json` | HQA route-around proposal with avoided targets and dry-run execution mode. |
| `hqa_v2/schemas/hal_manifest.schema.json` | Hardware-facing action manifest constrained to dry-run, shadow advisory, or blocked modes. |

## Evaluation Flow

1. Vendor provides a read-only topology snapshot.
2. Vendor or simulator provides syndrome records.
3. HQA produces a quarantine decision.
4. HQA produces a reroute proposal.
5. HQA produces a HAL manifest in dry-run or shadow-advisory mode.
6. Vendor-side controller decides whether anything physical happens.

## Hard Boundary

HQA V2 does not require, request, or assume live hardware authority.

The schema lane is designed for:

- local simulation
- digital twin replay
- shadow-mode advisory review
- technical due diligence

It is not designed for direct control of quantum hardware.

## Why This Matters

Without schemas, every demo becomes a story.

With schemas, HQA can be evaluated as a control-plane candidate:

- what it reads
- what it infers
- what it proposes
- what it refuses to do
- what remains under vendor/operator authority

That is the path from a lab prototype to a serious technical review.
