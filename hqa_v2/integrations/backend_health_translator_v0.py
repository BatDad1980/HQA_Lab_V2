"""Backend health translator for HQA V2.

This module turns provider calibration snapshots into one HQA "playing field"
grammar. It is shadow-only: it reads local evidence files, writes normalized
health summaries, and grants no hardware authority.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = HQA_V2_ROOT / "logs" / "ibm_backend_snapshots"
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "backend_health_translator_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_BACKEND_HEALTH_TRANSLATOR_V0.md"


def load_snapshots() -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    for path in sorted(SNAPSHOT_DIR.glob("ibm_backend_calibration_snapshot_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("snapshot_performed") and payload.get("snapshot"):
            snapshots.append(payload)
    return snapshots


def classify_pressure(degraded_fraction: float | None) -> str:
    if degraded_fraction is None:
        return "UNKNOWN"
    if degraded_fraction >= 0.35:
        return "HIGH_DEGRADATION"
    if degraded_fraction >= 0.20:
        return "MODERATE_DEGRADATION"
    if degraded_fraction >= 0.10:
        return "LOW_DEGRADATION"
    return "NOMINAL"


def intervention_hint(degraded_fraction: float | None, readout_error: float | None) -> str:
    if degraded_fraction is None:
        return "METADATA_INSUFFICIENT"
    if degraded_fraction >= 0.35 or (readout_error is not None and readout_error >= 0.028):
        return "QUARANTINE_REMAP_SHADOW"
    if degraded_fraction >= 0.20:
        return "MONITOR_WITH_SHADOW_OPTIMIZATION"
    return "NO_INTERVENTION"


def health_score(snapshot: dict[str, Any]) -> float | None:
    degraded_fraction = snapshot.get("degraded_fraction")
    readout_error = snapshot.get("mean_readout_error")
    mean_t1 = snapshot.get("mean_t1_us")
    mean_t2 = snapshot.get("mean_t2_us")
    if degraded_fraction is None or readout_error is None or mean_t1 is None or mean_t2 is None:
        return None

    defect_component = max(0.0, 1.0 - float(degraded_fraction))
    readout_component = max(0.0, 1.0 - (float(readout_error) / 0.05))
    t1_component = min(1.0, float(mean_t1) / 200.0)
    t2_component = min(1.0, float(mean_t2) / 150.0)
    score = (0.40 * defect_component) + (0.25 * readout_component) + (0.20 * t1_component) + (0.15 * t2_component)
    return round(score, 6)


def translate_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    snapshot = payload["snapshot"]
    degraded_fraction = snapshot.get("degraded_fraction")
    readout_error = snapshot.get("mean_readout_error")
    score = health_score(snapshot)
    edges = int(snapshot.get("coupling_edges") or 0)
    degraded = int(snapshot.get("degraded_qubits") or 0)
    qubits = int(snapshot.get("qubits") or 0)

    return {
        "schema_version": "hqa.backend_health_profile.v0",
        "provider": "ibm_qiskit_runtime",
        "source_backend": snapshot.get("backend_name"),
        "topology_family": "heavy_hex",
        "telemetry_visibility": "summary_calibration",
        "spatial_visibility": False,
        "spatial_limitation": "Current snapshot contains summary health metrics only; per-qubit clustering requires richer calibration capture.",
        "node_count": qubits,
        "coupling_edges": edges,
        "degraded_nodes": degraded,
        "degraded_fraction": degraded_fraction,
        "mean_t1_us": snapshot.get("mean_t1_us"),
        "mean_t2_us": snapshot.get("mean_t2_us"),
        "mean_readout_error": readout_error,
        "health_score": score,
        "pressure_class": classify_pressure(degraded_fraction),
        "intervention_hint": intervention_hint(degraded_fraction, readout_error),
        "edge_pressure_proxy": round(degraded / qubits, 6) if qubits else None,
        "estimated_safe_edge_floor": max(0, round(edges * (1.0 - float(degraded_fraction or 0.0)))),
        "hardware_authority": False,
        "jobs_submitted": payload.get("jobs_submitted", 0),
    }


def compare_profiles(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(
        [profile for profile in profiles if profile.get("health_score") is not None],
        key=lambda item: float(item["health_score"]),
        reverse=True,
    )
    if len(ordered) < 2:
        return {"comparison_available": False, "reason": "At least two backend profiles are required."}

    healthiest = ordered[0]
    roughest = ordered[-1]
    return {
        "comparison_available": True,
        "healthiest_backend": healthiest["source_backend"],
        "roughest_backend": roughest["source_backend"],
        "health_score_delta": round(float(healthiest["health_score"]) - float(roughest["health_score"]), 6),
        "degraded_fraction_delta": round(float(roughest["degraded_fraction"]) - float(healthiest["degraded_fraction"]), 6),
        "translation_rule": "Select behavior from normalized health profile, not backend name.",
    }


def run_translation() -> dict[str, Any]:
    snapshots = load_snapshots()
    profiles = [translate_snapshot(payload) for payload in snapshots]
    payload = {
        "schema_version": "hqa.backend_health_translator.v0",
        "execution_mode": "shadow_translation_only",
        "provider_count": len({profile["provider"] for profile in profiles}),
        "backend_count": len(profiles),
        "hardware_authority": False,
        "jobs_submitted": sum(int(profile.get("jobs_submitted") or 0) for profile in profiles),
        "profiles": profiles,
        "comparison": compare_profiles(profiles),
        "boundary": "Backend health translation normalizes local calibration evidence only. It does not submit jobs, run circuits, alter routing tables, change pulses, or authorize HAL execution.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Backend Health Translator V0",
        "",
        "## Purpose",
        "",
        "This report verifies the translation layer that lets HQA read different backend conditions through one normalized health grammar.",
        "",
        "The rule is simple: HQA adapts to the measured playing field, not the provider or backend name.",
        "",
        "## Summary",
        "",
        f"- Execution mode: `{payload['execution_mode']}`",
        f"- Backends translated: `{payload['backend_count']}`",
        f"- Hardware authority: `{payload['hardware_authority']}`",
        f"- Jobs submitted: `{payload['jobs_submitted']}`",
        "",
        "| Backend | Health Score | Degraded Fraction | Pressure Class | Intervention Hint |",
        "|---|---:|---:|---|---|",
    ]
    for profile in payload["profiles"]:
        lines.append(
            f"| `{profile['source_backend']}` | `{profile['health_score']}` | `{profile['degraded_fraction']}` | `{profile['pressure_class']}` | `{profile['intervention_hint']}` |"
        )

    comparison = payload["comparison"]
    if comparison.get("comparison_available"):
        lines.extend(
            [
                "",
                "## Comparison",
                "",
                f"- Healthiest backend by normalized score: `{comparison['healthiest_backend']}`",
                f"- Roughest backend by normalized score: `{comparison['roughest_backend']}`",
                f"- Health score delta: `{comparison['health_score_delta']}`",
                f"- Degraded fraction delta: `{comparison['degraded_fraction_delta']}`",
                f"- Translation rule: {comparison['translation_rule']}",
            ]
        )

    lines.extend(
        [
            "",
            "## Current Limitation",
            "",
            "The current IBM calibration snapshots preserve summary metrics. Spatial defect clustering requires a richer future snapshot that stores per-qubit classes and coupling-map adjacency.",
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_translation()
    write_report(payload)
    print(f"HQA backend health translator written: {REPORT_PATH}")
    print(f"- backends translated: {payload['backend_count']}")
    print(f"- jobs submitted: {payload['jobs_submitted']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
