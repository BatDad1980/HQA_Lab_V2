import time
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

    # 1. Initialize Fabric
    fabric = FabricSimulator(num_nodes=10)
    topology_map = fabric.get_topology_map()
    time.sleep(1)

    # 2. Inject Fault
    print("\n--- STAGE 1: FAULT DETECTION ---")
    damaged_node, coherence = fabric.inject_fault()
    time.sleep(1)

    # 3. Sentinel Reflex
    print("\n--- STAGE 2: SENTINEL REFLEX & QUARANTINE ---")
    sentinel = LocalSentinelReflex()
    decision = sentinel.evaluate_node(damaged_node, coherence)
    time.sleep(1)

    if decision == "QUARANTINE_REQUIRED":
        quarantine = QuarantineManager()
        topology_map = quarantine.execute_quarantine(damaged_node, topology_map)
        time.sleep(1)

        # 4. Topology Routing (Hippocampus)
        print("\n--- STAGE 3: HYPERPLASTIC REROUTING ---")
        router = TopologyRouter()
        new_path = router.reroute_circuit(damaged_node, topology_map)
        time.sleep(1)

        # 5. Pulse Translation & CUDA
        print("\n--- STAGE 4: EDGE KERNEL COMPILATION ---")
        translator = PulseTranslator()
        qasm = translator.generate_qasm(new_path)
        
        kernel = CUDAEdgeKernel()
        kernel.execute_kernel(qasm)
        time.sleep(1)

        # 6. HAL Bridge
        print("\n--- STAGE 5: HARDWARE ABSTRACTION LAYER (HAL) ---")
        hal = HALCryostatBridge()
        hal.dispatch_hardware_commands(damaged_node)

    print("\n=====================================================")
    print("  AUDIT LOG: Control loop terminated successfully.   ")
    print("=====================================================")

if __name__ == "__main__":
    run_integrated_control_loop()
