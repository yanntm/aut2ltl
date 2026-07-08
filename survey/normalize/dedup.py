"""Dedup a folder of inputs by a pluggable `key`: keep the first item per key,
drop the rest. This module knows the keep/drop decision only — not WHAT the key
means (the caller's callable, default polarity∘names). The walk, dry-run/`--prune`
and report come from `survey.normalize.sweep`.

A file contributes one item if it is HOA or `.sos`, one per non-comment formula
line if it is LTL. Dry run by default; `--prune` deletes duplicate HOA/`.sos` files
and strips duplicate formula lines from LTL files.

`.sos` (syntactic-ω-semigroup) dumps dedup by language identity — the whole-file
key of `survey.normalize.sos` ([SωS26, Thm. 5.1]: byte-equal ⟺ equal language).

For dedup AND AP-renaming in one pass, use `survey.normalize.canon` (HOA/LTL only).

CLI (from the repo root):
    python3 -m survey.normalize.dedup FOLDER           # dry run: per-file drop counts
    python3 -m survey.normalize.dedup --prune FOLDER   # apply: delete / rewrite dups
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Optional, Tuple

from survey.normalize import sweep
from survey.normalize.names import _is_hoa_text, normalize_text
from survey.normalize.polarity import polarity_normalize_text
from survey.normalize.sos import sos_key

Key = Callable[[str], str]

# The suffixes `dedup` walks: HOA/LTL (default) plus `.sos` language dumps.
SUFFIXES = sweep.SUFFIXES | {".sos"}


def default_key(text: str) -> str:
    """The combined key: name canonicalisation then polarity canonicalisation."""
    return polarity_normalize_text(normalize_text(text))


def dropper(key: Key = default_key) -> "sweep.Op":
    """A `sweep` Op that keeps the first item per `key` and drops later duplicates:
    a duplicate HOA or `.sos` file is deleted; duplicate LTL lines are stripped in
    place. `.sos` files are keyed by language identity (`sos.sos_key`), independent
    of `key` (which is the HOA/LTL AP-canonical key)."""
    seen: set[str] = set()

    def op(path: Path, text: str) -> Tuple[Optional[str], int]:
        if path.suffix == ".sos":
            k = sos_key(text)
            if k in seen:
                return "", 1                 # delete the duplicate language dump
            seen.add(k)
            return None, 0
        if _is_hoa_text(text):
            k = key(text)
            if k in seen:
                return "", 1                 # delete the duplicate automaton
            seen.add(k)
            return None, 0
        kept = []
        n = 0
        for line in text.splitlines():
            body = line.split("#", 1)[0].strip()
            if body:
                k = key(body)
                if k in seen:
                    n += 1
                    continue
                seen.add(k)
            kept.append(line)
        if n:
            return "\n".join(kept) + ("\n" if text.endswith("\n") else ""), n
        return None, 0

    return op


if __name__ == "__main__":
    raise SystemExit(sweep.cli(dropper(), sys.argv[1:], verb="drop", suffixes=SUFFIXES))
