"""Build a sample HQA vendor shadow-mode interface packet."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = HQA_V2_ROOT / "outputs" / "vendor_shadow_packet_v1"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_VENDOR_SHADOW_PACKET.md"


def write_json(name: str, payload: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_payloads() -> list[Path]:
    topology = {
        "schema_version": "hqa.topology_snapshot.v1",
        "snapshot_id": "TOPO-DEMO-001",
        "timestamp_utc": "2026-06-01T00:00:00Z",
        "nodes": [
            {"node_id": "Q_0", "status": "healthy", "coherence_score": 0.97, "role": "data"},
            {"node_id": "Q_1", "status": "degraded", "coherence_score": 0.42, "role": "data"},
            {"node_id": "Q_2", "status": "healthy", "coherence_score": 0.96, "role": "ancilla"},
            {"node_id": "Q_3", "status": "healthy", "coherence_score": 0.94, "role": "readout"}
        ],
        "edges": [
            {"source": "Q_0", "target": "Q_1", "coupling_score": 0.81},
            {"source": "Q_0", "target": "Q_2", "coupling_score": 0.93},
            {"source": "Q_2", "target": "Q_3", "coupling_score": 0.88}
        ]
    }
    syndrome = {
        "schema_version": "hqa.syndrome_record.v1",
        "record_id": "SYN-DEMO-001",
        "cycle": 3,
        "source_lane": "qiskit_aer",
        "syndrome_bits": "1110",
        "seed_error": "Q_1",
        "correlated_error": "Q_0",
        "decoder_signal": "CASCADE_LIKE_HISTORY",
        "confidence": 0.91
    }
    quarantine = {
        "schema_version": "hqa.quarantine_decision.v1",
        "decision_id": "QUAR-DEMO-001",
        "target_id": "Q_1",
        "reason": "Repeated syndrome activity with degraded coherence score.",
        "decision": "quarantine",
        "authority": "shadow_advisory",
        "source_records": ["SYN-DEMO-001"]
    }
    reroute = {
        "schema_version": "hqa.reroute_proposal.v1",
        "proposal_id": "ROUTE-DEMO-001",
        "source": "Q_0",
        "destination": "Q_3",
        "proposed_path": ["Q_0", "Q_2", "Q_3"],
        "avoided_targets": ["Q_1"],
        "execution_mode": "shadow_advisory",
        "score": 0.89
    }
    hal = {
        "schema_version": "hqa.hal_manifest.v1",
        "manifest_id": "HAL-DEMO-001",
        "requested_action": "advisory_quarantine_and_route_review",
        "target": "Q_1",
        "execution_mode": "dry_run",
        "safety_boundary": "No physical command emitted. Vendor controller retains authority.",
        "requires_human_approval": True
    }

    return [
        write_json("01_topology_snapshot.json", topology),
        write_json("02_syndrome_record.json", syndrome),
        write_json("03_quarantine_decision.json", quarantine),
        write_json("04_reroute_proposal.json", reroute),
        write_json("05_hal_manifest.json", hal),
    ]


def write_manifest(paths: list[Path]) -> Path:
    manifest = OUT_DIR / "MANIFEST_SHA256.txt"
    lines = [f"{sha256(path)}  {path.name}" for path in paths]
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def write_readme(paths: list[Path], manifest: Path) -> Path:
    readme = OUT_DIR / "README.md"
    lines = [
        "# HQA Vendor Shadow Packet V1",
        "",
        "## Purpose",
        "",
        "This packet demonstrates the HQA V2 shadow-mode data handoff shape.",
        "",
        "It is not a live hardware integration package. It contains only example JSON payloads and hashes.",
        "",
        "## Flow",
        "",
        "1. Read-only topology snapshot.",
        "2. Syndrome record from a simulator or shadow telemetry lane.",
        "3. HQA quarantine decision.",
        "4. HQA reroute proposal.",
        "5. HAL dry-run manifest requiring human/vendor approval.",
        "",
        "## Files",
        "",
    ]
    for path in paths:
        lines.append(f"- `{path.name}`")
    lines.extend(
        [
            f"- `{manifest.name}`",
            "",
            "## Boundary",
            "",
            "This packet grants no live hardware authority and submits no backend jobs.",
            "",
        ]
    )
    readme.write_text("\n".join(lines), encoding="utf-8")
    return readme


def write_report(paths: list[Path], manifest: Path, readme: Path) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Vendor Shadow Packet Report",
        "",
        "## Purpose",
        "",
        "This report records generation of the sample vendor shadow-mode interface packet.",
        "",
        "## Output",
        "",
        f"- Packet directory: `{OUT_DIR}`",
        f"- JSON payloads: `{len(paths)}`",
        f"- Manifest: `{manifest.name}`",
        f"- README: `{readme.name}`",
        "",
        "## Files",
        "",
        "| File | SHA-256 |",
        "|---|---|",
    ]
    for path in [*paths, manifest, readme]:
        lines.append(f"| `{path.name}` | `{sha256(path)}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The packet contains example shadow-mode payloads only. It does not validate physical quantum hardware, submit live jobs, or grant HQA hardware control authority.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    paths = build_payloads()
    manifest = write_manifest(paths)
    readme = write_readme(paths, manifest)
    write_report(paths, manifest, readme)
    print(f"HQA vendor shadow packet written: {OUT_DIR}")
    print(f"HQA vendor shadow packet report written: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
