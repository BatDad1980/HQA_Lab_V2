import time
from classical_hardware import CryostatController

# A dummy fabric class just for the test
class DummyFabric:
    def apply_cooling(self, qx, qy):
        pass

def run_test():
    fabric = DummyFabric()
    
    # Initialize HAL in physical mode
    print("Initializing Cryostat HAL in physical network mode...")
    hal = CryostatController(fabric, mode="physical", host="127.0.0.1", port=5000)
    
    print("\nSimulating Vagus Nerve triggering Quadrant (1, 1)...")
    time.sleep(1)
    
    # Trigger the HAL
    hal.activate_cryo_pump(1, 1)
    
    print("\nSimulating Vagus Nerve triggering Quadrant (0, 1)...")
    time.sleep(1)
    hal.activate_cryo_pump(0, 1)
    
    print("\nTest complete.")

if __name__ == "__main__":
    run_test()
