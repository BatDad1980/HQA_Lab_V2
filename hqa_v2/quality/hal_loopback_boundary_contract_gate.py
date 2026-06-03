"""Quality gate for HAL loopback boundary contract V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "hal_loopback_boundary_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_HAL_LOOPBACK_BOUNDARY_CONTRACT_GATE.md"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA HAL Loopback Boundary Contract Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that a reported mock cryostat loopback ACK remains transport evidence only and does not become real HAL authority.",
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
            "This gate validates a mock loopback contract only. It does not open sockets, transmit network traffic, activate pumps, validate physical cryostat control, or authorize HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("contract_output_exists", False, "Run hal_loopback_boundary_contract_v0.py first.")]
        write_report(checks)
        print(f"HQA HAL loopback boundary contract gate written: {REPORT_PATH}")
        return 1

    payload: dict[str, Any] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    evidence = payload.get("evidence", {})
    disallowed = "\n".join(payload.get("disallowed_interpretation", []))

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.hal_loopback_boundary_contract.v0", "Contract schema is V0."),
        ("reported_replay_mode", payload.get("execution_mode") == "reported_loopback_replay_no_socket", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_clean_network_calls", payload.get("clean_lane_network_calls") == 0 and evidence.get("clean_lane_network_calls") == 0, "Clean lane opened no sockets."),
        ("no_hardware_authority", payload.get("hardware_authority") is False and evidence.get("dispatch_authority") is False, "No hardware dispatch authority granted."),
        ("no_real_actuator_authority", payload.get("real_actuator_authority") is False and evidence.get("real_actuator_authority") is False, "No real actuator authority granted."),
        ("loopback_only", evidence.get("loopback_only") is True and evidence.get("host") == "127.0.0.1", "Endpoint is loopback-only."),
        ("mock_server_declared", evidence.get("mock_server_declared") is True and evidence.get("server_class") == "MockCryostatHandler", "Server is explicitly mock-classed."),
        ("command_registered", evidence.get("command_allowed") is True and evidence.get("command") == "SET:CRYO:PUMP:Q00 ON", "Reported command is the registered fixture command."),
        ("ack_valid_but_bounded", evidence.get("ack_valid") is True and evidence.get("clean_lane_mode") == "MOCK_LOOPBACK_ACK_ONLY", "ACK is accepted only as mock transport evidence."),
        ("decision_accepts_evidence_only", evidence.get("decision") == "ACCEPT_AS_MOCK_TRANSPORT_EVIDENCE", f"Decision: `{evidence.get('decision')}`."),
        ("disallowed_real_control", "validated real cryostat hardware control" in disallowed and "override the HAL safety governor" in disallowed, "Disallowed interpretations block real-control and safety-override claims."),
        ("boundary_blocks_actuation", "does not open sockets" in payload.get("boundary", "") and "grant physical HAL authority" in payload.get("boundary", ""), "Boundary blocks sockets and physical authority."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA HAL loopback boundary contract gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

