# HQA Claim Boundary

## Positioning

HQA V2 should be described as:

> A condition-aware, quantum-adjacent local-control architecture for telemetry intake, degraded-region quarantine, shadow routing, bounded advisory review, and dry-run/mock HAL safety contracts.

This is the clean public/technical-review position.

## Supported Claims

| Claim | Evidence Type |
|---|---|
| HQA can ingest and normalize backend telemetry snapshots. | IBM runtime readiness, backend health translator, field-map adapter. |
| HQA can classify degraded regions and produce shadow quarantine/reroute proposals. | Field-map replay, risk-field, shadow adaptive proposal gates. |
| HQA can abstain when intervention is not justified. | IBM live-validation abstention replay gate. |
| HQA can gate HAL-style commands in dry-run/mock settings. | HAL boundary, loopback boundary, pump hysteresis contracts. |
| HQA can fail closed under missing or invalid BACL authority. | BACL entropy and fail-closed authority gates. |
| HQA can bound LLM advisory output under deterministic gates. | Cognitive advisory and telemetry compression gates. |
| HQA can package evidence into replayable reports and logs. | Regression summary, technical index, vendor shadow packet validation. |

## Claims Requiring Stronger Evidence

| Claim Family | Required Evidence Before Use |
|---|---|
| Live QPU performance improvement | Job ID, backend, circuit, shots, counts, timestamp, route comparison, and reproducibility notes. |
| Production decoder superiority | Fair baseline against accepted decoders and explicit error model. |
| Cat-qubit hardware validation | Full solver or vendor-aligned model documentation with bosonic dynamics and assumptions. |
| Real cryostat/HAL control | Physical lab authorization, endpoint interlocks, operator review, audit logs, and safety approval. |
| Commercial product readiness | Installable package, CI, user docs, configuration management, release artifact, and support boundary. |

## Language Rules

Use:

- "proxy"
- "shadow-mode"
- "local noisy simulation"
- "real calibration telemetry"
- "mock loopback"
- "bounded advisory"
- "condition-aware intervention"
- "abstention-capable"
- "dry-run HAL boundary"

Avoid:

- claims that HQA has completed the whole quantum-control problem
- "physical hardware validated" without job proof
- "production QEC"
- "unrestricted control"
- "universal scaling"
- "always improves"
- "autonomous hardware authority"

## One-Sentence External Summary

HQA V2 is a local-control research prototype that uses real and simulated telemetry to test condition-aware quarantine, routing, abstention, and safety-boundary behavior before any real hardware authority is granted.

## Internal Motto

Disrupt the room, but keep the paperwork in order.
