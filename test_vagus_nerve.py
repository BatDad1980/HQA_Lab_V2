from qubit_fabric import QubitFabric
from sentinel_reflex import HQANetwork
from classical_hardware import CryostatController
from vagus_nerve import VagusNerve

def count_errors(fabric):
    return sum(1 for row in fabric.grid for cell in row if cell > 0)

def run_test():
    print("Initializing HQA V2 - Pillar 2 (Systemic Autonomic Responses - The Vagus Nerve)")
    
    # Create fabric with a low baseline noise
    width, height = 40, 40
    fabric = QubitFabric(width=width, height=height, noise_rate=0.01)
    
    # Initialize components
    classical_hardware = CryostatController(fabric)
    vagus_nerve = VagusNerve(fabric, classical_hardware, stress_threshold=20)
    network = HQANetwork(fabric, patch_size=5)
    
    print("\n--- PHASE 1: Baseline Homeostasis ---")
    for tick in range(1, 6):
        fabric.tick()
        network.step()
        vagus_nerve.monitor_and_regulate(network.sentinels)
        print(f"Tick {tick}: Errors remaining = {count_errors(fabric)}")
        
    print("\n--- PHASE 2: Thermal Event (Solar Flare hitting Top-Right Quadrant) ---")
    print("Increasing noise rate in Q(1, 0) by 50x...")
    fabric.trigger_thermal_event(qx=1, qy=0, intensity=50.0)
    
    for tick in range(6, 11):
        fabric.tick()
        network.step()
        
        # Here is where the magic happens:
        vagus_nerve.monitor_and_regulate(network.sentinels)
        
        print(f"Tick {tick}: Errors remaining = {count_errors(fabric)}")
        
    print("\n--- TEST CONCLUSION ---")
    if classical_hardware.get_pump_status()[0][1]:
        print("SUCCESS: Vagus Nerve successfully bridged the quantum-classical divide and saved the fabric.")
    else:
        print("FAILED: Vagus Nerve did not trigger cooling.")

if __name__ == "__main__":
    run_test()
