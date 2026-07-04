"""
bls/gate/gate.py — gate a translator on the LTL-definability screen.

The kr cascade is unsound on a language that is not counter-free: its holonomy
decomposition emits a group component the parser misreads, yielding a wrong
formula. `cascade_gate` fronts such a translator and admits it only behind a
proved-aperiodic reading of the deterministic transition monoid:

    safe = cascade_gate(inner)

Two outcomes:

  * the screen proves the transition monoid aperiodic — the language is
    star-free, an LTL formula exists — so `inner` builds: delegate, returning
    its result unchanged;
  * otherwise (a group is read, or the screen cannot run) — a non-absorbing
    decline carrying a PROBABLY_NOT_LTL diagnosis: `inner` is never called, no
    verdict is asserted, and every other translator remains free to answer.

A group may be an artefact of the deterministic encoding, so a non-aperiodic
reading is a suspicion, never a verdict — the gate declines, it does not reject.
The screen is computed once per Language and cached on it, so a gate wrapping
several rungs runs it once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from aut2ltl.result import LTLResult
from aut2ltl.translator import Translator
from .aperiodic import label_ltl_definable

if TYPE_CHECKING:
    from aut2ltl.language import Language


_DECLINE = (
    "PROBABLY_NOT_LTL -- the LTL-definability screen did not prove the language "
    "star-free (the deterministic transition monoid carries a non-trivial group, "
    "possibly an encoding artefact, or the screen could not run); definability is "
    "uncertified, so the cascade is fenced and other translators may still answer"
)


def cascade_gate(
    inner: Translator,
    *,
    gap_cmd: str = "gap",
    timeout: int = 180,
    max_aps: int = 5,
) -> Translator:
    """Wrap `inner`, delegating only behind a proved-aperiodic screen.

    On each Language the transition-monoid aperiodicity screen runs (cached on
    the Language). An aperiodic reading proves star-freeness and `inner` is
    called, its result returned unchanged. Any other reading — a group, or the
    screen unable to run — yields a non-absorbing PROBABLY_NOT_LTL decline;
    `inner` is never called."""

    def gated(lang: "Language") -> LTLResult:
        definable, _conclusive = label_ltl_definable(
            lang, gap_cmd=gap_cmd, timeout=timeout, max_aps=max_aps
        )
        if definable:
            return inner(lang)
        return LTLResult.decline(_DECLINE, "gate")

    return gated


__all__ = ["cascade_gate"]
