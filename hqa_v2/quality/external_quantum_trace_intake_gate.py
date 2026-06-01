"""Quality gate for HQA External Quantum Trace Intake V0."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = HQA_V2_ROOT / "logs" / "external_quantum_trace_intake_contract_v0.json"
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "external_trace_intake_v0"
DECISIONS_PATH = OUTPUT_ROOT / "intake_decisions.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_EXTERNAL_QUANTUM_TRACE_INTAKE_GATE.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_valid() -> tuple[bool, str]:
    manifest_path = OUTPUT_ROOT / "MANIFEST_SHA256.txt"
    if not manifest_path.exists():
        return False, "Manifest missing."
    failures: list[str] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, filename = line.split(maxsplit=1)
        path = OUTPUT_ROOT / filename.strip()
        if not path.exists():
            failures.append(f"{filename} missing")
            continue
        if sha256(path) != expected:
            failures.append(f"{filename} hash mismatch")
    if failures:
        return False, "; ".join(failures)
    return True, "All normalized trace hashes match."


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA External Quantum Trace Intake Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that external trace intake accepts only bounded, provenance-bearing traces and rejects unsafe inputs.",
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
            "This gate validates intake behavior only. It does not validate physical quantum hardware, production QEC performance, live vendor access, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not CONTRACT_PATH.exists() or not DECISIONS_PATH.exists():
        checks = [("intake_outputs_exist", False, "Contract or decisions file missing.")]
        write_report(checks)
        print(f"HQA external trace intake gate written: {REPORT_PATH}")
        return 1

    contract = load_json(CONTRACT_PATH)
    decisions_payload = load_json(DECISIONS_PATH)
    decisions = decisions_payload.get("decisions", [])
    accepted = [decision for decision in decisions if decision.get("accepted") is True]
    rejected = [decision for decision in decisions if decision.get("accepted") is False]
    normalized_files = list(OUTPUT_ROOT.glob("*_normalized.json"))
    manifest_ok, manifest_detail = manifest_valid()
    rejection_text = " ".join(";".join(decision.get("rejection_reasons", [])) for decision in rejected)

    checks = [
        ("contract_schema", contract.get("schema_version") == "hqa.external_quantum_trace_intake.v0", "Contract schema is V0."),
        ("intake_only", contract.get("execution_mode") == "intake_validation_only", f"Mode: `{contract.get('execution_mode')}`."),
        ("no_hardware_authority", contract.get("hardware_authority") is False and decisions_payload.get("hardware_authority") is False, "No intake artifact grants hardware authority."),
        ("accepted_one_trace", len(accepted) == 1, f"Accepted traces: `{len(accepted)}`."),
        ("rejected_one_trace", len(rejected) == 1, f"Rejected traces: `{len(rejected)}`."),
        ("normalized_only_accepted", len(normalized_files) == len(accepted), f"Normalized files: `{len(normalized_files)}`."),
        ("secret_rejected", "secret-like content detected" in rejection_text, "Secret-like trace was rejected."),
        ("live_authority_rejected", "forbidden live authority" in rejection_text, "Live-authority request was rejected."),
        ("manifest_valid", manifest_ok, manifest_detail),
        ("normalization_target_present", "hqa.topology_snapshot.v1" in contract.get("normalization_targets", []), "Topology normalization target exists."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA external trace intake gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
