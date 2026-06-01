"""Quality gate for the HQA legacy scar router harvest."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "legacy_scar_router_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_LEGACY_SCAR_ROUTER_GATE.md"


def load_payload() -> dict[str, Any]:
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Legacy Scar Router Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that the V1 scar-router harvest behaves as a bounded shadow replay artifact.",
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
            "This gate validates deterministic route-selection behavior only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("input_exists", False, "Run legacy_scar_router_v0.py first.")]
        write_report(checks)
        print(f"HQA legacy scar router gate written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    scenarios = payload.get("scenarios", {})
    scar = scenarios.get("scarred_sparse_grid", {})
    cat = scenarios.get("cat_phase_bias", {})
    blocked = scenarios.get("no_route_barrier", {})
    scar_path = scar.get("path") or []
    blocked_nodes = set(scar.get("blocked_nodes") or [])

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.legacy_scar_router.v0", "Schema is V0."),
        ("shadow_replay_only", payload.get("execution_mode") == "shadow_replay", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "No hardware authority present."),
        ("scar_route_exists", isinstance(scar_path, list) and len(scar_path) > 2, f"Path: `{scar_path}`."),
        ("scar_route_avoids_blocked", not any(node in blocked_nodes for node in scar_path), f"Blocked nodes: `{sorted(blocked_nodes)}`."),
        ("cat_phase_bias_applied", cat.get("risk_bias_applied") is True, f"Phase cost `{cat.get('phase_flip_cost')}`, generic cost `{cat.get('generic_cost')}`."),
        ("no_route_safe_hold", blocked.get("path") is None and blocked.get("action") == "SAFE_HOLD", f"Action: `{blocked.get('action')}`."),
        ("boundary_present", "does not validate physical quantum hardware" in payload.get("boundary", ""), "Boundary rejects physical validation claim."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA legacy scar router gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
