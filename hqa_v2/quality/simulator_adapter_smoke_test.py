"""Smoke-test optional HQA simulator adapters.

The adapters must stay lightweight: importing them should not import heavy
quantum simulator packages, and missing packages must degrade to a clean
unavailable status instead of breaking the base HQA stack.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = HQA_V2_ROOT.parent
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_SIMULATOR_ADAPTER_SMOKE.md"
JSON_PATH = HQA_V2_ROOT / "logs" / "simulator_adapter_smoke.json"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hqa_v2.integrations.simulator_adapters import get_adapter_statuses


def write_outputs(statuses) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    payload = [asdict(status) for status in statuses]
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    available = sum(1 for status in statuses if status.available)
    lines = [
        "# HQA Simulator Adapter Smoke Test",
        "",
        "## Purpose",
        "",
        "This smoke test verifies that optional simulator adapters can be inspected without making those simulator packages mandatory for HQA V2.",
        "",
        "## Results",
        "",
        f"- Adapters checked: `{len(statuses)}`",
        f"- Available: `{available}`",
        f"- Unavailable: `{len(statuses) - available}`",
        "",
        "| Adapter | Status | Boundary |",
        "|---|---:|---|",
    ]

    for status in statuses:
        result = "AVAILABLE" if status.available else "UNAVAILABLE"
        lines.append(f"| `{status.name}` | {result} | {status.boundary} |")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This test checks adapter availability and import discipline only. It does not validate physical quantum hardware, production QEC performance, or live backend access.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    statuses = get_adapter_statuses()
    write_outputs(statuses)
    print(f"HQA simulator adapter smoke written: {REPORT_PATH}")
    for status in statuses:
        result = "available" if status.available else "unavailable"
        print(f"- {status.name}: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
