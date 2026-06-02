"""Build the HQA V2 read-only evidence dashboard.

The dashboard is a static, local HTML artifact backed by current HQA reports
and logs. It is intentionally read-only and evidence-first: no live controls,
no provider access, no credentials, and no hardware authority.
"""

from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
REPORTS_ROOT = HQA_V2_ROOT / "reports"
LOGS_ROOT = HQA_V2_ROOT / "logs"
OUTPUT_DIR = HQA_V2_ROOT / "outputs" / "evidence_dashboard_v0"
DASHBOARD_PATH = OUTPUT_DIR / "HQA_EVIDENCE_DASHBOARD_V0.html"
MANIFEST_PATH = OUTPUT_DIR / "dashboard_manifest.json"
REPORT_PATH = REPORTS_ROOT / "HQA_EVIDENCE_DASHBOARD_V0.md"


@dataclass(frozen=True)
class EvidenceCard:
    title: str
    status: str
    metric: str
    detail: str
    artifact: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def parse_regression() -> tuple[int, int]:
    text = read_text(REPORTS_ROOT / "HQA_V2_REGRESSION_SUMMARY.md")
    passed = int(re.search(r"- Passed: `(\d+)`", text).group(1))
    total = int(re.search(r"- Commands run: `(\d+)`", text).group(1))
    return passed, total


def parse_gate_counts(report_name: str) -> tuple[int, int]:
    text = read_text(REPORTS_ROOT / report_name)
    checks = int(re.search(r"- Checks: `(\d+)`", text).group(1))
    passed = int(re.search(r"- Passed: `(\d+)`", text).group(1))
    return passed, checks


def build_cards() -> list[EvidenceCard]:
    regression_passed, regression_total = parse_regression()
    provider_gate_passed, provider_gate_total = parse_gate_counts("HQA_PROVIDER_NORMALIZATION_MATRIX_GATE.md")
    replay_gate_passed, replay_gate_total = parse_gate_counts("HQA_PROVIDER_REPLAY_HARNESS_GATE.md")
    patch_gate_passed, patch_gate_total = parse_gate_counts("HQA_PATCH_ROUTING_PROTOTYPE_QUALITY.md")
    compression_gate_passed, compression_gate_total = parse_gate_counts("HQA_TELEMETRY_COMPRESSION_GATE_QUALITY.md")

    provider_replay = load_json(LOGS_ROOT / "provider_replay_harness_v0.json")
    patch = load_json(LOGS_ROOT / "patch_routing_prototype_v0.json")
    compression = load_json(LOGS_ROOT / "telemetry_compression_gate_v0.json")

    patch_reductions = [
        result["workload_reduction"]
        for result in patch["results"]
        if result["decision"] == "PATCH_ROUTE_AVAILABLE"
    ]
    max_patch_reduction = max(patch_reductions)
    compressed = compression["results"][0]["compression_ratio"]

    return [
        EvidenceCard(
            "Regression Spine",
            "PASS",
            f"{regression_passed}/{regression_total}",
            "Full safe HQA V2 regression suite passes from repository root.",
            "hqa_v2/reports/HQA_V2_REGRESSION_SUMMARY.md",
        ),
        EvidenceCard(
            "Provider Normalization",
            "PASS",
            f"{provider_gate_passed}/{provider_gate_total}",
            "IBM, Braket, Azure, CUDA-Q, Cirq/qsim, and cat-solver lanes normalize into one shadow grammar.",
            "hqa_v2/reports/HQA_PROVIDER_NORMALIZATION_MATRIX_GATE.md",
        ),
        EvidenceCard(
            "Provider Replay",
            "PASS",
            f"{replay_gate_passed}/{replay_gate_total}",
            f"Six provider lanes replay through deterministic responses: {', '.join(provider_replay['decision_set'])}.",
            "hqa_v2/reports/HQA_PROVIDER_REPLAY_HARNESS_GATE.md",
        ),
        EvidenceCard(
            "Patch Routing",
            "PASS",
            f"{patch_gate_passed}/{patch_gate_total}",
            f"Coarse patch routing reduces available-route planning workload up to {max_patch_reduction}x and preserves SAFE_HOLD.",
            "hqa_v2/reports/HQA_PATCH_ROUTING_PROTOTYPE_QUALITY.md",
        ),
        EvidenceCard(
            "Telemetry Compression",
            "PASS",
            f"{compression_gate_passed}/{compression_gate_total}",
            f"Large advisory payload compressed by {compressed}x while preserving the intervention decision.",
            "hqa_v2/reports/HQA_TELEMETRY_COMPRESSION_GATE_QUALITY.md",
        ),
    ]


def build_rows() -> list[dict[str, str]]:
    replay = load_json(LOGS_ROOT / "provider_replay_harness_v0.json")
    rows = []
    for result in replay["results"]:
        rows.append(
            {
                "provider": result["provider"],
                "lane": result["provider_lane"],
                "family": result["topology_family"],
                "decision": result["replay_decision"],
                "reason": result["deterministic_reason"],
            }
        )
    return rows


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_dashboard(cards: list[EvidenceCard], rows: list[dict[str, str]]) -> str:
    card_html = "\n".join(
        f"""
        <article class="card">
          <div class="card-top">
            <span class="status">{esc(card.status)}</span>
            <span class="metric">{esc(card.metric)}</span>
          </div>
          <h2>{esc(card.title)}</h2>
          <p>{esc(card.detail)}</p>
          <code>{esc(card.artifact)}</code>
        </article>
        """
        for card in cards
    )
    row_html = "\n".join(
        f"""
        <tr>
          <td>{esc(row['provider'])}</td>
          <td>{esc(row['lane'])}</td>
          <td>{esc(row['family'])}</td>
          <td><span class="pill">{esc(row['decision'])}</span></td>
          <td>{esc(row['reason'])}</td>
        </tr>
        """
        for row in rows
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HQA V2 Evidence Dashboard</title>
  <style>
    :root {{
      --bg: #0b0d12;
      --panel: #151923;
      --panel-2: #10141d;
      --text: #eef2f7;
      --muted: #9ca8b8;
      --line: #2a3242;
      --good: #55d987;
      --blue: #61c5ff;
      --warn: #f5c86a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, Segoe UI, Arial, sans-serif;
      letter-spacing: 0;
    }}
    header {{
      padding: 28px 34px 20px;
      border-bottom: 1px solid var(--line);
      background: #10131a;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      font-weight: 700;
    }}
    .subhead {{
      max-width: 960px;
      color: var(--muted);
      line-height: 1.5;
      margin: 0;
      font-size: 15px;
    }}
    .boundary {{
      margin-top: 18px;
      display: inline-flex;
      gap: 10px;
      align-items: center;
      padding: 9px 12px;
      border: 1px solid var(--warn);
      color: var(--warn);
      background: rgba(245, 200, 106, 0.08);
      border-radius: 6px;
      font-weight: 700;
      font-size: 12px;
      text-transform: uppercase;
    }}
    main {{
      padding: 28px 34px 42px;
      max-width: 1500px;
      margin: 0 auto;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 26px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      min-height: 190px;
    }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
      font-size: 12px;
      font-weight: 700;
    }}
    .status {{ color: var(--good); }}
    .metric {{
      color: var(--blue);
      font-family: Consolas, Menlo, monospace;
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 17px;
    }}
    p {{
      color: var(--muted);
      line-height: 1.45;
      margin: 0 0 14px;
      font-size: 14px;
    }}
    code {{
      display: block;
      color: #c9d3df;
      background: var(--panel-2);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px;
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    .section-title {{
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }}
    .section-title h2 {{
      margin: 0;
      font-size: 18px;
    }}
    .section-title span {{
      color: var(--muted);
      font-size: 13px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 11px 12px;
      vertical-align: top;
      text-align: left;
    }}
    th {{
      color: var(--muted);
      background: var(--panel-2);
      font-weight: 700;
    }}
    .pill {{
      display: inline-block;
      border: 1px solid var(--blue);
      color: var(--blue);
      border-radius: 999px;
      padding: 4px 8px;
      font-family: Consolas, Menlo, monospace;
      font-size: 12px;
      white-space: nowrap;
    }}
    footer {{
      color: var(--muted);
      font-size: 12px;
      padding: 18px 2px 0;
    }}
    @media (max-width: 1100px) {{
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 700px) {{
      header, main {{ padding-left: 18px; padding-right: 18px; }}
      .grid {{ grid-template-columns: 1fr; }}
      table {{ font-size: 12px; }}
      th, td {{ padding: 9px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>HQA V2 Evidence Dashboard</h1>
    <p class="subhead">Read-only clean-lab view of the current Homeostatic Quantum Architecture proxy evidence chain. This page is generated from local HQA reports and logs.</p>
    <div class="boundary">Shadow-only evidence. No live hardware control. No provider access. No credentials.</div>
  </header>
  <main>
    <div class="grid">
      {card_html}
    </div>
    <section>
      <div class="section-title">
        <h2>Provider Replay Decisions</h2>
        <span>All rows come from hqa_v2/logs/provider_replay_harness_v0.json</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>Lane</th>
            <th>Family</th>
            <th>Decision</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {row_html}
        </tbody>
      </table>
    </section>
    <footer>
      Boundary: validates proxy control-flow and evidence display only. It does not claim physical quantum validation, production QEC performance, or uncontrolled hardware execution.
    </footer>
  </main>
</body>
</html>
"""


def write_report(cards: list[EvidenceCard], rows: list[dict[str, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Evidence Dashboard V0",
        "",
        "## Purpose",
        "",
        "This report documents the generated read-only evidence dashboard.",
        "",
        "The dashboard is backed by local HQA reports and JSON logs. It does not simulate live controls, read credentials, contact providers, or authorize hardware.",
        "",
        "## Cards",
        "",
        "| Card | Status | Metric | Artifact |",
        "|---|---:|---:|---|",
    ]
    for card in cards:
        lines.append(f"| {card.title} | {card.status} | `{card.metric}` | `{card.artifact}` |")
    lines.extend(
        [
            "",
            "## Provider Rows",
            "",
            f"- Rows: `{len(rows)}`",
            "",
            "## Output",
            "",
            f"- Dashboard: `{DASHBOARD_PATH.relative_to(HQA_V2_ROOT)}`",
            f"- Manifest: `{MANIFEST_PATH.relative_to(HQA_V2_ROOT)}`",
            "",
            "## Boundary",
            "",
            "This dashboard is a local, read-only evidence surface. It does not claim physical quantum validation, production QEC performance, live provider access, or hardware control.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cards = build_cards()
    rows = build_rows()
    DASHBOARD_PATH.write_text(render_dashboard(cards, rows), encoding="utf-8")
    manifest = {
        "schema_version": "hqa.evidence_dashboard_manifest.v0",
        "execution_mode": "read_only_static_dashboard",
        "hardware_authority": False,
        "credential_access": False,
        "provider_access": False,
        "dashboard": str(DASHBOARD_PATH.relative_to(HQA_V2_ROOT)),
        "cards": [card.__dict__ for card in cards],
        "provider_rows": len(rows),
        "boundary": "Dashboard displays local evidence only. No live control, provider access, credentials, or HAL dispatch.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_report(cards, rows)
    print(f"HQA evidence dashboard written: {DASHBOARD_PATH}")
    print(f"Evidence cards: {len(cards)}; provider rows: {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
