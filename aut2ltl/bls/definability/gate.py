"""
bls/definability/gate.py — the LTL-definability gate, as a Translator decorator.

The kr cascade is *unsound on a non-LTL language*: the holonomy decomposition still
succeeds, but emits a group component the parser reads as a reset, yielding a wrong
formula. So a non-definable Language must be intercepted *before* the cascade builds.
This module is that border — a decorator that wraps any Translator and gates it on
definability:

    safe = definability_gate(unsound_translator)

The gate has FOUR outcomes (see README.md; the screen's algebra is one-sided —
`tester/algorithm.md`, Soundness — and the suspect branch is decided exactly by
the syntactic-ω-semigroup oracle, `oracle/algorithm.md`):

  * **aperiodic reading** → delegate to `inner` (a proof of LTL; the cascade builds);
  * **group + oracle NOT_LTL** → the absorbing `NOT_LTL`, carrying the counting
    family the oracle replayed in-process against this Language's own automaton —
    a proof of non-LTL, independent of the algebra that produced it;
  * **group + oracle LTL** → a **non-absorbing decline stating the theorem**: the
    language is proven definable, but the cascade's unsoundness is *form*-based —
    the deterministic form still carries the group the holonomy parser misreads
    (`gf_aa_parity`-class) — so `inner` stays fenced and the Language's cached
    definability tag is NOT flipped; every other translator, each sound by
    construction, is free to answer (and now knows a formula exists);
  * **group + oracle INCONCLUSIVE** (a resource cap) → a **non-absorbing decline**
    carrying a `PROBABLY_NOT_LTL` diagnosis: no verdict is asserted; `inner` is
    never called. A wrong absorbing rejection is thereby impossible.

The screen failing to run at all (`definable=None`: extraction/GAP failure) takes
the same fence — a non-absorbing decline, `inner` never called — with its own
reason and no `PROBABLY_NOT_LTL` marker, since no group was read and no suspicion
exists. One behavior for everything the gate cannot certify: soundness holds by
construction, not by trusting that the cascade shares the oracle's failure mode.

With the knob off (`kr.produce_witness=0`) the oracle never runs, so a group
reading always takes the decline branch: disabling the decision disables absorbing
rejections (and proven-LTL declines), never soundness.

The suspect-branch decision is computed once per Language and cached, since the
gate wraps several portfolio rungs and a non-absorbing decline lets the walk
continue to the next gated arm.

LAYERING / dependencies. The gate orchestrates its leaves — none depends on another:

    gate ──► tester   (label_ltl_definable: definable, conclusive)
         ──► oracle   (decide: the exact verdict, witness replayed internally)
         ──► floor    (LTLResult, Translator)

It imports neither `Cascade` nor `aut2cas`; it wraps an arbitrary `Translator`, so it
composes around the cascade adapter without a cycle.
"""

from __future__ import annotations

import os
import weakref
from typing import TYPE_CHECKING

from aut2ltl.result import LTLResult
from aut2ltl.translator import Translator
from ..options import PRODUCE_WITNESS
from .oracle import decide, OracleVerdict, INCONCLUSIVE as ORACLE_INCONCLUSIVE, \
    LTL as ORACLE_LTL, NOT_LTL as ORACLE_NOT_LTL
from .tester import label_ltl_definable

if TYPE_CHECKING:
    from aut2ltl.language import Language


def _produce_witness() -> bool:
    """Whether to run the exact oracle on the suspect branch (knob
    `kr.produce_witness`, default on). Read at the call site via env, like the
    tester's SAT-min threshold."""
    raw = os.environ.get(PRODUCE_WITNESS.env)
    return PRODUCE_WITNESS.default if raw is None else raw != "0"


def _proven_ltl() -> str:
    """The diagnosis of a proven-definable decline: the theorem is stated, but the
    cascade stays fenced — its unsoundness is form-based, and the deterministic
    form still carries the group the holonomy parser misreads."""
    return (
        "LTL-definable (proven: the syntactic ω-semigroup is aperiodic), but the "
        "deterministic form carries a group the cascade would misread, so the "
        "cascade stays fenced; other translators may still answer"
    )


def _suspicion(reason: str) -> str:
    """The diagnosis of an uncertified suspicion — a decline, never a verdict. The
    `PROBABLY_NOT_LTL` marker is load-bearing: reporting layers key on it."""
    return (
        "PROBABLY_NOT_LTL -- the deterministic transition monoid carries a "
        f"non-trivial group but {reason}; the group may be an encoding artefact "
        "of the deterministic form, so no verdict is asserted (the cascade is "
        "fenced; other translators may still answer)"
    )


# The suspect-branch outcome, once per Language: the oracle's verdict.
_SUSPECT_CACHE: "weakref.WeakKeyDictionary[Language, OracleVerdict]" \
    = weakref.WeakKeyDictionary()


def _oracle_verdict(
    lang: "Language", *, gap_cmd: str, max_aps: int, em_cap: int
) -> OracleVerdict:
    """Run the exact oracle on a suspect `lang` (screen skipped — the tester just
    read the group) and cache the verdict per Language. Fail-safe on any error:
    INCONCLUSIVE, never a verdict; a NOT_LTL verdict always carries the family
    the oracle already replayed against this Language's own automaton."""
    try:
        return _SUSPECT_CACHE[lang]
    except KeyError:
        pass

    try:
        verdict = decide(lang, gap_cmd=gap_cmd, max_aps=max_aps, em_cap=em_cap,
                         screen=False)
    except Exception as exc:
        verdict = OracleVerdict(ORACLE_INCONCLUSIVE, f"the oracle raised: {exc}")

    _SUSPECT_CACHE[lang] = verdict
    return verdict


def definability_gate(
    inner: Translator,
    *,
    gap_cmd: str = "gap",
    timeout: int = 180,
    max_aps: int = 5,
    em_cap: int = 20000,
) -> Translator:
    """Wrap `inner` with the LTL-definability gate: delegate on an aperiodic reading,
    decide the suspect branch exactly with the oracle — the absorbing `NOT_LTL` on a
    replayed family, a theorem-stating decline on a proven-LTL answer (`inner` stays
    fenced: the form still carries the group), and a `PROBABLY_NOT_LTL` decline on a
    resource cap.

    The algebraic screen is cached on the Language (its tag is never written by the
    oracle) and the suspect-branch verdict in a per-Language cache, so this is a
    single choke point for all wrapped rungs."""

    def gated(lang: "Language") -> LTLResult:
        definable, _conclusive = label_ltl_definable(
            lang, gap_cmd=gap_cmd, timeout=timeout, max_aps=max_aps
        )
        if definable:
            return inner(lang)
        if definable is None:
            # The screen could not run: nothing was read in either direction, so
            # the gate cannot vouch for the cascade — same fence as an undecided
            # suspicion, but no suspicion is asserted (no group was read).
            return LTLResult.decline(
                "the definability screen could not run (extraction or GAP "
                "failure), so definability is uncertified and the cascade is "
                "fenced; other translators may still answer", "gate",
            )
        if not _produce_witness():
            return LTLResult.decline(
                _suspicion("the exact decision is disabled (kr.produce_witness=0)"),
                "gate")
        verdict = _oracle_verdict(lang, gap_cmd=gap_cmd, max_aps=max_aps,
                                  em_cap=em_cap)
        if verdict.answer == ORACLE_NOT_LTL:
            return LTLResult.not_definable(verdict.reason, "gate",
                                           witness=verdict.witness)
        if verdict.answer == ORACLE_LTL:
            return LTLResult.decline(_proven_ltl(), "gate")
        return LTLResult.decline(_suspicion(verdict.reason), "gate")

    return gated


__all__ = ["definability_gate"]
