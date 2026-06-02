"""Quality gate for HQA Evidence Dashboard V0."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = HQA_V2_ROOT / "outputs" / "evidence_dashboard_v0" / "HQA_EVIDENCE_DASHBOARD_V0.html"
MANIFEST_PATH = HQA_V2_ROOT / "outputs" / "evidence_dashboard_v0" / "dashboard_manifest.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_EVIDENCE_DASHBOARD_GATE.md"
REGRESSION_PATH = HQA_V2_ROOT / "reports" / "HQA_V2_REGRESSION_SUMMARY.md"

FORBIDDEN_PHRASES = [
    "guarantee",
    "unhackable",
    "physical quantum validation",
    "production qec performance",
    "live hardware control",
    "submit live jobs",
    "api key",
    "apikey",
    "password",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def current_regression_metric() -> str:
    text = REGRESSION_PATH.read_text(encoding="utf-8")
    passed = re.search(r"- Passed: `(\d+)`", text)
    total = re.search(r"- Commands run: `(\d+)`", text)
    if not passed or not total:
        return "unknown"
    return f"{passed.group(1)}/{total.group(1)}"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA Evidence Dashboard Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies the read-only evidence dashboard is backed by local proof artifacts and keeps clean boundaries.",
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
            "This gate validates a local static dashboard only. It does not validate live provider access, credentials, hardware control, physical quantum performance, or production QEC.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not DASHBOARD_PATH.exists() or not MANIFEST_PATH.exists():
        checks = [("dashboard_exists", False, "Run build_evidence_dashboard_v0.py first.")]
        write_report(checks)
        print(f"HQA evidence dashboard gate written: {REPORT_PATH}")
        return 1

    html = DASHBOARD_PATH.read_text(encoding="utf-8")
    lower = html.lower()
    manifest = load_json(MANIFEST_PATH)
    cards = manifest.get("cards", [])
    regression_metric = current_regression_metric()

    forbidden_hits = [
        phrase
        for phrase in FORBIDDEN_PHRASES
        if phrase in lower and phrase not in {"live hardware control", "physical quantum validation", "production qec performance"}
    ]
    # The three boundary phrases are allowed only as explicit non-claims.
    nonclaim_ok = all(
        phrase in lower and re.search(r"(does not claim|no )[^.]*" + re.escape(phrase), lower)
        for phrase in ["physical quantum validation", "production qec performance", "live hardware control"]
    )

    checks = [
        ("manifest_schema", manifest.get("schema_version") == "hqa.evidence_dashboard_manifest.v0", "Manifest schema is V0."),
        ("read_only_mode", manifest.get("execution_mode") == "read_only_static_dashboard", f"Mode: `{manifest.get('execution_mode')}`."),
        ("no_authority", manifest.get("hardware_authority") is False and manifest.get("credential_access") is False and manifest.get("provider_access") is False, "Manifest grants no authority or access."),
        ("card_count", len(cards) == 5, f"Cards: `{len(cards)}`."),
        ("provider_rows", manifest.get("provider_rows") == 6, f"Provider rows: `{manifest.get('provider_rows')}`."),
        ("regression_visible", regression_metric in html, f"Full regression count is visible: `{regression_metric}`."),
        ("provider_replay_visible", "Provider Replay Decisions" in html and "NO_INTERVENTION" in html and "PATCH_ROUTING_REPLAY" in html, "Provider replay decisions are visible."),
        ("boundary_visible", "Shadow-only evidence" in html and "No provider access" in html and "No credentials" in html, "Boundary banner is visible."),
        ("no_interactive_live_controls", "<button" not in lower and "onclick" not in lower and "fetch(" not in lower and "websocket" not in lower, "No buttons, onclick handlers, fetch calls, or sockets."),
        ("forbidden_claims_absent", not forbidden_hits and nonclaim_ok, f"Forbidden hits: `{', '.join(forbidden_hits) or '-'}`; nonclaims ok: `{nonclaim_ok}`."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA evidence dashboard gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
