class HALSafetyGovernor:
    """
    The absolute firewall. Scans Control Manifests for forbidden 
    commands and enforces thermal limits before allowing execution.
    """
    def __init__(self, logger):
        self.logger = logger
        self.FORBIDDEN_COMMANDS = ["EMERGENCY_VENT", "DISABLE_DILUTION", "OVERRIDE_INTERLOCK"]
        self.MAX_COOLING_INTENSITY = 15.0

    def evaluate_manifest(self, manifest):
        payload = manifest["payload"]
        intent = payload["intent"]
        
        self.logger.log("SAFETY_GOVERNOR", "MANIFEST_RECEIVED", {"issuer": payload["issuer"], "dry_run": payload["dry_run"]})

        # 1. Forbidden Command Scanner
        if "action" in intent and intent["action"] in self.FORBIDDEN_COMMANDS:
            self.logger.log("SAFETY_GOVERNOR", "MANIFEST_REJECTED", {"reason": f"FORBIDDEN_ACTION: {intent['action']}"})
            return "SAFE_HOLD"

        # 2. Cooling Policy Gate
        if "intensity" in intent and intent["intensity"] > self.MAX_COOLING_INTENSITY:
            self.logger.log("SAFETY_GOVERNOR", "MANIFEST_REJECTED", {"reason": f"THERMAL_VIOLATION: Intensity {intent['intensity']} > {self.MAX_COOLING_INTENSITY}"})
            return "SAFE_HOLD"

        # 3. Dry-Run Enforcement
        if payload["dry_run"]:
            self.logger.log("SAFETY_GOVERNOR", "DRY_RUN_ENFORCED", {"action": "Simulating SCPI Acknowledgement. No hardware touched."})
            return "SIMULATED_SUCCESS"

        self.logger.log("SAFETY_GOVERNOR", "MANIFEST_APPROVED", {"action": "Dispatching to physical HAL."})
        return "HARDWARE_DISPATCH_AUTHORIZED"
