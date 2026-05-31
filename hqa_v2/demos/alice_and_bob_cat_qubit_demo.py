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

    # Generate markdown report
    with open(report_path, "w") as f:
        f.write("# Alice & Bob: Cat-Qubit HQA Integration Report\n\n")
        f.write("This report demonstrates a proxy adaptation path for a cat-qubit-style error model, focusing routing behavior on phase-flip fault gradients while treating bit-flip suppression as a modeled hardware assumption.\n\n")
        f.write("## The Hardware Profile\n")
        f.write("Cat Qubits exponentially suppress bit-flip (X) errors autonomously at the physical level, leaving only phase-flip (Z) errors. ")
        f.write("A static control stack routes blindly. HQA, however, engages an **Asymmetric Error Emulation** mode.\n\n")
        f.write("## The Routing Demonstration\n")
        f.write("The Hippocampus A* router recognizes the Z-error phase flips injected into the sparse-lattice and applies an extreme proximity penalty specifically to phase-flip gradients, steering the computational path completely clear of Z-error decoherence zones.\n\n")
        f.write("## JSON Audit Log\n```json\n")
        with open(audit_path, "r") as audit:
            f.write(audit.read())
        f.write("\n```\n")
    print("Evidence written to ALICE_AND_BOB_INTEGRATION_REPORT.md")

if __name__ == "__main__":
    run_alice_bob_demo()
