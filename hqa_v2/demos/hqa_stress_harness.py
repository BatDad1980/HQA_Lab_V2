import time
from audit_logger import AuditLogger
from fabric_simulator import FabricSimulator
from local_sentinel_reflex import LocalSentinelReflex
from quarantine_manager import QuarantineManager
from topology_router import TopologyRouter
from pulse_translator import PulseTranslator
from cuda_edge_kernel import CUDAEdgeKernel
from hal_cryostat_bridge import HALCryostatBridge

def run_stress_harness():
    logger = AuditLogger()
    logger.log("SYSTEM", "STRESS_HARNESS_START", {"version": "2.1-Maturity"})
    
    # 1. Initialize Fabric with Sparse Lattice
    fabric = FabricSimulator(logger, width=5, height=5)
    topology_map = fabric.get_topology_map()
    
    # 2. Inject Multiple Faults (Stress)
    faults = fabric.inject_stress()
    
    # 3. Sentinel Reflex (with forced conflicting signal)
    sentinel = LocalSentinelReflex(logger)
    decisions = sentinel.evaluate_faults(faults, conflicting_signal=True)
    
    # 4. Quarantine Manager
    quarantine = QuarantineManager(logger)
    topology_map, isolated_nodes = quarantine.execute_quarantines(decisions, topology_map)
    
    # 5. Topology Router (Try to reroute, may fail if topology is heavily fractured)
    router = TopologyRouter(logger)
    # Give it explicit start/end for the A* router
    new_path = router.reroute_circuit(topology_map, start_node="Q_0_0", end_node="Q_4_4")
    
    if new_path:
        # 6. Pulse Translator
        translator = PulseTranslator(logger)
        qasm = translator.generate_qasm(new_path)
        
        # 7. CUDA Edge Kernel (Force Unavailable occasionally)
        kernel = CUDAEdgeKernel(logger)
        cuda_success = kernel.execute_kernel(qasm, force_unavailable=True) # Force edge case
        
        # 8. HAL Cryostat Bridge (Trigger the Governor Safety Block instead of force_failure)
        hal = HALCryostatBridge(logger)
        hal_success = hal.dispatch_hardware_commands(isolated_nodes, action="EMERGENCY_VENT", dry_run=False) # Will be blocked by governor

    logger.log("SYSTEM", "STRESS_HARNESS_COMPLETE", {"status": "survived"})
    print("Stress Harness execution complete. Audit log written to audit_log.json.")

if __name__ == "__main__":
    run_stress_harness()
