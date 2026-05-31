import time
import _bootstrap
from audit_logger import AuditLogger
from fabric_simulator import FabricSimulator
from local_sentinel_reflex import LocalSentinelReflex
from quarantine_manager import QuarantineManager
from topology_router import TopologyRouter
from pulse_translator import PulseTranslator
from cuda_edge_kernel import CUDAEdgeKernel
from hal_cryostat_bridge import HALCryostatBridge

def run_integrated_control_loop():
    print("=====================================================")
    print("  HQA V2: HOMEOSTATIC QUANTUM ARCHITECTURE DEMO      ")
    print("  Integrated Control Plane (Fault -> Hardware)       ")
    print("=====================================================\n")

    logger = AuditLogger(filepath=_bootstrap.log_path("integrated_control_audit.json"))
    logger.log("SYSTEM", "INTEGRATED_CONTROL_LOOP_START", {"version": "HQA_V2"})

    # 1. Initialize Fabric
    fabric = FabricSimulator(logger, width=5, height=5)
    topology_map = fabric.get_topology_map()
    time.sleep(0.1)

    # 2. Inject Fault
    print("\n--- STAGE 1: FAULT DETECTION ---")
    faults = fabric.inject_targeted_fault(x=2, y=2)
    damaged_node = faults[0]["node"] if faults else None
    time.sleep(0.1)

    # 3. Sentinel Reflex
    print("\n--- STAGE 2: SENTINEL REFLEX & QUARANTINE ---")
    sentinel = LocalSentinelReflex(logger)
    decisions = sentinel.evaluate_faults(faults)
    time.sleep(0.1)

    if damaged_node and decisions.get(damaged_node) == "QUARANTINE_REQUIRED":
        quarantine = QuarantineManager(logger)
        topology_map, isolated_nodes = quarantine.execute_quarantines(decisions, topology_map)
        time.sleep(0.1)

        # 4. Topology Routing (Hippocampus)
        print("\n--- STAGE 3: HYPERPLASTIC REROUTING ---")
        router = TopologyRouter(logger)
        new_path = router.reroute_circuit(topology_map, start_node="Q_0_0", end_node="Q_4_4")
        time.sleep(0.1)

        # 5. Pulse Translation & CUDA
        print("\n--- STAGE 4: EDGE KERNEL COMPILATION ---")
        translator = PulseTranslator(logger, fabric)
        manifest = translator.generate_hardware_instructions(new_path, dry_run=True)
        
        kernel = CUDAEdgeKernel(logger)
        kernel.execute_kernel(str(manifest))
        time.sleep(0.1)

        # 6. HAL Bridge
        print("\n--- STAGE 5: HARDWARE ABSTRACTION LAYER (HAL) ---")
        hal = HALCryostatBridge(logger)
        hal.dispatch_hardware_commands(isolated_nodes, dry_run=True)

    logger.log("SYSTEM", "INTEGRATED_CONTROL_LOOP_COMPLETE", {"status": "bounded_dry_run"})

    print("\n=====================================================")
    print("  AUDIT LOG: Control loop terminated successfully.   ")
    print("=====================================================")

if __name__ == "__main__":
    run_integrated_control_loop()
