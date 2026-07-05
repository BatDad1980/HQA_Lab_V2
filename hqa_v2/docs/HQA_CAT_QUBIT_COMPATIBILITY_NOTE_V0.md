# HQA Compatibility Note for Cat-Qubit-Oriented Quantum Architectures

**Prepared by:** Brent Sholes, Aural Nexus AI
**Disclosure level:** Non-confidential
**Technical status:** Audited research prototype
**Scope:** A calm technical description of how the Homeostatic Quantum
Architecture (HQA) control/telemetry layer accommodates the biased-noise profile
characteristic of cat-qubit hardware. This note makes no error-correction,
fidelity, or logical-qubit claim.

---

## 1. Purpose

HQA is a provider-neutral, hardware-aware control, telemetry, and validation
layer that sits between raw quantum-hardware condition data and hardware-facing
decisions. It normalizes backend health across architectures, maps degraded
topology, and produces bounded, reviewable routing and intervention
recommendations under fail-closed authority controls.

This note addresses one focused question: **does HQA's architecture already
account for the asymmetric (biased) noise physics of cat qubits, and if so, how?**
It is written for a first technical conversation, not as a benchmark or a
product claim. Cat qubits are the hardware; HQA is a software layer that aims to
reason about that hardware honestly.

## 2. HQA already speaks biased noise

Cat qubits do not have symmetric error rates. The mean photon number `n_bar` of
the stabilized oscillator sets a trade-off that HQA's cat lane encodes directly:

| Error | Model used in HQA | Behavior |
|---|---|---|
| Bit-flip (X) | `exp(-2 * n_bar)` | Exponentially suppressed as photon number grows |
| Phase-flip (Z) | `~ n_bar` | Grows linearly as protection increases |

Standard surface-code routers assume symmetric X/Z rates. For a cat fabric that
assumption is wrong: routing that spends its path budget avoiding bit-flip
regions is protecting against a threat the hardware has already suppressed, while
under-weighting the phase-flip accumulation that actually limits the computation.
HQA's `cat_biased_noise_router` replaces the symmetric cost function with an
asymmetric one — heavy weight on phase-flip proximity, residual-only weight on
bit-flip proximity — so a proposed route minimizes the risk that is real on a cat
fabric. This is an advisory routing proposal only; it carries no hardware
authority.

## 3. Setpoint homeostasis: an honest characterization

Because raising `n_bar` buys exponential bit-flip protection at a linear
phase-flip cost, there is an optimal operating photon number:

```
n_bar*  =  0.5 * ln( 2 * kappa_X / kappa_Z )
```

where `kappa_X` and `kappa_Z` are the environment's bit-flip and phase-flip
pressures. The key property: **n_bar\* depends on the noise asymmetry, not on the
overall noise magnitude.** HQA's role is to sense the current asymmetry and track
the setpoint to it — the same principle a homeostatic system uses to hold a
variable at its correct value as conditions change.

We characterized this in a local simulation (`cat_setpoint_homeostasis_sweep`)
with three honest findings:

1. **The phase-flip law is real.** A dynamiqs Lindblad simulation of an even cat
   stabilized by two-photon dissipation and exposed to single-photon loss gives a
   parity-decay (phase-flip) rate that scales linearly with `n_bar`, fitted slope
   within a few percent of the analytic expectation (R^2 ~ 0.98). The exponential
   bit-flip suppression is taken as the established cat-qubit result, not
   re-derived here.

2. **A fixed setpoint is not adaptation, and we report the null.** When only the
   overall severity changes at fixed asymmetry, the optimal drive stays constant
   (near the default), so forcing a different fixed drive value cannot help and
   can slightly overshoot. An earlier internal run showed exactly this — a small
   *negative* change from a hard-coded drive shift. We keep that null on the
   record; it is the correct scientific outcome, not a failure to hide.

3. **Tracking earns its keep when the asymmetry drifts.** When the bit/phase
   pressure ratio moves — across chips, temperatures, loss and dephasing rates —
   the optimal setpoint moves with it, and a controller that tracks it reduces
   logical error relative to any fixed setpoint. The benefit is U-shaped: ~0 at
   the environment the fixed setpoint was designed for, growing on either side as
   conditions drift. The result is a shape and a mechanism, not a single number.

## 4. What we do not claim

- HQA does not perform quantum error correction and is not a logical qubit.
- HQA does not claim improved physical fidelity on any live device.
- The photon-number and rate values above are representative model parameters,
  not Alice & Bob calibration data.
- No result here was produced on physical quantum hardware; all figures are from
  a local open-quantum-system simulation and an analytic trade-off model.

We are aware of, and aligned with, the discipline in Alice & Bob's *Defining the
Logical Qubit* — no cherry-picking, performance across all runs, results that
survive full-process conditions. Nothing in this note is presented as a logical
qubit under those criteria. HQA's relevance is upstream of that bar: as
hardware-aware validation and control tooling that preserves operating
conditions, compares adapted versus unadapted behavior, and abstains when
evidence is insufficient.

## 5. Where a first conversation could go

- Whether HQA's biased-noise routing and setpoint-tracking model reflect Alice &
  Bob's real device behavior, and where they diverge.
- Whether a vendor-neutral validation layer that keeps adapted-vs-unadapted
  operating conditions on the record is useful to a cat-qubit program.
- What minimal, non-confidential dataset would let HQA's normalization be checked
  against a real cat-qubit backend without granting any hardware authority.

## Boundary

Advisory research architecture. No hardware authority, no live backend access,
no pulse or cryostat control, no quantum-advantage or error-correction claim.
Intended for technical screening and discussion only.
