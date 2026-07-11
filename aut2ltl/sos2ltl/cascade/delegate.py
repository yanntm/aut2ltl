"""The engine's `LayerFallback`, implemented over the two halves.

`CascadeFallback` is what `engine.labels(…, fallback=…)` consumes: `omega`
answers a final-candidate layer class with the loop half's confined-tail
label (decomposing the tail-restricted acceptor — the presentation this
branch consults), `stem_finals` answers a no-width layer with Prop 4.14
labels for every class (one decomposition per layer, shared reach memos).
Every failure inside a half is absorbed into None — the engine then
declines exactly as it did without a delegate, and the translator's own
fallback chain takes over. The acceptor is pulled lazily and at most once:
a language whose layers never need the loop half never builds it.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple, TYPE_CHECKING

from .loop import loop_acceptance
from .machine import StemCascade, stem_cascade
from .stem import stem_label

from .. import anchoring as _anchoring
from .. import cayley as _cayley
from ..guards import Guards

if TYPE_CHECKING:
    import spot


class CascadeFallback:
    """One translation's delegate: lazy acceptor, per-layer memos."""

    def __init__(self, acceptor: Callable[[], "spot.twa_graph"], *,
                 gap_cmd: str = "gap", timeout: int = 60) -> None:
        self._acceptor = acceptor
        self._aut_d: Optional["spot.twa_graph"] = None
        self._gap_cmd = gap_cmd
        self._timeout = timeout
        self._omegas: Dict[Tuple[int, int], Optional["spot.formula"]] = {}

    def _d(self) -> "spot.twa_graph":
        if self._aut_d is None:
            self._aut_d = self._acceptor()
        return self._aut_d

    def omega(self, cay: "_cayley.Cayley", layer_id: int,
              cls: int) -> Optional["spot.formula"]:
        key = (layer_id, cls)
        if key not in self._omegas:
            try:
                em = loop_acceptance(cay, layer_id, self._d(), cls,
                                     gap_cmd=self._gap_cmd,
                                     timeout=self._timeout)
                self._omegas[key] = em.formula
            except Exception:
                self._omegas[key] = None
        return self._omegas[key]

    def stem_finals(self, cay: "_cayley.Cayley", layer_id: int,
                    la: "_anchoring.LayerAnchoring",
                    final: Dict[int, "spot.formula"], guards: Guards,
                    om: Callable[[int], Optional["spot.formula"]],
                    ) -> Optional[Dict[int, "spot.formula"]]:
        try:
            sc: StemCascade = stem_cascade(cay, layer_id,
                                           gap_cmd=self._gap_cmd,
                                           timeout=self._timeout)
        except Exception:
            return None
        out: Dict[int, "spot.formula"] = {}
        for c in la.layer:
            omega_c = om(c)
            if omega_c is None:
                return None
            try:
                out[c] = stem_label(cay, layer_id, la, c, final, guards,
                                    omega_c, sc=sc).formula
            except Exception:
                return None
        return out
