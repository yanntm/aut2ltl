"""genaut/gen/canonize.py — collapse a TGBA shape folder to its canonical tiers.

The census enumerates non-deterministic reduced TGBA into `corpus/tgba/<tag>/`.
This stage carries each survivor through the sosl construction to the two
canonical tiers of the corpus:

  corpus/det/<tag>/   the deterministic, complete, transition-based, generic
                      automaton D (`sosl ... importer.canonical`) as HOA — one
                      representative per distinct language;
  corpus/sos/<tag>/   the syntactic omega-semigroup 𝓘(L) as `.sos` — one per
                      distinct language, the compact canonical form later runs
                      consume directly (no presentation to reduce).

Both tiers are deduplicated by the **syntactic** key: the SHA-1 of the canonical
`𝓘` dump ([SωS26 Thm. 5.1] — byte-equal iff the languages are equal). Going
TGBA -> D collapses many relabel- and presentation-distinct automata onto one
language, so the language count is far below the TGBA `kept` count; the funnel
(combos -> byte-distinct -> AP-canonical -> **language-distinct**) is recorded in
each tier's `census.md` and composed into `SHAPES.md` by `shapes_table.py`.

Usage:
  python3 genaut/gen/canonize.py <tag> [--in DIR] [--corpus DIR] [--out DIR]
    <tag>     shape tag, e.g. 2state1ap1acc or 1state2ap2acc_parity
    --in      the TGBA source folder (default <corpus>/tgba/<tag>)
    --corpus  the corpus root to READ (default genaut/corpus)
    --out     the root to WRITE under, in the corpus's own layout (default
              logs/genaut/corpus, ignored scratch)

A run writes only under `--out`; adopting a generated tier into the tracked
corpus is a separate, deliberate copy.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import statistics
import sys
from collections import Counter
from typing import Dict, List, Optional

import spot

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

# Where a run writes. Never the read root: a generated tier is adopted into the
# tracked corpus by a separate, deliberate copy, never by the run that made it.
# The layout beneath is the corpus's own, so a run's output and the corpus differ
# only in their root.
_OUT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir,
                 "logs", "genaut", "corpus"))


def _ihash(dump: str) -> str:
    return hashlib.sha1(dump.encode()).hexdigest()[:16]


def _ap_canonical_key() -> "callable":
    """The shared AP-canonical dedup key (polarity ∘ names) from
    `survey.normalize`, the same gate `enumerate.py` applies to the TGBA tier —
    so the `spot_det` structural dedup is apples-to-apples with `tgba`."""
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from survey.normalize.dedup import default_key
    return default_key


def canonize(tag: str, in_dir: str, out_root: str) -> Dict:
    """Build the `det/` and `sos/` tiers for one shape from its TGBA folder,
    deduplicating by the syntactic `𝓘` key. Returns the funnel counts.

    Reads `in_dir`, writes under `out_root` in the corpus's own layout. The two
    are distinct roots: a run never writes where it read."""
    det_dir = os.path.join(out_root, "det", tag)
    sos_dir = os.path.join(out_root, "sos", tag)
    spot_det_dir = os.path.join(out_root, "spot_det", tag)
    for d in (det_dir, sos_dir, spot_det_dir):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    ap_key = _ap_canonical_key()
    files = sorted(f for f in os.listdir(in_dir) if f.endswith(".hoa"))
    seen: Dict[str, str] = {}                 # 𝓘-hash -> representative id
    abundance: Counter = Counter()            # 𝓘-hash -> automata realizing it
    sizes: Dict[str, int] = {}                # 𝓘-hash -> |𝒞|
    capped = 0
    det_md5: set = set()                      # byte-distinct determinized forms
    det_key: set = set()                      # AP-canonical determinized forms
    det_folded = 0
    for fname in files:
        ident = fname[:-4]                    # <tag>_<id>
        D = canonical(spot.automaton(os.path.join(in_dir, fname)))

        # spot_det tier: the SAME deterministic automaton D, deduped
        # *structurally* (md5 → AP-canonical, the TGBA gates) rather than by
        # language — the count of distinct deterministic presentations.
        #
        # The file is `D` canonically serialized, never polarity-flipped: it pairs
        # with a polarity-sensitive `.sos`. The dedup KEY is a different object —
        # the twins are folded on the text first, and only then is the presentation
        # canonicalized. Canonicalizing first would defeat the fold: `canon.normalize`
        # orders successors by the printed condition, so `a` and `!a` twins get
        # different state numberings and never converge.
        content = dump_hoa(D)
        key = dump_hoa(spot.automaton(ap_key(D.to_str("hoa"))))
        if hashlib.md5(content.encode()).hexdigest() not in det_md5:
            det_md5.add(hashlib.md5(content.encode()).hexdigest())
            if key in det_key:
                det_folded += 1
            else:
                det_key.add(key)
                with open(os.path.join(spot_det_dir, f"{ident}.hoa"), "w") as fh:
                    fh.write(content)

        inv = invariant_of(D)
        if inv is None:                       # algebra closure exceeded its cap
            capped += 1
            continue
        dump = dump_invariant(inv)
        h = _ihash(dump)
        abundance[h] += 1
        if h not in seen:                     # first automaton of this language wins
            seen[h] = ident
            sizes[h] = inv.n
            with open(os.path.join(det_dir, f"{ident}.hoa"), "w") as fh:
                fh.write(dump_hoa(D))
            with open(os.path.join(sos_dir, f"{ident}.sos"), "w") as fh:
                fh.write(dump)

    langs = len(seen)
    funnel = {
        "tag": tag, "tgba_in": len(files), "capped": capped,
        "languages": langs,
        "collapse": round(len(files) / langs, 2) if langs else 0.0,
        "abundance_max": max(abundance.values(), default=0),
        "abundance_median": int(statistics.median(abundance.values())) if abundance else 0,
        "size_min": min(sizes.values(), default=0),
        "size_median": int(statistics.median(sizes.values())) if sizes else 0,
        "size_max": max(sizes.values(), default=0),
        "spot_det": len(det_key), "spot_det_byte": len(det_md5),
        "spot_det_folded": det_folded,
    }
    _write_census(det_dir, sos_dir, funnel)
    _write_spot_det_census(spot_det_dir, funnel)
    return funnel


def _write_census(det_dir: str, sos_dir: str, f: Dict) -> None:
    """Record the language-dedup level next to each tier — the funnel step this
    stage owns; `shapes_table.py` joins it to the TGBA census for the full
    combos -> byte -> AP-canonical -> language funnel."""
    body = (
        f"# {f['tag']} — canonical (language) dedup\n\n"
        f"- TGBA survivors in (AP-canonical `kept`): {f['tgba_in']}\n"
        f"- **distinct languages (syntactic `𝓘` dedup): {f['languages']}**\n"
        f"- TGBA-to-language collapse: {f['collapse']}x"
        f"{f' ({f['capped']} capped)' if f['capped'] else ''}\n"
        f"- enumeration abundance per language: median {f['abundance_median']}, "
        f"max {f['abundance_max']}\n"
        f"- `N = |𝒞|` over languages: {f['size_min']} / {f['size_median']} / "
        f"{f['size_max']}  (min / median / max)\n\n"
        f"Built by `python3 genaut/gen/canonize.py {f['tag']}` from "
        f"`corpus/tgba/{f['tag']}/`.\n")
    with open(os.path.join(det_dir, "census.md"), "w") as fh:
        fh.write(body)
    with open(os.path.join(sos_dir, "census.md"), "w") as fh:
        fh.write(body)


def _write_spot_det_census(spot_det_dir: str, f: Dict) -> None:
    """Record the *structural* determinized-form count — the middle tier
    between `tgba` (presentation census) and `det`/`sos` (language census).
    Deduping the deterministic automaton `D` by its bytes (AP-canonical) rather
    than by `𝓘` keeps every distinct deterministic presentation of a language,
    so this count sits between the TGBA `kept` and the language count."""
    d2l = round(f["spot_det"] / f["languages"], 2) if f["languages"] else 0.0
    body = (
        f"# {f['tag']} — spot-determinized, structural dedup\n\n"
        f"- TGBA survivors in: {f['tgba_in']}\n"
        f"- byte-distinct determinized forms (md5): {f['spot_det_byte']}\n"
        f"- polarity/name twins folded: {f['spot_det_folded']}\n"
        f"- **kept (AP-canonical determinized forms): {f['spot_det']}**\n"
        f"- TGBA-to-det collapse: "
        f"{round(f['tgba_in'] / f['spot_det'], 2) if f['spot_det'] else 0.0}x\n"
        f"- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): "
        f"{f['languages']}  → det-to-language {d2l}x\n\n"
        f"The deterministic automaton `D` (`importer.canonical`) deduplicated by "
        f"its AP-canonical bytes, **not** by language — contrast the `det`/`sos` "
        f"tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by "
        f"`python3 genaut/gen/canonize.py {f['tag']}`.\n")
    with open(os.path.join(spot_det_dir, "census.md"), "w") as fh:
        fh.write(body)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="canonize")
    ap.add_argument("tag")
    ap.add_argument("--in", dest="in_dir",
                    help="the TGBA source folder (default <corpus>/tgba/<tag>)")
    ap.add_argument("--corpus", default=_CORPUS,
                    help="the corpus root to READ (default genaut/corpus)")
    ap.add_argument("--out", default=_OUT,
                    help="the root to WRITE under, in corpus layout "
                         "(default logs/genaut/corpus, ignored scratch)")
    args = ap.parse_args(argv)
    in_dir = args.in_dir or os.path.join(args.corpus, "tgba", args.tag)
    if not os.path.isdir(in_dir):
        print(f"no TGBA source folder: {in_dir}", file=sys.stderr)
        return 1
    f = canonize(args.tag, in_dir, args.out)
    print(f"[{f['tag']}] {f['tgba_in']} TGBA -> {f['spot_det']} determinized "
          f"forms (structural) -> {f['languages']} languages (semantic) "
          f"({f['collapse']}x collapse, {f['capped']} capped) "
          f"-> {args.out}/{{det,sos,spot_det}}/{f['tag']}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
