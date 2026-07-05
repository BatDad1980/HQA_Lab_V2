"""Claim-boundary smoke test for HQA V2.

The HQA lab can be ambitious without letting artifacts overclaim. This scanner
checks active demo / report / doc text for phrases that make proxy evidence sound
like physical quantum validation or impossible guarantees.

It is context-aware: a forbidden phrase is a violation only when it is *asserted*.
Phrases that are being *prohibited or quoted as forbidden* -- items under a
"does not claim" / "Forbidden phrasing:" / "Avoid:" heading, or a line that frames
the phrase as a non-claim -- are exempt, so the claim-discipline docs are allowed
to name the very words they forbid.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [
    HQA_V2_ROOT / "demos",
    HQA_V2_ROOT / "reports",
    HQA_V2_ROOT / "docs",
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

# A line that frames a forbidden phrase as a non-claim / quote rather than asserting it.
LINE_EXEMPT = re.compile(
    r"\bnot\b|non-?claim|no system is|\bavoid\b|do not|don't|does not|must not|"
    r"\bnever\b|prohibit|forbidden|overclaim|reframe|internal only|liability|"
    r"unsupported|instead of|do NOT say",
    re.IGNORECASE,
)

# A heading/label that opens a block of *prohibited* claims. Everything list-like
# beneath it (bullets, block-quotes, table rows) stays exempt until ordinary prose resumes.
BLOCK_OPENER = re.compile(
    r"forbidden|\bavoid\b|do not|does not|non-?claim|must not|not claim|prohibit|"
    r"language to avoid|do NOT say|claims? to avoid|makes? no claim|no claim|"
    r"asserts? no|will not claim|never claim",
    re.IGNORECASE,
)

LIST_LIKE = re.compile(r"^\s*(?:[-*>|]|\d+[.)])")

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
        in_prohibition = False
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()

            # Track whether we are inside a "prohibited claims" block. A block opener
            # turns it on; ordinary assertive prose (non-blank, non-list) turns it off;
            # blank lines and list-like lines preserve the current state.
            if BLOCK_OPENER.search(line):
                in_prohibition = True
            elif stripped and not LIST_LIKE.match(line):
                in_prohibition = False

            if in_prohibition or LINE_EXEMPT.search(line):
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
    print(f"Scanned {len(iter_text_files())} text files across {len(SCAN_DIRS)} directories.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
