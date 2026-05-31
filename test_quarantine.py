from qubit_fabric import QubitFabric
from topological_memory import Hippocampus
from sentinel_reflex import HQANetwork

def print_grid(fabric, title):
    print(f"\n--- {title} ---")
    for y in range(fabric.height):
        row_str = ""
        for x in range(fabric.width):
            if (x, y) in fabric.quarantined_nodes:
                row_str += " X " # Quarantined / Dead Zone
            elif fabric.grid[y][x] > 0:
                row_str += " 1 " # Noise
            else:
                row_str += " 0 " # Healthy
        print(row_str)

def print_weights(fabric):
    print(f"\n--- Logical Weight Distribution ---")
    for y in range(fabric.height):
        row_str = ""
        for x in range(fabric.width):
            if (x, y) in fabric.quarantined_nodes:
                row_str += " 0.00 "
            else:
                row_str += f"{fabric.logical_weights[y][x]:5.2f} "
        print(row_str)

def run_quarantine_test():
    print("Initializing HQA Phase 4: Sentinel Quarantine Protocol Test...")
    fabric = QubitFabric(width=8, height=8, noise_rate=0.0)
    hippocampus = Hippocampus(fabric)
    network = HQANetwork(fabric, patch_size=4, hippocampus=hippocampus)
    
    # We will simulate a massively degrading physical qubit at (3, 3)
    target_node = (3, 3)
    
    print("\n[TEST] Hammering Node (3, 3) with physical faults...")
    
    # Tick the simulation until the Sentinel reaches the plasticity threshold (default 5)
    for tick in range(1, 10):
        # Force a fault at (3, 3)
        if target_node not in fabric.quarantined_nodes:
            fabric.grid[target_node[1]][target_node[0]] = 1
            
        fabric.tick() # Physics happens
        network.step() # Sentinel reacts
        
        if target_node in fabric.quarantined_nodes:
            print(f"-> Tick {tick}: Node {target_node} was successfully Quarantined.")
            break
            
    print_grid(fabric, "Fabric State (X = Quarantined Dead Zone)")
    print_weights(fabric)
    
    # Verify A* routing flows around the quarantined node
    start = (1, 3)
    end = (5, 3)
    path = hippocampus.route_path(start, end)
    print(f"\n[A* ROUTING] Path from {start} to {end} around the dead zone:")
    print(path)

if __name__ == "__main__":
    run_quarantine_test()
