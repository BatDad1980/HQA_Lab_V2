"""Run a deterministic HQA simulator stress schedule.

This schedule exercises the risk-field/proposal chain across four profiles:
nominal, mild stress, correlated stress, and no-route hold. It is a local
evidence generator only; it does not submit backend jobs or issue HAL actions.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "simulator_stress_schedule_v0"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_SIMULATOR_STRESS_SCHEDULE_V0.md"


@dataclass(frozen=True)
class StressScenario:
    name: str
    degraded_node: str
    correlated_node: str | None
    coherence: dict[str, float]
    coupling: dict[tuple[str, str], float]
    syndrome_confidence: float
    decoder_signal: str
    nominal_cascade_rate: float
    stress_cascade_rate: float
    route_available: bool
    expected_action: str


@dataclass
class ScenarioResult:
    scenario: str
    suspected_patch: str
    cascade_contrast: float
    top_risk_score: float
    top_risk_band: str
    advisory_action: str
    hardware_authority: bool
    route_available: bool
    proposal_mode: str
    output_dir: str


BASE_NODES = [
    {"node_id": "Q_0", "role": "data"},
    {"node_id": "Q_1", "role": "data"},
    {"node_id": "Q_2", "role": "ancilla"},
    {"node_id": "Q_3", "role": "readout"},
]


SCENARIOS = [
    StressScenario(
        name="nominal",
        degraded_node="Q_1",
        correlated_node=None,
        coherence={"Q_0": 0.97, "Q_1": 0.93, "Q_2": 0.96, "Q_3": 0.94},
        coupling={("Q_0", "Q_1"): 0.91, ("Q_0", "Q_2"): 0.93, ("Q_2", "Q_3"): 0.88},
        syndrome_confidence=0.12,
        decoder_signal="LOW_ACTIVITY_HISTORY",
        nominal_cascade_rate=0.027344,
        stress_cascade_rate=0.042969,
        route_available=True,
        expected_action="MONITOR_ONLY",
    ),
    StressScenario(
        name="mild_stress",
        degraded_node="Q_1",
        correlated_node="Q_0",
        coherence={"Q_0": 0.95, "Q_1": 0.72, "Q_2": 0.95, "Q_3": 0.93},
        coupling={("Q_0", "Q_1"): 0.84, ("Q_0", "Q_2"): 0.92, ("Q_2", "Q_3"): 0.87},
        syndrome_confidence=0.54,
        decoder_signal="WATCHLIST_HISTORY",
        nominal_cascade_rate=0.027344,
        stress_cascade_rate=0.28125,
        route_available=True,
        expected_action="MONITOR_WITH_ROUTE_REVIEW",
    ),
    StressScenario(
        name="correlated_stress",
        degraded_node="Q_1",
        correlated_node="Q_0",
        coherence={"Q_0": 0.91, "Q_1": 0.42, "Q_2": 0.94, "Q_3": 0.93},
        coupling={("Q_0", "Q_1"): 0.81, ("Q_0", "Q_2"): 0.93, ("Q_2", "Q_3"): 0.88},
        syndrome_confidence=0.91,
        decoder_signal="CASCADE_LIKE_HISTORY",
        nominal_cascade_rate=0.027344,
        stress_cascade_rate=0.914062,
        route_available=True,
        expected_action="ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL",
    ),
    StressScenario(
        name="no_route_hold",
        degraded_node="Q_1",
        correlated_node="Q_0",
        coherence={"Q_0": 0.62, "Q_1": 0.33, "Q_2": 0.51, "Q_3": 0.49},
        coupling={("Q_0", "Q_1"): 0.44, ("Q_0", "Q_2"): 0.38, ("Q_2", "Q_3"): 0.36},
        syndrome_confidence=0.96,
        decoder_signal="CASCADE_LIKE_HISTORY",
        nominal_cascade_rate=0.027344,
        stress_cascade_rate=0.96875,
        route_available=False,
        expected_action="NO_ROUTE_HOLD_REVIEW",
    ),
]


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def risk_band(score: float) -> str:
    if score >= 0.85:
        return "critical"
    if score >= 0.65:
        return "high"
    if score >= 0.35:
        return "elevated"
    return "low"


def advisory_action(max_score: float, cascade_contrast: float, route_available: bool) -> str:
    if not route_available:
        return "NO_ROUTE_HOLD_REVIEW"
    if max_score >= 0.85:
        return "ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL"
    if max_score >= 0.65:
        return "QUARANTINE_PROPOSAL"
    if max_score >= 0.35 or cascade_contrast >= 0.20:
        return "MONITOR_WITH_ROUTE_REVIEW"
    return "MONITOR_ONLY"


def topology_for(scenario: StressScenario) -> dict[str, Any]:
    nodes = []
    for node in BASE_NODES:
        node_id = node["node_id"]
        nodes.append(
            {
                "node_id": node_id,
                "role": node["role"],
                "status": "degraded" if node_id == scenario.degraded_node else "healthy",
                "coherence_score": scenario.coherence[node_id],
            }
        )
    edges = [
        {"source": source, "target": target, "coupling_score": score}
        for (source, target), score in scenario.coupling.items()
    ]
    return {
        "schema_version": "hqa.topology_snapshot.v1",
        "snapshot_id": f"TOPO-SCHEDULE-{scenario.name.upper()}",
        "timestamp_utc": "2026-06-01T00:00:00Z",
        "nodes": nodes,
        "edges": edges,
    }


def syndrome_for(scenario: StressScenario) -> dict[str, Any]:
    return {
        "schema_version": "hqa.syndrome_record.v1",
        "record_id": f"SYN-SCHEDULE-{scenario.name.upper()}",
        "cycle": 3,
        "source_lane": "simulator_stress_schedule_v0",
        "syndrome_bits": "1110" if scenario.decoder_signal == "CASCADE_LIKE_HISTORY" else "0100",
        "seed_error": scenario.degraded_node,
        "correlated_error": scenario.correlated_node,
        "decoder_signal": scenario.decoder_signal,
        "confidence": scenario.syndrome_confidence,
    }


def coupling_fragility(node_id: str, edges: list[dict[str, Any]]) -> float:
    connected = [edge for edge in edges if edge["source"] == node_id or edge["target"] == node_id]
    if not connected:
        return 0.25
    return clamp(1.0 - min(float(edge["coupling_score"]) for edge in connected))


def node_risks(scenario: StressScenario, topology: dict[str, Any], syndrome: dict[str, Any]) -> list[dict[str, Any]]:
    cascade_contrast = max(0.0, scenario.stress_cascade_rate - scenario.nominal_cascade_rate)
    syndrome_targets = {scenario.degraded_node}
    if scenario.correlated_node:
        syndrome_targets.add(scenario.correlated_node)
    cascade_boost = clamp(cascade_contrast) * 0.18
    nodes = []
    for node in topology["nodes"]:
        node_id = node["node_id"]
        coherence = float(node["coherence_score"])
        fragility = coupling_fragility(node_id, topology["edges"])
        pressure = 0.0
        if syndrome["seed_error"] == node_id:
            pressure += 0.36 * scenario.syndrome_confidence
        if syndrome.get("correlated_error") == node_id:
            pressure += 0.22 * scenario.syndrome_confidence
        if scenario.decoder_signal == "CASCADE_LIKE_HISTORY":
            pressure += 0.10
        elif scenario.decoder_signal == "WATCHLIST_HISTORY":
            pressure += 0.05
        status_penalty = 0.14 if node["status"] == "degraded" else 0.0
        node_cascade_pressure = cascade_boost if node_id in syndrome_targets else cascade_boost * 0.35
        score = clamp(
            ((1.0 - coherence) * 0.34)
            + (fragility * 0.16)
            + clamp(pressure)
            + status_penalty
            + node_cascade_pressure
        )
        nodes.append(
            {
                "node_id": node_id,
                "role": node["role"],
                "status": node["status"],
                "coherence_score": round(coherence, 6),
                "coupling_fragility": round(fragility, 6),
                "syndrome_pressure": round(clamp(pressure), 6),
                "cascade_pressure": round(node_cascade_pressure, 6),
                "risk_score": round(score, 6),
                "risk_band": risk_band(score),
            }
        )
    return sorted(nodes, key=lambda item: item["risk_score"], reverse=True)


def risk_field_for(scenario: StressScenario, topology: dict[str, Any], syndrome: dict[str, Any]) -> dict[str, Any]:
    nodes = node_risks(scenario, topology, syndrome)
    cascade_contrast = max(0.0, scenario.stress_cascade_rate - scenario.nominal_cascade_rate)
    top_score = nodes[0]["risk_score"]
    return {
        "schema_version": "hqa.stress_schedule_risk_field.v0",
        "field_id": f"RISK-SCHEDULE-{scenario.name.upper()}",
        "scenario": scenario.name,
        "execution_mode": "shadow_advisory",
        "hardware_authority": False,
        "route_available": scenario.route_available,
        "cascade_contrast": round(cascade_contrast, 6),
        "suspected_patch": nodes[0]["node_id"],
        "recommended_advisory_action": advisory_action(top_score, cascade_contrast, scenario.route_available),
        "nodes": nodes,
        "boundary": "Stress schedule advisory only; no backend job, pulse change, quarantine command, or HAL execution is authorized.",
    }


def proposal_for(risk_field: dict[str, Any]) -> dict[str, Any]:
    action = risk_field["recommended_advisory_action"]
    target = risk_field["suspected_patch"]
    return {
        "schema_version": "hqa.stress_schedule_proposal.v0",
        "proposal_id": f"PROPOSAL-SCHEDULE-{risk_field['scenario'].upper()}",
        "scenario": risk_field["scenario"],
        "target": target,
        "recommended_advisory_action": action,
        "execution_mode": "shadow_advisory" if action != "NO_ROUTE_HOLD_REVIEW" else "blocked",
        "requires_vendor_review": True,
        "requires_human_approval": True,
        "hardware_authority": False,
        "review_packet": {
            "quarantine_review": action in {"QUARANTINE_PROPOSAL", "ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL", "NO_ROUTE_HOLD_REVIEW"},
            "reroute_review": action in {"MONITOR_WITH_ROUTE_REVIEW", "ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL", "NO_ROUTE_HOLD_REVIEW"},
            "hal_dry_run_review": action != "MONITOR_ONLY",
        },
        "boundary": "Proposal only. It does not modify topology, issue HAL commands, or authorize live hardware action.",
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_report(results: list[ScenarioResult]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Simulator Stress Schedule V0",
        "",
        "## Purpose",
        "",
        "This report runs deterministic local stress profiles through the HQA risk-field and shadow-proposal chain.",
        "",
        "The schedule is intended to show control-flow behavior across multiple conditions. It does not submit backend jobs or authorize hardware action.",
        "",
        "## Results",
        "",
        "| Scenario | Suspected Patch | Cascade Contrast | Top Risk | Band | Advisory Action | Proposal Mode |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for result in results:
        lines.append(
            f"| `{result.scenario}` | `{result.suspected_patch}` | `{result.cascade_contrast}` | `{result.top_risk_score}` | `{result.top_risk_band}` | `{result.advisory_action}` | `{result.proposal_mode}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Simulator Stress Schedule V0 is a deterministic local evidence schedule. It does not validate physical quantum hardware, production QEC performance, or live HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_schedule() -> list[ScenarioResult]:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    results: list[ScenarioResult] = []
    manifest_lines: list[str] = []

    for scenario in SCENARIOS:
        scenario_dir = OUTPUT_ROOT / scenario.name
        scenario_dir.mkdir(parents=True, exist_ok=True)
        topology = topology_for(scenario)
        syndrome = syndrome_for(scenario)
        risk_field = risk_field_for(scenario, topology, syndrome)
        proposal = proposal_for(risk_field)

        paths = {
            "topology": scenario_dir / "01_topology_snapshot.json",
            "syndrome": scenario_dir / "02_syndrome_record.json",
            "risk_field": scenario_dir / "03_risk_field.json",
            "proposal": scenario_dir / "04_shadow_proposal.json",
        }
        write_json(paths["topology"], topology)
        write_json(paths["syndrome"], syndrome)
        write_json(paths["risk_field"], risk_field)
        write_json(paths["proposal"], proposal)
        for path in paths.values():
            manifest_lines.append(f"{sha256(path)}  {path.relative_to(OUTPUT_ROOT)}")

        top = risk_field["nodes"][0]
        results.append(
            ScenarioResult(
                scenario=scenario.name,
                suspected_patch=risk_field["suspected_patch"],
                cascade_contrast=risk_field["cascade_contrast"],
                top_risk_score=top["risk_score"],
                top_risk_band=top["risk_band"],
                advisory_action=risk_field["recommended_advisory_action"],
                hardware_authority=risk_field["hardware_authority"] or proposal["hardware_authority"],
                route_available=scenario.route_available,
                proposal_mode=proposal["execution_mode"],
                output_dir=str(scenario_dir.relative_to(HQA_V2_ROOT)),
            )
        )

    (OUTPUT_ROOT / "MANIFEST_SHA256.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    summary = {"schema_version": "hqa.simulator_stress_schedule.v0", "results": [asdict(result) for result in results]}
    write_json(OUTPUT_ROOT / "schedule_summary.json", summary)
    write_report(results)
    return results


def main() -> int:
    results = build_schedule()
    print(f"HQA simulator stress schedule written: {OUTPUT_ROOT}")
    for result in results:
        print(f"- {result.scenario}: {result.advisory_action} on {result.suspected_patch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
