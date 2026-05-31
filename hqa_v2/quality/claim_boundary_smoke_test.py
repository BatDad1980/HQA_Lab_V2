"""Claim-boundary smoke test for HQA V2.

The HQA lab can be ambitious without letting generated artifacts overclaim.
This scanner checks active demo/report text for phrases that make proxy
evidence sound like physical quantum validation or impossible guarantees.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [
    HQA_V2_ROOT / "demos",
    HQA_V2_ROOT / "reports",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"\bThis document proves\b", re.IGNORECASE),
    re.compile(r"\bproves HQA\b", re.IGNORECASE),
    re.compile(r"\bproves the\b", re.IGNORECASE),
    re.compile(r"\bachieved true homeostasis\b", re.IGNORECASE),
    re.compile(r"\bGod Protocol\b", re.IGNORECASE),
    re.compile(r"\binfinite scalability\b", re.IGNORECASE),
    re.compile(r"\b100%\s+cascade prevention\b", re.IGNORECASE),
    re.compile(r"\bsolved quantum\b", re.IGNORECASE),
    re.compile(r"\bunhackable\b", re.IGNORECASE),
    re.compile(r"\bguarantee(?:d|s)?\b", re.IGNORECASE),
]

TEXT_EXTENSIONS = {".md", ".py", ".txt"}


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for directory in SCAN_DIRS:
        if not directory.exists():
            continue
        files.extend(path for path in directory.rglob("*") if path.suffix in TEXT_EXTENSIONS)
    return sorted(files)


def main() -> int:
    violations: list[str] = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            normalized = line.lower()
            if "not " in normalized or "non-claim" in normalized or "no system is" in normalized:
                continue
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    rel = path.relative_to(HQA_V2_ROOT)
                    violations.append(f"{rel}:{line_number}: {line.strip()}")

    if violations:
        print("CLAIM BOUNDARY SMOKE TEST: FAIL")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("CLAIM BOUNDARY SMOKE TEST: PASS")
    print(f"Scanned {len(iter_text_files())} text files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
