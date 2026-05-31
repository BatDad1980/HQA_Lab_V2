from control_manifest import ControlManifest
from microwave_pulse_shaper import MicrowavePulseShaper

class PulseTranslator:
    def __init__(self, logger, fabric):
        self.logger = logger
        self.fabric = fabric
        self.shaper = MicrowavePulseShaper(logger, fabric)

    def generate_hardware_instructions(self, circuit_path, dry_run=True):
        if not circuit_path:
            return None
            
        # Instead of abstract QASM, we now generate explicit analog pulses
        analog_schedule = self.shaper.shape_pulses(circuit_path)
        
        # Package into manifest
        intent = {"action": "EXECUTE_ANALOG_SCHEDULE", "schedule": analog_schedule}
        manifest = ControlManifest.create_manifest("PULSE_TRANSLATOR", "AWG_CONTROLLER", intent, dry_run)
        return manifest
