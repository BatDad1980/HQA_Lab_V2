"""Benchmark telemetry contract for HQA V2.

The active bench may run local QEC benchmarks and expose telemetry for review.
This contract defines what that telemetry lane is allowed to do and, more
importantly, what it is not allowed to become.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = HQA_V2_ROOT / "logs" / "benchmark_telemetry_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_BENCHMARK_TELEMETRY_CONTRACT_V0.md"


def sha256_json(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def benchmark_records() -> list[dict[str, Any]]:
    records = []
    for distance, rounds, failure_rate in [(3, 3, 0.0875), (5, 5, 0.0312), (7, 7, 0.0109)]:
        record = {
            "schema_version": "hqa.benchmark_record.v0",
            "benchmark_id": f"QEC-REP-D{distance}",
            "decoder_family": "repetition_code_boundary_policy",
            "distance": distance,
            "rounds": rounds,
            "shots": 4096,
            "logical_failure_rate_proxy": failure_rate,
            "source": "local_simulation",
            "hardware_authority": False,
            "jobs_submitted": 0,
        }
        record["record_hash"] = sha256_json(record)
        records.append(record)
    return records


def telemetry_contract() -> dict[str, Any]:
    commands = [
        {
            "name": "run-telemetry",
            "allowed": ["start local read-only telemetry service", "emit bounded status records"],
            "forbidden": ["store credentials", "dispatch commands", "call HAL", "submit provider jobs"],
        },
        {
            "name": "benchmark-qec",
            "allowed": ["run local repetition-code benchmark", "write markdown report", "write hashed telemetry records"],
            "forbidden": ["claim production QEC", "touch live backend", "authorize intervention"],
        },
    ]
    records = benchmark_records()
    return {
        "schema_version": "hqa.benchmark_telemetry_contract.v0",
        "execution_mode": "contract_and_fixture_records",
        "commands": commands,
        "benchmark_distances": [record["distance"] for record in records],
        "records": records,
        "server_permissions": {
            "observe": True,
            "record": True,
            "hash": True,
            "authorize": False,
            "actuate": False,
            "store_credentials": False,
            "remote_command_dispatch": False,
            "hal_authority": False,
        },
        "payload_limits": {
            "max_record_bytes": 8192,
            "max_batch_records": 512,
            "credential_like_payloads": "reject",
        },
        "hardware_authority": False,
        "jobs_submitted": 0,
        "boundary": "Benchmark Telemetry Contract V0 allows local observation, recording, hashing, and report writing only. It does not authorize hardware action, store credentials, expose remote command dispatch, submit provider jobs, or grant HAL authority.",
    }


def write_outputs(payload: dict[str, Any]) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# HQA Benchmark Telemetry Contract V0",
        "",
        "## Purpose",
        "",
        "This report defines the clean boundary for CLI benchmark and telemetry-server expansion work.",
        "",
        "Telemetry may observe, record, and hash. Telemetry may not authorize or actuate.",
        "",
        "## Commands",
        "",
        "| Command | Allowed | Forbidden |",
        "|---|---|---|",
    ]
    for command in payload["commands"]:
        lines.append(
            f"| `{command['name']}` | {', '.join(command['allowed'])} | {', '.join(command['forbidden'])} |"
        )

    lines.extend(
        [
            "",
            "## Benchmark Fixture Records",
            "",
            "| Benchmark | Distance | Rounds | Shots | Logical Failure Proxy | Hash Prefix |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for record in payload["records"]:
        lines.append(
            f"| `{record['benchmark_id']}` | `{record['distance']}` | `{record['rounds']}` | `{record['shots']}` | `{record['logical_failure_rate_proxy']}` | `{record['record_hash'][:12]}` |"
        )

    permissions = payload["server_permissions"]
    lines.extend(
        [
            "",
            "## Permission Boundary",
            "",
            f"- Observe: `{permissions['observe']}`",
            f"- Record: `{permissions['record']}`",
            f"- Hash: `{permissions['hash']}`",
            f"- Authorize: `{permissions['authorize']}`",
            f"- Actuate: `{permissions['actuate']}`",
            f"- Store credentials: `{permissions['store_credentials']}`",
            f"- Remote command dispatch: `{permissions['remote_command_dispatch']}`",
            f"- HAL authority: `{permissions['hal_authority']}`",
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = telemetry_contract()
    write_outputs(payload)
    print(f"HQA benchmark telemetry contract written: {REPORT_PATH}")
    print(f"- benchmark distances: {payload['benchmark_distances']}")
    print(f"- jobs submitted: {payload['jobs_submitted']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
