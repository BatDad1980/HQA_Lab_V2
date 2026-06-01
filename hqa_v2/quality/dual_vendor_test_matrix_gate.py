"""Quality gate for HQA Dual Vendor Test Matrix V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = HQA_V2_ROOT / "logs" / "dual_vendor_test_matrix_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_DUAL_VENDOR_TEST_MATRIX_GATE.md"

EXPECTED_LANES = {"CAT-ALICE-BOB", "IBM-HEAVY-HEX", "GOOGLE-GRID", "NEUTRAL-VENDOR-GRAPH"}
EXPECTED_TOPOLOGIES = {"bosonic_cat", "heavy_hex", "grid_lattice", "neutral_graph"}


def load_payload() -> dict[str, Any]:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Dual Vendor Test Matrix Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that HQA's dual vendor test matrix covers cat and non-cat lanes without granting authority or collapsing claims.",
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
        status = "PASS" if ok else "FAIL"
        lines.append(f"| {name} | {status} | {detail} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate validates test-matrix readiness only. It does not validate physical quantum hardware, production QEC performance, live vendor access, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not MATRIX_PATH.exists():
        checks = [("matrix_exists", False, f"Missing `{MATRIX_PATH}`")]
        write_report(checks)
        print(f"HQA dual vendor test matrix gate written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    lanes = payload.get("lanes", [])
    lane_ids = {lane.get("lane_id") for lane in lanes}
    topology_families = {lane.get("topology_family") for lane in lanes}
    boundaries = " ".join(lane.get("boundary", "") for lane in lanes)

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.dual_vendor_test_matrix.v0", "Matrix schema is V0."),
        ("planning_only", payload.get("execution_mode") == "planning_and_readiness_only", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "Matrix grants no hardware authority."),
        ("all_lanes_present", lane_ids == EXPECTED_LANES, f"Lanes: `{sorted(lane_ids)}`."),
        ("all_topologies_present", topology_families == EXPECTED_TOPOLOGIES, f"Topologies: `{sorted(topology_families)}`."),
        ("cat_lane_separated", any(lane.get("lane_id") == "CAT-ALICE-BOB" and lane.get("topology_family") == "bosonic_cat" for lane in lanes), "Cat lane is separate."),
        ("ibm_lane_heavy_hex", any(lane.get("lane_id") == "IBM-HEAVY-HEX" and lane.get("topology_family") == "heavy_hex" for lane in lanes), "IBM lane uses heavy_hex."),
        ("google_lane_grid", any(lane.get("lane_id") == "GOOGLE-GRID" and lane.get("topology_family") == "grid_lattice" for lane in lanes), "Google lane uses grid_lattice."),
        ("boundaries_avoid_overclaim", "not be described as Alice & Bob physical validation" in boundaries and "distinguish physical calibration access" in boundaries, "Lane boundaries preserve claim discipline."),
        ("all_lanes_have_next_evidence", all(len(lane.get("required_next_evidence", [])) >= 3 for lane in lanes), "Every lane lists required next evidence."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA dual vendor test matrix gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
