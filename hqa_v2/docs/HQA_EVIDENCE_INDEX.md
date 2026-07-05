# HQA Evidence Index — Start Here

**Audience:** an external technical reviewer under NDA.
**Purpose:** a single map from each HQA proof artifact to *what it demonstrates* and
*what it explicitly does not claim*, so the package can be diligenced quickly and
challenged fairly.

---

## What HQA is (one paragraph)

HQA is a provider-neutral, hardware-aware control, telemetry, and validation layer
that sits between raw quantum-hardware condition data and hardware-facing decisions.
It normalizes backend health across architectures, maps degraded topology, proposes
bounded routing/quarantine interventions, and preserves replayable evidence — all
under fail-closed authority controls. It is an advisory proxy. It does not perform
quantum error correction, does not control hardware, and submits no live jobs.

## The claim boundary (read before any artifact)

HQA evidence does **not** establish: production quantum error correction; quantum
advantage; physical quantum-hardware validation; improved physical fidelity on a
live device; vendor-certified integration; or autonomous hardware control. Every
result below is a simulation, a calibration-derived analysis, or an architectural
demonstration, with its own stated boundary.

---

## The proofs

| # | Artifact | Demonstrates | Does NOT claim |
|---|---|---|---|
| 1 | **Multi-backend adaptation** — `integrations/multi_backend_adaptation_demo_v0.py` → `reports/HQA_MULTI_BACKEND_ADAPTATION_V0.md` | One pipeline ingests 6 *different real* IBM device snapshots and produces materially different per-chip quarantine + routing decisions. Zero jobs, zero cost. | Fidelity gain, live control, that the route is optimal |
| 2 | **Cat-qubit setpoint homeostasis** — `integrations/cat_setpoint_homeostasis_sweep_v0.py` → `reports/HQA_CAT_SETPOINT_HOMEOSTASIS_V0.md` | dynamiqs Lindblad solve confirms phase-flip rate is linear in n̄ (slope 0.097 vs 0.10, R²≈0.98); adaptive setpoint tracking reduces logical error only when noise asymmetry drifts (and correctly nothing when it doesn't). | A fixed fidelity gain; any physical-device result |
| 3 | **Cat biased-noise routing** — `integrations/cat_biased_noise_router_v0.py` → `reports/HQA_CAT_BIASED_NOISE_ROUTER_V0.md` | Routing that weights phase-flip proximity heavily and bit-flip proximity residually — correct for a cat fabric where bit flips are suppressed. | Live cat-qubit calibration; a QEC result |
| 4 | **Provider normalization matrix** — `integrations/provider_normalization_matrix_v0.py` → `reports/HQA_PROVIDER_NORMALIZATION_MATRIX_V0.md` | One shadow-adapter grammar accepts several provider dialects (IBM, Braket, Azure, cuda-q, Cirq, cat solver). | Provider performance; live cloud access (uses representative fixtures) |
| 5 | **Fail-closed safety** — `safety/hal_safety_governor.py`; `demos/alice_and_bob_cat_qubit_demo.py` → `reports/ALICE_AND_BOB_INTEGRATION_REPORT.md` | Under a malformed manifest or an unroutable fabric, HQA holds/abstains rather than acting or proposing an unsafe route. | Any hardware-authority or successful-routing claim in the degraded case |
| 6 | **Compatibility note** — `docs/HQA_CAT_QUBIT_COMPATIBILITY_NOTE_V0.md` | Calm, claim-bounded description of how HQA accommodates cat-qubit biased noise, aligned with Alice & Bob's *Defining the Logical Qubit* discipline. | A logical-qubit or fidelity claim |
| 7 | **Reproducibility & discipline** — `quality/hqa_v2_regression_runner.py`, `quality/claim_boundary_smoke_test.py` | 78/78 regression checks; claim-boundary scan over 115 text files; IBM readiness with zero jobs submitted. | — |

## How to reproduce

```bash
cd hqa_v2
python integrations/multi_backend_adaptation_demo_v0.py     # proof 1 (needs qiskit-ibm-runtime fake_provider)
python integrations/cat_setpoint_homeostasis_sweep_v0.py    # proof 2 (needs dynamiqs)
python integrations/cat_biased_noise_router_v0.py           # proof 3
python integrations/provider_normalization_matrix_v0.py     # proof 4
python demos/alice_and_bob_cat_qubit_demo.py                # proof 5
python quality/hqa_v2_regression_runner.py                  # proof 7: expect 78/78
python quality/claim_boundary_smoke_test.py                 # proof 7: expect PASS
```

## What is retired, and why (honesty ledger)

Earlier drafts carried a `+2.68%` cat-qubit fidelity headline and a
total-cascade-prevention billion-qubit headline (phrases we no longer use). Neither
was reproducible: the only real cat run was a null, and the billion-qubit comparison
used a non-quarantining strawman baseline. Both have been retired and reframed honestly (see
`HQA_CAT_SETPOINT_HOMEOSTASIS_V0.md` and `HQA_MASSIVE_SCALE_RESULTS.md`). This ledger
is kept deliberately: the discipline that removed those claims is itself part of the
evidence.

## Boundary

Advisory research architecture for technical screening. No hardware authority, no
live backend access, no pulse or cryostat control, no quantum-advantage or
error-correction claim.
