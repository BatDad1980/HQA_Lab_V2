"""Smoke-test HQA vendor interface schema contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = HQA_V2_ROOT / "schemas"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_SCHEMA_CONTRACT_SMOKE.md"

REQUIRED_SCHEMAS = [
    "topology_snapshot.schema.json",
    "syndrome_record.schema.json",
    "quarantine_decision.schema.json",
    "reroute_proposal.schema.json",
    "hal_manifest.schema.json",
]


def check_schema(path: Path) -> tuple[str, bool, str]:
    if not path.exists():
        return path.name, False, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return path.name, False, f"invalid JSON: {exc}"

    required_top = ["$schema", "title", "type", "required", "properties"]
    missing = [key for key in required_top if key not in payload]
    if missing:
        return path.name, False, f"missing top-level keys: {', '.join(missing)}"
    if payload.get("type") != "object":
        return path.name, False, "schema type must be object"
    if payload.get("additionalProperties") is not False:
        return path.name, False, "additionalProperties must be false"
    return path.name, True, payload.get("title", "ok")


def write_report(results: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in results if ok)
    lines = [
        "# HQA Schema Contract Smoke Test",
        "",
        "## Purpose",
        "",
        "This smoke test verifies that HQA V2 vendor-interface schemas are present, parseable, and strict enough for shadow-mode integration review.",
        "",
        "## Results",
        "",
        f"- Schemas checked: `{len(results)}`",
        f"- Passed: `{passed}`",
        f"- Failed: `{len(results) - passed}`",
        "",
        "| Schema | Status | Detail |",
        "|---|---:|---|",
    ]
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        lines.append(f"| `{name}` | {status} | {detail} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These schemas define dry-run and shadow-advisory data contracts. They do not grant HQA physical hardware authority.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results = [check_schema(SCHEMA_ROOT / name) for name in REQUIRED_SCHEMAS]
    write_report(results)
    failed = [result for result in results if not result[1]]
    print(f"HQA schema contract smoke written: {REPORT_PATH}")
    print(f"Passed {len(results) - len(failed)}/{len(results)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
