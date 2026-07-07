"""A membership oracle for counting families, over any Spot acceptor.

A counting `Family` is a *portable* non-LTL certificate: it is validated by
membership queries alone — `toggles(family, member)` asks `2·p+1` lasso
memberships and checks the declared toggle. This module supplies one such
`member: Lasso → bool`, backed by Spot membership against whatever automaton
the client holds: `spot.parse_word` intersects the one-lasso automaton of the
word with the acceptor, so the check is acceptance-agnostic (Büchi, parity,
Rabin, generic Emerson–Lei) and references no internal state — the point
being that membership is language-invariant while state indices are not.

The verifier side thus never touches the algebra: it needs only *an* acceptor
of the language and the alphabet to render `sosl.sos` letters into Spot's
word syntax. Spot is imported lazily so the pure `witness/` core stays
Spot-free (repo discipline: Spot is bounded-or-skipped).
"""
from __future__ import annotations

from typing import Callable

from sosl.sos import Alphabet, Lasso, Word


def render_letter(alphabet: Alphabet, a: int) -> str:
    """A single letter as a Spot cube: every proposition pinned, `p` when true
    in `a` and `!p` when false (`"t"` for a propositionless alphabet)."""
    trues = set(alphabet.true_aps(a))
    return " & ".join(p if p in trues else "!" + p
                      for p in alphabet.aps) or "t"


def render_lasso(alphabet: Alphabet, lasso: Lasso) -> str:
    """The lasso `stem · loop^ω` in Spot's ultimately-periodic word syntax,
    `l; …; cycle{l; …}` (the loop is non-empty by the `Lasso` invariant)."""
    def letters(w: Word) -> list:
        return [render_letter(alphabet, a) for a in w]
    body = "cycle{" + "; ".join(letters(lasso.loop)) + "}"
    return "; ".join(letters(lasso.stem) + [body])


def spot_membership(aut: "object", alphabet: Alphabet) -> Callable[[Lasso], bool]:
    """A `Lasso → bool` membership oracle deciding `word ∈ L(aut)` by Spot
    lasso-intersection — presentation-agnostic, one loaded acceptor `aut`."""
    from aut2ltl.verifier.check import member  # local: pulls spot
    return lambda lasso: member(aut, render_lasso(alphabet, lasso))


def oracle_for_hoa(hoa_path: str, alphabet: Alphabet) -> Callable[[Lasso], bool]:
    """A membership oracle over the automaton parsed from `hoa_path`. The HOA's
    propositions must be the `alphabet`'s (the rendered cubes name them)."""
    import spot  # local: bounded-or-skipped per repo discipline
    aut = spot.automaton(hoa_path)
    return spot_membership(aut, alphabet)


__all__ = ["render_letter", "render_lasso", "spot_membership", "oracle_for_hoa"]
