"""Merge census drops into one keyed CSV — the committed record of a grown catalogue.

    python3 -m tests.sosl.merge_drops --key case_id,config_id -o OUT.csv IN.csv...
    python3 -m tests.sosl.merge_drops --key case,kind -o OUT.csv IN.csv...

A drop is additive: each run covers the languages the previous ones did not, so the
record is the concatenation of their CSVs. Concatenation is only safe if no key is
claimed twice — a duplicate `(case, config)` means two runs computed the same cell,
which silently corrupts every tally downstream — so a repeated key is a **hard
error**, not a last-writer-wins merge, unless `--allow-dup` says the rows agree by
construction (then the first is kept).

Later files win nothing and lose nothing: order is irrelevant to the result, only to
which file a duplicate is blamed on. The header is taken from the first input, and
every input must carry the same columns.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


def merge(paths: Sequence[Path], key_cols: Sequence[str],
          allow_dup: bool = False) -> Tuple[List[str], List[dict]]:
    """Concatenate ``paths``, keyed by ``key_cols``. Raises on a repeated key
    (unless ``allow_dup``) or on inputs whose columns disagree."""
    fields: Optional[List[str]] = None
    seen: Dict[Tuple[str, ...], Path] = {}
    rows: List[dict] = []
    for p in paths:
        with open(p, newline="") as fh:
            rd = csv.DictReader(fh)
            if fields is None:
                fields = list(rd.fieldnames or [])
            elif list(rd.fieldnames or []) != fields:
                raise SystemExit(
                    f"merge_drops: {p} has different columns than {paths[0]}")
            for r in rd:
                k = tuple(r[c] for c in key_cols)
                if k in seen:
                    if allow_dup:
                        continue
                    raise SystemExit(
                        f"merge_drops: duplicate key {k} in {p} (already in "
                        f"{seen[k]}) — two runs computed the same cell; refusing "
                        f"to merge")
                seen[k] = p
                rows.append(r)
    if fields is None:
        raise SystemExit("merge_drops: no inputs")
    return fields, rows


def main(argv: List[str]) -> int:
    key_cols: List[str] = ["case_id", "config_id"]
    out: str = ""
    allow_dup = False
    inputs: List[Path] = []
    skip = -1
    for i, a in enumerate(argv):
        if i == skip:
            continue
        if a == "--key":
            key_cols = argv[i + 1].split(","); skip = i + 1
        elif a in ("-o", "--out"):
            out = argv[i + 1]; skip = i + 1
        elif a == "--allow-dup":
            allow_dup = True
        else:
            inputs.append(Path(a))
    if not inputs or not out:
        print(__doc__, file=sys.stderr)
        return 2

    fields, rows = merge(inputs, key_cols, allow_dup)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    keys = {tuple(r[c] for c in key_cols) for r in rows}
    print(f"merged {len(inputs)} file(s) -> {out}: {len(rows)} rows, "
          f"{len(keys)} distinct {'+'.join(key_cols)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
