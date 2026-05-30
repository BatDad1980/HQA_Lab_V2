from qubit_fabric import QubitFabric
from sentinel_reflex import HQANetwork
from topological_memory import Hippocampus

def display_path_on_fabric(fabric, hippocampus, path):
    """Draws the grid, the hot zones (X), danger gradients (.), and the routing path (*)"""
    print("\n--- Topologically Routed Fabric ---")
    for y in range(fabric.height):
        row_str = ""
        for x in range(fabric.width):
            if path and (x, y) in path:
                row_str += "* " # The Path
            elif hippocampus.fault_map[y][x] == 1.0:
                row_str += "X " # Known Fault
            elif hippocampus.fault_map[y][x] > 0.0:
                row_str += ". " # Danger Gradient
            else:
                row_str += "  " # Pristine Fabric
        print(row_str)
    print("-----------------------------------")

def run_test():
    print("Initializing HQA V2 - Pillar 1 (Topological Memory)")
    
    # 1. Create a 40x40 Fabric
    width, height = 40, 20
    fabric = QubitFabric(width=width, height=height, noise_rate=0.0)
    
    # Inject clustered thermal fault zones right in the middle
    fabric.inject_hardware_faults(num_faults=0, cluster_zones=3, cluster_radius=3)
    
    # 2. Attach the Hippocampus and Network
    hippocampus = Hippocampus(fabric)
    network = HQANetwork(fabric, patch_size=5, hippocampus=hippocampus)
    
    print("Running initial calibration sweeps to map the fabric...")
    # 3. Simulate several ticks so Sentinels encounter the faults and report them
    for _ in range(10):
        fabric.tick()
        network.step()
        
    print(f"Calibration complete. Hippocampus mapped {len([c for row in hippocampus.fault_map for c in row if c == 1.0])} permanent faults.")
    
    # 4. Request a routing path from left to right
    start = (0, height // 2)
    end = (width - 1, height // 2)
    
    print(f"Requesting logical quantum route from {start} to {end}...")
    
    # Straight line baseline (pre-Hippocampus) would just march across y=10.
    path = hippocampus.route_path(start, end)
    
    if path:
        print(f"SUCCESS: Hippocampus found a pristine route of length {len(path)}.")
        display_path_on_fabric(fabric, hippocampus, path)
    else:
        print("FAILED: No safe route found across the fabric.")
        
    # Check if the path actually avoided faults
    if path:
        faults_crossed = sum(1 for (x, y) in path if hippocampus.fault_map[y][x] == 1.0)
        print(f"Straight Line (V1) would cross the cluster.")
        print(f"Proactive Router (V2) crossed {faults_crossed} known faults.")

if __name__ == "__main__":
    run_test()
