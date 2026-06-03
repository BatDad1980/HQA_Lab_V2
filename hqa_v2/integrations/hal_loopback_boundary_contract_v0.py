"""HAL loopback boundary contract for reported mock cryostat ACKs.

This module does not open sockets. It replays a reported adjacent-lane loopback
transaction as bounded evidence and formalizes the clean-lane rule:
localhost ACKs from a mock server prove serialization and controller state
updates only; they do not grant real actuator authority.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "hal_loopback_boundary_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_HAL_LOOPBACK_BOUNDARY_CONTRACT_V0.md"


@dataclass(frozen=True)
class LoopbackTransaction:
    host: str
    port: int
    server_class: str
    controller_mode_reported: str
    command: str
    ack: str
    simulated_delay: bool
    state_update_reported: bool


REPORTED_TRANSACTION = LoopbackTransaction(
    host="127.0.0.1",
    port=5000,
    server_class="MockCryostatHandler",
    controller_mode_reported="physical",
    command="SET:CRYO:PUMP:Q00 ON",
    ack="ACK_OK: PUMPS_ENGAGED",
    simulated_delay=True,
    state_update_reported=True,
)


def stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def classify_transaction(transaction: LoopbackTransaction) -> dict[str, Any]:
    command_allowed = transaction.command == "SET:CRYO:PUMP:Q00 ON"
    loopback_only = transaction.host in {"127.0.0.1", "localhost"} and transaction.port == 5000
    mock_server_declared = transaction.server_class == "MockCryostatHandler"
    ack_valid = transaction.ack.startswith("ACK_OK:")

    clean_lane_mode = "MOCK_LOOPBACK_ACK_ONLY"
    dispatch_authority = False
    real_actuator_authority = False

    if not loopback_only:
        decision = "REJECT_NON_LOOPBACK_ENDPOINT"
    elif not mock_server_declared:
        decision = "REJECT_UNKNOWN_HARDWARE_SERVER"
    elif not command_allowed:
        decision = "REJECT_UNREGISTERED_COMMAND"
    elif not ack_valid:
        decision = "REJECT_INVALID_ACK"
    else:
        decision = "ACCEPT_AS_MOCK_TRANSPORT_EVIDENCE"

    evidence = {
        **asdict(transaction),
        "loopback_only": loopback_only,
        "mock_server_declared": mock_server_declared,
        "command_allowed": command_allowed,
        "ack_valid": ack_valid,
        "clean_lane_mode": clean_lane_mode,
        "decision": decision,
        "dispatch_authority": dispatch_authority,
        "real_actuator_authority": real_actuator_authority,
        "clean_lane_network_calls": 0,
        "boundary": "Loopback ACK validates transport serialization and internal state update only. It is not evidence of real cryostat control and does not authorize physical actuation.",
    }
    evidence["transaction_hash"] = stable_hash(evidence)
    return evidence


def run_contract() -> dict[str, Any]:
    evidence = classify_transaction(REPORTED_TRANSACTION)
    payload = {
        "schema_version": "hqa.hal_loopback_boundary_contract.v0",
        "execution_mode": "reported_loopback_replay_no_socket",
        "source_class": "adjacent_lane_reported_mock_cryostat_transaction",
        "clean_lane_network_calls": 0,
        "hardware_authority": False,
        "real_actuator_authority": False,
        "evidence": evidence,
        "allowed_interpretation": [
            "The controller can serialize a cryostat command string.",
            "A mock loopback server can receive the command and return an ACK.",
            "The controller can update internal state after receiving the ACK.",
        ],
        "disallowed_interpretation": [
            "The system has validated real cryostat hardware control.",
            "The system may dispatch to non-loopback endpoints.",
            "A network ACK can override the HAL safety governor.",
            "Mock physical mode grants real actuator authority.",
        ],
        "boundary": "This clean-lane replay does not open sockets, submit network traffic, activate hardware, or grant physical HAL authority.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    evidence = payload["evidence"]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA HAL Loopback Boundary Contract V0",
        "",
        "## Purpose",
        "",
        "This report records a reported mock cryostat loopback transaction and defines the clean-lane boundary around it.",
        "",
        "The important result is not that HQA can touch hardware. The important result is that HQA can treat a loopback ACK as transport evidence while refusing to promote it into real actuator authority.",
        "",
        "## Reported Transaction",
        "",
        f"- Source class: `{payload['source_class']}`",
        f"- Execution mode: `{payload['execution_mode']}`",
        f"- Clean-lane network calls: `{payload['clean_lane_network_calls']}`",
        f"- Hardware authority: `{payload['hardware_authority']}`",
        f"- Real actuator authority: `{payload['real_actuator_authority']}`",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Host | `{evidence['host']}` |",
        f"| Port | `{evidence['port']}` |",
        f"| Server class | `{evidence['server_class']}` |",
        f"| Controller mode reported | `{evidence['controller_mode_reported']}` |",
        f"| Command | `{evidence['command']}` |",
        f"| ACK | `{evidence['ack']}` |",
        f"| Clean-lane mode | `{evidence['clean_lane_mode']}` |",
        f"| Decision | `{evidence['decision']}` |",
        f"| Transaction hash | `{evidence['transaction_hash']}` |",
        "",
        "## Allowed Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["allowed_interpretation"])
    lines.extend(["", "## Disallowed Interpretation", ""])
    lines.extend(f"- {item}" for item in payload["disallowed_interpretation"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_contract()
    write_report(payload)
    print(f"HQA HAL loopback boundary contract written: {REPORT_PATH}")
    print(f"- decision: {payload['evidence']['decision']}")
    print(f"- clean-lane network calls: {payload['clean_lane_network_calls']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

