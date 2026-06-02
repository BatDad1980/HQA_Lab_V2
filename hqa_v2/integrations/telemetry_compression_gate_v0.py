"""Telemetry Compression Gate V0.

Compresses large quantum telemetry payloads into bounded risk features before
any cognitive advisory layer sees them. The gate verifies that compression
preserves HQA intervention decisions while reducing payload size.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "telemetry_compression_gate_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_TELEMETRY_COMPRESSION_GATE_V0.md"

FEEDBACK_BUDGET_MS = 250.0


@dataclass(frozen=True)
class CompressionScenario:
    scenario_id: str
    title: str
    node_count: int
    degraded_count: int
    active_parity_count: int
    visual_threat_mass: int
    baseline_latency_ms: float
    expected_decision: str


@dataclass(frozen=True)
class CompressionResult:
    scenario_id: str
    title: str
    raw_bytes: int
    compressed_bytes: int
    compression_ratio: float
    degraded_fraction: float
    syndrome_fraction: float
    visual_risk: float
    raw_decision: str
    compressed_decision: str
    decision_preserved: bool
    estimated_compressed_latency_ms: float
    under_budget: bool
    hardware_authority: bool


SCENARIOS = [
    CompressionScenario(
        scenario_id="TCG-001",
        title="Stable small packet",
        node_count=64,
        degraded_count=2,
        active_parity_count=1,
        visual_threat_mass=0,
        baseline_latency_ms=90.0,
        expected_decision="ACCEPT_ANNOTATION",
    ),
    CompressionScenario(
        scenario_id="TCG-002",
        title="Moderate device drift",
        node_count=256,
        degraded_count=48,
        active_parity_count=35,
        visual_threat_mass=1200,
        baseline_latency_ms=310.0,
        expected_decision="MONITOR_WITH_ROUTE_REVIEW",
    ),
    CompressionScenario(
        scenario_id="TCG-003",
        title="Cognitive overload monster payload",
        node_count=1000,
        degraded_count=500,
        active_parity_count=1000,
        visual_threat_mass=99_999_999,
        baseline_latency_ms=1242.0,
        expected_decision="QUARANTINE_REMAP_REVIEW",
    ),
    CompressionScenario(
        scenario_id="TCG-004",
        title="Collapse payload",
        node_count=1000,
        degraded_count=950,
        active_parity_count=1000,
        visual_threat_mass=99_999_999,
        baseline_latency_ms=1330.0,
        expected_decision="SAFE_HOLD",
    ),
]


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def build_raw_payload(scenario: CompressionScenario) -> dict[str, Any]:
    nodes = []
    for idx in range(scenario.node_count):
        degraded = idx < scenario.degraded_count
        nodes.append(
            {
                "node_id": f"Q_{idx}",
                "status": "degraded" if degraded else "stable",
                "coherence_score": 0.41 if degraded else 0.91,
                "readout_error": 0.052 if degraded else 0.018,
                "t1_us": 71.0 if degraded else 188.0,
                "t2_us": 35.0 if degraded else 106.0,
            }
        )
    syndrome = [{"cycle": idx, "active": idx < scenario.active_parity_count} for idx in range(scenario.node_count)]
    return {
        "schema_version": "hqa.raw_telemetry_packet.v0",
        "scenario_id": scenario.scenario_id,
        "nodes": nodes,
        "syndrome": syndrome,
        "world_state": {
            "visual_threat_mass": scenario.visual_threat_mass,
            "environment": "stress_replay",
        },
        "hardware_authority": False,
    }


def summarize(payload: dict[str, Any]) -> dict[str, Any]:
    nodes = payload["nodes"]
    syndrome = payload["syndrome"]
    node_count = len(nodes)
    degraded = [node for node in nodes if node.get("status") == "degraded"]
    active = [item for item in syndrome if item.get("active")]
    mean_readout = sum(float(node["readout_error"]) for node in nodes) / node_count if node_count else 0.0
    mean_coherence = sum(float(node["coherence_score"]) for node in nodes) / node_count if node_count else 0.0
    visual_mass = int(payload.get("world_state", {}).get("visual_threat_mass", 0))
    visual_risk = clamp(visual_mass / 10_000.0)
    degraded_fraction = len(degraded) / node_count if node_count else 0.0
    syndrome_fraction = len(active) / len(syndrome) if syndrome else 0.0
    risk_score = clamp((degraded_fraction * 0.42) + (syndrome_fraction * 0.32) + (visual_risk * 0.20) + (mean_readout * 0.06))
    return {
        "schema_version": "hqa.compressed_telemetry_summary.v0",
        "scenario_id": payload["scenario_id"],
        "node_count": node_count,
        "degraded_count": len(degraded),
        "degraded_fraction": round(degraded_fraction, 6),
        "active_syndrome_count": len(active),
        "syndrome_fraction": round(syndrome_fraction, 6),
        "mean_readout_error": round(mean_readout, 6),
        "mean_coherence_score": round(mean_coherence, 6),
        "visual_risk": round(visual_risk, 6),
        "risk_score": round(risk_score, 6),
        "hardware_authority": False,
        "retained_features": [
            "node_count",
            "degraded_fraction",
            "syndrome_fraction",
            "mean_readout_error",
            "mean_coherence_score",
            "visual_risk",
            "risk_score",
        ],
    }


def decide_from_features(degraded_fraction: float, syndrome_fraction: float, visual_risk: float, risk_score: float) -> str:
    if degraded_fraction >= 0.90 or (syndrome_fraction >= 0.95 and risk_score >= 0.90):
        return "SAFE_HOLD"
    if degraded_fraction >= 0.45 or syndrome_fraction >= 0.75 or visual_risk >= 0.75:
        return "QUARANTINE_REMAP_REVIEW"
    if degraded_fraction >= 0.15 or syndrome_fraction >= 0.12 or risk_score >= 0.25:
        return "MONITOR_WITH_ROUTE_REVIEW"
    return "ACCEPT_ANNOTATION"


def estimate_latency(raw_latency_ms: float, raw_bytes: int, compressed_bytes: int) -> float:
    if raw_bytes <= 0:
        return raw_latency_ms
    transport_ratio = compressed_bytes / raw_bytes
    # Keep a small fixed reasoning floor; the rest scales with payload size.
    return round(60.0 + ((raw_latency_ms - 60.0) * transport_ratio), 3)


def run_scenario(scenario: CompressionScenario) -> CompressionResult:
    raw = build_raw_payload(scenario)
    summary = summarize(raw)
    raw_json = json.dumps(raw, sort_keys=True)
    compressed_json = json.dumps(summary, sort_keys=True)
    raw_bytes = len(raw_json.encode("utf-8"))
    compressed_bytes = len(compressed_json.encode("utf-8"))
    compression_ratio = raw_bytes / compressed_bytes if compressed_bytes else 0.0
    raw_decision = decide_from_features(
        scenario.degraded_count / scenario.node_count,
        scenario.active_parity_count / scenario.node_count,
        clamp(scenario.visual_threat_mass / 10_000.0),
        float(summary["risk_score"]),
    )
    compressed_decision = decide_from_features(
        float(summary["degraded_fraction"]),
        float(summary["syndrome_fraction"]),
        float(summary["visual_risk"]),
        float(summary["risk_score"]),
    )
    estimated_latency = estimate_latency(scenario.baseline_latency_ms, raw_bytes, compressed_bytes)
    return CompressionResult(
        scenario_id=scenario.scenario_id,
        title=scenario.title,
        raw_bytes=raw_bytes,
        compressed_bytes=compressed_bytes,
        compression_ratio=round(compression_ratio, 3),
        degraded_fraction=float(summary["degraded_fraction"]),
        syndrome_fraction=float(summary["syndrome_fraction"]),
        visual_risk=float(summary["visual_risk"]),
        raw_decision=raw_decision,
        compressed_decision=compressed_decision,
        decision_preserved=raw_decision == compressed_decision == scenario.expected_decision,
        estimated_compressed_latency_ms=estimated_latency,
        under_budget=estimated_latency <= FEEDBACK_BUDGET_MS,
        hardware_authority=False,
    )


def run_gate() -> dict[str, Any]:
    results = [run_scenario(scenario) for scenario in SCENARIOS]
    return {
        "schema_version": "hqa.telemetry_compression_gate.v0",
        "execution_mode": "shadow_compression_gate",
        "hardware_authority": False,
        "feedback_budget_ms": FEEDBACK_BUDGET_MS,
        "scenario_count": len(results),
        "results": [asdict(result) for result in results],
        "boundary": "Telemetry compression summarizes evidence for advisory review only. It does not authorize live hardware control, backend jobs, pulse changes, or HAL dispatch.",
    }


def write_report(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Telemetry Compression Gate V0",
        "",
        "## Purpose",
        "",
        "This report verifies that large telemetry payloads can be compressed into bounded risk features before cognitive advisory review.",
        "",
        "The gate checks that compression reduces payload size, preserves the intervention decision, and keeps estimated advisory latency within the feedback budget.",
        "",
        "## Results",
        "",
        "| Scenario | Raw Bytes | Compressed Bytes | Ratio | Raw Decision | Compressed Decision | Preserved | Estimated Latency | Under Budget |",
        "|---|---:|---:|---:|---|---|---:|---:|---:|",
    ]
    for result in payload["results"]:
        lines.append(
            f"| `{result['scenario_id']}` {result['title']} | `{result['raw_bytes']}` | `{result['compressed_bytes']}` | `{result['compression_ratio']}` | `{result['raw_decision']}` | `{result['compressed_decision']}` | `{result['decision_preserved']}` | `{result['estimated_compressed_latency_ms']}` | `{result['under_budget']}` |"
        )
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
    payload = run_gate()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_report(payload)
    print(f"HQA telemetry compression gate written: {OUTPUT_PATH}")
    print(f"HQA telemetry compression report written: {REPORT_PATH}")
    for result in payload["results"]:
        print(
            f"- {result['scenario_id']}: {result['compression_ratio']}x, "
            f"{result['compressed_decision']}, {result['estimated_compressed_latency_ms']} ms"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
