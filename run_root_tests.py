"""Execute the eight legacy root-level HQA verification scripts.

These files are executable verification scenarios rather than pytest or
unittest test cases, so they must be run as independent processes.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECKS = (
    "test_cuda_latency.py",
    "test_heavy_hex.py",
    "test_hippocampus.py",
    "test_physical_hal.py",
    "test_pulse_translation.py",
    "test_quarantine.py",
    "test_sleep_cycle.py",
    "test_vagus_nerve.py",
)


def main() -> int:
    failures: list[tuple[str, int]] = []
    for filename in CHECKS:
        path = ROOT / filename
        if not path.is_file():
            print(f"[FAIL] {filename}: missing")
            failures.append((filename, 2))
            continue

        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"[{status}] {filename}")
        if result.returncode != 0:
            failures.append((filename, result.returncode))
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

    passed = len(CHECKS) - len(failures)
    print(f"Passed {passed}/{len(CHECKS)} root verification scripts.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
