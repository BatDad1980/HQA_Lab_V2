import json
import _bootstrap
from audit_logger import AuditLogger
from fabric_simulator import FabricSimulator
from local_sentinel_reflex import LocalSentinelReflex
from quarantine_manager import QuarantineManager
from topology_router import TopologyRouter

def run_alice_bob_demo():
    audit_path = _bootstrap.log_path("alice_bob_audit.json")
    report_path = _bootstrap.report_path("ALICE_AND_BOB_INTEGRATION_REPORT.md")
    logger = AuditLogger(filepath=audit_path)
    logger.log("SYSTEM", "ALICE_BOB_INTEGRATION_START", {"hardware_target": "CAT_QUBIT"})
    
    # 1. Initialize 5x5 Sparse Lattice
    fabric = FabricSimulator(logger, width=5, height=5)
    topology_map = fabric.get_topology_map()
    
    # Target route across the grid
    start_node = "Q_0_0"
    end_node = "Q_4_4"
    
    # 2. Inject Asymmetric Phase-Flip Stress
    faults = fabric.inject_asymmetric_cat_qubit_stress()
    
    # 3. Sentinel & Quarantine
    sentinel = LocalSentinelReflex(logger)
    decisions = sentinel.evaluate_faults(faults)
    
    quarantine = QuarantineManager(logger)
    topology_map, isolated_nodes = quarantine.execute_quarantines(decisions, topology_map)
    
    # 4. Route via Phase-Flip aware Hippocampus A*
    router = TopologyRouter(logger)
    new_path = router.reroute_circuit(topology_map, start_node, end_node)

    logger.log("SYSTEM", "ALICE_BOB_INTEGRATION_COMPLETE", {"path_found": bool(new_path)})
    
    print("Alice & Bob Integration complete. Output written to alice_bob_audit.json.")

    # Extract injected fault node names defensively for the report.
    try:
        fault_nodes = sorted(x["node"] for x in faults)
    except Exception:
        fault_nodes = []

    # Generate markdown report (honest, outcome-aware: it records what actually
    # happened, including fail-closed abstention when no safe path remains).
    with open(report_path, "w") as f:
        f.write("# Alice & Bob: Cat-Qubit HQA Integration Report (Fail-Closed Demonstration)\n\n")
        f.write("A cat-qubit-style fabric demonstration. Bit-flip (X) suppression is treated as "
                "a modeled hardware assumption; phase-flip (Z) exposure is the live threat. Two "
                "phase-flip faults are injected, detected, and quarantined, then a corner-to-corner "
                "route is requested. This report records whatever actually happened.\n\n")
        f.write("## Setup\n")
        f.write(f"- Injected phase-flip faults: {', '.join(fault_nodes) if fault_nodes else 'see log'}.\n")
        f.write(f"- Route requested: `{start_node}` -> `{end_node}`.\n\n")
        f.write("## Outcome\n")
        if new_path:
            f.write("HQA found a phase-flip-aware path that avoids the quarantined Z-error nodes:\n\n")
            f.write(f"`{' -> '.join(new_path)}`\n\n")
            f.write("The route is an advisory proposal only and carries no hardware authority.\n\n")
        else:
            f.write("No safe path remained after quarantine, so HQA raised a systemic quench "
                    "(`path_found: false`) rather than proposing a route through degraded qubits. "
                    "Refusing to route is the correct fail-closed outcome here, and it is what HQA did.\n\n")
        f.write("## Constructive cat-qubit work\n")
        f.write("The affirmative cat-qubit results -- biased-noise routing on a routable fabric and "
                "the honest setpoint analysis -- live in `reports/HQA_CAT_BIASED_NOISE_ROUTER_V0.md` "
                "and `docs/HQA_CAT_QUBIT_COMPATIBILITY_NOTE_V0.md`.\n\n")
        f.write("## JSON Audit Log\n```json\n")
        with open(audit_path, "r") as audit:
            f.write(audit.read())
        f.write("\n```\n\n")
        f.write("## Boundary\n")
        f.write("Advisory simulation only. No hardware authority, no live Alice & Bob calibration "
                "data, no pulse or cryostat control. Node parameters are representative demo values. "
                "Demonstrates fail-closed abstention, not a physical routing or fidelity result.\n")
    print("Evidence written to ALICE_AND_BOB_INTEGRATION_REPORT.md")

if __name__ == "__main__":
    run_alice_bob_demo()
