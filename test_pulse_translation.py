from qubit_fabric import QubitFabric
from topological_memory import Hippocampus
from sentinel_reflex import HQANetwork
from microwave_pulse_translator import MicrowavePulseTranslator

def run_translation_test():
    print("Initializing HQA Phase 1: Pulse-Level Translation Test...")
    fabric_width = 8
    fabric = QubitFabric(width=fabric_width, height=8, noise_rate=0.0)
    
    # Initialize the Pulse Translator
    translator = MicrowavePulseTranslator(fabric_width=fabric_width)
    
    # Initialize Sentinel Network with the translator attached
    network = HQANetwork(fabric, patch_size=4, hippocampus=None, pulse_translator=translator)
    
    # Inject a random error at (5, 2)
    error_x, error_y = 5, 2
    fabric.grid[error_y][error_x] = 2 # Age 2 (slightly more severe)
    
    print(f"\n[TEST] Mathematical error injected at ({error_x}, {error_y}).")
    print(f"Waiting for Sentinel Agent to trigger quench reflex...\n")
    
    # Run one tick so Sentinel detects and quenches
    network.step()
    
    # Retrieve the physical instructions
    pulse_qasm = translator.get_latest_pulse()
    
    if pulse_qasm:
        print("[SENTINEL] Mathematical quench triggered.")
        print("[PULSE COMPILER] Generating OpenQASM 3.0 instruction block for physical cryostat AWG:\n")
        print("--------------------------------------------------")
        print(pulse_qasm)
        print("--------------------------------------------------")
        print("Successfully translated O(1) logic into physical microwave waveforms.")
    else:
        print("Test failed: No pulse generated.")

if __name__ == "__main__":
    run_translation_test()
