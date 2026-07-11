"""genaut/gen/hunt.py — hunt a shape's id space for derivative-regime languages.

The Wagner-degree read-off on the syntactic invariant resolves every language
except those in the derivative regime `m >= 1 & n+ = n-` (the classifier emits
PARTIAL there; `sos_classification.md` §4). The regime's sharp floor is the
three-state, two-colour parity shape (§7), which the corpus holds only as a
non-exhaustive sample — and that sample has no PARTIAL language. This script
hunts one: it draws combo ids uniformly at random (the `sample.py` index trick
and dedup gates), runs the census chain on each draw
(`build -> reduce -> canonical D -> 𝓘(L)`), classifies the invariant, and
keeps exactly the draws whose degree tail is PARTIAL — each a corpus-native
specimen of the regime, written with its det HOA, `.sos`, and `.cat`.

Every hit is deduplicated by the `flatten --canon` language identity (`B_k`
orbit of the minimized invariant), so relabel/polarity twins keep one entry.
Output goes under the scratch --out root, never the tracked corpus:

    <out>/hunt/<tag>__seed<S>/det/<tag>_<id>.hoa     canonical D per hit
    <out>/hunt/<tag>__seed<S>/sos/<tag>_<id>.sos     𝓘(L) per hit
    <out>/hunt/<tag>__seed<S>/sos/<tag>_<id>.cat     its classification record

Usage:
  python3 genaut/gen/hunt.py <n,k,c[,acc]> [--sample K] [--target-hits H]
                             [--seed S] [--out DIR]
    e.g.  python3 genaut/gen/hunt.py 3,1,2,parity --sample 20000 --seed 0
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from typing import Dict, List, Optional

import spot

# sibling modules (path-script: genaut/gen is sys.path[0])
from build import build_aut, reduce_aut
from enumerate import _ap_canonical_key, parse_shape
from sample import _OUT, canon_key, combo_of
from shape import Shape

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
_SOSL = os.path.join(_REPO, "sosl")
for p in (_SOSL, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from aut2ltl.ltl.twa import dump_hoa                     # noqa: E402
from sosl.sos import dump_invariant                      # noqa: E402
from sosl.sos.build.importer import canonical            # noqa: E402
from sosl.sos.classify import classify                   # noqa: E402
from sosl.sos.classify.io import cat_text                # noqa: E402
from sosl.sos.core.quotient import invariant_of          # noqa: E402


def hunt(shape: Shape, sample_draws: int, target_hits: Optional[int],
         seed: int, out_root_base: str) -> Dict:
    """Draw ids until ``sample_draws`` draws (or ``target_hits`` PARTIAL
    languages) and keep every draw whose classification needs the derivative.
    Returns the run summary; hits are written incrementally."""
    import random
    tag = shape.tag
    out_root = os.path.join(out_root_base, "hunt", f"{tag}__seed{seed}")
    det_dir = os.path.join(out_root, "det")
    sos_dir = os.path.join(out_root, "sos")
    for d in (det_dir, sos_dir):
        os.makedirs(d, exist_ok=True)

    rng = random.Random(seed)
    bdict = spot.make_bdd_dict()
    ap_key = _ap_canonical_key()
    seen_ids: set = set()
    seen_md5: set = set()
    seen_key: set = set()
    hits: Dict[str, str] = {}          # canon_key -> representative id
    draws = capped = 0
    t0 = time.time()

    def done() -> bool:
        if target_hits is not None and len(hits) >= target_hits:
            return True
        return draws >= sample_draws

    while not done():
        i = rng.randrange(shape.num_combos)
        if i in seen_ids:
            continue
        seen_ids.add(i)
        draws += 1
        if draws % 2000 == 0:
            print(f"  ... {draws} draws, {len(hits)} hits, {capped} capped, "
                  f"{draws / (time.time() - t0):.0f} draws/s",
                  file=sys.stderr, flush=True)
        red = reduce_aut(build_aut(shape, combo_of(shape, i), bdict))
        digest = hashlib.md5(dump_hoa(red).encode()).hexdigest()
        if digest in seen_md5:
            continue
        seen_md5.add(digest)
        key = dump_hoa(spot.automaton(ap_key(red.to_str("hoa"))))
        if key in seen_key:
            continue
        seen_key.add(key)
        D = canonical(red)
        inv = invariant_of(D)
        if inv is None:
            capped += 1
            continue
        rec = classify(inv)
        if not rec.gamma_partial:
            continue
        ck = canon_key(D)              # dedup hits by language up to relabeling
        if ck is None or ck in hits:
            continue
        ident = f"{tag}_{i:0{shape.id_width}d}"
        hits[ck] = ident
        with open(os.path.join(det_dir, f"{ident}.hoa"), "w") as fh:
            fh.write(dump_hoa(D))
        with open(os.path.join(sos_dir, f"{ident}.sos"), "w") as fh:
            fh.write(dump_invariant(inv))
        with open(os.path.join(sos_dir, f"{ident}.cat"), "w") as fh:
            fh.write(cat_text(rec))
        coords = (rec.m_plus, rec.m_minus, rec.n_plus, rec.n_minus)
        print(f"HIT {ident}: coords {coords}, mu = {rec.mu}, |C| = "
              f"{len(inv.keys)}, LTL = {rec.aperiodic}", flush=True)

    return {"tag": tag, "seed": seed, "draws": draws, "hits": len(hits),
            "capped": capped, "seconds": round(time.time() - t0, 1),
            "out": out_root}


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="hunt")
    ap.add_argument("token", help="shape: n,k,c[,acc]")
    ap.add_argument("--sample", type=int, default=20000,
                    help="stop after this many draws (default 20000)")
    ap.add_argument("--target-hits", type=int, default=None,
                    help="stop early at this many PARTIAL languages")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=_OUT,
                    help="root to write hunt/<tag>__seed<S>/ under "
                         "(default logs/genaut/corpus, ignored scratch)")
    args = ap.parse_args(argv)

    shape = parse_shape(args.token)
    if shape.naps < 1:
        raise SystemExit(f"{shape.tag}: 0-AP shapes are linguistically empty.")
    print(f"=== hunt {shape.tag} (N={shape.num_combos}) seed={args.seed} "
          f"sample={args.sample} target_hits={args.target_hits} ===", flush=True)
    s = hunt(shape, args.sample, args.target_hits, args.seed, args.out)
    print(f"[{s['tag']}] {s['draws']} draws in {s['seconds']}s -> "
          f"{s['hits']} derivative-regime languages ({s['capped']} capped) "
          f"-> {s['out']}", flush=True)
    return s["hits"] == 0                    # exit 1 when the hunt comes home empty
    # (a finding either way: hits give fixtures, none bounds the regime's density)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
