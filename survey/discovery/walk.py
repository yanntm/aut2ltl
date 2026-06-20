"""survey.discovery.walk — recurse the given PATHs into candidate files.

A PATH may be a file (yielded as-is) or a folder (descended recursively).
Hidden dirs, `logs/` and `__pycache__/` are skipped. Pure filesystem — no
format knowledge here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator

_SKIP_DIRS = {"logs", "__pycache__"}


def walk(paths: Iterable[Path]) -> Iterator[Path]:
    """Yield candidate files under each PATH, deterministically (sorted)."""
    for p in paths:
        p = Path(p)
        if p.is_file():
            yield p
        elif p.is_dir():
            for child in sorted(p.rglob("*")):
                if not child.is_file():
                    continue
                parts = child.relative_to(p).parts
                if any(part in _SKIP_DIRS or part.startswith(".") for part in parts):
                    continue
                yield child
