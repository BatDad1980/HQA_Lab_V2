"""Quality gate for HQA Cat Solver Contract V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = HQA_V2_ROOT / "logs" / "cat_solver_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_CAT_SOLVER_CONTRACT_GATE.md"

REQUIRED_NAMES = {
    "solver_name",
    "solver_version",
    "trajectory_id",
    "cycles",
    "parity_history",
    "photon_loss_events",
    "logical_error_proxy",
    "wigner_metadata",
    "cascade_indicator",
    "confidence",
}


def load_payload() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Cat Solver Contract Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that the cat-qubit solver contract is complete, bounded, and contract-only.",
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
            "This gate validates a solver evidence contract only. It does not validate physical cat-qubit hardware, production QEC performance, or live HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not CONTRACT_PATH.exists():
        checks = [("contract_exists", False, f"Missing `{CONTRACT_PATH}`")]
        write_report(checks)
        print(f"HQA cat solver contract gate written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    fields = payload.get("required_fields", [])
    names = {field.get("name") for field in fields}
    required_flags = [field.get("required") is True for field in fields]
    rules = " ".join(payload.get("rejection_rules", []))
    mapping = payload.get("hqa_mapping_rules", {})

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.cat_solver_contract.v0", "Contract schema is V0."),
        ("contract_only", payload.get("execution_mode") == "contract_only", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "Contract grants no hardware authority."),
        ("accepted_solvers", set(payload.get("accepted_solvers", [])) == {"qutip", "dynamiqs_jax"}, f"Solvers: `{payload.get('accepted_solvers')}`."),
        ("required_fields_complete", names == REQUIRED_NAMES, f"Fields: `{sorted(names)}`."),
        ("all_fields_required", all(required_flags), "All evidence fields are required."),
        ("confidence_rule_present", "confidence outside [0, 1]" in rules, "Confidence rejection rule is present."),
        ("live_control_rejected", "live hardware" in rules and "HAL execution" in rules, "Live control rejection rule is present."),
        ("heavy_arrays_rejected", "heavy binary/image arrays" in rules, "Heavy artifact rejection rule is present."),
        ("mapping_covers_cascade", "cascade_indicator" in mapping and "confidence" in mapping, "Cascade and confidence mapping rules exist."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA cat solver contract gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
