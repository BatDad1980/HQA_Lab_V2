"""Clean-lab harvest of the V1 vagus/autonomic stress primitive.

The legacy idea aggregated Sentinel correction pressure across local patches
and triggered a systemic response when a region got hot. This rewrite keeps the
useful control shape but converts every output into a bounded advisory decision.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "legacy_autonomic_stress_regulator_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_LEGACY_AUTONOMIC_STRESS_REGULATOR_V0.md"


@dataclass(frozen=True)
class PatchTick:
    tick: int
    patch_id: str
    correction_count: int
    drift_velocity: float
    syndrome_confidence: float
    scar_route_available: bool


@dataclass(frozen=True)
class PatchDecision:
    patch_id: str
    total_corrections: int
    max_drift_velocity: float
    mean_syndrome_confidence: float
    stress_score: float
    stress_band: str
    advisory_action: str
    reason: str


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def stress_band(score: float) -> str:
    if score >= 0.85:
        return "red_hold"
    if score >= 0.65:
        return "orange_reroute_review"
    if score >= 0.40:
        return "yellow_calibration_hold"
    return "green_monitor"


def action_for(score: float, route_available: bool) -> str:
    if score >= 0.85:
        return "SAFE_HOLD"
    if score >= 0.65 and route_available:
        return "PROPOSE_REROUTE_REVIEW"
    if score >= 0.40:
        return "PROPOSE_CALIBRATION_HOLD"
    return "MONITOR_ONLY"


def score_patch(ticks: list[PatchTick]) -> PatchDecision:
    total_corrections = sum(item.correction_count for item in ticks)
    max_drift = max(abs(item.drift_velocity) for item in ticks)
    mean_confidence = sum(item.syndrome_confidence for item in ticks) / len(ticks)
    route_available = any(item.scar_route_available for item in ticks)

    correction_pressure = clamp(total_corrections / 42.0)
    drift_pressure = clamp(max_drift / 0.35)
    confidence_pressure = clamp(mean_confidence)
    route_penalty = 0.0 if route_available else 0.18
    score = clamp((correction_pressure * 0.42) + (drift_pressure * 0.30) + (confidence_pressure * 0.18) + route_penalty)
    band = stress_band(score)
    action = action_for(score, route_available)

    if action == "SAFE_HOLD":
        reason = "Stress crossed red threshold or no safe recovery path is available."
    elif action == "PROPOSE_REROUTE_REVIEW":
        reason = "Patch stress is high but a scar route remains available."
    elif action == "PROPOSE_CALIBRATION_HOLD":
        reason = "Patch stress is elevated enough to pause and recalibrate."
    else:
        reason = "Patch remains within monitor-only range."

    return PatchDecision(
        patch_id=ticks[0].patch_id,
        total_corrections=total_corrections,
        max_drift_velocity=round(max_drift, 6),
        mean_syndrome_confidence=round(mean_confidence, 6),
        stress_score=round(score, 6),
        stress_band=band,
        advisory_action=action,
        reason=reason,
    )


def build_ticks() -> list[PatchTick]:
    return [
        PatchTick(1, "PATCH_NW", 2, -0.03, 0.12, True),
        PatchTick(2, "PATCH_NW", 1, -0.02, 0.10, True),
        PatchTick(3, "PATCH_NW", 2, -0.01, 0.11, True),
        PatchTick(1, "PATCH_NE", 7, -0.09, 0.42, True),
        PatchTick(2, "PATCH_NE", 9, -0.12, 0.48, True),
        PatchTick(3, "PATCH_NE", 8, -0.08, 0.46, True),
        PatchTick(1, "PATCH_SW", 12, -0.18, 0.74, True),
        PatchTick(2, "PATCH_SW", 14, -0.23, 0.77, True),
        PatchTick(3, "PATCH_SW", 13, -0.21, 0.80, True),
        PatchTick(1, "PATCH_SE", 15, -0.31, 0.91, False),
        PatchTick(2, "PATCH_SE", 16, -0.34, 0.93, False),
        PatchTick(3, "PATCH_SE", 17, -0.33, 0.95, False),
    ]


def run_regulator() -> dict[str, object]:
    ticks = build_ticks()
    grouped: dict[str, list[PatchTick]] = {}
    for tick in ticks:
        grouped.setdefault(tick.patch_id, []).append(tick)

    decisions = [score_patch(items) for _, items in sorted(grouped.items())]
    highest = max(decisions, key=lambda item: item.stress_score)

    return {
        "schema_version": "hqa.legacy_autonomic_stress_regulator.v0",
        "source_lineage": "HQA_V1 vagus_nerve.py, sentinel_reflex.py, hqa_v2/core/vagus_nerve_predictor.py",
        "execution_mode": "shadow_advisory",
        "hardware_authority": False,
        "tick_count": len(ticks),
        "patch_count": len(decisions),
        "decisions": [asdict(item) for item in decisions],
        "highest_stress_patch": highest.patch_id,
        "system_recommendation": highest.advisory_action,
        "disallowed_outputs": {
            "live_cooling_command": 0,
            "pulse_change": 0,
            "hal_dispatch": 0,
            "backend_job": 0,
        },
        "boundary": "This artifact converts legacy autonomic stress logic into advisory patch-state decisions only. It does not dispatch cooling, pulses, backend jobs, or HAL commands.",
    }


def write_report(payload: dict[str, object]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Legacy Autonomic Stress Regulator V0",
        "",
        "## Purpose",
        "",
        "This report records a clean-lab harvest of the legacy V1 vagus/autonomic control primitive.",
        "",
        "Instead of commanding hardware, the regulator aggregates local patch stress and emits bounded advisory decisions.",
        "",
        "## Summary",
        "",
        f"- Execution mode: `{payload['execution_mode']}`",
        f"- Hardware authority: `{payload['hardware_authority']}`",
        f"- Patch count: `{payload['patch_count']}`",
        f"- Highest stress patch: `{payload['highest_stress_patch']}`",
        f"- System recommendation: `{payload['system_recommendation']}`",
        "",
        "## Patch Decisions",
        "",
        "| Patch | Corrections | Max Drift | Mean Syndrome Confidence | Stress Score | Band | Advisory Action |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for decision in payload["decisions"]:
        lines.append(
            f"| `{decision['patch_id']}` | `{decision['total_corrections']}` | `{decision['max_drift_velocity']}` | `{decision['mean_syndrome_confidence']}` | `{decision['stress_score']}` | `{decision['stress_band']}` | `{decision['advisory_action']}` |"
        )
    lines.extend(
        [
            "",
            "## Harvested Pattern",
            "",
            "- V1 correction counts become local patch pressure.",
            "- V1 thermal/autonomic reflex becomes advisory state classification.",
            "- V1 preemptive degradation tracking becomes drift-velocity pressure.",
            "- Missing safe routes push the system toward `SAFE_HOLD`, not forced execution.",
            "",
            "## Disallowed Outputs",
            "",
            "| Output | Count |",
            "|---|---:|",
        ]
    )
    for name, count in payload["disallowed_outputs"].items():
        lines.append(f"| `{name}` | `{count}` |")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_regulator()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_report(payload)
    print(f"HQA legacy autonomic stress log written: {OUTPUT_PATH}")
    print(f"HQA legacy autonomic stress report written: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
