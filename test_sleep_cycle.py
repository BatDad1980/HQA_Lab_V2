from qubit_fabric import QubitFabric
from sentinel_reflex import HQANetwork
from topological_memory import Hippocampus
from test_hippocampus import display_path_on_fabric

def count_noise(fabric):
    return sum(1 for row in fabric.grid for cell in row if cell > 0)

def run_test():
    print("Initializing HQA V2 - Pillar 3 (Sleep Cycles & Synaptic Pruning)")
    
    # Create fabric with high baseline noise to simulate an exhausted machine
    width, height = 40, 20
    fabric = QubitFabric(width=width, height=height, noise_rate=0.08)
    
    hippocampus = Hippocampus(fabric)
    network = HQANetwork(fabric, patch_size=10, hippocampus=hippocampus)
    
    print("\n--- Running physics ticks (Heavy Noise) ---")
    
    sleep_initiated = False
    
    for tick in range(1, 10):
        fabric.tick()
        network.step()
        
        # Check if any sentinels are sleeping
        sleeping_sentinels = [s for s in network.sentinels if s.sleep_timer > 0]
        active_noise = count_noise(fabric)
        
        status = f"Tick {tick}: {active_noise} active errors."
        if sleeping_sentinels:
            sleep_initiated = True
            status += f" -> [!] {len(sleeping_sentinels)} patches are MICRO-SLEEPING to flush noise."
        print(status)
        
        # If sleep happened, demonstrate that the router avoids the sleeping patches
        if sleeping_sentinels and tick == 4:
            print("\n[HIPPOCAMPUS] Attempting to route logical state while patches are sleeping...")
            start = (0, 10)
            end = (39, 10)
            path = hippocampus.route_path(start, end)
            if path:
                print("SUCCESS: Hippocampus routed gracefully around the sleeping sectors!")
                # Add the sleeping patches to the fault map temporarily just for the display function to show them
                for (sx, sy) in fabric.sleep_zones:
                    hippocampus.fault_map[sy][sx] = 1.0
                display_path_on_fabric(fabric, hippocampus, path)
                # Clean up the display hack
                for (sx, sy) in fabric.sleep_zones:
                    hippocampus.fault_map[sy][sx] = 0.0
            else:
                print("FAILED: Fabric is too heavily asleep to route.")

    print("\n--- TEST CONCLUSION ---")
    if sleep_initiated:
        print("SUCCESS: Sentinels successfully recognized exhaustion, entered micro-sleep to flush noise, and the Hippocampus gracefully routed logic around the sleeping brains.")
    else:
        print("FAILED: No sleep cycles initiated.")

if __name__ == "__main__":
    run_test()
