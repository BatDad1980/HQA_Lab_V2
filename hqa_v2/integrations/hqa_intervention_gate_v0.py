"""HQA Intervention Gate V0.

This gate turns recent stress-run breakpoints into explicit intervention
policy. The goal is not to force HQA into every loop. The goal is to decide
when HQA should stand down, monitor, shadow test, propose remap, or hold.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "hqa_intervention_gate_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_INTERVENTION_GATE_V0.md"


@dataclass(frozen=True)
class InterventionScenario:
    scenario_id: str
    title: str
    vector: str
    metrics: dict[str, Any]
    expected_decision: str
    expected_breakpoint: str


@dataclass(frozen=True)
class InterventionResult:
    scenario_id: str
    title: str
    vector: str
    decision: str
    breakpoint: str
    reviewer_required: bool
    hardware_authority: bool
    reason: str


SCENARIOS = [
    InterventionScenario(
        scenario_id="INT-001",
        title="IBM stable calibration rerun",
        vector="real_device_calibration",
        metrics={
            "backend": "ibm_marrakesh",
            "qubits": 156,
            "degraded_qubits": 55,
            "mean_readout_error": 0.02681,
            "unadapted_fidelity": 0.9854,
            "adapted_fidelity": 0.9561,
            "route_latency_ms": 12.0,
        },
        expected_decision="NO_INTERVENTION",
        expected_breakpoint="adapted_route_underperforms",
    ),
    InterventionScenario(
        scenario_id="INT-002",
        title="IBM unstable calibration style",
        vector="real_device_calibration",
        metrics={
            "backend": "ibm_marrakesh",
            "qubits": 156,
            "degraded_qubits": 55,
            "mean_readout_error": 0.03476,
            "unadapted_fidelity": 0.9727,
            "adapted_fidelity": 0.9756,
            "route_latency_ms": 11.0,
        },
        expected_decision="SHADOW_REMAP_CANDIDATE",
        expected_breakpoint="adapted_route_improves",
    ),
    InterventionScenario(
        scenario_id="INT-003",
        title="A-star routing latency ceiling",
        vector="algorithmic_routing",
        metrics={"grid_nodes": 22500, "route_latency_ms": 205.0, "feedback_budget_ms": 250.0, "quarantine_fraction": 0.95},
        expected_decision="PATCH_ROUTING_REQUIRED",
        expected_breakpoint="latency_near_budget",
    ),
    InterventionScenario(
        scenario_id="INT-004",
        title="A-star routing over budget",
        vector="algorithmic_routing",
        metrics={"grid_nodes": 40000, "route_latency_ms": 390.0, "feedback_budget_ms": 250.0, "quarantine_fraction": 0.95},
        expected_decision="SAFE_HOLD",
        expected_breakpoint="latency_over_budget",
    ),
    InterventionScenario(
        scenario_id="INT-005",
        title="BACL Lamport key overuse",
        vector="cryptographic_boundary",
        metrics={"signatures_observed": 4, "estimated_key_material_exposed": 0.9336},
        expected_decision="KEY_ROTATION_REQUIRED",
        expected_breakpoint="lamport_reuse_risk",
    ),
    InterventionScenario(
        scenario_id="INT-006",
        title="BACL Lamport key exhausted",
        vector="cryptographic_boundary",
        metrics={"signatures_observed": 9, "estimated_key_material_exposed": 1.0},
        expected_decision="HARD_BLOCK",
        expected_breakpoint="lamport_key_exhausted",
    ),
    InterventionScenario(
        scenario_id="INT-007",
        title="Cat optimizer modest gain",
        vector="cat_qubit_noise",
        metrics={"noise_severity": 1.0, "static_fidelity": 0.9489, "adapted_fidelity": 0.9495, "minimum_error_proxy": 0.051},
        expected_decision="MONITOR_WITH_SHADOW_OPTIMIZATION",
        expected_breakpoint="small_positive_delta",
    ),
    InterventionScenario(
        scenario_id="INT-008",
        title="Cat physics unrecoverable",
        vector="cat_qubit_noise",
        metrics={"noise_severity": 100.0, "static_fidelity": 0.0, "adapted_fidelity": 0.0, "minimum_error_proxy": 1.17},
        expected_decision="SAFE_HOLD",
        expected_breakpoint="physics_error_proxy_exceeds_one",
    ),
    InterventionScenario(
        scenario_id="INT-009",
        title="Cognitive advisor under budget",
        vector="cognitive_advisory",
        metrics={"inference_latency_ms": 246.0, "feedback_budget_ms": 250.0, "payload_nodes": 0, "action": "none"},
        expected_decision="ACCEPT_ANNOTATION",
        expected_breakpoint="within_latency_budget",
    ),
    InterventionScenario(
        scenario_id="INT-010",
        title="Cognitive advisor overload",
        vector="cognitive_advisory",
        metrics={"inference_latency_ms": 1242.0, "feedback_budget_ms": 250.0, "payload_nodes": 1000, "degraded_qubits": 500, "action": "quench"},
        expected_decision="REQUIRE_SUMMARY_COMPRESSION",
        expected_breakpoint="advisory_latency_over_budget",
    ),
]


def fidelity_delta(metrics: dict[str, Any]) -> float:
    return float(metrics.get("adapted_fidelity", 0.0)) - float(metrics.get("unadapted_fidelity", metrics.get("static_fidelity", 0.0)))


def evaluate(scenario: InterventionScenario) -> InterventionResult:
    metrics = scenario.metrics
    vector = scenario.vector
    reviewer = True

    if vector == "real_device_calibration":
        delta = fidelity_delta(metrics)
        readout_error = float(metrics["mean_readout_error"])
        if delta < 0:
            decision = "NO_INTERVENTION"
            breakpoint = "adapted_route_underperforms"
            reviewer = False
            reason = "Default compiler route outperformed HQA remap on current calibration. HQA should stand down."
        elif delta > 0 and readout_error >= 0.03:
            decision = "SHADOW_REMAP_CANDIDATE"
            breakpoint = "adapted_route_improves"
            reason = "Calibration is noisy enough and adapted route improved in local shadow comparison."
        else:
            decision = "MONITOR_ONLY"
            breakpoint = "nominal_device"
            reviewer = False
            reason = "Device appears nominal; no remap pressure."
    elif vector == "algorithmic_routing":
        latency = float(metrics["route_latency_ms"])
        budget = float(metrics["feedback_budget_ms"])
        if latency >= budget:
            decision = "SAFE_HOLD"
            breakpoint = "latency_over_budget"
            reason = "Global pathfinding exceeded the feedback budget."
        elif latency >= budget * 0.75:
            decision = "PATCH_ROUTING_REQUIRED"
            breakpoint = "latency_near_budget"
            reason = "Global pathfinding is near feedback budget and should move to patch/local routing."
        else:
            decision = "ACCEPT_SHADOW"
            breakpoint = "within_latency_budget"
            reviewer = False
            reason = "Routing latency remains inside the feedback budget."
    elif vector == "cryptographic_boundary":
        signatures = int(metrics["signatures_observed"])
        exposed = float(metrics["estimated_key_material_exposed"])
        if signatures >= 9 or exposed >= 1.0:
            decision = "HARD_BLOCK"
            breakpoint = "lamport_key_exhausted"
            reason = "Lamport one-time key material is exhausted and must not sign another command."
        elif signatures >= 2 or exposed >= 0.50:
            decision = "KEY_ROTATION_REQUIRED"
            breakpoint = "lamport_reuse_risk"
            reason = "Lamport key reuse risk is too high; rotate before further signing."
        else:
            decision = "ACCEPT_SHADOW"
            breakpoint = "single_use_ok"
            reviewer = False
            reason = "Observed signing remains within one-time key expectations."
    elif vector == "cat_qubit_noise":
        error_proxy = float(metrics["minimum_error_proxy"])
        delta = float(metrics["adapted_fidelity"]) - float(metrics["static_fidelity"])
        if error_proxy >= 1.0:
            decision = "SAFE_HOLD"
            breakpoint = "physics_error_proxy_exceeds_one"
            reason = "Noise model exceeded recoverable probability bounds; optimization cannot preserve useful state."
        elif delta > 0:
            decision = "MONITOR_WITH_SHADOW_OPTIMIZATION"
            breakpoint = "small_positive_delta"
            reviewer = False
            reason = "Cat optimization is bounded and mildly positive; keep it in shadow/monitor mode."
        else:
            decision = "MONITOR_ONLY"
            breakpoint = "no_positive_delta"
            reviewer = False
            reason = "Cat optimization did not improve the static baseline."
    elif vector == "cognitive_advisory":
        latency = float(metrics["inference_latency_ms"])
        budget = float(metrics["feedback_budget_ms"])
        if latency > budget:
            decision = "REQUIRE_SUMMARY_COMPRESSION"
            breakpoint = "advisory_latency_over_budget"
            reason = "Cognitive advisory exceeded the feedback budget; summarize telemetry before model intake."
        else:
            decision = "ACCEPT_ANNOTATION"
            breakpoint = "within_latency_budget"
            reviewer = False
            reason = "Cognitive advisory completed inside the feedback budget and remains annotation-only."
    else:
        decision = "REVIEW_LOCK"
        breakpoint = "unknown_vector"
        reason = "Unknown intervention vector requires human review."

    return InterventionResult(
        scenario_id=scenario.scenario_id,
        title=scenario.title,
        vector=vector,
        decision=decision,
        breakpoint=breakpoint,
        reviewer_required=reviewer,
        hardware_authority=False,
        reason=reason,
    )


def run_gate() -> dict[str, Any]:
    results = [evaluate(scenario) for scenario in SCENARIOS]
    return {
        "schema_version": "hqa.intervention_gate.v0",
        "execution_mode": "shadow_policy_gate",
        "hardware_authority": False,
        "scenario_count": len(results),
        "results": [asdict(result) for result in results],
        "expected": [
            {
                "scenario_id": scenario.scenario_id,
                "expected_decision": scenario.expected_decision,
                "expected_breakpoint": scenario.expected_breakpoint,
            }
            for scenario in SCENARIOS
        ],
        "thresholds": {
            "feedback_budget_ms": 250.0,
            "routing_patch_required_fraction": 0.75,
            "mean_readout_instability_threshold": 0.03,
            "lamport_rotation_after_any_reuse": True,
            "cat_error_proxy_safe_hold": 1.0,
        },
        "boundary": "The intervention gate chooses shadow policy only. It does not authorize live hardware control, backend jobs, pulse changes, or cryptographic signing.",
    }


def write_report(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Intervention Gate V0",
        "",
        "## Purpose",
        "",
        "This report converts recent stress-run breakpoints into explicit intervention policy.",
        "",
        "The gate decides when HQA should stand down, monitor, shadow-test, require patch routing, rotate keys, compress advisory payloads, or enter safe hold.",
        "",
        "## Results",
        "",
        "| Scenario | Vector | Decision | Breakpoint | Reviewer Required | Hardware Authority |",
        "|---|---|---|---|---:|---:|",
    ]
    for result in payload["results"]:
        lines.append(
            f"| `{result['scenario_id']}` {result['title']} | `{result['vector']}` | `{result['decision']}` | `{result['breakpoint']}` | `{result['reviewer_required']}` | `{result['hardware_authority']}` |"
        )

    lines.extend(["", "## Reasons", ""])
    for result in payload["results"]:
        lines.append(f"### `{result['scenario_id']}`")
        lines.append("")
        lines.append(result["reason"])
        lines.append("")

    lines.extend(
        [
            "## Thresholds",
            "",
            "| Threshold | Value |",
            "|---|---:|",
        ]
    )
    for key, value in payload["thresholds"].items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_gate()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_report(payload)
    print(f"HQA intervention gate written: {OUTPUT_PATH}")
    print(f"HQA intervention report written: {REPORT_PATH}")
    for result in payload["results"]:
        print(f"- {result['scenario_id']}: {result['decision']} at {result['breakpoint']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
