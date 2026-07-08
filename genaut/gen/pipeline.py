"""genaut/gen/pipeline.py — one shape, end to end: enumerate -> promote -> canonize.

Chains the whole generation pipeline for each shape token, so a census (local or
on a cluster) is one command:

  enumerate   gen/enumerate.py — exhaustive slot enumeration -> raw/<tag>/ (the
              two pre-write dedup gates: md5, then AP-canonical);
  promote     raw/<tag>/ -> corpus/tgba/<tag>/ (the git-tracked TGBA tier);
  canonize    gen/canonize.py — each survivor -> canonical D (det/) + 𝓘 (sos/),
              deduped by the syntactic key.

Most enumerated automata disappear at canonization (many presentations per
language), so the disk cost is the TGBA survivors, not the id space. The wall for
a large shape is *time* (one Spot pass per combo), not disk — submit those to a
cluster; this script is the unit of work.

Usage:
  python3 genaut/gen/pipeline.py <n,k,c[,acc]> [...] [--limit N]
    e.g.  python3 genaut/gen/pipeline.py 2,1,2,parity 2,1,2
    --limit  cap the enumeration at the first N combos (a smoke test / sample)
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from typing import List, Optional

# path-script: gen/ is sys.path[0], so the siblings import directly
import enumerate as _enum
from canonize import canonize

_CORPUS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, "corpus"))
_RAW = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, "raw"))


def pipeline(token: str, limit: Optional[int]) -> None:
    shape = _enum.parse_shape(token)
    tag = shape.tag
    print(f"=== {tag}: enumerate ===", flush=True)
    _enum.main(shape, limit)

    src = os.path.join(_RAW, tag)
    dst = os.path.join(_CORPUS, "tgba", tag)
    print(f"=== {tag}: promote raw -> corpus/tgba ===", flush=True)
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)

    print(f"=== {tag}: canonize -> det/ + sos/ ===", flush=True)
    f = canonize(tag, dst, _CORPUS)
    print(f"[{tag}] {f['tgba_in']} TGBA -> {f['languages']} languages "
          f"({f['collapse']}x collapse, {f['capped']} capped)", flush=True)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="pipeline")
    ap.add_argument("tokens", nargs="+")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args(argv)
    for token in args.tokens:
        pipeline(token, args.limit)
    print("=== pipeline done; refresh SHAPES.md with shapes_table.py ===",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
