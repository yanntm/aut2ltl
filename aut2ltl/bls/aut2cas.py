"""
bls/aut2cas.py — lift a CascadeTranslator up to a Translator via the GAP bridge.

A CascadeTranslator works on an already-decomposed `Cascade`; a `Translator`
works on a contract `Language` (the floor input type). `as_translator` is the
adapter that closes the gap: given a Language it builds the Krohn-Rhodes cascade
with `decompose_lang` (pulls `Language.det_parity_sbacc()` -> GAP SgpDec holonomy)
and runs the cascade-translator on it. The result `LTLResult` (formula +
technique) is forwarded unchanged.

This adapter is PURE: it knows nothing of LTL-definability. The cascade is unsound
on a non-LTL language, so callers must wrap it in `definability_gate`
(`bls/definability`) — the border that intercepts a non-definable Language as
NOT_LTL (with a witness) before this adapter ever decomposes. Keeping the gate out
keeps `as_translator` a reusable brick (gated or not, the caller decides).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from aut2ltl.translator import Translator
from .cascade_translator import CascadeTranslator
from aut2ltl.result import LTLResult
from .gap import decompose_lang
from .cascade import CascadeHolder

if TYPE_CHECKING:
    from aut2ltl.language import Language


def as_translator(
    ct: CascadeTranslator,
    *,
    gap_cmd: str = "gap",
    timeout: int = 180,
    max_aps: int = 5,
) -> Translator:
    """Lift a CascadeTranslator to a Translator: decompose the Language to a
    cascade (GAP) and run `ct` on it. Decomposition options are captured at build
    time; the returned Translator takes only the Language (the contract shape)."""

    def reconstruct(lang: "Language") -> LTLResult:
        # PURE cascade adapter: decompose, then run the cascade-translator. The
        # LTL-definability gate is NOT here — callers wrap this in `definability_gate`
        # (the cascade is unsound on a non-LTL language; the gate intercepts it
        # before we ever decompose).
        casc = decompose_lang(lang, gap_cmd=gap_cmd, timeout=timeout, max_aps=max_aps)
        # Depth guard dropped (was 3 levels during find-issues-small-first dev):
        # the ladder is green through 3L and the construction is fully memoized
        # with a distinct-subproblem guard (KR_REACH_GUARD), which is the real
        # runaway protection. KR_MAX_LEVELS gives an opt-in ceiling if ever needed.
        max_levels = int(os.environ.get("KR_MAX_LEVELS", "0"))
        if max_levels > 0 and casc.num_levels > max_levels:
            raise NotImplementedError(
                f"Reconstruction depth ceiling KR_MAX_LEVELS={max_levels} "
                f"(got {casc.num_levels} levels)."
            )
        # The CascadeHolder carries this build's memos + counters (no module
        # globals, no reset); discarding it after the build IS the reset.
        holder = CascadeHolder(casc)
        return ct(holder)

    return reconstruct


__all__ = ["as_translator"]
