# HQA Cat-Qubit Setpoint Homeostasis V0

*Illustrative model + local Lindblad simulation. No hardware authority, no live
Alice & Bob calibration data, no physical-fidelity claim. Logical error rates are
per-cycle illustrative quantities for comparing control strategies.*

## 1. The biased-noise trade-off

| Error | Model | Behavior |
|---|---|---|
| Bit-flip (X) | `kappa_X * exp(-2 n_bar)` | Exponentially suppressed with photon number |
| Phase-flip (Z) | `kappa_Z * n_bar` | Grows linearly with photon number |

Optimal setpoint: `n_bar* = 0.5 * ln(2 kappa_X / kappa_Z)` -- a function of the
environmental **asymmetry**, not of overall noise magnitude.

## 2. Phase-flip scaling: real Lindblad cross-check (dynamiqs)

Even cat stabilized by two-photon dissipation, exposed to single-photon loss;
parity decay measures the phase-flip rate.

| n_bar | alpha | parity-decay rate | rate / (kappa1 * n_bar) |
|---:|---:|---:|---:|
| 2.0 | 1.4142 | 0.174323 | 1.7432 |
| 2.5 | 1.5811 | 0.236993 | 1.8959 |
| 3.0 | 1.7321 | 0.292584 | 1.9506 |
| 3.5 | 1.8708 | 0.345258 | 1.9729 |
| 4.0 | 2.0 | 0.396467 | 1.9823 |

Linear-through-origin slope **0.09712** vs expected `2*kappa1 = 0.1` (R^2 = 0.9829). Confirms `p_Z ~ n_bar` from first-principles dynamics.

## 3. Why the June raw cat run was a null (validation anchor)

Fixed noise asymmetry, varying overall severity. The optimal setpoint n_bar* is constant (~1.5), so forcing alpha=1.35 overshoots it and is marginally WORSE than the alpha=1.20 default at every severity -- reproducing the observed null / slight-negative raw result.

With the raw-run coefficients the optimal drive is a constant **alpha ~ 1.2239** -- essentially the alpha=1.20 default. The hard-coded 'adapt to alpha=1.35' overshoots it:

| Severity | optimal alpha | forced alpha=1.35 vs static alpha=1.20 |
|---:|---:|---:|
| 0.5 | 1.2239 | -4.116% |
| 1.0 | 1.2239 | -4.116% |
| 1.5 | 1.2239 | -4.116% |
| 2.0 | 1.2239 | -4.116% |
| 3.0 | 1.2239 | -4.116% |

Every entry is <= 0: forcing alpha=1.35 is marginally worse at all severities,
reproducing the observed slight-negative (-0.18%) raw result. The null was real
and correct -- a fixed setpoint mislabeled as adaptation, not a broken idea.

## 4. Where adaptive setpoint control earns its keep

Fixed control setpoint (n_bar=4.0) vs a homeostatic controller that re-solves n_bar* as the noise asymmetry drifts. Error reduction is ~0 where the environment matches the setpoint and grows with drift.

| kappa_X / kappa_Z | optimal n_bar | static error | adaptive error | error reduction |
|---:|---:|---:|---:|---:|
| 1.0 | 2.0 | 2.000e-02 | 1.009e-02 | 49.546% |
| 4.0 | 2.0 | 2.001e-02 | 1.037e-02 | 48.186% |
| 10.0 | 2.0 | 2.002e-02 | 1.092e-02 | 45.467% |
| 40.0 | 2.191 | 2.007e-02 | 1.346e-02 | 32.95% |
| 200.0 | 2.9957 | 2.034e-02 | 1.748e-02 | 14.048% |
| 1000.0 | 3.8005 | 2.168e-02 | 2.150e-02 | 0.808% |
| 4000.0 | 4.4936 | 2.671e-02 | 2.497e-02 | 6.519% |
| 20000.0 | 5.2983 | 5.355e-02 | 2.899e-02 | 45.857% |

The benefit is **U-shaped**, and the shape is the point, not any single number. It falls to ~0 near ratio 1000-1500, where the fixed n_bar=4 already sits at the optimum -- the controller correctly claims nothing it did not earn. It grows on either side as the environment drifts (hotter, lossier, a different chip), reaching tens of percent of logical-error reduction at the edges of the swept range. A fixed setpoint is right for one environment; setpoint tracking is right for all of them.

## 5. Honest summary

- The retired `+2.68%` headline is not reproduced and is not supported by any run.
- The genuine result: **homeostatic setpoint tracking** reduces cat-qubit logical
  error precisely when the noise asymmetry drifts, and correctly does nothing when
  it does not. That is the biologically faithful claim: match the setpoint to the
  environment; do not assume a fixed one.
- Value to a cat-qubit platform is **architecture-level accommodation** of biased
  noise, not a fixed fidelity gain.

## Boundary

Advisory analysis only. Illustrative per-cycle error model; single-mode Lindblad
simulation with representative rates; exponential bit-flip suppression taken as a
modeled/established assumption. No live hardware, no vendor calibration data, no
physical-fidelity or QEC-threshold claim.
