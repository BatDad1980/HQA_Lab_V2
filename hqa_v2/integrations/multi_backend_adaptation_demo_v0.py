"""Multi-backend hardware-adaptive demonstration for HQA V2.

THE CLAIM THIS MAKES CONCRETE
-----------------------------
"Route to whichever chip you plug in." HQA ingests each backend's *own* snapshotted
calibration, normalizes it into one health vocabulary, and produces a per-hardware
quarantine + routing decision. Because the chips genuinely differ, the decisions
genuinely differ -- with the same code, at zero cost, submitting zero jobs.

WHY THIS IS FREE AND HONEST
---------------------------
Qiskit's fake_provider ships real, snapshotted calibration data (T1, T2, readout
error, coupling map) from IBM devices. We read that bundled metadata only. We do
NOT contact IBM, submit jobs, read credentials, or touch hardware. Running a
circuit on a live QPU would cost ~$96/second; reading the snapshot costs nothing.

WHAT IT DOES AND DOES NOT SHOW
------------------------------
Shows: one normalization + adaptation pipeline consumes several *different* real
device snapshots and adapts its degraded-region map and routing per device.
Does NOT show: improved physical fidelity, live control, QEC, or that HQA's route
is optimal. It is an advisory, calibration-derived analysis.
"""

from __future__ import annotations

import json
import sys
import warnings
from collections import deque
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore")

HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = HQA_V2_ROOT / "logs" / "multi_backend_adaptation_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_MULTI_BACKEND_ADAPTATION_V0.md"

# Provider-neutral health thresholds (one vocabulary for every backend).
# Matches the thresholds documented in the earlier IBM calibration work.
T1_MIN_US = 100.0
T2_MIN_US = 40.0
READOUT_MAX = 0.030

# Real snapshotted backends to adapt across (mixed processor families/sizes).
CANDIDATES = [
    "FakeFez",          # Heron r2, 156q
    "FakeMarrakesh",    # Heron r2, 156q
    "FakeTorino",       # Heron r1, 133q
    "FakeSherbrooke",   # Eagle r3, 127q
    "FakeBrisbane",     # Eagle r3, 127q
    "FakeOsaka",        # Eagle r3, 127q
]


def load_backends() -> list[Any]:
    import qiskit_ibm_runtime.fake_provider as fp

    backends = []
    for name in CANDIDATES:
        cls = getattr(fp, name, None)
        if cls is None:
            continue
        try:
            backends.append(cls())
        except Exception:
            continue
    return backends


def _readout_error(target, q: int) -> float | None:
    try:
        return float(target["measure"][(q,)].error)
    except Exception:
        return None


def _two_qubit_gate_name(target) -> str | None:
    for name in ("ecr", "cz", "cx"):
        if name in target.operation_names:
            return name
    return None


def ingest(backend: Any) -> dict[str, Any]:
    """Pull the real snapshot into a provider-neutral health profile."""
    target = backend.target
    n = backend.num_qubits

    edges = set()
    for pair in (backend.coupling_map or []):
        a, b = int(pair[0]), int(pair[1])
        edges.add((min(a, b), max(a, b)))

    t1s, t2s, ros = [], [], []
    statuses: dict[int, str] = {}
    for q in range(n):
        try:
            qp = target.qubit_properties[q]
            t1 = qp.t1 * 1e6 if qp.t1 else None
            t2 = qp.t2 * 1e6 if qp.t2 else None
        except Exception:
            t1 = t2 = None
        ro = _readout_error(target, q)
        if t1 is not None:
            t1s.append(t1)
        if t2 is not None:
            t2s.append(t2)
        if ro is not None:
            ros.append(ro)

        reasons = []
        if t1 is not None and t1 < T1_MIN_US:
            reasons.append("T1")
        if t2 is not None and t2 < T2_MIN_US:
            reasons.append("T2")
        if ro is not None and ro > READOUT_MAX:
            reasons.append("readout")
        statuses[q] = "DEGRADED" if reasons else "HEALTHY"

    degraded = [q for q, s in statuses.items() if s == "DEGRADED"]
    healthy = [q for q, s in statuses.items() if s == "HEALTHY"]

    return {
        "backend": backend.name,
        "num_qubits": n,
        "coupling_edges": len(edges),
        "edges": edges,
        "mean_t1_us": round(sum(t1s) / len(t1s), 2) if t1s else None,
        "mean_t2_us": round(sum(t2s) / len(t2s), 2) if t2s else None,
        "mean_readout_error": round(sum(ros) / len(ros), 5) if ros else None,
        "two_qubit_gate": _two_qubit_gate_name(target),
        "degraded_qubits": degraded,
        "healthy_qubits": healthy,
    }


def _healthy_adjacency(profile: dict[str, Any]) -> dict[int, list[int]]:
    healthy = set(profile["healthy_qubits"])
    adj: dict[int, list[int]] = {q: [] for q in healthy}
    for a, b in profile["edges"]:
        if a in healthy and b in healthy:
            adj[a].append(b)
            adj[b].append(a)
    return adj


def healthy_components(profile: dict[str, Any]) -> tuple[dict[int, list[int]], list[list[int]]]:
    adj = _healthy_adjacency(profile)
    seen: set[int] = set()
    comps: list[list[int]] = []
    for start in adj:
        if start in seen:
            continue
        comp: list[int] = []
        dq = deque([start])
        seen.add(start)
        while dq:
            node = dq.popleft()
            comp.append(node)
            for nb in adj[node]:
                if nb not in seen:
                    seen.add(nb)
                    dq.append(nb)
        comps.append(comp)
    return adj, comps


def _bfs_farthest(adj: dict[int, list[int]], src: int, allowed: set[int]):
    dist = {src: 0}
    came: dict[int, int | None] = {src: None}
    far = src
    dq = deque([src])
    while dq:
        node = dq.popleft()
        for nb in adj[node]:
            if nb in allowed and nb not in dist:
                dist[nb] = dist[node] + 1
                came[nb] = node
                dq.append(nb)
                if dist[nb] > dist[far]:
                    far = nb
    return far, came


def longest_corridor(adj: dict[int, list[int]], comp: list[int]) -> list[int] | None:
    """Longest all-healthy corridor in a component (double-BFS diameter path)."""
    if len(comp) < 2:
        return None
    allowed = set(comp)
    u, _ = _bfs_farthest(adj, comp[0], allowed)
    v, came = _bfs_farthest(adj, u, allowed)
    path = []
    cur: int | None = v
    while cur is not None:
        path.append(cur)
        cur = came[cur]
    return list(reversed(path))


def adapt(profile: dict[str, Any]) -> dict[str, Any]:
    n = profile["num_qubits"]
    adj, comps = healthy_components(profile)
    comps.sort(key=len, reverse=True)
    largest = comps[0] if comps else []
    corridor = longest_corridor(adj, largest) if len(largest) >= 2 else None
    return {
        "quarantine_count": len(profile["degraded_qubits"]),
        "quarantine_pct": round(100.0 * len(profile["degraded_qubits"]) / n, 1),
        "healthy_regions": len(comps),
        "largest_healthy_region": len(largest),
        "longest_corridor_hops": (len(corridor) - 1) if corridor else 0,
        "longest_corridor_endpoints": [corridor[0], corridor[-1]] if corridor else None,
    }


def run() -> dict[str, Any]:
    backends = load_backends()
    rows = []
    for backend in backends:
        profile = ingest(backend)
        decision = adapt(profile)
        rows.append(
            {
                "backend": profile["backend"],
                "num_qubits": profile["num_qubits"],
                "coupling_edges": profile["coupling_edges"],
                "two_qubit_gate": profile["two_qubit_gate"],
                "mean_t1_us": profile["mean_t1_us"],
                "mean_t2_us": profile["mean_t2_us"],
                "mean_readout_error": profile["mean_readout_error"],
                "decision": decision,
            }
        )
    return {
        "schema_version": "hqa.multi_backend_adaptation.v0",
        "execution_mode": "snapshot_calibration_adaptation",
        "hardware_authority": False,
        "jobs_submitted": 0,
        "credential_access": False,
        "health_thresholds": {
            "t1_min_us": T1_MIN_US,
            "t2_min_us": T2_MIN_US,
            "readout_max": READOUT_MAX,
        },
        "backends_adapted": len(rows),
        "rows": rows,
        "boundary": (
            "Reads Qiskit-bundled snapshotted device calibration only. No live IBM "
            "access, no jobs submitted, no credentials, no hardware authority. "
            "Advisory calibration-derived analysis; not a fidelity or QEC claim."
        ),
    }


def write_report(payload: dict[str, Any]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    th = payload["health_thresholds"]
    L = [
        "# HQA Multi-Backend Hardware-Adaptive Demonstration V0",
        "",
        "*Reads Qiskit-bundled snapshotted device calibration only. Zero jobs submitted,",
        "no credentials, no hardware authority. Calibration-derived advisory analysis --",
        "not a fidelity, control, or QEC claim.*",
        "",
        "## What this shows",
        "",
        "One HQA pipeline ingests several **different real device snapshots**, normalizes",
        "each into the same health vocabulary, and produces a per-hardware quarantine and",
        "routing decision. The chips differ, so the decisions differ -- with the same code.",
        "",
        f"Health thresholds (identical for every backend): T1 < {th['t1_min_us']} us, "
        f"T2 < {th['t2_min_us']} us, readout > {th['readout_max']}.",
        "",
        "| Backend | Qubits | Edges | 2q gate | Mean T1 (us) | Mean T2 (us) | Mean readout | Quarantined | Healthy regions | Largest region | Longest healthy corridor |",
        "|---|---:|---:|:--:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in payload["rows"]:
        d = r["decision"]
        ep = d["longest_corridor_endpoints"]
        corridor = f"{d['longest_corridor_hops']} hops ({ep[0]}→{ep[1]})" if ep else "—"
        L.append(
            f"| `{r['backend']}` | {r['num_qubits']} | {r['coupling_edges']} | "
            f"{r['two_qubit_gate']} | {r['mean_t1_us']} | {r['mean_t2_us']} | "
            f"{r['mean_readout_error']} | {d['quarantine_count']} ({d['quarantine_pct']}%) | "
            f"{d['healthy_regions']} | {d['largest_healthy_region']} | {corridor} |"
        )
    L += [
        "",
        "## Reading the result",
        "",
        "- **Quarantined** differs per chip because each device's real T1/T2/readout snapshot",
        "  differs -- HQA adapts its degraded-region map to the hardware in front of it.",
        "- **Largest healthy region** is the biggest contiguous all-healthy patch left after",
        "  quarantine: a per-device answer to 'how much usable fabric remains, and where.'",
        "- **Longest healthy corridor** is the longest all-healthy path HQA can offer on that",
        "  chip (its diameter through healthy qubits) -- a route that actually exists, with",
        "  different length and endpoints per device.",
        "",
        "The point is not any single number; it is that the *same normalization and",
        "adaptation logic* produces hardware-appropriate, materially different decisions",
        "across real IBM device snapshots, at zero cost.",
        "",
        "## Scope note",
        "",
        "Real-data anchors here are IBM snapshots (the free real calibration available).",
        "Non-IBM providers are covered as dialects in `HQA_PROVIDER_NORMALIZATION_MATRIX_V0`",
        "using representative fixtures; live cross-vendor snapshots would require partner data.",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        "",
    ]
    REPORT_PATH.write_text("\n".join(L), encoding="utf-8")


def main() -> int:
    payload = run()
    write_report(payload)
    print(f"Report: {REPORT_PATH}")
    print(f"Backends adapted: {payload['backends_adapted']} (jobs submitted: {payload['jobs_submitted']})")
    for r in payload["rows"]:
        d = r["decision"]
        print(
            f"  {r['backend']:<16} q={r['num_qubits']:<4} quarantined={d['quarantine_count']:<3}"
            f"({d['quarantine_pct']}%)  largest_healthy={d['largest_healthy_region']:<4}"
            f"corridor={d['longest_corridor_hops']}h"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
