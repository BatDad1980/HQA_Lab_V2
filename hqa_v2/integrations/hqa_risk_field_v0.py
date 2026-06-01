"""Generate an HQA-native cascade risk field from local evidence.

The risk field is an advisory layer. It ranks topology nodes by local
coherence, coupling fragility, syndrome evidence, and simulator cascade
contrast. It does not authorize hardware execution or live pulse changes.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = HQA_V2_ROOT / "outputs" / "vendor_shadow_packet_v1"
TOPOLOGY_PATH = PACKET_ROOT / "01_topology_snapshot.json"
SYNDROME_PATH = PACKET_ROOT / "02_syndrome_record.json"
AER_SUMMARY_PATH = HQA_V2_ROOT / "logs" / "qiskit_aer_cascade_noise_probe.json"
JSON_PATH = HQA_V2_ROOT / "logs" / "hqa_risk_field_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_RISK_FIELD_V0.md"


@dataclass
class NodeRisk:
    node_id: str
    role: str
    status: str
    coherence_score: float
    coupling_fragility: float
    syndrome_pressure: float
    cascade_pressure: float
    risk_score: float
    risk_band: str
    evidence: list[str]


@dataclass
class RiskField:
    schema_version: str
    field_id: str
    execution_mode: str
    hardware_authority: bool
    source_topology: str
    source_syndrome: str
    cascade_contrast: float
    suspected_patch: str
    recommended_advisory_action: str
    nodes: list[NodeRisk]
    boundary: str


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def advisory_action(max_score: float, cascade_contrast: float) -> str:
    if max_score >= 0.85:
        return "ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL"
    if max_score >= 0.65:
        return "QUARANTINE_PROPOSAL"
    if max_score >= 0.35 or cascade_contrast >= 0.40:
        return "MONITOR_WITH_ROUTE_REVIEW"
    return "MONITOR_ONLY"


def cascade_rates() -> tuple[float, float, float]:
    if not AER_SUMMARY_PATH.exists():
        return 0.0, 0.0, 0.0
    payload = load_json(AER_SUMMARY_PATH)
    summaries = {item.get("profile"): item for item in payload.get("summaries", [])}
    nominal = float(summaries.get("nominal", {}).get("cascade_like_rate", 0.0))
    stress = float(summaries.get("stress", {}).get("cascade_like_rate", 0.0))
    return nominal, stress, max(0.0, stress - nominal)


def coupling_fragility(node_id: str, edges: list[dict[str, Any]]) -> tuple[float, list[str]]:
    connected = [edge for edge in edges if edge.get("source") == node_id or edge.get("target") == node_id]
    if not connected:
        return 0.25, ["topology: isolated or unconnected in sample graph"]
    weakest = min(float(edge.get("coupling_score", 1.0)) for edge in connected)
    fragility = clamp(1.0 - weakest)
    evidence = [f"topology: weakest coupling `{weakest:.2f}`"]
    return fragility, evidence


def syndrome_pressure(node_id: str, syndrome: dict[str, Any]) -> tuple[float, list[str]]:
    pressure = 0.0
    evidence: list[str] = []
    confidence = float(syndrome.get("confidence", 0.0))
    if syndrome.get("seed_error") == node_id:
        pressure += 0.36 * confidence
        evidence.append(f"syndrome: seed_error at `{node_id}` confidence `{confidence:.2f}`")
    if syndrome.get("correlated_error") == node_id:
        pressure += 0.22 * confidence
        evidence.append(f"syndrome: correlated_error at `{node_id}` confidence `{confidence:.2f}`")
    if syndrome.get("decoder_signal") == "CASCADE_LIKE_HISTORY":
        pressure += 0.10
        evidence.append("syndrome: cascade-like decoder signal")
    return clamp(pressure), evidence


def build_risk_field() -> RiskField:
    topology = load_json(TOPOLOGY_PATH)
    syndrome = load_json(SYNDROME_PATH)
    nominal_rate, stress_rate, cascade_contrast = cascade_rates()

    syndrome_targets = {
        value
        for value in [syndrome.get("seed_error"), syndrome.get("correlated_error")]
        if isinstance(value, str)
    }
    cascade_boost = clamp(cascade_contrast) * 0.18
    nodes: list[NodeRisk] = []

    for node in topology.get("nodes", []):
        node_id = str(node["node_id"])
        status = str(node.get("status", "unknown"))
        coherence = float(node.get("coherence_score", 0.0))
        role = str(node.get("role", "unknown"))

        fragility, topology_evidence = coupling_fragility(node_id, topology.get("edges", []))
        pressure, syndrome_evidence = syndrome_pressure(node_id, syndrome)
        status_penalty = 0.14 if status == "degraded" else 0.0
        coherence_pressure = clamp(1.0 - coherence)
        node_cascade_pressure = cascade_boost if node_id in syndrome_targets else cascade_boost * 0.35

        score = clamp(
            (coherence_pressure * 0.34)
            + (fragility * 0.16)
            + pressure
            + status_penalty
            + node_cascade_pressure
        )
        evidence = [
            f"coherence: `{coherence:.2f}`",
            f"status: `{status}`",
            f"cascade contrast: stress `{stress_rate:.6f}` minus nominal `{nominal_rate:.6f}`",
        ]
        evidence.extend(topology_evidence)
        evidence.extend(syndrome_evidence or ["syndrome: no direct syndrome target evidence"])

        nodes.append(
            NodeRisk(
                node_id=node_id,
                role=role,
                status=status,
                coherence_score=round(coherence, 6),
                coupling_fragility=round(fragility, 6),
                syndrome_pressure=round(pressure, 6),
                cascade_pressure=round(node_cascade_pressure, 6),
                risk_score=round(score, 6),
                risk_band=risk_band(score),
                evidence=evidence,
            )
        )

    nodes.sort(key=lambda item: item.risk_score, reverse=True)
    max_score = nodes[0].risk_score if nodes else 0.0
    suspected_patch = nodes[0].node_id if nodes else "UNKNOWN"

    return RiskField(
        schema_version="hqa.risk_field.v0",
        field_id="RISK-FIELD-V0-001",
        execution_mode="shadow_advisory",
        hardware_authority=False,
        source_topology=str(TOPOLOGY_PATH.relative_to(HQA_V2_ROOT)),
        source_syndrome=str(SYNDROME_PATH.relative_to(HQA_V2_ROOT)),
        cascade_contrast=round(cascade_contrast, 6),
        suspected_patch=suspected_patch,
        recommended_advisory_action=advisory_action(max_score, cascade_contrast),
        nodes=nodes,
        boundary="Advisory risk ranking only; no live backend job, pulse change, quarantine command, or HAL execution is authorized.",
    )


def write_outputs(field: RiskField) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(field)
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# HQA Risk Field V0",
        "",
        "## Purpose",
        "",
        "This report converts HQA-native evidence into a bounded cascade-risk field.",
        "",
        "The field is designed to rank local risk and recommend shadow-mode review actions. It does not authorize physical hardware control.",
        "",
        "## Inputs",
        "",
        f"- Topology source: `{field.source_topology}`",
        f"- Syndrome source: `{field.source_syndrome}`",
        "- Cascade source: `logs/qiskit_aer_cascade_noise_probe.json`",
        "",
        "## Field Summary",
        "",
        f"- Execution mode: `{field.execution_mode}`",
        f"- Hardware authority: `{field.hardware_authority}`",
        f"- Cascade contrast: `{field.cascade_contrast}`",
        f"- Suspected patch: `{field.suspected_patch}`",
        f"- Recommended advisory action: `{field.recommended_advisory_action}`",
        "",
        "## Node Risk Ranking",
        "",
        "| Rank | Node | Role | Status | Coherence | Coupling Fragility | Syndrome Pressure | Cascade Pressure | Risk Score | Band |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for rank, node in enumerate(field.nodes, start=1):
        lines.append(
            f"| {rank} | `{node.node_id}` | `{node.role}` | `{node.status}` | `{node.coherence_score}` | `{node.coupling_fragility}` | `{node.syndrome_pressure}` | `{node.cascade_pressure}` | `{node.risk_score}` | `{node.risk_band}` |"
        )

    lines.extend(["", "## Evidence Notes", ""])
    for node in field.nodes:
        lines.append(f"### `{node.node_id}`")
        lines.append("")
        for item in node.evidence:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(
        [
            "## Boundary",
            "",
            field.boundary,
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    missing = [path for path in [TOPOLOGY_PATH, SYNDROME_PATH] if not path.exists()]
    if missing:
        print("HQA Risk Field V0: missing required inputs")
        for path in missing:
            print(f"- {path}")
        return 1

    field = build_risk_field()
    write_outputs(field)
    print(f"HQA risk field written: {REPORT_PATH}")
    print(f"- suspected patch: {field.suspected_patch}")
    print(f"- advisory action: {field.recommended_advisory_action}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
