"""
kr/aut2cas.py — lift a CascadeTranslator up to a Translator via the GAP bridge.

A CascadeTranslator works on an already-decomposed `Cascade`; a `Translator`
works on a contract `Language` (the floor input type). `as_translator` is the
adapter that closes the gap: given a Language it builds the Krohn-Rhodes cascade
with `decompose_lang` (pulls `Language.det_parity_sbacc()` -> GAP SgpDec holonomy)
and runs the cascade-translator on it. The result `LTLFormulaResult` (formula +
technique) is forwarded unchanged.

The module builds the default endpoint singleton `reconstruct`
(= `as_translator(hierarchy_class)`): the pure-kr Language -> LTLFormulaResult
entry, the cascade-level construction lifted to the Language level.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from aut2ltl.contract import LTLFormulaResult, Translator, CascadeTranslator
from aut2ltl.language import SAT_MIN_STATES
from .gap import decompose_lang
from .cascade import CascadeHolder
from .hierarchy_class import hierarchy_class

if TYPE_CHECKING:
    from aut2ltl.language import Language


def _sat_min_threshold() -> int:
    """The state count at/below which `Language` SAT-minimizes D — the regime in
    which a non-aperiodic reading is taken as a conclusive NOT_LTL proof (above
    it D may be non-minimal, so the verdict is only PROBABLY_NOT_LTL)."""
    return int(os.environ.get(SAT_MIN_STATES.env, SAT_MIN_STATES.default))


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

    def reconstruct(lang: "Language") -> LTLFormulaResult:
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
        # LTL-DEFINABILITY GATE (at cascade time). The holonomy decomposition
        # succeeds even when D's transition monoid is non-aperiodic — it just
        # produces a GROUP component the parser labels a reset, from which the
        # cascade members would build a WRONG formula (the kinská counting/ cases).
        # IsAperiodicSemigroup(T) is the sound oracle (LTL == star-free ==
        # counter-free == aperiodic): on a False reading, decline to build and
        # report the impossibility instead. This is the one choke point for ALL
        # cascade members (they each run only after this). The verdict is a proof
        # only when D was state-minimal (<= the SAT-min threshold); above it D may
        # be non-minimal so a spurious group is possible -> PROBABLY_NOT_LTL.
        if casc.aperiodic is False:
            n = casc.num_states
            conclusive = n <= _sat_min_threshold()
            note = (
                f"transition monoid of D ({n} states) is non-aperiodic "
                f"(carries a non-trivial group), so the language is not "
                f"star-free / counter-free and no LTL formula exists"
                + ("" if conclusive else
                   f"; D is above the SAT-min threshold ({_sat_min_threshold()}) "
                   f"so it may be non-minimal — treat as a strong hint, not a proof")
            )
            return LTLFormulaResult.not_ltl_definable(conclusive=conclusive, note=note)
        # The CascadeHolder carries this build's memos + counters (no module
        # globals, no reset); discarding it after the build IS the reset.
        holder = CascadeHolder(casc)
        return ct(holder)

    return reconstruct


reconstruct: Translator = as_translator(hierarchy_class)


__all__ = ["as_translator", "reconstruct"]
