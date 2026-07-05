# HQA Sentinel Reflex — Compute-Scalability Demonstration (Classical Simulation)

**What this is:** a *classical* simulation that measures the compute cost of the
edge-parallel Sentinel monitoring scheme on very large grids. It is **not**
quantum error correction, is **not** run on qubits, and makes **no** fidelity,
cascade-prevention, or quantum-advantage claim. The "errors" below are flagged
cells in a classical cellular grid model, not physical qubit errors.

**Why it can scale:** each grid cell is watched by a local fixed-size patch.
Because the patches are independent, the scheme is embarrassingly parallel and
its per-patch work is constant regardless of total grid size. The point of the
runs below is to show that the *monitoring layer's compute* stays tractable as
the grid grows — nothing more.

## Baseline caveat (read first)

The "Traditional Matrix Decoder" column is a **non-quarantining null baseline**:
it flags nothing and isolates nothing, so it accumulates one flagged cell per
injected fault by construction. It is **not** a real MWPM / union-find / belief-
propagation decoder. The large error-count contrast is therefore *not* a decoder
comparison, and no claim of superiority over real decoders is made or implied.
The only defensible reading of these tables is the wall-clock column: how long
the edge-parallel scheme takes to sweep a grid of a given size.

## Wall-clock scaling (the defensible result)

| Backend | Grid | Cells | Injected faults | Engine | Wall-clock (50 ticks) |
|---|---|---:|---:|---|---:|
| CPU (pure Python) | 1000×1000 | 1,000,000 | 5,000 | single-thread | — |
| CPU (pure Python) | 2000×2000 | 4,000,000 | 20,000 | single-thread | — |
| GPU (CUDA/PyTorch) | 3162×3162 | 10,000,000 | 50,000 | CUDA cores | 0.632 s |
| GPU (CUDA/PyTorch) | 10000×10000 | 100,000,000 | — | CUDA cores | 6.816 s |
| Rust (bare-metal CPU) | 3162×3162 | 10,000,000 | 50,000 | system RAM | 8.25 s |
| Rust (bare-metal CPU) | 31622×31622 | 1,000,000,000 | 5,000,000 | system RAM | 817.37 s |

The 1-billion-cell GPU run did **not** complete: the local 6 GB VRAM was
exhausted allocating the required tensors, so that scale was only reached on the
CPU/RAM path. That is a hardware limit of one workstation, not evidence of a
mathematical scaling limit — and equally, completing a classical grid sweep is
not evidence of quantum-scale error correction.

## What this does and does not support

- **Supports:** the edge-parallel patch scheme has constant per-patch cost, so a
  classical fault-flagging sweep of very large grids is computationally feasible
  on commodity hardware.
- **Does not support:** any quantum error-correction result, any cascade
  prevention on physical qubits, any comparison against a real decoder, or any
  fidelity / quantum-advantage claim.

## Boundary

Classical simulation only. No quantum hardware, no qubits, no QEC, no live
backend, no hardware authority. Timing figures are commodity-hardware
measurements of a classical grid model and are advisory context only.
