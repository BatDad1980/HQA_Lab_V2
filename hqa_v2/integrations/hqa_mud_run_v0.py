"""HQA Mud Run V0.

This is a deterministic abuse/breakpoint harness for the clean HQA lab. It
does not try to prove the architecture always succeeds. It tries to find where
HQA stops, rejects, or demands review when inputs get hostile or physically
unusable.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "hqa_mud_run_v0"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_MUD_RUN_V0.md"


@dataclass(frozen=True)
class MudScenario:
    scenario_id: str
    title: str
    payload: dict[str, Any]
    expected_disposition: str
    expected_breakpoint: str


@dataclass(frozen=True)
class MudResult:
    scenario_id: str
    title: str
    disposition: str
    breakpoint: str
    reviewer_required: bool
    hardware_authority: bool
    reason: str


FORBIDDEN_SECRET_MARKERS = {"apikey", "api_key", "token", "password", "hunter2", "secret"}
SUPPORTED_FAMILIES = {"heavy_hex", "grid_lattice", "bosonic_cat", "neutral_graph"}


SCENARIOS = [
    MudScenario(
        scenario_id="MUD-001",
        title="Malformed vendor trace",
        payload={
            "schema_version": "hqa.external_trace.v0",
            "trace_id": "TRACE-MALFORMED-001",
            "vendor": "IBM",
            "topology_family": "heavy_hex",
            "nodes": [{"node_id": "Q0", "coherence_score": 1.4}],
            "edges": [],
            "hardware_authority": False,
        },
        expected_disposition="REJECT",
        expected_breakpoint="schema_bounds",
    ),
    MudScenario(
        scenario_id="MUD-002",
        title="Secret-bearing trace",
        payload={
            "schema_version": "hqa.external_trace.v0",
            "trace_id": "TRACE-SECRET-001",
            "vendor": "IBM",
            "topology_family": "heavy_hex",
            "provenance": "operator pasted IBM token=abc123 into notes",
            "hardware_authority": False,
        },
        expected_disposition="QUARANTINE",
        expected_breakpoint="secret_containment",
    ),
    MudScenario(
        scenario_id="MUD-003",
        title="Unsupported topology family",
        payload={
            "schema_version": "hqa.external_trace.v0",
            "trace_id": "TRACE-UNKNOWN-FAMILY-001",
            "vendor": "UnknownVendor",
            "topology_family": "magic_lattice",
            "provenance": "redacted synthetic packet",
            "hardware_authority": False,
        },
        expected_disposition="REVIEW_LOCK",
        expected_breakpoint="topology_compensation_gap",
    ),
    MudScenario(
        scenario_id="MUD-004",
        title="Live authority request",
        payload={
            "schema_version": "hqa.external_trace.v0",
            "trace_id": "TRACE-LIVE-AUTH-001",
            "vendor": "IBM",
            "topology_family": "heavy_hex",
            "requested_action": "dispatch_hal_cooling",
            "hardware_authority": True,
        },
        expected_disposition="SAFE_HOLD",
        expected_breakpoint="hardware_authority_boundary",
    ),
    MudScenario(
        scenario_id="MUD-005",
        title="No-route fabric collapse",
        payload={
            "schema_version": "hqa.route_trial.v0",
            "trace_id": "ROUTE-COLLAPSE-001",
            "topology_family": "grid_lattice",
            "nodes": [
                {"node_id": "Q_0", "status": "stable"},
                {"node_id": "Q_1", "status": "quarantined"},
                {"node_id": "Q_2", "status": "quarantined"},
                {"node_id": "Q_3", "status": "stable"},
            ],
            "edges": [{"source": "Q_0", "target": "Q_1"}, {"source": "Q_1", "target": "Q_2"}, {"source": "Q_2", "target": "Q_3"}],
            "hardware_authority": False,
        },
        expected_disposition="SAFE_HOLD",
        expected_breakpoint="no_route_available",
    ),
    MudScenario(
        scenario_id="MUD-006",
        title="Conflicting calibration snapshot",
        payload={
            "schema_version": "hqa.external_trace.v0",
            "trace_id": "TRACE-CONFLICT-001",
            "vendor": "IBM",
            "topology_family": "heavy_hex",
            "nodes": [
                {"node_id": "Q_7", "t1_us": 210.0, "status": "healthy"},
                {"node_id": "Q_7", "t1_us": 41.0, "status": "degraded"},
            ],
            "hardware_authority": False,
        },
        expected_disposition="REVIEW_LOCK",
        expected_breakpoint="conflicting_calibration",
    ),
    MudScenario(
        scenario_id="MUD-007",
        title="Valid but extreme cat profile",
        payload={
            "schema_version": "hqa.cat_solver_trace.v0",
            "trace_id": "CAT-EXTREME-001",
            "vendor": "AliceBobCandidate",
            "topology_family": "bosonic_cat",
            "alpha": 2.4,
            "parity_flip_rate": 0.94,
            "photon_loss_events": 87,
            "hardware_authority": False,
        },
        expected_disposition="SAFE_HOLD",
        expected_breakpoint="extreme_cat_noise",
    ),
    MudScenario(
        scenario_id="MUD-008",
        title="Clean harsh profile",
        payload={
            "schema_version": "hqa.external_trace.v0",
            "trace_id": "TRACE-HARSH-CLEAN-001",
            "vendor": "IBM",
            "topology_family": "heavy_hex",
            "provenance": "redacted calibration-derived telemetry",
            "nodes": [
                {"node_id": "Q_0", "coherence_score": 0.88, "status": "stable"},
                {"node_id": "Q_1", "coherence_score": 0.42, "status": "degraded"},
                {"node_id": "Q_2", "coherence_score": 0.83, "status": "stable"},
            ],
            "edges": [
                {"source": "Q_0", "target": "Q_2", "coupling_score": 0.77},
                {"source": "Q_2", "target": "Q_1", "coupling_score": 0.71},
            ],
            "hardware_authority": False,
        },
        expected_disposition="ACCEPT_SHADOW",
        expected_breakpoint="none",
    ),
]


def contains_secret(payload: Any) -> bool:
    text = json.dumps(payload, sort_keys=True).lower()
    return any(marker in text for marker in FORBIDDEN_SECRET_MARKERS)


def has_invalid_bounds(payload: dict[str, Any]) -> bool:
    for node in payload.get("nodes", []):
        for field in ["coherence_score", "coupling_score"]:
            if field in node:
                value = float(node[field])
                if value < 0.0 or value > 1.0:
                    return True
    for edge in payload.get("edges", []):
        if "coupling_score" in edge:
            value = float(edge["coupling_score"])
            if value < 0.0 or value > 1.0:
                return True
    return False


def has_conflicting_nodes(payload: dict[str, Any]) -> bool:
    seen: dict[str, dict[str, Any]] = {}
    for node in payload.get("nodes", []):
        node_id = node.get("node_id")
        if not node_id:
            continue
        if node_id in seen and seen[node_id] != node:
            return True
        seen[node_id] = node
    return False


def route_collapsed(payload: dict[str, Any]) -> bool:
    nodes = {node["node_id"]: node for node in payload.get("nodes", []) if "node_id" in node}
    if not nodes:
        return False
    stable = {node_id for node_id, node in nodes.items() if node.get("status") == "stable"}
    if len(stable) < 2:
        return True
    for edge in payload.get("edges", []):
        source = edge.get("source")
        target = edge.get("target")
        if source in stable and target in stable:
            return False
    return True


def evaluate(scenario: MudScenario) -> MudResult:
    payload = scenario.payload
    if contains_secret(payload):
        disposition = "QUARANTINE"
        breakpoint = "secret_containment"
        reviewer = True
        reason = "Payload contains secret-like material and cannot enter active evaluation."
    elif payload.get("hardware_authority") is True:
        disposition = "SAFE_HOLD"
        breakpoint = "hardware_authority_boundary"
        reviewer = True
        reason = "Payload requests live authority; HQA lab only permits shadow evidence."
    elif has_invalid_bounds(payload):
        disposition = "REJECT"
        breakpoint = "schema_bounds"
        reviewer = False
        reason = "Payload contains numeric values outside allowed physical score bounds."
    elif payload.get("topology_family") not in SUPPORTED_FAMILIES:
        disposition = "REVIEW_LOCK"
        breakpoint = "topology_compensation_gap"
        reviewer = True
        reason = "Topology family has no compensation profile."
    elif has_conflicting_nodes(payload):
        disposition = "REVIEW_LOCK"
        breakpoint = "conflicting_calibration"
        reviewer = True
        reason = "Calibration snapshot contains conflicting records for the same node."
    elif route_collapsed(payload):
        disposition = "SAFE_HOLD"
        breakpoint = "no_route_available"
        reviewer = True
        reason = "No valid stable path exists across the supplied topology."
    elif payload.get("schema_version") == "hqa.cat_solver_trace.v0" and float(payload.get("parity_flip_rate", 0.0)) > 0.90:
        disposition = "SAFE_HOLD"
        breakpoint = "extreme_cat_noise"
        reviewer = True
        reason = "Cat lane noise exceeds the current shadow proposal envelope."
    else:
        disposition = "ACCEPT_SHADOW"
        breakpoint = "none"
        reviewer = False
        reason = "Payload is harsh but bounded, redacted, and shadow-only."

    return MudResult(
        scenario_id=scenario.scenario_id,
        title=scenario.title,
        disposition=disposition,
        breakpoint=breakpoint,
        reviewer_required=reviewer,
        hardware_authority=False,
        reason=reason,
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_report(results: list[MudResult]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Mud Run V0",
        "",
        "## Purpose",
        "",
        "This report intentionally runs harsh, malformed, conflicting, and boundary-violating payloads through the HQA clean-lab intake logic.",
        "",
        "The goal is to identify where HQA stops, rejects, quarantines, or requires human review.",
        "",
        "## Results",
        "",
        "| Scenario | Disposition | Breakpoint | Reviewer Required | Hardware Authority |",
        "|---|---|---|---:|---:|",
    ]
    for result in results:
        lines.append(
            f"| `{result.scenario_id}` {result.title} | `{result.disposition}` | `{result.breakpoint}` | `{result.reviewer_required}` | `{result.hardware_authority}` |"
        )
    lines.extend(["", "## Reasons", ""])
    for result in results:
        lines.append(f"### `{result.scenario_id}`")
        lines.append("")
        lines.append(result.reason)
        lines.append("")
    lines.extend(
        [
            "## Boundary",
            "",
            "Mud Run V0 is an adversarial local evidence harness. It does not submit backend jobs, validate physical quantum hardware, change pulses, authorize quarantine commands, or dispatch HAL actions.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    results = [evaluate(scenario) for scenario in SCENARIOS]
    summary = {
        "schema_version": "hqa.mud_run.v0",
        "execution_mode": "adversarial_shadow_harness",
        "hardware_authority": False,
        "scenario_count": len(results),
        "results": [asdict(result) for result in results],
        "expected": [
            {
                "scenario_id": scenario.scenario_id,
                "expected_disposition": scenario.expected_disposition,
                "expected_breakpoint": scenario.expected_breakpoint,
            }
            for scenario in SCENARIOS
        ],
        "boundary": "Local adversarial harness only; no live hardware authority.",
    }
    summary_path = OUTPUT_ROOT / "mud_run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    manifest = f"{sha256(summary_path)}  {summary_path.name}\n"
    (OUTPUT_ROOT / "MANIFEST_SHA256.txt").write_text(manifest, encoding="utf-8")
    write_report(results)
    print(f"HQA mud run summary written: {summary_path}")
    print(f"HQA mud run report written: {REPORT_PATH}")
    for result in results:
        print(f"- {result.scenario_id}: {result.disposition} at {result.breakpoint}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
