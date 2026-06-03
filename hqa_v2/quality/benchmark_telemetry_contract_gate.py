"""Quality gate for Benchmark Telemetry Contract V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "benchmark_telemetry_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_BENCHMARK_TELEMETRY_CONTRACT_GATE.md"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA Benchmark Telemetry Contract Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that benchmark telemetry can observe, record, hash, and report without becoming a command or authority surface.",
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
            "This gate validates telemetry contract shape only. It does not start a server, submit jobs, run live hardware, authorize interventions, or validate production QEC.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("contract_exists", False, "Run benchmark_telemetry_contract_v0.py first.")]
        write_report(checks)
        print(f"HQA benchmark telemetry contract gate written: {REPORT_PATH}")
        return 1
    payload: dict[str, Any] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    permissions = payload.get("server_permissions", {})
    commands = {command.get("name"): command for command in payload.get("commands", [])}
    records = payload.get("records", [])

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.benchmark_telemetry_contract.v0", "Contract schema is V0."),
        ("commands_present", {"run-telemetry", "benchmark-qec"}.issubset(commands), f"Commands: `{', '.join(sorted(commands))}`."),
        ("benchmark_distances", payload.get("benchmark_distances") == [3, 5, 7], f"Distances: `{payload.get('benchmark_distances')}`."),
        ("records_hashed", all(record.get("record_hash") for record in records), "Every benchmark record has a hash."),
        ("observe_record_hash_allowed", permissions.get("observe") is True and permissions.get("record") is True and permissions.get("hash") is True, "Observation, recording, and hashing are allowed."),
        ("no_authorize_or_actuate", permissions.get("authorize") is False and permissions.get("actuate") is False, "Authorization and actuation are denied."),
        ("no_credential_storage", permissions.get("store_credentials") is False, "Credential storage is denied."),
        ("no_remote_dispatch", permissions.get("remote_command_dispatch") is False, "Remote command dispatch is denied."),
        ("no_hal_authority", permissions.get("hal_authority") is False and payload.get("hardware_authority") is False, "HAL and hardware authority are denied."),
        ("no_jobs_submitted", payload.get("jobs_submitted") == 0 and all(record.get("jobs_submitted") == 0 for record in records), "Zero provider jobs submitted."),
        ("payload_limits_present", payload.get("payload_limits", {}).get("credential_like_payloads") == "reject", "Credential-like payloads are rejected."),
        ("boundary_present", "store credentials" in payload.get("boundary", "") and "remote command dispatch" in payload.get("boundary", "") and "grant HAL authority" in payload.get("boundary", ""), "Boundary blocks credentials, command dispatch, and HAL authority."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA benchmark telemetry contract gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
