# HQA Codex Audit — 2026-06-20

## Verdict

HQA's authoritative active lineage is:

```text
X:\HQA_LAB_V1
branch: HQA_V2
baseline commit: 6bbdd481ea69132ad49e269af7e9f376cc4f8ccf
```

The repository is a bounded quantum-control proxy and shadow-advisory lab. It
does not establish physical quantum validation, production QEC performance,
live cryostat control, or quantum advantage.

## Repository provenance

- `X:\DARPA_QBI_IVV_HQA` contains two positioning documents only. It is not an
  HQA implementation repository.
- `X:\HQA_V1` is the older May 2026 lineage.
- `X:\HQA_LAB_V1` is the newer HQA V2 clean-room lineage and the sole active
  source authority for RTI preparation.

## Finding and repair

The clean-room status claimed 78/78 reproducible regression checks. A fresh
clone from the frozen commit produced 77/78 because the Backend Health
Translator depended on two ignored, machine-local JSON files under
`hqa_v2/logs/ibm_backend_snapshots`.

This was an evidence-custody defect rather than a model or quantum-control
failure: the committed gate could not reproduce its own accepted evidence
from repository contents alone.

Repair:

1. Added sanitized, immutable calibration replay fixtures under:

   ```text
   hqa_v2/fixtures/ibm_backend_snapshots
   ```

2. Bound the deterministic Backend Health Translator replay to those tracked
   fixtures instead of ignored local logs.
3. Added the previously referenced but absent `run_root_tests.py`, which
   executes the eight legacy root verification scenarios as isolated
   subprocesses and fails closed on missing scripts or nonzero exits.

The fixtures contain calibration metadata only. They contain no credentials,
tokens, account identifiers, or hardware authority.

## Independent validation

Validation was executed in:

```text
X:\scratch\HQA_CODEX_VALIDATION_20260620
```

Results:

| Check | Result |
|---|---:|
| Backend translator producer | 2 backends, 0 jobs |
| Backend translator gate | 12/12 PASS |
| HQA V2 regression runner | 78/78 PASS |
| Root verification runner | 8/8 PASS |
| Claim-boundary smoke test | PASS; 95 text files scanned |
| Python compilation | PASS |

The authoritative repository was not used as the generated-output workspace.

## Credential and archive warning

The older `X:\HQA_V1` repository contains a tracked credential-shaped
`apikey.json`. Its value was not displayed or used during this audit.

Treat the credential as exposed:

- rotate or revoke it;
- quarantine the older repository from RTI packaging;
- never copy its `apikey.json` into a data room;
- use `X:\HQA_LAB_V1` as the only HQA source authority.

## RTI disposition

HQA is technically ready for a refreshed, claim-bounded RTI evidence packet
after this repair is frozen. The June 4 Black Drive HQA packet remains a valid
dated archive, but it must not be represented as the current HQA release.
