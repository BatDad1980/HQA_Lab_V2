"""Validate the sample HQA vendor shadow packet against local schemas."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = HQA_V2_ROOT / "schemas"
PACKET_ROOT = HQA_V2_ROOT / "outputs" / "vendor_shadow_packet_v1"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_VENDOR_SHADOW_PACKET_VALIDATION.md"

PAYLOADS = [
    ("01_topology_snapshot.json", "topology_snapshot.schema.json"),
    ("02_syndrome_record.json", "syndrome_record.schema.json"),
    ("03_quarantine_decision.json", "quarantine_decision.schema.json"),
    ("04_reroute_proposal.json", "reroute_proposal.schema.json"),
    ("05_hal_manifest.json", "hal_manifest.schema.json"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate_value(value: Any, schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")

    if isinstance(expected_type, list):
        if not any(type_matches(value, candidate) for candidate in expected_type):
            errors.append(f"{path}: expected one of {expected_type}, got {type(value).__name__}")
            return errors
    elif isinstance(expected_type, str) and not type_matches(value, expected_type):
        errors.append(f"{path}: expected {expected_type}, got {type(value).__name__}")
        return errors

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} not in enum {schema['enum']!r}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: length below minLength {schema['minLength']}")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            errors.append(f"{path}: does not match pattern {schema['pattern']!r}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: item count below minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_value(item, item_schema, f"{path}[{index}]"))
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}.{key}: missing required field")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            for key in extra:
                errors.append(f"{path}.{key}: additional property not allowed")
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, dict):
                errors.extend(validate_value(value[key], child_schema, f"{path}.{key}"))
    return errors


def validate_payload(payload_name: str, schema_name: str) -> tuple[str, bool, str]:
    payload_path = PACKET_ROOT / payload_name
    schema_path = SCHEMA_ROOT / schema_name
    if not payload_path.exists():
        return payload_name, False, "payload missing"
    if not schema_path.exists():
        return payload_name, False, "schema missing"

    payload, payload_error = load_json(payload_path)
    schema, schema_error = load_json(schema_path)
    if payload_error:
        return payload_name, False, payload_error
    if schema_error:
        return payload_name, False, schema_error

    errors = validate_value(payload, schema, "$")
    if errors:
        return payload_name, False, "; ".join(errors[:5])
    return payload_name, True, f"validated against `{schema_name}`"


def validate_manifest() -> tuple[str, bool, str]:
    manifest = PACKET_ROOT / "MANIFEST_SHA256.txt"
    if not manifest.exists():
        return "MANIFEST_SHA256.txt", False, "manifest missing"
    failures: list[str] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, filename = line.split(maxsplit=1)
        path = PACKET_ROOT / filename.strip()
        if not path.exists():
            failures.append(f"{filename} missing")
            continue
        actual = sha256(path)
        if actual != expected:
            failures.append(f"{filename} hash mismatch")
    if failures:
        return "MANIFEST_SHA256.txt", False, "; ".join(failures)
    return "MANIFEST_SHA256.txt", True, "all packet hashes match"


def write_report(results: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in results if ok)
    lines = [
        "# HQA Vendor Shadow Packet Validation",
        "",
        "## Purpose",
        "",
        "This validation confirms that the generated vendor shadow packet payloads conform to the local HQA schema contracts and that the packet manifest hashes match.",
        "",
        "## Results",
        "",
        f"- Checks: `{len(results)}`",
        f"- Passed: `{passed}`",
        f"- Failed: `{len(results) - passed}`",
        "",
        "| Check | Status | Detail |",
        "|---|---:|---|",
    ]
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        lines.append(f"| `{name}` | {status} | {detail} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This validation checks local shadow-mode packet structure only. It does not validate physical quantum hardware, submit live jobs, or grant HQA hardware control authority.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results = [validate_payload(payload, schema) for payload, schema in PAYLOADS]
    results.append(validate_manifest())
    write_report(results)
    failed = [result for result in results if not result[1]]
    print(f"HQA vendor shadow packet validation written: {REPORT_PATH}")
    print(f"Passed {len(results) - len(failed)}/{len(results)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
