"""survey.discovery.detect — classify a candidate file by content.

Answers only "can survey read this, and as what?": HOA automaton (first non-blank
line `HOA:`, by content, whatever the extension), an sos invariant (first
non-blank line `SOS v1`, by content), or an LTL list (a `.ltl`/`.txt` file, one
formula per line), or skip. No technique knowledge here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

_LTL_SUFFIXES = {".ltl", ".txt"}


def detect(path: Path) -> Optional[str]:
    """Return "hoa", "sos", "ltl", or None (skip). HOA and sos win by content
    (first non-blank line); otherwise a `.ltl`/`.txt` file is an LTL list.
    Unreadable files are skipped."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    for line in text.splitlines():
        if line.strip():
            head = line.lstrip()
            if head.startswith("HOA:"):
                return "hoa"
            if head.startswith("SOS v"):
                return "sos"
            break
    if path.suffix.lower() in _LTL_SUFFIXES:
        return "ltl"
    return None
