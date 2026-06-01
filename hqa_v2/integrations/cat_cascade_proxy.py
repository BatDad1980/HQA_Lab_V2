"""Cat-qubit cascade proxy specification for HQA V2.

Cat qubits live in bosonic oscillator phase space. Standard gate simulators are
useful for control-plane plumbing, but they do not capture the physics HQA needs
for cat-qubit cascade work. This module writes a solver-ready proxy
specification for Dynamiqs/QuTiP without pretending those solvers are installed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_CAT_CASCADE_PROXY.md"
JSON_PATH = HQA_V2_ROOT / "logs" / "cat_cascade_proxy.json"


@dataclass
class BosonicSolverReadiness:
    qutip_available: bool
    dynamiqs_available: bool
    jax_available: bool
    selected_lane: str


@dataclass
class CatCascadeModelSpec:
    primary_seed: str
    secondary_seed: str
    state_space: str
    key_observables: list[str]
    evidence_streams: list[str]
    sentinel_trigger: str
    quarantine_target: str
    hqa_action: str


@dataclass
class SolverHook:
    solver: str
    status: str
    intended_use: str
    missing_reason: str | None


def available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def collect_readiness() -> BosonicSolverReadiness:
    qutip = available("qutip")
    dynamiqs = available("dynamiqs")
    jax = available("jax")
    if dynamiqs and jax:
        selected = "dynamiqs"
    elif qutip:
        selected = "qutip"
    else:
        selected = "spec_only"
    return BosonicSolverReadiness(
        qutip_available=qutip,
        dynamiqs_available=dynamiqs,
        jax_available=jax,
        selected_lane=selected,
    )


def build_model_spec() -> CatCascadeModelSpec:
    return CatCascadeModelSpec(
        primary_seed="single-photon-loss event in oscillator mode",
        secondary_seed="ancilla/readout fault that masks parity change",
        state_space="truncated bosonic Hilbert space / oscillator phase-space proxy",
        key_observables=[
            "parity expectation over correction cycles",
            "photon-number drift",
            "logical bit-flip proxy",
            "phase-flip proxy",
            "Wigner negativity / lobe separation proxy",
        ],
        evidence_streams=[
            "cycle-indexed parity measurements",
            "trajectory-indexed jump records",
            "Wigner snapshot metadata",
            "sentinel trigger timestamp",
            "quarantine/reroute decision manifest",
        ],
        sentinel_trigger="parity anomaly persists or repeats across correction cycles",
        quarantine_target="oscillator_mode_or_patch_id",
        hqa_action="SENTINEL_QUARANTINE_AND_ROUTE_AROUND_PATCH_PROPOSAL",
    )


def build_solver_hooks(readiness: BosonicSolverReadiness) -> list[SolverHook]:
    return [
        SolverHook(
            solver="Dynamiqs/JAX",
            status="available" if readiness.dynamiqs_available and readiness.jax_available else "unavailable",
            intended_use="GPU/JAX Monte Carlo trajectories and Lindblad dynamics for photon-loss cascade studies.",
            missing_reason=None if readiness.dynamiqs_available and readiness.jax_available else "dynamiqs and jax must both be installed.",
        ),
        SolverHook(
            solver="QuTiP",
            status="available" if readiness.qutip_available else "unavailable",
            intended_use="Academic-reference open-system master equation and trajectory checks.",
            missing_reason=None if readiness.qutip_available else "qutip is not installed.",
        ),
    ]


def write_outputs(readiness: BosonicSolverReadiness, spec: CatCascadeModelSpec, hooks: list[SolverHook]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(
        json.dumps(
            {
                "readiness": asdict(readiness),
                "model_spec": asdict(spec),
                "solver_hooks": [asdict(hook) for hook in hooks],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# HQA Cat Cascade Proxy",
        "",
        "## Purpose",
        "",
        "This report defines the cat-qubit cascade evidence lane for HQA V2.",
        "",
        "Gate-level simulators are useful for control-plane plumbing, but cat-qubit cascade work requires bosonic/open-system solvers. This proxy captures the intended model and evidence stream without pretending unavailable solvers have run.",
        "",
        "## Solver Readiness",
        "",
        f"- QuTiP available: `{readiness.qutip_available}`",
        f"- Dynamiqs available: `{readiness.dynamiqs_available}`",
        f"- JAX available: `{readiness.jax_available}`",
        f"- Selected lane: `{readiness.selected_lane}`",
        "",
        "| Solver | Status | Intended Use | Missing Reason |",
        "|---|---:|---|---|",
    ]

    for hook in hooks:
        lines.append(
            f"| {hook.solver} | {hook.status} | {hook.intended_use} | {hook.missing_reason or '-'} |"
        )

    lines.extend(
        [
            "",
            "## Cascade Model",
            "",
            f"- Primary seed: `{spec.primary_seed}`",
            f"- Secondary seed: `{spec.secondary_seed}`",
            f"- State space: `{spec.state_space}`",
            f"- Sentinel trigger: `{spec.sentinel_trigger}`",
            f"- Quarantine target: `{spec.quarantine_target}`",
            f"- HQA action: `{spec.hqa_action}`",
            "",
            "## Required Observables",
            "",
        ]
    )

    for observable in spec.key_observables:
        lines.append(f"- {observable}")

    lines.extend(["", "## Required Evidence Streams", ""])
    for stream in spec.evidence_streams:
        lines.append(f"- {stream}")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a solver-ready proxy specification. It does not run a bosonic simulation unless QuTiP or Dynamiqs/JAX is installed, and it does not validate physical cat-qubit hardware, production QEC performance, or live control authority.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    readiness = collect_readiness()
    spec = build_model_spec()
    hooks = build_solver_hooks(readiness)
    write_outputs(readiness, spec, hooks)
    print(f"HQA cat cascade proxy written: {REPORT_PATH}")
    print(f"- selected lane: {readiness.selected_lane}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
