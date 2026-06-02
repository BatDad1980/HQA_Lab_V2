"""Quality gate for Patch Routing Prototype V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "patch_routing_prototype_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_PATCH_ROUTING_PROTOTYPE_QUALITY.md"


def load_payload() -> dict[str, Any]:
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Patch Routing Prototype Quality",
        "",
        "## Purpose",
        "",
        "This gate verifies that patch routing reduces planning workload while preserving route/no-route decisions.",
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
            "This gate validates shadow route-planning behavior only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("input_exists", False, "Run patch_routing_prototype_v0.py first.")]
        write_report(checks)
        print(f"HQA patch routing quality written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    results = {item["scenario_id"]: item for item in payload.get("results", [])}
    expected = {item["scenario_id"]: item for item in payload.get("expected", [])}
    no_authority = payload.get("hardware_authority") is False and all(item.get("hardware_authority") is False for item in results.values())
    expected_match = all(results.get(sid, {}).get("decision") == item["expected_decision"] for sid, item in expected.items())
    route_results = [item for item in results.values() if item["decision"] == "PATCH_ROUTE_AVAILABLE"]
    reductions = [float(item["workload_reduction"]) for item in route_results]
    patch_latencies = [float(item["patch_latency_estimate_ms"]) for item in route_results]
    global_latencies = [float(item["global_latency_estimate_ms"]) for item in route_results]

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.patch_routing_prototype.v0", "Schema is V0."),
        ("shadow_mode", payload.get("execution_mode") == "shadow_routing_prototype", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", no_authority, "No patch routing result grants hardware authority."),
        ("four_scenarios", len(results) == 4 and len(expected) == 4, f"Results `{len(results)}`, expected `{len(expected)}`."),
        ("expected_decisions_match", expected_match, "All route/no-route decisions match expected outcomes."),
        ("routes_have_paths", all(item.get("patch_path") for item in route_results), "Every available route includes a patch path."),
        ("no_route_safe_hold", results.get("PR-004", {}).get("decision") == "SAFE_HOLD" and results.get("PR-004", {}).get("patch_path") is None, "Patch wall triggers safe hold."),
        ("large_reductions", all(reduction >= 50.0 for reduction in reductions), f"Reductions: `{reductions}`."),
        ("patch_latency_under_budget", all(latency < 250.0 for latency in patch_latencies), f"Patch latencies: `{patch_latencies}`."),
        ("global_latency_exposes_need", any(latency >= 250.0 for latency in global_latencies), f"Global latencies: `{global_latencies}`."),
        ("boundary_present", "does not validate physical quantum hardware" in payload.get("boundary", ""), "Boundary rejects physical validation claim."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA patch routing quality written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
