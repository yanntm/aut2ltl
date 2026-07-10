"""genaut/gen/sample.py — reproducible random sampling of a shape's id space to a
target number of *distinct languages*, for shapes past the exhaustive wall.

For a shape whose id space `N = |guards|^|slots|` is too large to enumerate
(`SHAPES.md`'s "beyond the wall"), this draws combo ids uniformly at random with
a fixed seed, decodes each with the **index trick** (base-|guards| digits — NOT
`Shape.combo_at`, which is O(index) and unusable here), builds and reduces the
automaton, canonizes it to its syntactic invariant `𝓘(L)`, and keeps it only if
its language is new. Sampling is uniform over *presentations*, so a language with
many encodings is likelier drawn — the sample is a probe of the shape, honestly
**not** an exhaustive census.

Two dedup gates: the reduced HOA md5 (skip re-canonizing byte-identical draws)
and, decisively, the `𝓘` dump (the language key). It stops at `--target-langs`
distinct languages (default), or `--sample` draws, or the `--max-draws` safety
cap — whichever first. Keepers are written incrementally, so an interrupted
overnight run keeps everything found so far.

Output is a clearly-non-exhaustive tree so it never masquerades as a census:

    corpus/sampled/<tag>__seed<S>/det/<tag>_<id>.hoa      canonical D per language
    corpus/sampled/<tag>__seed<S>/sos/<tag>_<id>.sos      𝓘(L) per language
    corpus/sampled/<tag>__seed<S>/sample.json             seed, draws, yield, cap

Usage:
  python3 genaut/gen/sample.py <n,k,c[,acc]> [--target-langs T] [--sample K]
                               [--max-draws M] [--seed S] [--corpus DIR]
    e.g.  python3 genaut/gen/sample.py 2,1,2,parity --target-langs 1024 --seed 0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shutil
import sys
from typing import Dict, List, Optional, Tuple

import spot

# sibling modules (path-script: genaut/gen is sys.path[0])
from build import build_aut, reduce_aut
from shape import Shape
from enumerate import _ap_canonical_key, parse_shape

# sosl carries the canonical construction; put its package root on the path.
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
_SOSL = os.path.join(_REPO, "sosl")
if _SOSL not in sys.path:
    sys.path.insert(0, _SOSL)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from aut2ltl.ltl.twa import dump_hoa                    # noqa: E402
from sosl.sos import dump_invariant                     # noqa: E402
from sosl.sos.build.importer import canonical           # noqa: E402
from sosl.sos.core.quotient import invariant_of         # noqa: E402

_CORPUS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, "corpus"))


def combo_of(shape: Shape, index: int) -> Tuple[int, ...]:
    """The guard tuple at generator id ``index`` by direct base-|guards| decode —
    O(|slots|), the fast inverse of the driver's `itertools.product` order (last
    slot fastest). This is the index trick that makes random sampling of a huge
    id space feasible where `Shape.combo_at` (O(index)) is not."""
    guards = shape.guards
    g = len(guards)
    s = len(shape.slots)
    digits: List[int] = [0] * s
    for pos in range(s - 1, -1, -1):
        index, r = divmod(index, g)
        digits[pos] = r
    return tuple(guards[d] for d in digits)


def sample(
    shape: Shape, target_langs: Optional[int], sample_draws: Optional[int],
    max_draws: int, seed: int, corpus: str,
) -> Dict:
    """Draw ids until the stop condition, keeping one representative per distinct
    language. Returns the run summary (and writes the det/ + sos/ tiers)."""
    tag = shape.tag
    n = shape.num_combos
    width = shape.id_width
    out_root = os.path.join(corpus, "sampled", f"{tag}__seed{seed}")
    det_dir = os.path.join(out_root, "det")
    sos_dir = os.path.join(out_root, "sos")
    for d in (det_dir, sos_dir):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    rng = random.Random(seed)
    bdict = spot.make_bdd_dict()
    ap_key = _ap_canonical_key()      # polarity o names — the census dedup gate
    seen_ids: set = set()
    seen_md5: set = set()             # byte-identical reduced HOA
    seen_key: set = set()             # AP-canonical twin (a<->!a, AP rename)
    langs: Dict[str, str] = {}        # 𝓘 dump -> representative id
    draws = folded = capped = 0

    def done() -> bool:
        if target_langs is not None and len(langs) >= target_langs:
            return True
        if sample_draws is not None and draws >= sample_draws:
            return True
        return draws >= max_draws

    while not done():
        i = rng.randrange(n)
        if i in seen_ids:
            continue
        seen_ids.add(i)
        draws += 1
        combo = combo_of(shape, i)
        red = reduce_aut(build_aut(shape, combo, bdict))
        content = dump_hoa(red)           # canonical bytes, as the census writes
        digest = hashlib.md5(content.encode()).hexdigest()
        if digest in seen_md5:
            continue
        seen_md5.add(digest)
        # fold a<->!a / AP-rename twins on the text, THEN canonicalize, as the
        # census does — canonicalizing first defeats the fold (canon.normalize
        # orders successors by the printed condition).
        key = dump_hoa(spot.automaton(ap_key(red.to_str("hoa"))))
        if key in seen_key:
            folded += 1
            continue
        seen_key.add(key)
        D = canonical(red)
        inv = invariant_of(D)
        if inv is None:
            capped += 1
            continue
        dump = dump_invariant(inv)
        if dump in langs:
            continue
        ident = f"{tag}_{i:0{width}d}"
        langs[dump] = ident
        with open(os.path.join(det_dir, f"{ident}.hoa"), "w") as fh:
            fh.write(dump_hoa(D))
        with open(os.path.join(sos_dir, f"{ident}.sos"), "w") as fh:
            fh.write(dump)
        if len(langs) % 64 == 0:
            print(f"  ... {draws} draws, {len(langs)} languages "
                  f"({capped} capped)", file=sys.stderr, flush=True)

    summary = {
        "tag": tag, "seed": seed, "num_combos": n,
        "target_langs": target_langs, "sample_draws": sample_draws,
        "max_draws": max_draws, "draws": draws, "languages": len(langs),
        "polarity_name_twins_folded": folded, "capped": capped, "exhaustive": False,
        "yield_per_draw": round(len(langs) / draws, 4) if draws else 0.0,
    }
    with open(os.path.join(out_root, "sample.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")
    return summary


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="sample")
    ap.add_argument("token", help="shape: n,k,c[,acc]")
    ap.add_argument("--target-langs", type=int, default=1024,
                    help="stop at this many distinct languages (default 1024)")
    ap.add_argument("--sample", type=int, default=None,
                    help="alternatively, stop after this many draws")
    ap.add_argument("--max-draws", type=int, default=None,
                    help="optional cap on draws; default is to exhaust the id space "
                         "(so the only stops are --target-langs or exhaustion)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--corpus", default=_CORPUS)
    args = ap.parse_args(argv)

    shape = parse_shape(args.token)
    if shape.naps < 1:
        raise SystemExit(f"{shape.tag}: 0-AP shapes are linguistically empty.")
    # Default: run to the target language count OR exhaust the id space. There is
    # no arbitrary draw cap unless the user sets one explicitly.
    max_draws = args.max_draws if args.max_draws is not None else shape.num_combos
    max_draws = min(max_draws, shape.num_combos)

    print(f"=== sample {shape.tag} (N={shape.num_combos}) seed={args.seed} "
          f"target_langs={args.target_langs} sample={args.sample} "
          f"max_draws={max_draws} ===", flush=True)
    s = sample(shape, args.target_langs, args.sample, max_draws, args.seed,
               args.corpus)
    print(f"[{s['tag']}] {s['draws']} draws -> {s['languages']} languages "
          f"({s['capped']} capped, {s['yield_per_draw']} lang/draw) -> "
          f"corpus/sampled/{s['tag']}__seed{s['seed']}/", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
