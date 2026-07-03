"""deep_nobls_sort recipe — `deep_nobls` over the SORTED peel (precise before heuristic).

The same deep round-trip shape as `deep_nobls`, but BOTH engines are the new sorted
`peel` (`portfolio/builder.py`): per descent it tries the EXACT producers first —
`Daisy` → `DaisystarDet` (rejecting deterministic SCC) → `PartScc` (accepting terminal
SCC) — and only then the oracle-gated heuristics `Daisy2` / `Daisystar`, before the
floor. The two engines differ ONLY in that floor, exactly the `deep_nobls`
two-engine split:

  * forward seed — `peel(bls)`: floors on the bls cascade, so it always answers and
    the seed DAG is complete (blobs and all, as the seed is allowed to be);
  * return labeler — `peel(decline)`: floors on `decline` (NO cascade), so a node it
    cannot re-derive without bls is declined and the seed's node is kept — bls is
    counterproductive on the return path (the `deep_nobls` rationale).

`deep_roundtrip` re-presents every DAG node bottom-up via the return labeler, kept per
node only when not larger (`best_of([identity, relabel])`); a final `hi` simplifier
over the whole. Copied into its own file to leave `deep_nobls` untouched; the forward
seed may be swapped to `peel_decomp(bls)` (decomp woven per descent) for the A/B, and
the two recipes may fuse once the better configuration is settled.
"""
from __future__ import annotations

from typing import Optional

from aut2ltl.translator import Translator
from aut2ltl.options import Options
from aut2ltl.combinators.best_of import best_of
from aut2ltl.ltl_rewriter import identity, relabel, as_translator
from aut2ltl.roundtrip import deep_roundtrip
from aut2ltl.simplify_ltl import Simplify
from ..builder import peel, decline, bls


def deep_nobls_sort(options: Optional[Options] = None) -> Translator:
    """Forward `peel(bls)` seeds a formula; `deep_roundtrip` re-presents every DAG node
    bottom-up via `peel(decline)` (no cascade), kept per node only when not larger
    (`best_of([identity, relabel])`); a final `hi` simplifier over the whole."""
    forward = Simplify(peel(bls(options)), "hi")
    represent = best_of([identity, relabel(Simplify(peel(decline), "hi"))],
                        name="deep_nobls_sort_arm")
    rewriter = deep_roundtrip(represent)
    return Simplify(as_translator(forward, rewriter), "hi")


__all__ = ["deep_nobls_sort"]
