"""Demo path bootstrap for direct script execution.

The HQA demos are intentionally lightweight scripts. This helper lets them run
from a clean clone with commands like:

    python hqa_v2/demos/hqa_stress_harness.py

without requiring callers to set PYTHONPATH by hand.
"""

from __future__ import annotations

import sys
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = HQA_V2_ROOT / "logs"
REPORT_DIR = HQA_V2_ROOT / "reports"

for subdir in ("core", "safety", "routing", "physics"):
    path = str(HQA_V2_ROOT / subdir)
    if path not in sys.path:
        sys.path.insert(0, path)


def log_path(name: str) -> str:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return str(LOG_DIR / name)


def report_path(name: str) -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    return str(REPORT_DIR / name)
