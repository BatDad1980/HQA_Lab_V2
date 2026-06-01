"""Quality gate for the local Qiskit Aer cascade-noise probe."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = HQA_V2_ROOT / "logs" / "qiskit_aer_cascade_noise_probe.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_QISKIT_AER_CASCADE_GATE.md"


def load_summaries() -> dict[str, dict]:
    payload = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    return {summary["profile"]: summary for summary in payload.get("summaries", [])}


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Qiskit Aer Cascade Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that the local Aer cascade probe separates a quiet nominal profile from an intentionally stressed profile.",
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
            "This gate evaluates local simulator-observation behavior only. It does not validate physical quantum hardware, production QEC performance, or live backend behavior.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not SUMMARY_PATH.exists():
        checks = [("summary_exists", False, f"Missing `{SUMMARY_PATH}`")]
        write_report(checks)
        print(f"HQA Qiskit Aer cascade gate written: {REPORT_PATH}")
        return 1

    summaries = load_summaries()
    nominal = summaries.get("nominal", {})
    stress = summaries.get("stress", {})

    nominal_rate = float(nominal.get("cascade_like_rate", 1.0))
    stress_rate = float(stress.get("cascade_like_rate", 0.0))

    checks = [
        ("nominal_profile_present", bool(nominal), "Nominal profile summary exists."),
        ("stress_profile_present", bool(stress), "Stress profile summary exists."),
        ("nominal_aer_ran", bool(nominal.get("ran_local_aer")), "Nominal profile ran local Aer."),
        ("stress_aer_ran", bool(stress.get("ran_local_aer")), "Stress profile ran local Aer."),
        ("nominal_stays_quiet", nominal_rate <= 0.10, f"Nominal cascade-like rate `{nominal_rate}` <= `0.10`."),
        ("stress_lights_up", stress_rate >= 0.50, f"Stress cascade-like rate `{stress_rate}` >= `0.50`."),
        (
            "profile_separation",
            stress_rate - nominal_rate >= 0.40,
            f"Stress minus nominal separation `{round(stress_rate - nominal_rate, 6)}` >= `0.40`.",
        ),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA Qiskit Aer cascade gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
