"""Quality gate for HQA Provider Replay Harness V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "provider_replay_harness_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_PROVIDER_REPLAY_HARNESS_GATE.md"


EXPECTED_PROVIDERS = {
    "ibm_qiskit_runtime",
    "aws_braket",
    "azure_quantum",
    "nvidia_cuda_q",
    "cirq_qsim",
    "qutip_dynamiqs",
}


def load_payload() -> dict[str, Any]:
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA Provider Replay Harness Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that all normalized provider lanes replay through bounded deterministic HQA responses.",
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
            "This gate validates shadow replay only. It does not validate live provider access, physical quantum performance, production QEC, credentials, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not OUTPUT_PATH.exists():
        checks = [("replay_output_exists", False, "Run provider_replay_harness_v0.py first.")]
        write_report(checks)
        print(f"HQA provider replay harness gate written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    results = payload.get("results", [])
    providers = {result.get("provider") for result in results}
    decisions = {result.get("replay_decision") for result in results}
    provider_to_decision = {result.get("provider"): result.get("replay_decision") for result in results}

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.provider_replay_harness.v0", "Replay schema is V0."),
        ("shadow_only", payload.get("execution_mode") == "shadow_replay_only", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", payload.get("hardware_authority") is False and all(result.get("hardware_authority") is False for result in results), "Replay grants no hardware authority."),
        ("no_credentials", payload.get("credential_access") is False and all(result.get("credential_access") is False for result in results), "Replay reads no credentials."),
        ("no_live_jobs", payload.get("live_jobs_submitted") is False and all(result.get("live_job_submitted") is False for result in results), "Replay submits no jobs."),
        ("provider_coverage", providers == EXPECTED_PROVIDERS, f"Providers: `{', '.join(sorted(str(provider) for provider in providers))}`."),
        ("provider_count", len(results) == 6, f"Results: `{len(results)}`."),
        ("ibm_stands_down", provider_to_decision.get("ibm_qiskit_runtime") == "NO_INTERVENTION", "IBM stable calibration replays as stand-down."),
        ("cuda_replay", provider_to_decision.get("nvidia_cuda_q") == "ACCEPT_SIMULATOR_REPLAY", "CUDA-Q metadata replays as simulator replay."),
        ("cat_shadow_optimization", provider_to_decision.get("qutip_dynamiqs") == "MONITOR_WITH_SHADOW_OPTIMIZATION", "Cat solver lane replays as shadow optimization monitor."),
        ("grid_patch_replay", provider_to_decision.get("cirq_qsim") == "PATCH_ROUTING_REPLAY", "Grid/lattice lane exercises patch-routing replay."),
        ("aggregators_metadata_only", provider_to_decision.get("aws_braket") == "METADATA_ONLY_REPLAY" and provider_to_decision.get("azure_quantum") == "METADATA_ONLY_REPLAY", "Aggregator lanes remain metadata-only."),
        ("decision_diversity", len(decisions) >= 5, f"Decision set size: `{len(decisions)}`."),
        ("features_used", all(result.get("normalized_features_used") for result in results), "Every replay declares normalized feature classes used."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA provider replay harness gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
