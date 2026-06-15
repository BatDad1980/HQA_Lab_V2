# HQA Clean-Room Custody Plan

Date: 2026-06-04

## Purpose

This document records the clean-room custody plan for HQA after development responsibility moved fully into the clean lane.

Clean lane:

`X:\HQA_LAB_V1`

Storm / source lane:

`Z:\Homeostatic_Quantum_Architecture\Quantum_Jedi`

Buyer staging lane:

`D:\Aural_Nexus_Buyer_Staging_CURRENT`

## Current Position

HQA is no longer just a concept folder. It has:

- a structured HQA V2 clean implementation,
- claim boundary documents,
- known limitation documents,
- IBM calibration-readiness reports,
- topology routing reports,
- HAL safety reports,
- cat-qubit proxy reports,
- simulator adapter smoke reports,
- evidence dashboard outputs,
- regression summary outputs,
- a vendor shadow packet.

The clean-room job is not to make larger claims.

The clean-room job is to make the existing work harder to dismiss.

## Source Lane Treatment

The Quantum_Jedi folder may contain useful implementation ideas, reports, stress harnesses, and proof artifacts.

It should not be treated as buyer-facing by default.

Source-lane material should be classified as:

- `HARVEST`: useful and clean enough to port into X.
- `REFRAME`: technically useful but needs claim boundary and wording cleanup.
- `QUARANTINE`: useful internally but unsuitable for buyer-facing review.
- `IGNORE`: duplicate, noisy, outdated, or irrelevant.

## Immediate Findings From Quantum_Jedi Intake

Strong harvest candidates:

- 87 passing local tests.
- Intervention gate logic.
- Cognitive advisory hardening.
- Cryostat telemetry and feedback regulation.
- BACL entropy red-team and hardened key derivation proof.
- QEC MWPM boundary handling.
- Telemetry server and dashboard ideas.
- Hardware validation report structure.
- Safety and claim boundary documents.

Risk areas requiring cleanup before import:

- hardcoded credential assumptions,
- root-level zip/cache artifacts,
- duplicate package layout,
- overly hot wording around massive-scale simulations,
- inconsistent hardware report metadata,
- live/hardware phrasing that may sound like direct physical control,
- LLM-in-the-middle wording that may imply authority instead of advisory status.

## Credential Hygiene

Quantum_Jedi no longer has an `apikey.json` file present, and the file is ignored by Git.

The clean rule is:

- credentials must come from environment variables or an explicit external file path,
- credentials must not be stored inside repos,
- credential paths must not be hardcoded to local project folders.

Preferred environment variables:

- `IBM_QUANTUM_TOKEN`
- `IBM_QUANTUM_INSTANCE_CRN`

Optional external-file override:

- `IBM_QUANTUM_KEY_FILE`

## Claim Boundary

HQA may claim:

- local control-plane routing and quarantine logic,
- simulation-based local edge quenching behavior,
- replayable IBM calibration telemetry intake,
- topology-aware routing compensation,
- HAL command boundary enforcement,
- cat-qubit proxy modeling,
- cryptographic authorization constraints,
- abstention and intervention-gate behavior.

HQA must not claim:

- production QEC deployment,
- universal decoder replacement,
- direct vendor cryostat ownership,
- quantum supremacy,
- physical cat-qubit state validation,
- guaranteed performance,
- solved quantum error correction,
- real hardware actuation outside approved lab interfaces.

## LLM Advisory Boundary

Any LLM advisory layer must be treated as non-authoritative.

Allowed:

- summarize telemetry,
- produce advisory recommendations,
- help rank attention targets,
- compress high-dimensional state into human-readable notes.

Not allowed:

- authorize HAL commands,
- override intervention gates,
- override BACL,
- override Boundary Gateway,
- certify a physical action,
- substitute for deterministic control logic.

Clean phrase:

> The advisory model may inform operator review, but deterministic safety gates authorize or block all control-plane actions.

## HQA Buyer-Ready Definition

HQA is buyer-ready when the following are true:

1. Clean lane tests pass.
2. Claim boundary scan passes.
3. No credentials or secret paths exist in artifacts.
4. Reports have consistent backend metadata.
5. Massive-scale benchmarks are described as algorithmic simulation bounds.
6. HAL reports are explicitly simulation / loopback / vendor-interface scaffolding unless live vendor approval exists.
7. HQA and HPP are not merged in buyer materials.
8. HQA and HPPW are not merged in buyer materials.
9. Vendor-facing packet contains only docs, reports, schemas, manifests, and safe demo outputs.
10. Source code is shared only under MNDA or technical review scope.

## Next Clean-Room Work Orders

1. Reconcile X clean-lane reports against the latest Quantum_Jedi evidence.
2. Harvest only deterministic gate logic and reports that improve buyer credibility.
3. Create a `HQA_JEDI_HARVEST_MAP.md` with per-file disposition.
4. Refresh HQA claim-boundary scan after harvest.
5. Run the clean-lane regression runner.
6. Build a fresh HQA buyer-stage packet on D.
7. Keep HQA separate from HPP and HPPW unless explicitly building a portfolio overview.

## Custody Rule

Storm-lane work may be brilliant.

Buyer-lane work must be boring, bounded, verified, and impossible to misread.

