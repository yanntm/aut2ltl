"""genaut/gen/rebuild.py — (re)build the canonical corpus tiers from TGBA.

Loops `canonize` over shapes, turning each `corpus/tgba/<tag>/` into its
`corpus/det/<tag>/`, `corpus/sos/<tag>/` and `corpus/spot_det/<tag>/` tiers (see
`canonize.py`). Additive by default — a shape whose three tier folders already
exist is **skipped**, so re-running only fills in what is missing (including the
`spot_det` tier for shapes built before it existed); pass `--force` to `rm` and
rebuild every named shape. (A direct `canonize.py <tag>` always rebuilds one shape.)

This does not enumerate: the TGBA tier is produced by `enumerate.py` and promoted
to `corpus/tgba/` first (see README). To add a shape to the census, enumerate it,
promote it, then run this.

Usage:
  python3 genaut/gen/rebuild.py [--force] [--corpus DIR] [tag ...]
    tag        shapes to build (default: every folder under corpus/tgba/)
    --force    rebuild even shapes already present
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

from canonize import canonize, _CORPUS


def _shapes(corpus: str, tags: List[str]) -> List[str]:
    tgba_root = os.path.join(corpus, "tgba")
    if tags:
        return tags
    if not os.path.isdir(tgba_root):
        return []
    return sorted(d for d in os.listdir(tgba_root)
                  if os.path.isdir(os.path.join(tgba_root, d)))


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="rebuild")
    ap.add_argument("tags", nargs="*")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--corpus", default=_CORPUS)
    args = ap.parse_args(argv)

    shapes = _shapes(args.corpus, args.tags)
    if not shapes:
        print(f"no shapes under {args.corpus}/tgba/", file=sys.stderr)
        return 1

    built = skipped = 0
    for tag in shapes:
        in_dir = os.path.join(args.corpus, "tgba", tag)
        if not os.path.isdir(in_dir):
            print(f"  ! {tag}: no TGBA source, skipped", file=sys.stderr)
            continue
        tiers = [os.path.join(args.corpus, t, tag)
                 for t in ("det", "sos", "spot_det")]
        if not args.force and all(os.path.isdir(t) for t in tiers):
            print(f"  = {tag}: already built, skipped (--force to rebuild)")
            skipped += 1
            continue
        f = canonize(tag, in_dir, args.corpus)
        print(f"  + {tag}: {f['tgba_in']} TGBA -> {f['spot_det']} det forms "
              f"-> {f['languages']} languages ({f['collapse']}x, {f['capped']} capped)")
        built += 1

    print(f"rebuild: {built} built, {skipped} skipped, {len(shapes)} shapes total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
