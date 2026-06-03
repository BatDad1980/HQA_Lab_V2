"""Quality gate for HQA IBM Backend Field Map V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "ibm_backend_field_map_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_IBM_BACKEND_FIELD_MAP_GATE.md"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA IBM Backend Field Map Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that IBM backend field-map evidence exposes qubit and edge neighborhoods without expanding authority.",
        "",
        "## Results",
        "",
        f"- Checks: `{len(checks)}`",
        f"- Passed: `{passed}`",
        f"- Failed: `{len(checks) - passed}`",
        "",
        "| Check | Status | Detail |",
        "|---|---:|---|",
    ]
    for name, ok, detail in checks:
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate validates field-map evidence shape only. It does not validate live quantum performance, submit jobs, run circuits, alter pulses, or authorize HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("field_map_exists", False, "Run ibm_backend_field_map_v0.py first.")]
        write_report(checks)
        print(f"HQA IBM backend field map gate written: {REPORT_PATH}")
        return 1
    payload: dict[str, Any] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    qubits = payload.get("qubits", [])
    edges = payload.get("edges", [])
    summary = payload.get("summary", {})
    degraded_qubits = [qubit for qubit in qubits if qubit.get("status") == "degraded"]
    degraded_edges = [edge for edge in edges if edge.get("status") == "degraded_neighborhood"]

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.ibm_backend_field_map.v0", "Field-map schema is V0."),
        ("ibm_heavy_hex", payload.get("provider") == "ibm_qiskit_runtime" and payload.get("topology_family") == "heavy_hex", "IBM heavy-hex lane is declared."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "No HAL authority granted."),
        ("no_jobs_submitted", payload.get("jobs_submitted") == 0, "Zero provider jobs submitted."),
        ("qubit_fields_present", all({"index", "t1_us", "t2_us", "readout_error", "status", "reasons"}.issubset(qubit) for qubit in qubits), "Every qubit has health fields."),
        ("edge_fields_present", all({"source", "target", "status", "endpoint_degraded_count", "coupling_risk"}.issubset(edge) for edge in edges), "Every edge has neighborhood fields."),
        ("degraded_reasons_present", all(qubit.get("reasons") for qubit in degraded_qubits), "Every degraded qubit has a reason."),
        ("degraded_edges_visible", len(degraded_edges) == summary.get("degraded_neighborhood_edges"), "Summary matches degraded edge count."),
        ("cluster_proxy_visible", summary.get("degraded_clusters_visible") is True and summary.get("largest_degraded_component", 0) >= 1, "Cluster proxy is available."),
        ("fixture_offline_by_default", payload.get("collection_mode") in {"offline_fixture", "live_metadata_snapshot"}, f"Mode: `{payload.get('collection_mode')}`."),
        ("boundary_present", "submits zero jobs" in payload.get("boundary", "") and "grants no HAL authority" in payload.get("boundary", ""), "Boundary blocks jobs and HAL authority."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA IBM backend field map gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
