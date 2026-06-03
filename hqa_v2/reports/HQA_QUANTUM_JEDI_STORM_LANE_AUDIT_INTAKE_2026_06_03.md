# HQA Quantum Jedi Storm-Lane Audit Intake

Date: 2026-06-03

## Purpose

This note records a read-only audit pass over the separate `Z:\Homeostatic_Quantum_Architecture\Quantum_Jedi` storm-lab lane.

The storm lane is intentionally exploratory. This clean-lane intake does not import its claims as proof. It identifies what should be fixed in the storm lane, what should be harvested into `X:\HQA_LAB_V1`, and what should remain private or experimental.

## Local Test Health

The storm-lane local pytest run completed with:

| Result | Count |
|---|---:|
| Passed | 76 |
| Failed | 1 |
| Warnings | 16 |

The single failure was in `tests/test_vagus_autonomic.py::TestVagusAutonomic::test_bacl_signed_manifest_cooling`.

Observed behavior:

- the BACL-signed stress response successfully activated pump `Q10`
- the newly added stabilization logic immediately deactivated the same pump because simulated temperature was already `10.00mK`
- the old test expected the pump to remain active

Interpretation: the new feedback behavior and the old test are out of sync. This is not a fatal architecture failure. It is a behavior-contract issue around same-cycle activation/deactivation.

## High-Priority Findings

| Finding | Risk | Recommended Treatment |
|---|---|---|
| Missing BACL keys fall back to raw unverified pump activation. | A cryptographic safety layer should fail closed, not bypass itself. | Change missing-key behavior to `SAFE_HOLD`, simulation-only refusal, or operator-review lock. |
| Mock cryostat loopback uses `physical` mode language. | External reviewers may confuse mock TCP loopback with real cryostat control. | Rename external-facing language to `mock_loopback_hal` or `loopback_transport_evidence`. |
| IBM validation language says physical/QPU validation while the comparison primarily uses local noisy simulation from real calibration/topology. | Overstates the evidence if no `--real-qpu` job ID exists. | Use: "real IBM calibration/topology telemetry + local noisy simulator." |
| Hardcoded local IBM key path exists in the provider helper. | Not leaked, but poor packaging hygiene and too machine-specific. | Prefer environment variables and keep local key-file access private to the storm lane. |
| Legacy scale language claims perfect 1-billion-qubit scaling. | Buyer/lab reviewers may treat this as an unsupported production-performance claim. | Keep private or rewrite as stress-test observation with exact assumptions and limits. |

## Strong Signals To Preserve

- BACL one-time signature reuse protection is present.
- The BACL entropy red-team result is useful: public telemetry must never regenerate signing authority.
- IBM Fez vs Kingston behavior produced an important intervention lesson: degraded fields may benefit from quarantine routing, healthier fields may require abstention.
- Mock cryostat TCP ACK testing proves transport serialization and internal state update mechanics.
- Cerebras advisory has telemetry compression and deterministic safety fallback instead of pure model trust.
- QEC decoder boundary handling is a useful formal harvest target.

## Clean-Lane Harvest Candidates

| Candidate | Clean-Lane Destination |
|---|---|
| Same-cycle pump activation/deactivation conflict | HAL loopback and autonomic regulation boundary contract. |
| Missing-key fail-closed rule | BACL entropy and HAL authority policy. |
| Mock cryostat telemetry queries | Mock HAL telemetry contract, explicitly no live actuation. |
| IBM validation wording correction | Provider replay, backend health translator, and reviewer brief language. |
| Cerebras telemetry compression | Cognitive advisory contract and telemetry compression gate. |
| QEC boundary partner handling | QEC decoder boundary policy. |

## Keep In Storm Lane

- raw local dashboard controls
- active WebSocket telemetry experiments
- direct local API-key file handling
- unsterilized IBM/Cerebras reports
- legacy 1-billion-qubit stress language
- anything called physical control unless it is explicitly mock/shadow/dry-run

## Recommended Next Fix Order

1. Update Vagus/autonomic logic so a pump activated due to stress is not deactivated in the same regulation tick solely because the pre-action temperature is at the stabilization floor.
2. Remove raw unverified pump fallback when BACL credentials are missing.
3. Rename loopback-facing artifacts from physical language to mock-loopback language.
4. Correct IBM report wording to distinguish real telemetry from local noisy simulation.
5. Add a local storm-lane claim-boundary smoke test before any external packet generation.

## Boundary

This audit intake is not a buyer packet and not a certification. It is an internal clean-lane triage note for turning storm-lab discoveries into bounded, replayable evidence.

