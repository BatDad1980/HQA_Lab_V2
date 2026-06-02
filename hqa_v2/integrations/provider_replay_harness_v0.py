"""Provider Replay Harness V0 for HQA V2.

Provider Normalization Matrix V0 proves that major provider dialects can enter
one HQA shadow grammar. This harness proves the next step: normalized packets
from each lane can be replayed through one deterministic response grammar.

No provider SDKs are imported. No credentials are read. No jobs are submitted.
No live hardware or HAL actions are authorized.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "provider_replay_harness_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_PROVIDER_REPLAY_HARNESS_V0.md"

if str(HQA_V2_ROOT) not in sys.path:
    sys.path.insert(0, str(HQA_V2_ROOT))

from integrations.provider_normalization_matrix_v0 import run_matrix  # noqa: E402


@dataclass(frozen=True)
class ProviderReplayResult:
    provider: str
    provider_lane: str
    topology_family: str
    replay_decision: str
    deterministic_reason: str
    reviewer_required: bool
    normalized_features_used: list[str]
    hardware_authority: bool
    credential_access: bool
    live_job_submitted: bool


def decide_replay(packet: dict[str, Any]) -> ProviderReplayResult:
    features = packet["normalized_features"]
    risk = features.get("risk_inputs", {})
    topology = features.get("topology_inputs", {})
    latency = features.get("latency_inputs", {})
    provider = packet["provider"]
    family = packet["topology_family"]

    used = ["risk_inputs", "topology_inputs"]
    reviewer_required = False

    if family == "heavy_hex":
        defect_density = float(risk.get("defect_density", 0.0))
        readout_error = float(risk.get("readout_error", 0.0))
        if readout_error < 0.03:
            decision = "NO_INTERVENTION"
            reason = "Heavy-hex calibration is below readout instability threshold; HQA stands down."
        elif defect_density >= 0.25:
            decision = "SHADOW_REMAP_CANDIDATE"
            reason = "Heavy-hex defect density is elevated under noisy readout; shadow remap is reviewable."
            reviewer_required = True
        else:
            decision = "MONITOR_ONLY"
            reason = "Heavy-hex packet is noncritical; monitor without remap."
    elif family == "grid_lattice":
        patch_alert_density = float(risk.get("patch_alert_density", 0.0))
        depth = int(risk.get("depth", 0))
        if patch_alert_density >= 0.05 and depth >= 40:
            decision = "PATCH_ROUTING_REPLAY"
            reason = "Grid/lattice packet has enough local patch pressure to exercise patch-routing replay."
            reviewer_required = True
        else:
            decision = "MONITOR_ONLY"
            reason = "Grid/lattice packet does not justify patch rerouting."
    elif family == "bosonic_cat":
        parity = float(risk.get("parity_persistence", 0.0))
        photon_loss = float(risk.get("photon_loss_rate", 0.0))
        if parity >= 0.9 and photon_loss < 0.01:
            decision = "MONITOR_WITH_SHADOW_OPTIMIZATION"
            reason = "Cat solver packet is stable enough for bounded shadow optimization monitoring."
        else:
            decision = "SAFE_HOLD"
            reason = "Cat solver packet falls outside stable parity/loss bounds."
            reviewer_required = True
    else:
        if provider == "nvidia_cuda_q":
            used.append("latency_inputs")
            budget = latency.get("latency_budget_ms")
            if budget and float(budget) <= 250:
                decision = "ACCEPT_SIMULATOR_REPLAY"
                reason = "CUDA-Q packet is local simulator metadata inside the latency budget."
            else:
                decision = "REQUIRE_LATENCY_REVIEW"
                reason = "CUDA-Q packet lacks a bounded latency budget."
                reviewer_required = True
        elif provider in {"aws_braket", "azure_quantum"}:
            decision = "METADATA_ONLY_REPLAY"
            reason = "Aggregator packet is provider metadata only; no intervention decision can be promoted."
        else:
            decision = "REVIEW_LOCK"
            reason = "Unknown neutral provider requires manual review."
            reviewer_required = True

    return ProviderReplayResult(
        provider=provider,
        provider_lane=packet["provider_lane"],
        topology_family=family,
        replay_decision=decision,
        deterministic_reason=reason,
        reviewer_required=reviewer_required,
        normalized_features_used=used,
        hardware_authority=False,
        credential_access=False,
        live_job_submitted=False,
    )


def run_replay() -> dict[str, Any]:
    matrix = run_matrix()
    results = [decide_replay(packet) for packet in matrix["packets"]]
    payload = {
        "schema_version": "hqa.provider_replay_harness.v0",
        "execution_mode": "shadow_replay_only",
        "hardware_authority": False,
        "credential_access": False,
        "live_jobs_submitted": False,
        "provider_count": len(results),
        "results": [asdict(result) for result in results],
        "decision_set": sorted({result.replay_decision for result in results}),
        "boundary": (
            "Provider replay validates deterministic shadow responses to normalized telemetry. "
            "It does not contact providers, submit jobs, prove provider performance, or authorize hardware control."
        ),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Provider Replay Harness V0",
        "",
        "## Purpose",
        "",
        "This report verifies that normalized provider packets can be replayed through one deterministic HQA response grammar.",
        "",
        "The harness is shadow-only: it does not import cloud SDKs, read credentials, submit jobs, or authorize HAL actions.",
        "",
        "## Results",
        "",
        f"- Providers replayed: `{payload['provider_count']}`",
        f"- Execution mode: `{payload['execution_mode']}`",
        f"- Hardware authority: `{payload['hardware_authority']}`",
        f"- Credential access: `{payload['credential_access']}`",
        f"- Live jobs submitted: `{payload['live_jobs_submitted']}`",
        f"- Decision set: `{', '.join(payload['decision_set'])}`",
        "",
        "| Provider | Lane | Family | Replay Decision | Reviewer Required | Reason |",
        "|---|---|---|---|---:|---|",
    ]
    for result in payload["results"]:
        lines.append(
            f"| `{result['provider']}` | `{result['provider_lane']}` | `{result['topology_family']}` | `{result['replay_decision']}` | `{result['reviewer_required']}` | {result['deterministic_reason']} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_replay()
    write_report(payload)
    print(f"HQA provider replay harness written: {REPORT_PATH}")
    print(f"Providers replayed: {payload['provider_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
