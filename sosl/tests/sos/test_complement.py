"""`Invariant.complement` — the free P-flip.

Checks the three laws the operation is used for, over the committed `.sos`
corpus (the flat_canon catalogue, which is complement-closed by construction):

  1. **involution** — ``inv.complement().complement() == inv``;
  2. **table-preserving** — only the ``P`` block moves, so the dump differs from
     the original's in that block alone and the algebra stays byte-identical;
  3. **agreement with the automaton** — the flip realizes the same language as
     `spot.dualize` on the paired canonical `det/` HOA (the cross-check
     `genaut/gen/flatten.py` asserts when it closes the catalogue), and it
     decides membership dually on every linked pair.

Run: ``python3 -m tests.sos.test_complement [N]`` from ``sosl/`` (N = how many
corpus languages to sample, default 40).
"""
from __future__ import annotations

import os
import sys
from typing import List

_SOSL = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if _SOSL not in sys.path:
    sys.path.insert(0, _SOSL)

import spot  # noqa: E402

from sosl.sos import dump_invariant, load_invariant  # noqa: E402
from sosl.sos.build.importer import canonical  # noqa: E402
from sosl.sos.core.quotient import invariant_of  # noqa: E402

_CORPUS = os.path.normpath(os.path.join(
    _SOSL, os.pardir, "genaut", "corpus", "flat_canon"))


def _cases(limit: int) -> List[str]:
    sos_dir = os.path.join(_CORPUS, "sos")
    names = sorted(f[:-4] for f in os.listdir(sos_dir) if f.endswith(".sos"))
    if len(names) <= limit:
        return names
    step = len(names) / limit                      # spread over the catalogue
    return [names[int(i * step)] for i in range(limit)]


def main(argv: List[str]) -> int:
    limit = int(argv[0]) if argv else 40
    names = _cases(limit)
    for ident in names:
        with open(os.path.join(_CORPUS, "sos", ident + ".sos")) as fh:
            text = fh.read()
        inv = load_invariant(text)
        comp = inv.complement()

        # 1. involution
        assert dump_invariant(comp.complement()) == dump_invariant(inv), \
            f"{ident}: complement is not an involution"

        # 2. the algebra is untouched; P is exactly the linked complement
        assert comp.alphabet == inv.alphabet and comp.keys == inv.keys, ident
        assert comp.mult == inv.mult and comp.identity == inv.identity, ident
        assert comp.letter_class == inv.letter_class, ident
        linked = inv.linked_pairs()
        assert comp.accept == linked - inv.accept, ident
        assert not (comp.accept & inv.accept) and comp.accept | inv.accept == linked, \
            f"{ident}: P and its complement do not partition the linked pairs"
        comp.validate()

        # 3a. membership is dual on every linked pair
        for pair in linked:
            assert (pair in inv.accept) != (pair in comp.accept), ident

        # 3b. the flip agrees with dualizing the paired canonical automaton
        det = os.path.join(_CORPUS, "det", ident + ".hoa")
        if os.path.isfile(det):
            Dc = canonical(spot.dualize(spot.automaton(open(det).read())))
            got = invariant_of(Dc)
            assert got is not None, f"{ident}: dualized automaton exceeded the cap"
            assert dump_invariant(got) == dump_invariant(comp), \
                f"{ident}: flip-P disagrees with dualize(det)"

    print(f"SUCCESS: Invariant.complement — {len(names)} languages "
          f"(involution, table-preserving, dual to spot.dualize)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
