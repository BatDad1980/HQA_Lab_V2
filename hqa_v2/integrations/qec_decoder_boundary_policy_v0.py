"""QEC decoder boundary-partner policy for HQA V2.

This module formalizes a decoder robustness invariant harvested from the storm
lane: odd syndrome cardinality must resolve to a virtual boundary partner, not
crash, silently drop a syndrome, or pretend the observation was clean.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = HQA_V2_ROOT / "logs" / "qec_decoder_boundary_policy_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_QEC_DECODER_BOUNDARY_POLICY_V0.md"


def pair_syndromes(active_nodes: list[str]) -> dict[str, Any]:
    nodes = list(active_nodes)
    pairs: list[dict[str, str]] = []
    boundary_used = False
    while len(nodes) >= 2:
        left = nodes.pop(0)
        right = nodes.pop(0)
        pairs.append({"left": left, "right": right, "match_type": "syndrome_partner"})
    if nodes:
        boundary_used = True
        pairs.append({"left": nodes.pop(0), "right": "VIRTUAL_BOUNDARY", "match_type": "boundary_partner"})
    return {
        "active_syndrome_count": len(active_nodes),
        "cardinality": "odd" if len(active_nodes) % 2 else "even",
        "pairs": pairs,
        "boundary_partner_used": boundary_used,
        "decoder_status": "RESOLVED_WITH_BOUNDARY" if boundary_used else "RESOLVED_DIRECTLY",
        "crashed": False,
        "dropped_syndromes": 0,
    }


def run_policy() -> dict[str, Any]:
    cases = [
        {"case_id": "QEC-EVEN-002", "active_nodes": ["Q_1", "Q_4"]},
        {"case_id": "QEC-ODD-003", "active_nodes": ["Q_1", "Q_4", "Q_7"]},
        {"case_id": "QEC-ODD-001", "active_nodes": ["Q_3"]},
        {"case_id": "QEC-CLEAR-000", "active_nodes": []},
    ]
    results = []
    for case in cases:
        resolution = pair_syndromes(case["active_nodes"])
        results.append({**case, **resolution})
    return {
        "schema_version": "hqa.qec_decoder_boundary_policy.v0",
        "execution_mode": "local_policy_replay",
        "policy_rule": "Odd active syndrome cardinality must map the unpaired syndrome to a virtual boundary partner.",
        "results": results,
        "hardware_authority": False,
        "jobs_submitted": 0,
        "boundary": "QEC Decoder Boundary Policy V0 is local decoder policy replay only. It does not validate production decoding, submit backend jobs, run circuits, change pulses, or authorize HAL execution.",
    }


def write_outputs(payload: dict[str, Any]) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# HQA QEC Decoder Boundary Policy V0",
        "",
        "## Purpose",
        "",
        "This report formalizes the decoder rule that odd syndrome sets must resolve through a virtual boundary partner instead of crashing.",
        "",
        "## Policy Rule",
        "",
        payload["policy_rule"],
        "",
        "## Results",
        "",
        "| Case | Active Count | Cardinality | Status | Boundary Used | Dropped | Crashed |",
        "|---|---:|---|---|---:|---:|---:|",
    ]
    for item in payload["results"]:
        lines.append(
            f"| `{item['case_id']}` | `{item['active_syndrome_count']}` | `{item['cardinality']}` | `{item['decoder_status']}` | `{item['boundary_partner_used']}` | `{item['dropped_syndromes']}` | `{item['crashed']}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_policy()
    write_outputs(payload)
    odd_resolved = sum(1 for item in payload["results"] if item["cardinality"] == "odd" and item["boundary_partner_used"])
    print(f"HQA QEC decoder boundary policy written: {REPORT_PATH}")
    print(f"- odd cases resolved with boundary: {odd_resolved}")
    print(f"- jobs submitted: {payload['jobs_submitted']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
