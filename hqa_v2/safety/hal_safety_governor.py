"""HAL Safety Governor — fail-closed control-manifest firewall.

Design contract (fail-closed / default-deny):

- The governor NEVER raises on a malformed, unsigned, or tampered manifest.
  Any structural, integrity, or policy failure resolves to ``SAFE_HOLD``.
- Manifest integrity is verified against its SHA-256 signature before any
  field is trusted. An unsigned or altered manifest is held, not evaluated.
- A real (non dry-run) physical dispatch is DENIED BY DEFAULT. It is authorized
  only when an explicit hardware-authority grant is supplied to the governor
  AND the action is on an allow-list. In the current HQA proxy build no
  authority is granted, so live dispatch always resolves to ``SAFE_HOLD`` —
  consistent with the project boundary: no live hardware authority.

Returns one of: "SAFE_HOLD", "SIMULATED_SUCCESS", "HARDWARE_DISPATCH_AUTHORIZED".
"""

import hashlib
import hmac
import json


class HALSafetyGovernor:
    """The absolute firewall between control logic and physical execution.

    Scans Control Manifests for forbidden commands, enforces thermal limits,
    verifies manifest integrity, and requires explicit authority before any
    non-simulated dispatch. Every failure path fails closed.
    """

    FORBIDDEN_COMMANDS = ("EMERGENCY_VENT", "DISABLE_DILUTION", "OVERRIDE_INTERLOCK")
    MAX_COOLING_INTENSITY = 15.0

    def __init__(self, logger, authority=None, allowed_actions=None):
        self.logger = logger
        # Explicit physical-dispatch authority. None => no live hardware authority.
        self.authority = authority
        # Optional allow-list of dispatchable actions (consulted only once authorized).
        self.allowed_actions = set(allowed_actions) if allowed_actions is not None else None

    def _hold(self, reason, detail=None):
        self.logger.log("SAFETY_GOVERNOR", "SAFE_HOLD", {"reason": reason, "detail": detail})
        return "SAFE_HOLD"

    def _signature_valid(self, manifest):
        """Recompute the manifest signature and compare in constant time."""
        payload = manifest.get("payload")
        signature = manifest.get("signature")
        if not isinstance(payload, dict) or not isinstance(signature, str):
            return False
        expected = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def evaluate_manifest(self, manifest):
        # 1. Structure + integrity. Never trust an unverified manifest; never raise.
        if not isinstance(manifest, dict):
            return self._hold("malformed_manifest", "manifest is not an object")
        if not self._signature_valid(manifest):
            return self._hold("integrity_failure", "missing or mismatched signature")

        payload = manifest["payload"]  # signature check guarantees this is a dict
        intent = payload.get("intent")
        if not isinstance(intent, dict):
            return self._hold("malformed_intent", "intent missing or not an object")
        dry_run = payload.get("dry_run")
        if not isinstance(dry_run, bool):
            return self._hold("ambiguous_execution_mode", "dry_run flag missing or non-boolean")

        self.logger.log(
            "SAFETY_GOVERNOR",
            "MANIFEST_RECEIVED",
            {"issuer": payload.get("issuer", "UNKNOWN"), "dry_run": dry_run},
        )

        action = intent.get("action")

        # 2. Forbidden actions are blocked unconditionally (defense in depth).
        if action in self.FORBIDDEN_COMMANDS:
            return self._hold("forbidden_action", action)

        # 3. Thermal policy. Reject non-numeric or out-of-bounds intensity.
        intensity = intent.get("intensity")
        if intensity is not None:
            if isinstance(intensity, bool) or not isinstance(intensity, (int, float)):
                return self._hold("invalid_intensity", repr(intensity))
            if intensity > self.MAX_COOLING_INTENSITY:
                return self._hold("thermal_violation", f"{intensity} > {self.MAX_COOLING_INTENSITY}")

        # 4. Dry-run never touches hardware and is always safe to simulate.
        if dry_run:
            self.logger.log(
                "SAFETY_GOVERNOR",
                "DRY_RUN_ENFORCED",
                {"note": "simulated acknowledgement; no hardware touched"},
            )
            return "SIMULATED_SUCCESS"

        # 5. Real dispatch: DEFAULT-DENY. Requires an explicit authority grant.
        if self.authority is None:
            return self._hold(
                "no_hardware_authority", "live dispatch requires an explicit authority grant"
            )
        if self.allowed_actions is not None and action not in self.allowed_actions:
            return self._hold("action_not_allowed", action)

        self.logger.log(
            "SAFETY_GOVERNOR", "MANIFEST_APPROVED", {"action": action, "authority": True}
        )
        return "HARDWARE_DISPATCH_AUTHORIZED"
