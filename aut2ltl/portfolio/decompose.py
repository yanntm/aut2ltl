"""
portfolio/decompose.py — the `Decompose` Translator (Composite + Decorator).

`Decompose(leaf: Translator)` IS a Translator: given a `Language` it splits the
language (AND by acceptance conjunct / OR by strength) and recombines the parts
with a root boolean operator, recursing on ITSELF so nested splits fall out; when
the language does not split it delegates the whole to `leaf`. No special cases —
each Translator pulls the representation it wants from the `Language` it is
handed; `Decompose` only splits (on the determinized form), recombines, and
delegates.

Soundness (kr/sl are language-faithful; a ROOT boolean op is a pure position-0
language op — no temporal-placement / acceptance-coupling caveats):

  * AND by acceptance set.  On a DETERMINISTIC automaton every word has one run,
    so for conjunctive acceptance  acc = ⋀ᵢ cᵢ:
        L(A) = ⋂ᵢ L(A | acc:=cᵢ)        (shared run -> exact)
    Determinism is REQUIRED here (on a nondeterministic automaton ⋂L(Aᵢ) ⊋ L(A)).

  * OR by strength.  Spot's strength decomposition splits an automaton into
    weak / terminal / strong sub-automata whose UNION is the language
    (Renault et al., TACAS'13; exact for any automaton):
        L(A) = ⋃ₖ L(decompose_scc(A,k))

The split form is `Language.det_generic_minimal()` — deterministic (the AND-split
precondition), generic (keeps the generalized-Büchi ⋀Inf / Streett conjunctive
shape instead of collapsing to parity), state-minimal (kr's census is acutely
state-count sensitive). `recombine` declines if any part declines — the split is
sound only if every part reconstructs.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import spot

from aut2ltl.contract import LTLFormulaResult, Translator
from aut2ltl.language import Language


def _and_pieces(aut: "spot.twa_graph") -> List["spot.twa_graph"]:
    """One single-condition sub-automaton per top-level acceptance conjunct.
    Empty/singleton list means 'not a conjunction' (no AND split)."""
    conj = aut.acc().get_acceptance().top_conjuncts()
    if len(conj) < 2:
        return []
    pieces = []
    for c in conj:
        sub = spot.automaton(aut.to_str("hoa"))  # independent clone
        sub.set_acceptance(spot.acc_cond(aut.num_sets(), c))
        spot.cleanup_acceptance_here(sub)
        pieces.append(sub)
    return pieces


def _or_pieces(aut: "spot.twa_graph") -> List["spot.twa_graph"]:
    """Strength decomposition: weak / terminal / strong sub-automata whose union
    is the language. Returns [] when the automaton is single-strength (the
    decomposition would just return the whole automaton)."""
    si = spot.scc_info(aut)
    pieces = []
    for keep in ("w", "t", "s"):
        try:
            sub = spot.decompose_scc(si, keep)
        except Exception:
            sub = None
        if sub is not None and sub.num_states() > 0:
            pieces.append(sub)
    # A genuine split needs at least two strengths present.
    return pieces if len(pieces) >= 2 else []


def _split(aut: "spot.twa_graph") -> Tuple[Optional[str], List["spot.twa_graph"]]:
    """How the root splits this (deterministic) automaton: ('and'|'or', pieces),
    or (None, []) when it is atomic. Conjunctive first, else multi-strength."""
    and_p = _and_pieces(aut)
    if and_p:
        return ("and", and_p)
    or_p = _or_pieces(aut)
    if or_p:
        return ("or", or_p)
    return (None, [])


def _recombine(op: str, subs: List[LTLFormulaResult]) -> LTLFormulaResult:
    """Recombine sub-results with the root ⋀/⋁. Propagates a NOT_LTL part upward
    (a part that is (probably) not LTL-definable cannot be built, and no later
    recombination recovers it); declines if any part declines; else And/Or of the
    part formulas, technique = ⋃ parts ∪ {op<n>}."""
    # Checked before the decline test: a NOT_LTL part also has formula None, and a
    # non-definable part is a stronger fact than a plain decline. Prefer a
    # conclusive verdict if several parts report one.
    not_ltls = [s for s in subs if s.not_ltl]
    if not_ltls:
        return next((s for s in not_ltls if s.conclusive), not_ltls[0])
    if any(s.declined or s.formula is None for s in subs):
        return LTLFormulaResult.decline()
    forms = [s.formula for s in subs]
    tech = set()
    for s in subs:
        tech |= s.technique
    tech.add(f"{op}{len(subs)}")
    f = spot.formula.And(forms) if op == "and" else spot.formula.Or(forms)
    return LTLFormulaResult(formula=f, technique=tech)


class Decompose:
    """The decompose-and-recombine Composite as a Translator over a leaf
    Translator. Splits unconditionally when it can (recursing on itself), else
    delegates the whole `Language` to `leaf`. Transparent on technique: it adds
    `and<n>`/`or<n>` and forwards the parts' techniques."""

    name = "decompose"

    def __init__(self, leaf: Translator) -> None:
        self._leaf = leaf

    def __call__(self, lang: Language) -> LTLFormulaResult:
        op, pieces = _split(lang.det_generic_minimal())
        if pieces:
            return _recombine(op, [self(Language.of(p)) for p in pieces])
        return self._leaf(lang)


def split_report(lang: Language) -> Tuple[str, int]:
    """Diagnose how the root would split this language (no reconstruction).
    Returns (kind, n_pieces): kind in {'and','or','none'}."""
    op, pieces = _split(lang.det_generic_minimal())
    return (op, len(pieces)) if op else ("none", 1)


__all__ = ["Decompose", "split_report", "_split"]
