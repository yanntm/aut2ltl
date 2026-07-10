"""genaut/gen/pipeline.py — one shape, end to end: enumerate -> canonize, into scratch.

Chains the whole generation pipeline for each shape token, so a census (local or
on a cluster) is one command:

  enumerate   gen/enumerate.py — exhaustive slot enumeration -> <out>/tgba/<tag>/
              (the two pre-write dedup gates: md5, then AP-canonical);
  canonize    gen/canonize.py — each survivor -> canonical D (det/) + 𝓘 (sos/),
              deduped by the syntactic key.

Everything lands under the scratch --out root in the corpus's own layout; adopting
a shape's tiers into the tracked corpus is a separate, deliberate copy.

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
import sys
from typing import List, Optional

# path-script: gen/ is sys.path[0], so the siblings import directly
import enumerate as _enum
from canonize import canonize

# Where a run writes: ignored scratch, in the corpus's own layout. Adopting a
# shape's tiers into the tracked corpus is a separate, deliberate copy — the run
# never writes tracked source.
_OUT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir,
                 "logs", "genaut", "corpus"))


def pipeline(token: str, limit: Optional[int], out_root: str) -> None:
    shape = _enum.parse_shape(token)
    tag = shape.tag
    # Enumerate straight into <out>/tgba/<tag>: that layout *is* the TGBA tier, so
    # there is no promote-into-tracked step, only a scratch tree to adopt later.
    tgba = os.path.join(out_root, "tgba")
    print(f"=== {tag}: enumerate -> tgba/ ===", flush=True)
    _enum.main(shape, limit, tgba)

    print(f"=== {tag}: canonize -> det/ + sos/ ===", flush=True)
    f = canonize(tag, os.path.join(tgba, tag), out_root)
    print(f"[{tag}] {f['tgba_in']} TGBA -> {f['languages']} languages "
          f"({f['collapse']}x collapse, {f['capped']} capped)", flush=True)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="pipeline")
    ap.add_argument("tokens", nargs="+")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out", default=_OUT,
                    help="root to write the tiers under, in corpus layout "
                         "(default logs/genaut/corpus, ignored scratch)")
    args = ap.parse_args(argv)
    for token in args.tokens:
        pipeline(token, args.limit, args.out)
    print("=== pipeline done; adopt from --out, then refresh SHAPES.md ===",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
