"""Quality gate for HQA Risk Field V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = HQA_V2_ROOT / "logs" / "hqa_risk_field_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_RISK_FIELD_GATE.md"


def load_payload() -> dict[str, Any]:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Risk Field Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that HQA Risk Field V0 produces bounded, advisory-only risk rankings from HQA-native evidence.",
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
            "This gate checks risk-field structure and advisory boundaries only. It does not validate physical quantum hardware, production QEC performance, or live HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not JSON_PATH.exists():
        checks = [("risk_field_exists", False, f"Missing `{JSON_PATH}`")]
        write_report(checks)
        print(f"HQA risk field gate written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    nodes = payload.get("nodes", [])
    top_node = nodes[0] if nodes else {}
    node_ids = {node.get("node_id") for node in nodes}
    scores = [float(node.get("risk_score", -1.0)) for node in nodes]
    bands = {node.get("risk_band") for node in nodes}
    advisory_action = str(payload.get("recommended_advisory_action", ""))

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.risk_field.v0", "Risk field schema version is V0."),
        ("shadow_advisory_mode", payload.get("execution_mode") == "shadow_advisory", "Risk field remains in shadow advisory mode."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "Risk field grants no hardware authority."),
        ("all_vendor_nodes_present", node_ids == {"Q_0", "Q_1", "Q_2", "Q_3"}, f"Node IDs found: `{sorted(node_ids)}`."),
        ("scores_bounded", all(0.0 <= score <= 1.0 for score in scores), f"Scores: `{scores}`."),
        ("q1_highest_risk", top_node.get("node_id") == "Q_1", f"Highest-risk node: `{top_node.get('node_id')}`."),
        ("suspected_patch_matches", payload.get("suspected_patch") == top_node.get("node_id"), "Suspected patch matches top-ranked node."),
        ("cascade_contrast_detected", float(payload.get("cascade_contrast", 0.0)) >= 0.40, f"Cascade contrast: `{payload.get('cascade_contrast')}`."),
        ("advisory_action_only", advisory_action in {"MONITOR_ONLY", "MONITOR_WITH_ROUTE_REVIEW", "QUARANTINE_PROPOSAL", "ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL"}, f"Action: `{advisory_action}`."),
        ("risk_bands_known", bands <= {"low", "elevated", "high", "critical"}, f"Bands: `{sorted(bands)}`."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA risk field gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
