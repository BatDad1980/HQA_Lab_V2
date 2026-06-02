"""Quality gate for Telemetry Compression Gate V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "telemetry_compression_gate_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_TELEMETRY_COMPRESSION_GATE_QUALITY.md"


def load_payload() -> dict[str, Any]:
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Telemetry Compression Gate Quality",
        "",
        "## Purpose",
        "",
        "This gate verifies that telemetry compression preserves HQA intervention decisions and keeps advisory payloads inside the latency budget.",
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
            "This gate validates telemetry summarization only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("input_exists", False, "Run telemetry_compression_gate_v0.py first.")]
        write_report(checks)
        print(f"HQA telemetry compression quality written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    results = payload.get("results", [])
    by_id = {item["scenario_id"]: item for item in results}
    ratios = [float(item["compression_ratio"]) for item in results]
    decisions = {item["compressed_decision"] for item in results}
    no_authority = payload.get("hardware_authority") is False and all(item.get("hardware_authority") is False for item in results)
    budget = float(payload.get("feedback_budget_ms", 0.0))

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.telemetry_compression_gate.v0", "Schema is V0."),
        ("shadow_mode", payload.get("execution_mode") == "shadow_compression_gate", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", no_authority, "No compression result grants hardware authority."),
        ("four_scenarios", len(results) == 4, f"Results: `{len(results)}`."),
        ("all_decisions_preserved", all(item.get("decision_preserved") is True for item in results), "Every compressed summary preserved the raw intervention decision."),
        ("all_under_budget", all(float(item.get("estimated_compressed_latency_ms", 9999.0)) <= budget for item in results), f"Budget: `{budget}` ms."),
        ("monster_compressed_enough", float(by_id.get("TCG-003", {}).get("compression_ratio", 0.0)) >= 100.0, f"Monster ratio: `{by_id.get('TCG-003', {}).get('compression_ratio')}`."),
        ("collapse_still_safe_hold", by_id.get("TCG-004", {}).get("compressed_decision") == "SAFE_HOLD", f"Collapse decision: `{by_id.get('TCG-004', {}).get('compressed_decision')}`."),
        ("decision_variety", {"ACCEPT_ANNOTATION", "MONITOR_WITH_ROUTE_REVIEW", "QUARANTINE_REMAP_REVIEW", "SAFE_HOLD"} <= decisions, f"Decisions: `{sorted(decisions)}`."),
        ("compression_positive", all(ratio > 1.0 for ratio in ratios), f"Ratios: `{ratios}`."),
        ("boundary_present", "does not authorize live hardware control" in payload.get("boundary", ""), "Boundary rejects live authority."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA telemetry compression quality written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
