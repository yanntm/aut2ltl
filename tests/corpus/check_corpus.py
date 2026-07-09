"""Structural checks on `corpus/{det,sos}/` — the language tier.

The build (`corpus/canonize.py`) claims four things. This asserts them against the
committed corpus, not against the build's own bookkeeping:

  1. **paired** — `det/` and `sos/` hold the same basenames, one each;
  2. **irredundant** — the `.sos` dumps are pairwise distinct, so no language is
     catalogued twice (byte-equal ⟺ equal language, [SωS26 Thm. 5.1]);
  3. **complement-closed** — every language's dual is also catalogued, every
     `<x>_c` has its primal `<x>`, and the catalogue is therefore even;
  4. **coherent** — each `det/*.hoa` really presents the language its `sos/*.sos`
     names: `invariant_of(canonical(D))` reproduces the dump byte-for-byte.

Check 4 reruns the construction, so it is sampled (`N`, default 40); 1-3 are cheap
and run over the whole corpus.

Run: ``python3 -m tests.corpus.check_corpus [N]`` from the repo root.
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
for _p in (_REPO, os.path.join(_REPO, "sosl")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import spot  # noqa: E402

from sosl.sos import dump_invariant, load_invariant  # noqa: E402
from sosl.sos.build.importer import canonical  # noqa: E402
from sosl.sos.core.quotient import invariant_of  # noqa: E402
from survey.normalize.sos import sos_key  # noqa: E402

_CORPUS = os.path.join(_REPO, "corpus")


def main(argv: List[str]) -> int:
    limit = int(argv[0]) if argv else 40
    det_dir, sos_dir = os.path.join(_CORPUS, "det"), os.path.join(_CORPUS, "sos")

    # 1. paired
    dets = sorted(f[:-4] for f in os.listdir(det_dir) if f.endswith(".hoa"))
    soss = sorted(f[:-4] for f in os.listdir(sos_dir) if f.endswith(".sos"))
    assert dets == soss, (
        f"det/ and sos/ disagree: {len(dets)} vs {len(soss)}; "
        f"only in det: {sorted(set(dets) - set(soss))[:5]}, "
        f"only in sos: {sorted(set(soss) - set(dets))[:5]}")
    n = len(soss)
    assert n, "empty corpus"

    # 2. irredundant
    by_key: Dict[str, str] = {}
    texts: Dict[str, str] = {}
    for ident in soss:
        with open(os.path.join(sos_dir, ident + ".sos")) as fh:
            texts[ident] = fh.read()
        key = sos_key(texts[ident])
        assert key not in by_key, \
            f"duplicate language: {ident} == {by_key[key]}"
        by_key[key] = ident

    # 3. complement-closed
    assert n % 2 == 0, f"catalogue is odd ({n}) — no language is its own complement"
    for ident in soss:
        comp = sos_key(dump_invariant(load_invariant(texts[ident]).complement()))
        assert comp in by_key, f"{ident}: its complement is not catalogued"
        assert by_key[comp] != ident, f"{ident}: is its own complement (impossible)"
    for ident in soss:
        if ident.endswith("_c"):
            assert ident[:-2] in by_key.values(), \
                f"{ident}: dual without its primal {ident[:-2]}"

    # 4. coherent (sampled)
    step = max(1, n // limit)
    sample = soss[::step][:limit]
    for ident in sample:
        D = canonical(spot.automaton(os.path.join(det_dir, ident + ".hoa")))
        inv = invariant_of(D)
        assert inv is not None, f"{ident}: det/ automaton exceeded the closure cap"
        assert sos_key(dump_invariant(inv)) == sos_key(texts[ident]), \
            f"{ident}: det/ HOA does not present the language its .sos names"

    duals = sum(1 for i in soss if i.endswith("_c"))
    print(f"SUCCESS: corpus — {n} languages ({n - duals} primal + "
          f"{duals} dual), paired, irredundant, complement-closed; "
          f"det/sos coherent on {len(sample)} sampled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
