"""
aut2ltl/contract.py — the contract floor: the portfolio result struct.

kr has become a PORTFOLIO: a given automaton is reconstructed by whichever
method wins at each node of the decompose-and-recombine dispatch — the
buchi2ltl gate, an AND/OR strength/acceptance split, or one of the leaf
acceptance-dispatch forms (acc / weak / buchi / cobuchi / the Muller-DNF
cascade `bls`). The bare `spot.formula` return hid which method fired, so the
top-level entry now returns this struct, carrying the formula plus the SET of
methods that contributed.

`.technique` is a set (deduped) accumulated down the dispatch tree:
  * 'and<n>' / 'or<n>'           — a boolean split into n pieces occurred at some
                                   node (n = number of conjuncts / disjuncts);
                                   subsumes the old `split_report` side channel;
  * 'sl' / 't2' / 'f2'           — the buchi2ltl gate produced a node (its own
                                   technique tokens, split on '+');
  * 'acc' / 'weak' / 'buchi' /
    'cobuchi' / 'bls'            — the leaf acceptance-dispatch method
                                   (`bls` = the general Muller-DNF cascade);
  * 'base'                       — a custom (non-default) reconstruct callable
                                   produced a leaf (probes/tests).

MT-safe by construction: the accumulator is a per-call local threaded by
reference through the dispatch, never a module-level/global recorder.

This module is the contract FLOOR both engines depend on: the data signature
`LTLFormulaResult` and the behavioral signatures `Translator` (automaton in) and
`CascadeTranslator` (decomposed cascade in). The key reification is an explicit
`status` (OK / DECLINED / NOT_LTL / PROBABLY_NOT_LTL) — "not me" is no longer
smuggled as the `UNSUPPORTED` string inside `.formula`. NOT_LTL / PROBABLY_NOT_LTL
are the impossibility verdicts (the language is (probably) not LTL-definable),
distinct from DECLINED ("not my method"): a consumer keeps trying on DECLINED but
stops on the NOT_LTL family (`.not_ltl`; `.conclusive` for strength). `status` plus
the dataclass being the single extension point (add a `cost`/size field when a
pick-smaller combinator needs an ordering) is what lets the combinators compose
soundly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol, Set, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from aut2ltl.language import Language

# status values
OK = "OK"
DECLINED = "DECLINED"
# Two POSITIVE non-answers, distinct from DECLINED: the input language is not
# LTL-definable (its deterministic transition monoid is non-aperiodic — it carries
# a non-trivial group — so the language is not star-free / counter-free and no LTL
# formula exists). DECLINED means "not my method, try another"; these mean "no
# method can succeed, stop". The verdict is rigorous only when D is state-minimal:
# on a non-minimal D a spurious group can appear, so the two are split by D's size
# against the SAT-min threshold —
#   NOT_LTL           — D was state-minimal: a PROOF of non-definability.
#   PROBABLY_NOT_LTL  — D was above the SAT-min threshold (not minimized): a strong
#                       hint, not a proof (the group may be a non-minimality
#                       artifact). Reported honestly as tentative.
# `.not_ltl` is True for both (both are impossibility verdicts, no usable formula);
# branch on `status` / `.conclusive` when the distinction matters.
NOT_LTL = "NOT_LTL"
PROBABLY_NOT_LTL = "PROBABLY_NOT_LTL"

# Legacy decline sentinel. The engines (buchi2ltl, sl) still use this string
# INTERNALLY to propagate "this state has no exact label" through their
# backward-labeling recursion; that is an engine detail, not the contract. At
# the contract boundary, decline is `status == DECLINED`. Recognized here only
# transitionally, so a consumer can switch to `.declined` before every producer
# sets `status` explicitly. TODO (P-ARCH): drop once all producers are migrated.
_LEGACY_UNSUPPORTED = "UNSUPPORTED"


@dataclass
class LTLFormulaResult:
    """A reconstructed formula DAG, the set of methods that built it, and an
    explicit status. On DECLINE `.formula` is None and `.status` is DECLINED
    (use `LTLFormulaResult.decline(...)`); never a sentinel string in `.formula`."""
    formula: Optional["spot.formula"]
    technique: Set[str] = field(default_factory=set)
    status: str = OK
    # Human-facing detail. For the NOT_LTL verdicts it explains the reason (the
    # non-aperiodic monoid) and whether D was state-minimal.
    note: Optional[str] = None

    @property
    def declined(self) -> bool:
        """True iff this is a "not me" result. Consumers branch on this. NOT_LTL
        is NOT a decline — it is a positive impossibility verdict (see `.not_ltl`)."""
        if self.status == DECLINED:
            return True
        # Transitional: some producers still smuggle the UNSUPPORTED string in
        # `.formula` instead of setting status. See `_LEGACY_UNSUPPORTED`.
        return isinstance(self.formula, str) and _LEGACY_UNSUPPORTED in self.formula

    @property
    def not_ltl(self) -> bool:
        """True iff this is a non-definability verdict (NOT_LTL or PROBABLY_NOT_LTL):
        the language is (probably) not LTL-definable, so no technique can produce a
        faithful formula. Consumers short-circuit; use `.conclusive` for strength."""
        return self.status in (NOT_LTL, PROBABLY_NOT_LTL)

    @property
    def conclusive(self) -> bool:
        """For a NOT_LTL-family verdict: True iff rigorous (status NOT_LTL, D was
        state-minimal), False iff tentative (PROBABLY_NOT_LTL). False otherwise."""
        return self.status == NOT_LTL

    @property
    def ok(self) -> bool:
        """True iff this carries a real (language-faithful) formula. DECLINED and
        both NOT_LTL verdicts are non-answers (no usable formula)."""
        return self.status == OK and not self.declined

    @classmethod
    def decline(cls, technique: Optional[Set[str]] = None) -> "LTLFormulaResult":
        """The "not me" result: no formula, DECLINED status."""
        return cls(formula=None, technique=technique or set(), status=DECLINED)

    @classmethod
    def not_ltl_definable(
        cls,
        *,
        conclusive: bool = True,
        note: Optional[str] = None,
        technique: Optional[Set[str]] = None,
    ) -> "LTLFormulaResult":
        """The non-definability verdict: the language is (probably) not LTL-definable
        (no formula exists). `conclusive=True` (D state-minimal) yields NOT_LTL — a
        proof; `conclusive=False` (D above the SAT-min threshold) yields
        PROBABLY_NOT_LTL — a strong hint. `note` carries the explanation."""
        return cls(formula=None, technique=technique or set(),
                   status=NOT_LTL if conclusive else PROBABLY_NOT_LTL, note=note)

    def technique_str(self) -> str:
        """Stable '+'-joined rendering (sorted) for logs/surveys."""
        return "+".join(sorted(self.technique)) if self.technique else "-"


@runtime_checkable
class Translator(Protocol):
    """The behavioral contract: translate a `Language` to LTL.

    A Translator is a callable `Language -> LTLFormulaResult`. The input is a
    `Language` (the floor handle over language-equivalent automaton
    representations — `aut2ltl.language`), not a raw automaton: each translator
    pulls the representation it wants (`tgba` / `det_parity_sbacc` / `det_generic`
    / `det_generic_minimal`). The kr endpoint `aut2cas.reconstruct` realizes this;
    the portfolio combinators (Gate / Decompose / SlDriven / Portfolio) are
    themselves Translators over Translators (their migration to a `Language` input
    is the Phase-2 portfolio pass — until then `reconstruct_decomposed` still
    takes a raw automaton).

    Contract invariant (NOT type-checkable, the load-bearing rule): the returned
    LTLFormulaResult is either language-faithful (`status` OK, `.formula` ≡ L(lang))
    or DECLINED — NEVER a wrong formula. That single rule is what makes composition
    sound.
    """

    def __call__(self, lang: "Language") -> "LTLFormulaResult": ...


@runtime_checkable
class CascadeTranslator(Protocol):
    """The cascade-level peer of `Translator`: translate a Krohn-Rhodes Cascade
    to LTL.

    Same `LTLFormulaResult` and the same load-bearing invariant — the result is
    language-faithful (OK) or DECLINED, never wrong — but the input is an already
    decomposed cascade (a `CascadeHolder` wrapping it) instead of a raw automaton.

    Realized as an OO family: each construction is a *member* — a small class
    (singleton instance) with a fixed `name` (its technique identity, e.g.
    'acc' / 'buchi' / 'cobuchi' / 'weak' / 'bls') and a `__call__` that is
    self-gating (it inspects the cascade and either builds its faithful form or
    DECLINES). The member stamps its own `name` into the LTLFormulaResult's technique,
    so composites (`first_success`) need no out-of-band tagging. `decompose_aut`
    is the adapter that lifts a member up to a `Translator` (twa -> Cascade ->
    result).

    The `CascadeHolder` annotation is a bare forward-ref string (like
    `Translator`'s `spot.twa_graph`) so this floor module stays import-free of the
    engines. The holder wraps the pure `Cascade` with that build's caches/counters
    (kr/cascade/holder.py); members read cascade attributes off it transparently.
    """

    name: str

    def __call__(self, casc: "CascadeHolder") -> "LTLFormulaResult": ...
