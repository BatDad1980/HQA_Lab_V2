"""Replay IBM live-validation outcomes into bounded intervention policy.

The live QPU validation numbers were reported from an adjacent HQA lane. This
clean-lane module treats them as directional replay fixtures, not as proof by
assertion. The purpose is to formalize the decision rule they exposed:
intervene when degraded topology benefits from quarantine routing; abstain when
healthy topology does not.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "ibm_live_validation_abstention_replay_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_IBM_LIVE_VALIDATION_ABSTENTION_REPLAY_V0.md"


@dataclass(frozen=True)
class LiveValidationFixture:
    backend: str
    qubits: int
    mean_t1_us: float
    mean_t2_us: float
    mean_readout_error: float
    defects_identified: int
    default_qiskit_fidelity: float
    hqa_quarantine_fidelity: float
    original_mode: str

    @property
    def defect_density(self) -> float:
        return round(self.defects_identified / self.qubits, 6)

    @property
    def fidelity_delta(self) -> float:
        return round(self.hqa_quarantine_fidelity - self.default_qiskit_fidelity, 6)


FIXTURES = [
    LiveValidationFixture(
        backend="ibm_fez",
        qubits=156,
        mean_t1_us=152.63,
        mean_t2_us=105.99,
        mean_readout_error=0.02936,
        defects_identified=55,
        default_qiskit_fidelity=0.9404,
        hqa_quarantine_fidelity=0.9648,
        original_mode="quarantine_route_around_active_defects",
    ),
    LiveValidationFixture(
        backend="ibm_kingston",
        qubits=156,
        mean_t1_us=168.61,
        mean_t2_us=118.96,
        mean_readout_error=0.02107,
        defects_identified=33,
        default_qiskit_fidelity=0.9824,
        hqa_quarantine_fidelity=0.9648,
        original_mode="monitor_and_shadow_optimize",
    ),
]


def classify_policy(fixture: LiveValidationFixture) -> dict[str, Any]:
    """Convert a validation outcome into a bounded intervention decision."""

    density = fixture.defect_density
    delta = fixture.fidelity_delta

    if density >= 0.30 and delta > 0:
        decision = "INTERVENE_WITH_QUARANTINE_REMAP_SHADOW"
        lesson = "Degraded field improved when HQA steered around defect pressure."
    elif density < 0.30 and delta < 0:
        decision = "ABSTAIN_AND_MONITOR"
        lesson = "Forced remap under healthier conditions underperformed default routing; stand down and shadow-optimize."
    elif delta > 0:
        decision = "MONITOR_WITH_OPTIONAL_SHADOW_REMAP"
        lesson = "Measured improvement exists, but thresholding should remain conservative."
    else:
        decision = "SAFE_HOLD_PENDING_REVIEW"
        lesson = "Outcome does not justify automatic intervention."

    return {
        "backend": fixture.backend,
        "defect_density": density,
        "fidelity_delta": delta,
        "default_qiskit_fidelity": fixture.default_qiskit_fidelity,
        "hqa_quarantine_fidelity": fixture.hqa_quarantine_fidelity,
        "original_mode": fixture.original_mode,
        "policy_decision": decision,
        "lesson": lesson,
        "hardware_authority": False,
        "jobs_submitted_by_clean_lane": 0,
    }


def run_replay() -> dict[str, Any]:
    decisions = [classify_policy(fixture) for fixture in FIXTURES]
    payload = {
        "schema_version": "hqa.ibm_live_validation_abstention_replay.v0",
        "execution_mode": "reported_fixture_policy_replay",
        "source_class": "adjacent_lane_reported_live_validation",
        "clean_lane_jobs_submitted": 0,
        "hardware_authority": False,
        "fixtures": [asdict(fixture) | {"defect_density": fixture.defect_density, "fidelity_delta": fixture.fidelity_delta} for fixture in FIXTURES],
        "decisions": decisions,
        "core_rule": "HQA should intervene only when measured field conditions justify it; otherwise it should abstain, monitor, or shadow-optimize.",
        "boundary": "This replay formalizes a policy lesson from reported adjacent-lane results. It does not submit IBM jobs, run circuits, reserve hardware, alter pulses, or claim production quantum performance.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA IBM Live Validation Abstention Replay V0",
        "",
        "## Purpose",
        "",
        "This replay captures the policy lesson from reported IBM live-validation outcomes: HQA is not an always-remap system. It is a condition-aware intervention layer.",
        "",
        "The fixtures below came from an adjacent HQA lane and are treated as replay inputs, not clean-lane proof until independently reproduced here.",
        "",
        "## Summary",
        "",
        f"- Execution mode: `{payload['execution_mode']}`",
        f"- Source class: `{payload['source_class']}`",
        f"- Clean-lane jobs submitted: `{payload['clean_lane_jobs_submitted']}`",
        f"- Hardware authority: `{payload['hardware_authority']}`",
        "",
        "| Backend | Defect Density | Default Qiskit | HQA Quarantine | Delta | Policy Decision |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for decision in payload["decisions"]:
        lines.append(
            f"| `{decision['backend']}` | `{decision['defect_density']:.6f}` | `{decision['default_qiskit_fidelity']:.4f}` | "
            f"`{decision['hqa_quarantine_fidelity']:.4f}` | `{decision['fidelity_delta']:+.6f}` | `{decision['policy_decision']}` |"
        )

    lines.extend(
        [
            "",
            "## Lessons",
            "",
        ]
    )
    for decision in payload["decisions"]:
        lines.append(f"- `{decision['backend']}`: {decision['lesson']}")

    lines.extend(
        [
            "",
            "## Core Rule",
            "",
            payload["core_rule"],
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_replay()
    write_report(payload)
    print(f"HQA IBM live validation abstention replay written: {REPORT_PATH}")
    print(f"- backends replayed: {len(payload['decisions'])}")
    print(f"- clean-lane jobs submitted: {payload['clean_lane_jobs_submitted']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

