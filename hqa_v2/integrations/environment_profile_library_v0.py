"""Build the HQA Environment Profile Library V0.

The library translates Chaos-Worldmodel "pile" language into HQA-native
review postures. Profiles tune thresholds and buffers for interpreting local
evidence; they do not authorize live quantum hardware action.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "environment_profile_library_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_ENVIRONMENT_PROFILE_LIBRARY_V0.md"


@dataclass(frozen=True)
class EnvironmentProfile:
    profile_id: str
    display_name: str
    internal_codename: str
    regime: str
    simulator_mapping: str
    risk_threshold_monitor: float
    risk_threshold_route_review: float
    risk_threshold_quarantine_review: float
    tracer_buffer: str
    reflex_posture: str
    learning_permission: str
    hqa_allowed_actions: list[str]
    boundary: str


PROFILES = [
    EnvironmentProfile(
        profile_id="ENV-EARTH-BASELINE",
        display_name="Earth Baseline",
        internal_codename="earth",
        regime="stable_homeostatic",
        simulator_mapping="nominal",
        risk_threshold_monitor=0.20,
        risk_threshold_route_review=0.40,
        risk_threshold_quarantine_review=0.80,
        tracer_buffer="short",
        reflex_posture="observe_small_slips",
        learning_permission="safe_to_record_as_baseline_evidence",
        hqa_allowed_actions=["MONITOR_ONLY", "MONITOR_WITH_ROUTE_REVIEW"],
        boundary="Use as quiet baseline calibration only; no hardware authority.",
    ),
    EnvironmentProfile(
        profile_id="ENV-TITAN-DAMPED",
        display_name="Titan Damped",
        internal_codename="titan",
        regime="high_latency_damped",
        simulator_mapping="mild_stress",
        risk_threshold_monitor=0.18,
        risk_threshold_route_review=0.34,
        risk_threshold_quarantine_review=0.76,
        tracer_buffer="long",
        reflex_posture="slow_feedback_expand_observation_window",
        learning_permission="record_only_after_decay_check",
        hqa_allowed_actions=["MONITOR_ONLY", "MONITOR_WITH_ROUTE_REVIEW", "QUARANTINE_PROPOSAL"],
        boundary="Treat slow signals as delayed evidence, not permission for live correction.",
    ),
    EnvironmentProfile(
        profile_id="ENV-ASTEROID-RUPTURE",
        display_name="Asteroid Rupture",
        internal_codename="asteroid",
        regime="high_velocity_rupture",
        simulator_mapping="correlated_stress",
        risk_threshold_monitor=0.12,
        risk_threshold_route_review=0.28,
        risk_threshold_quarantine_review=0.65,
        tracer_buffer="burst",
        reflex_posture="fast_local_quench_review",
        learning_permission="no_unsupervised_learning_during_rupture",
        hqa_allowed_actions=["MONITOR_WITH_ROUTE_REVIEW", "QUARANTINE_PROPOSAL", "ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL"],
        boundary="Rupture mode increases review sensitivity but still grants no live hardware authority.",
    ),
    EnvironmentProfile(
        profile_id="ENV-DEEP-VACUUM-BRITTLE",
        display_name="Deep Vacuum Brittle",
        internal_codename="deep_vacuum",
        regime="low_interference_brittle",
        simulator_mapping="no_route_hold",
        risk_threshold_monitor=0.10,
        risk_threshold_route_review=0.24,
        risk_threshold_quarantine_review=0.55,
        tracer_buffer="precision",
        reflex_posture="hold_on_shatter_risk",
        learning_permission="block_training_until_operator_review",
        hqa_allowed_actions=["NO_ROUTE_HOLD_REVIEW"],
        boundary="If safe route evidence collapses, hold rather than force a correction.",
    ),
    EnvironmentProfile(
        profile_id="ENV-PULSE-BREATH",
        display_name="Pulse/Breath Cycle",
        internal_codename="pulse_breath",
        regime="cyclical_expansion_contraction",
        simulator_mapping="schedule_overlay",
        risk_threshold_monitor=0.16,
        risk_threshold_route_review=0.32,
        risk_threshold_quarantine_review=0.70,
        tracer_buffer="phase_aware",
        reflex_posture="phase_gate_before_escalation",
        learning_permission="record_phase_tagged_evidence_only",
        hqa_allowed_actions=["MONITOR_ONLY", "MONITOR_WITH_ROUTE_REVIEW", "QUARANTINE_PROPOSAL"],
        boundary="Cycle profile is an interpretation overlay; it does not drive live pulse shaping.",
    ),
]


def write_outputs() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "hqa.environment_profile_library.v0",
        "execution_mode": "interpretation_only",
        "hardware_authority": False,
        "profiles": [asdict(profile) for profile in PROFILES],
        "boundary": "Profiles tune advisory interpretation only. They do not authorize backend jobs, pulse changes, quarantine commands, or HAL execution.",
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# HQA Environment Profile Library V0",
        "",
        "## Purpose",
        "",
        "This report translates Chaos-Worldmodel regime language into HQA-native environment profiles.",
        "",
        "The profiles explain how local evidence should be interpreted across stable, damped, rupture, brittle, and cyclic regimes. They do not replace measured topology, syndrome, or simulator evidence.",
        "",
        "## Profiles",
        "",
        "| Profile | Regime | Stress Mapping | Route Review Threshold | Quarantine Review Threshold | Reflex Posture |",
        "|---|---|---|---:|---:|---|",
    ]
    for profile in PROFILES:
        lines.append(
            f"| `{profile.display_name}` | `{profile.regime}` | `{profile.simulator_mapping}` | `{profile.risk_threshold_route_review}` | `{profile.risk_threshold_quarantine_review}` | `{profile.reflex_posture}` |"
        )

    lines.extend(["", "## Interpretation Rules", ""])
    lines.append("- Profiles are labels for advisory posture, not physical environments.")
    lines.append("- HQA-native evidence still comes from topology, syndrome history, route health, and simulator traces.")
    lines.append("- Lower thresholds increase review sensitivity only; they do not grant live control.")
    lines.append("- Deep Vacuum/Brittle mode prefers hold behavior when no safe route exists.")
    lines.append("- Pulse/Breath mode is phase-tagging guidance, not live pulse-shaping authority.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    write_outputs()
    print(f"HQA environment profile library written: {OUTPUT_PATH}")
    print(f"HQA environment profile report written: {REPORT_PATH}")
    print(f"- profiles: {len(PROFILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
