# HQA Lab V1

## Purpose

HQA Lab V1 is the clean laboratory lane for the Homeostatic Quantum Architecture work.

The active branch is `HQA_V2`.

This repository focuses on claim-bounded quantum-control proxy research:

- local sentinel-style fault response
- topology-aware quarantine and reroute proposals
- simulator-facing cascade observation
- cat-qubit solver contracts
- vendor-neutral shadow-mode schemas
- dry-run HAL boundaries
- replayable reports and smoke tests

## Start Here

For a technical review, begin with:

- `hqa_v2/docs/HQA_REVIEWER_BRIEF.md`
- `hqa_v2/docs/HQA_TECHNICAL_INDEX.md`
- `hqa_v2/reports/HQA_V2_REGRESSION_SUMMARY.md`

## Verify

From the repository root:

```powershell
python hqa_v2/quality/hqa_v2_regression_runner.py
python hqa_v2/quality/claim_boundary_smoke_test.py
```

Current expected state:

- HQA V2 regression passes.
- Claim-boundary smoke passes.
- No live hardware authority is granted.

## Boundary

HQA Lab V1 does not claim physical quantum hardware validation, production QEC performance, live cryostat control, or quantum advantage.

It is a controlled proxy and shadow-advisory lab designed to make future technical review easier, safer, and more reproducible.
