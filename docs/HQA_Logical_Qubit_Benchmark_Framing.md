# HQA Logical-Qubit Benchmark Framing

## Purpose

This note frames Homeostatic Quantum Architecture (HQA) in relation to serious logical-qubit benchmarking discussions, including Alice & Bob's June 2026 memo on defining logical-qubit claims.

The goal is to keep HQA in its correct lane:

HQA does not claim to create logical qubits or solve fault-tolerant quantum computing.

HQA is a hardware-state control and evidence layer that can help make quantum execution and logical-qubit benchmark claims more auditable under real operating conditions.

## Benchmark Context

Serious logical-qubit claims need discipline.

Useful evaluation requires more than saying a logical qubit exists. Reviewers need to understand:

- whether logical lifetime exceeds physical-qubit lifetime
- whether the code or physical stabilization mechanism has scalable parameters
- whether enough QEC cycles were run for errors to appear
- whether results are reproducible without heavy cherry-picking or post-selection
- whether error correction lasts on timescales relevant to useful computation

Those criteria belong to the logical-qubit benchmark itself.

HQA sits adjacent to that.

It asks:

- What was the hardware state during execution?
- Which physical qubits or coupling regions were degraded?
- What did calibration telemetry show?
- Which routing/control decisions were made?
- Did the system intervene or abstain?
- Were post-selection and discarded runs documented?
- Did the result improve, regress, or remain neutral under those conditions?

## HQA Positioning

Short version:

> Logical-qubit claims need benchmark criteria. Quantum control stacks need operating-condition ledgers.

HQA is being developed as that kind of operating-condition layer.

It is designed to:

- read live or simulated hardware telemetry
- identify degraded qubits and coupling regions
- quarantine weak areas when justified
- route execution around degraded topology when useful
- abstain when intervention would likely hurt
- preserve the full evidence trail
- learn from good and bad runs

## Why Good And Bad Runs Both Matter

HQA should not be presented as a magic optimizer.

Recent IBM backend validation showed the correct lesson:

- On degraded hardware, intervention can help.
- On healthier hardware, unnecessary routing constraints can hurt.

That is not a weakness of the architecture.

That is exactly why HQA needs an intervention gate.

The system should learn when to act and when to stand down. Both outcomes improve the control policy if the evidence is preserved.

## Operating-Condition Ledger

For each benchmark or execution trial, HQA should aim to log:

- backend name
- timestamp
- qubit count
- calibration snapshot
- T1 / T2 distributions
- readout error distribution
- degraded qubit list
- degraded coupling edge list
- routing path
- intervention mode
- abstention reason, if applicable
- QEC cycle metadata, if available
- post-selection/discard policy
- raw and adapted result metrics
- known limitations

This creates a record that can be reviewed independently.

## Public-Safe Framing

Use:

> HQA is a hardware-aware quantum control and evidence layer designed to track device health, route around degraded regions when justified, abstain when intervention is not warranted, and preserve the operating record behind quantum execution results.

Avoid:

- "HQA solved logical qubits"
- "HQA proves fault tolerance"
- "HQA guarantees fidelity improvement"
- "HQA eliminates decoherence"
- "HQA is a replacement for QEC"

## Suggested LinkedIn Comment

Strong logical-qubit benchmarks need more than headline numbers.

They need operating context:

- hardware state
- calibration drift
- degraded regions
- QEC cycles
- routing decisions
- post-selection rules
- runtime duration
- reproducibility across all runs

That is the lane I am focused on with HQA.

Not claiming to solve logical qubits, but building the control and evidence layer that helps make quantum execution results easier to audit under real hardware conditions.

Show the good runs.

Show the bad runs too.

That is where the engineering boundary gets learned.

## One-Line Version

HQA is not a logical-qubit claim; it is an operating-condition ledger and control layer for understanding when quantum hardware intervention helps, hurts, or should abstain.
