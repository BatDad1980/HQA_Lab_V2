"""Build shadow adaptive proposals from HQA Risk Field V0.

This layer translates risk ranking into reviewable artifacts. It does not
execute quarantine, reroute, or HAL commands.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
RISK_FIELD_PATH = HQA_V2_ROOT / "logs" / "hqa_risk_field_v0.json"
VENDOR_PACKET_ROOT = HQA_V2_ROOT / "outputs" / "vendor_shadow_packet_v1"
REROUTE_TEMPLATE_PATH = VENDOR_PACKET_ROOT / "04_reroute_proposal.json"
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "shadow_adaptive_proposal_v0"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_SHADOW_ADAPTIVE_PROPOSAL_V0.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def source_records(risk_field: dict[str, Any]) -> list[str]:
    records: list[str] = []
    source_syndrome = risk_field.get("source_syndrome")
    if isinstance(source_syndrome, str):
        records.append(source_syndrome)
    records.append("logs/hqa_risk_field_v0.json")
    return records


def quarantine_decision(risk_field: dict[str, Any]) -> dict[str, Any]:
    target = str(risk_field["suspected_patch"])
    action = str(risk_field["recommended_advisory_action"])
    decision = "quarantine" if "QUARANTINE" in action else "monitor"
    return {
        "schema_version": "hqa.quarantine_decision.v1",
        "decision_id": "QUAR-RISK-FIELD-V0-001",
        "target_id": target,
        "reason": f"Risk Field V0 ranked `{target}` highest under `{action}` with advisory-only authority.",
        "decision": decision,
        "authority": "shadow_advisory",
        "source_records": source_records(risk_field),
    }


def reroute_review(risk_field: dict[str, Any]) -> dict[str, Any]:
    template = load_json(REROUTE_TEMPLATE_PATH) if REROUTE_TEMPLATE_PATH.exists() else {}
    target = str(risk_field["suspected_patch"])
    proposed_path = template.get("proposed_path", [])
    avoided_targets = sorted(set(template.get("avoided_targets", []) + [target]))
    return {
        "schema_version": "hqa.shadow_reroute_review.v0",
        "review_id": "ROUTE-REVIEW-RISK-FIELD-V0-001",
        "source_proposal": template.get("proposal_id", "unknown"),
        "risk_field_id": risk_field.get("field_id"),
        "suspected_patch": target,
        "proposed_path": proposed_path,
        "avoided_targets": avoided_targets,
        "execution_mode": "shadow_advisory",
        "requires_vendor_review": True,
        "boundary": "Route review only; no live routing table, backend, or control plane is modified.",
    }


def hal_manifest(risk_field: dict[str, Any]) -> dict[str, Any]:
    target = str(risk_field["suspected_patch"])
    action = str(risk_field["recommended_advisory_action"]).lower()
    return {
        "schema_version": "hqa.hal_manifest.v1",
        "manifest_id": "HAL-RISK-FIELD-V0-001",
        "requested_action": f"dry_run_review_{action}",
        "target": target,
        "execution_mode": "dry_run",
        "safety_boundary": "No physical command emitted. Vendor controller retains authority.",
        "requires_human_approval": True,
    }


def manifest(paths: list[Path]) -> str:
    lines = []
    for path in sorted(paths):
        lines.append(f"{sha256(path)}  {path.name}")
    return "\n".join(lines) + "\n"


def write_report(payloads: dict[str, dict[str, Any]], manifest_path: Path) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    quarantine = payloads["quarantine"]
    reroute = payloads["reroute"]
    hal = payloads["hal"]
    lines = [
        "# HQA Shadow Adaptive Proposal V0",
        "",
        "## Purpose",
        "",
        "This report translates HQA Risk Field V0 into reviewable shadow-mode control artifacts.",
        "",
        "The output is intentionally non-executing. It proposes what a vendor/operator should review next; it does not modify hardware, backend topology, pulse schedules, or routing tables.",
        "",
        "## Generated Artifacts",
        "",
        "| Artifact | Purpose | Authority |",
        "|---|---|---|",
        "| `01_quarantine_decision.json` | Review whether the suspected patch should be quarantined or monitored. | `shadow_advisory` |",
        "| `02_reroute_review.json` | Review route avoidance around the suspected patch. | `shadow_advisory` |",
        "| `03_hal_dry_run_manifest.json` | Review the HAL-facing dry-run request boundary. | `dry_run` |",
        "| `MANIFEST_SHA256.txt` | Tamper-evident hashes for the generated artifacts. | n/a |",
        "",
        "## Summary",
        "",
        f"- Suspected patch: `{reroute['suspected_patch']}`",
        f"- Quarantine decision: `{quarantine['decision']}`",
        f"- HAL requested action: `{hal['requested_action']}`",
        f"- Manifest: `{manifest_path.relative_to(HQA_V2_ROOT)}`",
        "",
        "## Boundary",
        "",
        "Shadow Adaptive Proposal V0 is a review packet only. It does not authorize live quantum hardware actions, live backend jobs, live pulse changes, or physical HAL execution.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_packet() -> dict[str, Path]:
    risk_field = load_json(RISK_FIELD_PATH)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    payloads = {
        "quarantine": quarantine_decision(risk_field),
        "reroute": reroute_review(risk_field),
        "hal": hal_manifest(risk_field),
    }
    paths = {
        "quarantine": OUTPUT_ROOT / "01_quarantine_decision.json",
        "reroute": OUTPUT_ROOT / "02_reroute_review.json",
        "hal": OUTPUT_ROOT / "03_hal_dry_run_manifest.json",
    }
    for key, path in paths.items():
        write_json(path, payloads[key])

    manifest_path = OUTPUT_ROOT / "MANIFEST_SHA256.txt"
    manifest_path.write_text(manifest(list(paths.values())), encoding="utf-8")
    paths["manifest"] = manifest_path
    write_report(payloads, manifest_path)
    return paths


def main() -> int:
    if not RISK_FIELD_PATH.exists():
        print(f"HQA shadow adaptive proposal missing risk field: {RISK_FIELD_PATH}")
        return 1
    paths = build_packet()
    print(f"HQA shadow adaptive proposal written: {OUTPUT_ROOT}")
    for name, path in paths.items():
        print(f"- {name}: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
