"""Replay an HQA field map into bounded shadow response artifacts.

Field Map Replay V0 consumes the richer qubit/edge neighborhood map and
produces a reviewable quarantine/reroute/intervention packet. It does not
execute routes, submit provider jobs, change pulses, or call HAL.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
FIELD_MAP_PATH = HQA_V2_ROOT / "logs" / "ibm_backend_field_map_v0.json"
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "field_map_replay_v0"
JSON_PATH = HQA_V2_ROOT / "logs" / "field_map_replay_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_FIELD_MAP_REPLAY_V0.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qubit_risk(qubit: dict[str, Any], degraded_edge_count: int) -> float:
    reasons = qubit.get("reasons", [])
    base = 0.20 * len(reasons)
    if "high_readout_error" in reasons:
        base += 0.15
    if "weak_t1" in reasons or "weak_t2" in reasons:
        base += 0.12
    base += min(0.25, degraded_edge_count * 0.08)
    return round(max(0.0, min(1.0, base)), 6)


def edge_counts(edges: list[dict[str, Any]]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for edge in edges:
        if edge.get("status") != "degraded_neighborhood":
            continue
        counts[int(edge["source"])] = counts.get(int(edge["source"]), 0) + 1
        counts[int(edge["target"])] = counts.get(int(edge["target"]), 0) + 1
    return counts


def rank_qubits(field_map: dict[str, Any]) -> list[dict[str, Any]]:
    counts = edge_counts(field_map.get("edges", []))
    ranked = []
    for qubit in field_map.get("qubits", []):
        index = int(qubit["index"])
        degraded_edges = counts.get(index, 0)
        risk = qubit_risk(qubit, degraded_edges)
        if qubit.get("status") == "degraded" or degraded_edges:
            ranked.append(
                {
                    "qubit_id": f"Q_{index}",
                    "index": index,
                    "status": qubit.get("status"),
                    "reasons": qubit.get("reasons", []),
                    "degraded_neighborhood_edges": degraded_edges,
                    "risk_score": risk,
                }
            )
    ranked.sort(key=lambda item: (item["risk_score"], item["degraded_neighborhood_edges"]), reverse=True)
    return ranked


def intervention_mode(summary: dict[str, Any], ranked: list[dict[str, Any]]) -> str:
    degraded_fraction = float(summary.get("degraded_fraction") or 0.0)
    largest_component = int(summary.get("largest_degraded_component") or 0)
    max_risk = float(ranked[0]["risk_score"]) if ranked else 0.0
    if degraded_fraction >= 0.35 or largest_component >= 3 or max_risk >= 0.70:
        return "QUARANTINE_REMAP_SHADOW"
    if degraded_fraction >= 0.20 or max_risk >= 0.45:
        return "MONITOR_WITH_SHADOW_OPTIMIZATION"
    return "NO_INTERVENTION"


def build_replay(field_map: dict[str, Any]) -> dict[str, Any]:
    ranked = rank_qubits(field_map)
    summary = field_map.get("summary", {})
    mode = intervention_mode(summary, ranked)
    targets = [item["qubit_id"] for item in ranked[:3]]
    avoided_edges = [
        {"source": f"Q_{edge['source']}", "target": f"Q_{edge['target']}", "coupling_risk": edge["coupling_risk"]}
        for edge in field_map.get("edges", [])
        if edge.get("status") == "degraded_neighborhood"
    ]
    return {
        "schema_version": "hqa.field_map_replay.v0",
        "execution_mode": "shadow_replay_only",
        "source_backend": field_map.get("source_backend"),
        "source_collection_mode": field_map.get("collection_mode"),
        "hardware_authority": False,
        "jobs_submitted": 0,
        "field_map_summary": summary,
        "ranked_quarantine_candidates": ranked,
        "recommended_targets": targets,
        "avoided_edge_neighborhoods": avoided_edges,
        "intervention_mode": mode,
        "review_packet": {
            "quarantine_review_required": bool(targets),
            "reroute_review_required": bool(avoided_edges),
            "operator_review_required": mode != "NO_INTERVENTION",
            "reason": "Field-map replay converts damaged neighborhoods into shadow review only.",
        },
        "boundary": "Field Map Replay V0 produces review artifacts only. It submits zero jobs, runs zero circuits, changes no routing table or pulses, and grants no HAL authority.",
    }


def artifact_payloads(replay: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "01_quarantine_candidates.json": {
            "schema_version": "hqa.field_map_quarantine_candidates.v0",
            "authority": "shadow_review",
            "source_backend": replay["source_backend"],
            "recommended_targets": replay["recommended_targets"],
            "ranked_candidates": replay["ranked_quarantine_candidates"],
            "hardware_authority": False,
        },
        "02_reroute_review.json": {
            "schema_version": "hqa.field_map_reroute_review.v0",
            "execution_mode": "shadow_review",
            "source_backend": replay["source_backend"],
            "avoid_targets": replay["recommended_targets"],
            "avoid_edge_neighborhoods": replay["avoided_edge_neighborhoods"],
            "requires_operator_review": replay["review_packet"]["reroute_review_required"],
            "hardware_authority": False,
        },
        "03_intervention_hint.json": {
            "schema_version": "hqa.field_map_intervention_hint.v0",
            "execution_mode": "shadow_replay_only",
            "source_backend": replay["source_backend"],
            "intervention_mode": replay["intervention_mode"],
            "operator_review_required": replay["review_packet"]["operator_review_required"],
            "hardware_authority": False,
            "jobs_submitted": 0,
        },
    }


def manifest(paths: list[Path]) -> str:
    return "\n".join(f"{sha256(path)}  {path.name}" for path in sorted(paths)) + "\n"


def write_outputs(replay: dict[str, Any]) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    JSON_PATH.write_text(json.dumps(replay, indent=2), encoding="utf-8")
    payloads = artifact_payloads(replay)
    paths = []
    for filename, payload in payloads.items():
        path = OUTPUT_ROOT / filename
        write_json(path, payload)
        paths.append(path)
    manifest_path = OUTPUT_ROOT / "MANIFEST_SHA256.txt"
    manifest_path.write_text(manifest(paths), encoding="utf-8")

    lines = [
        "# HQA Field Map Replay V0",
        "",
        "## Purpose",
        "",
        "This report replays an IBM-style field map into bounded shadow quarantine and reroute review artifacts.",
        "",
        "## Summary",
        "",
        f"- Source backend: `{replay['source_backend']}`",
        f"- Source collection mode: `{replay['source_collection_mode']}`",
        f"- Execution mode: `{replay['execution_mode']}`",
        f"- Hardware authority: `{replay['hardware_authority']}`",
        f"- Jobs submitted: `{replay['jobs_submitted']}`",
        f"- Intervention mode: `{replay['intervention_mode']}`",
        f"- Recommended targets: `{', '.join(replay['recommended_targets']) or '-'}`",
        f"- Avoided edge neighborhoods: `{len(replay['avoided_edge_neighborhoods'])}`",
        "",
        "## Top Candidates",
        "",
        "| Rank | Qubit | Status | Reasons | Degraded Edges | Risk Score |",
        "|---:|---|---|---|---:|---:|",
    ]
    for rank, item in enumerate(replay["ranked_quarantine_candidates"][:8], start=1):
        lines.append(
            f"| {rank} | `{item['qubit_id']}` | `{item['status']}` | `{', '.join(item['reasons']) or '-'}` | `{item['degraded_neighborhood_edges']}` | `{item['risk_score']}` |"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `01_quarantine_candidates.json`",
            "- `02_reroute_review.json`",
            "- `03_intervention_hint.json`",
            "- `MANIFEST_SHA256.txt`",
            "",
            "## Boundary",
            "",
            replay["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not FIELD_MAP_PATH.exists():
        print(f"Field map replay missing input: {FIELD_MAP_PATH}")
        return 1
    field_map = load_json(FIELD_MAP_PATH)
    replay = build_replay(field_map)
    write_outputs(replay)
    print(f"HQA field map replay written: {REPORT_PATH}")
    print(f"- intervention mode: {replay['intervention_mode']}")
    print(f"- targets: {', '.join(replay['recommended_targets']) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
