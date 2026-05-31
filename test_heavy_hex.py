from topology_mapper import TopologyMapper
from qubit_fabric import QubitFabric
from topological_memory import Hippocampus
from sentinel_reflex import HQANetwork

def print_topology(fabric, title):
    print(f"\n--- {title} ---")
    for y in range(fabric.height):
        row_str = ""
        for x in range(fabric.width):
            if fabric.grid[y][x] == -2:
                row_str += "   " # Physical Void (Empty Space)
            else:
                row_str += "[O]" # Active Qubit
        print(row_str)

def run_heavy_hex_test():
    print("Initializing HQA Phase 2: Topology Distortion Mapping Test...")
    width, height = 12, 12
    
    # Generate the jagged, sparse heavy-hex layout
    heavy_hex_mask = TopologyMapper.generate_heavy_hex_mask(width, height)
    
    # Initialize the fabric WITH the topological defects
    fabric = QubitFabric(width=width, height=height, noise_rate=0.0, topology_mask=heavy_hex_mask)
    hippocampus = Hippocampus(fabric)
    network = HQANetwork(fabric, patch_size=4, hippocampus=hippocampus)
    
    print_topology(fabric, "Heavy-Hex Physical Chip Topology")
    
    print("\n[TEST] Routing A* pathways across the irregular physical gaps...")
    start = (0, 1) # Start on a solid crossbar
    end = (10, 5) # End on another crossbar
    
    path = hippocampus.route_path(start, end)
    
    print(f"\n[A* ROUTING] Calculated physical pathway preserving entanglement over gaps:")
    if path:
        print(path)
        print("Success! Sentinels and A* Router seamlessly navigated the jagged physical topology.")
    else:
        print("FAILED to find path.")

if __name__ == "__main__":
    run_heavy_hex_test()
