# HQA V2 Optional Quantum Simulator Integrations

## Purpose

This folder defines optional simulator lanes for HQA V2.

HQA must remain runnable without heavyweight quantum dependencies. These integrations are therefore optional adapters, not required runtime dependencies.

## Integration Lanes

### Qiskit / IBM Quantum

Use for:

- IBM-style circuit execution
- Aer simulation
- future backend-oriented adapter work

Optional packages:

```bash
pip install qiskit qiskit-aer qiskit-ibm-runtime
```

GPU lane, only when compatible with the local environment:

```bash
pip install qiskit-aer-gpu
```

Live IBM backend access is intentionally separated from simulator readiness.
Set credentials through environment variables only:

```powershell
$env:IBM_QUANTUM_TOKEN = "<token>"
$env:IBM_QUANTUM_INSTANCE_CRN = "<instance-crn>"
python hqa_v2/integrations/ibm_runtime_readiness.py --live
```

Do not commit API keys, `.env` files, or local credential JSON files.

### Cirq / qsim

Use for:

- Google-style circuit simulation
- fast qsim-backed experiments
- topology/circuit replay comparisons

Optional packages:

```bash
pip install cirq qsimcirq
```

### QuTiP

Use for:

- open quantum systems
- master equation experiments
- academic-style noise modeling

Optional package:

```bash
pip install qutip
```

### Dynamiqs / JAX

Use for:

- GPU/JAX-based bosonic and cat-qubit-style simulation work
- high-performance open-system solver experiments

Optional package:

```bash
pip install dynamiqs
```

For GPU execution, install the JAX build that matches the active CUDA toolkit.

## Boundary

These adapters are for simulator and trace integration.

They do not validate physical quantum hardware, production QEC performance, or live hardware control.
