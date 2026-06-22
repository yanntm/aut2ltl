"""Canonicalise a whole corpus folder: AP-rename every file AND dedup, in one
recursive pass — `dedup` with renaming built in, the maximal normalize.

Per file: a HOA is AP-renamed (`normalize_hoa`); an LTL list has each formula line
AP-renamed (`normalize_ltl`, comments preserved). Then the dedup key (polarity∘names
of the renamed form) drops later duplicates: a duplicate HOA file is deleted,
duplicate LTL lines are stripped. The walk, dry-run/`--prune` and report come from
`survey.normalize.sweep`; the key is `dedup.default_key`.

For an isolated, print-only rename of ONE file or formula, use
`survey.normalize.names`. For dedup WITHOUT renaming, use `survey.normalize.dedup`.

CLI (from the repo root):
    python3 -m survey.normalize.canon FOLDER           # dry run: per-file change counts
    python3 -m survey.normalize.canon --prune FOLDER   # apply: rewrite renamed / drop dups
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

from survey.normalize import sweep
from survey.normalize.dedup import Key, default_key
from survey.normalize.names import _is_hoa_text, normalize_hoa, normalize_ltl


def canonicalizer(key: Key = default_key) -> "sweep.Op":
    """A `sweep` Op that AP-renames each file to canonical form and drops later
    duplicates under `key`. A file changes if it is renamed and/or loses items."""
    seen: set[str] = set()

    def op(path: Path, text: str) -> Tuple[Optional[str], int]:
        if _is_hoa_text(text):
            renamed = normalize_hoa(text)
            k = key(renamed)
            if k in seen:
                return "", 1                       # delete the duplicate automaton
            seen.add(k)
            return (renamed, 1) if renamed != text else (None, 0)
        out: List[str] = []
        n = 0
        for line in text.splitlines():
            body = line.split("#", 1)[0].strip()
            if not body:
                out.append(line)
                continue
            renamed = normalize_ltl(body)
            if key(renamed) in seen:
                n += 1                             # drop the duplicate formula line
                continue
            seen.add(key(renamed))
            new_line = line.replace(body, renamed) if renamed != body else line
            n += new_line != line
            out.append(new_line)
        new_text = "\n".join(out) + ("\n" if text.endswith("\n") else "")
        return (new_text, n) if (n or new_text != text) else (None, 0)

    return op


if __name__ == "__main__":
    raise SystemExit(sweep.cli(canonicalizer(), sys.argv[1:], verb="normalize"))
