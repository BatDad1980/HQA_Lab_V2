"""Quality gate for QEC Decoder Boundary Policy V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "qec_decoder_boundary_policy_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_QEC_DECODER_BOUNDARY_POLICY_GATE.md"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA QEC Decoder Boundary Policy Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that odd syndrome cardinality resolves through a virtual boundary partner without crash or silent loss.",
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
            "This gate validates local decoder policy only. It does not validate production decoding, submit jobs, run circuits, alter pulses, or authorize HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("policy_output_exists", False, "Run qec_decoder_boundary_policy_v0.py first.")]
        write_report(checks)
        print(f"HQA QEC decoder boundary policy gate written: {REPORT_PATH}")
        return 1

    payload: dict[str, Any] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    results = payload.get("results", [])
    odd = [item for item in results if item.get("cardinality") == "odd"]
    even = [item for item in results if item.get("cardinality") == "even" and item.get("active_syndrome_count", 0) > 0]

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.qec_decoder_boundary_policy.v0", "Policy schema is V0."),
        ("local_policy_replay", payload.get("execution_mode") == "local_policy_replay", f"Mode: `{payload.get('execution_mode')}`."),
        ("odd_cases_present", len(odd) >= 2, f"Odd cases: `{len(odd)}`."),
        ("odd_uses_boundary", all(item.get("boundary_partner_used") is True for item in odd), "Every odd case uses a virtual boundary partner."),
        ("even_no_boundary", all(item.get("boundary_partner_used") is False for item in even), "Even nonzero cases resolve directly."),
        ("no_crashes", all(item.get("crashed") is False for item in results), "No case crashed."),
        ("no_silent_drops", all(item.get("dropped_syndromes") == 0 for item in results), "No syndrome was silently dropped."),
        ("boundary_partner_recorded", any(pair.get("right") == "VIRTUAL_BOUNDARY" for item in odd for pair in item.get("pairs", [])), "Boundary partner appears in pair list."),
        ("policy_rule_present", "virtual boundary partner" in payload.get("policy_rule", ""), "Policy rule names the virtual boundary partner."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "No hardware authority granted."),
        ("no_jobs_submitted", payload.get("jobs_submitted") == 0, "Zero provider jobs submitted."),
        ("boundary_present", "does not validate production decoding" in payload.get("boundary", "") and "authorize HAL execution" in payload.get("boundary", ""), "Boundary blocks production and HAL claims."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA QEC decoder boundary policy gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
