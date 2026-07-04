"""Test whether a deterministic automaton's TRANSITION monoid is aperiodic.

Independent of the cascade and the definability oracle: it closes the monoid of
letter transformations on the state set and checks aperiodicity directly (a monoid
is aperiodic iff every element x satisfies x^n = x^(n+1) for some n -- no element
generates a nontrivial cyclic group). For a star-free LANGUAGE the syntactic
monoid is aperiodic, but a minimal ω-automaton's transition monoid need not be;
a non-aperiodic transition monoid on a minimal star-free form is exactly the
object the Π₂ hunt is after (it forces a group into the holonomy cascade).

Usage:  python3 tests/pi2_hunt/monoid_check.py <file.hoa>
Prints the monoid size, aperiodicity verdict, and a period>1 witness word if any.
Exit 0 if aperiodic, 1 if a group element is found, 2 on error.
"""
from __future__ import annotations

import sys
from typing import Dict, List, Tuple

import spot

from aut2ltl.bls.generators import extract_generators


Transf = Tuple[int, ...]


def _compose(f: Transf, g: Transf) -> Transf:
    """(f then g): apply f, then g."""
    return tuple(g[f[s]] for s in range(len(f)))


def _period(t: Transf) -> int:
    """The period of the cyclic part of <t>: powers t^1,t^2,... eventually cycle
    with some length; return that cycle length (1 == aperiodic element)."""
    seen: Dict[Transf, int] = {}
    p = t
    i = 1
    while p not in seen:
        seen[p] = i
        p = _compose(p, t)
        i += 1
    return i - seen[p]  # length of the tail-to-repeat cycle


def analyze(aut: "spot.twa_graph") -> Tuple[int, int, int, str, Transf]:
    """Close the transition monoid and return
    (n_states, monoid_size, max_period, witness_word, witness_image).
    max_period == 1 means the monoid is aperiodic; >1 means it carries a group.
    Raises OverflowError if the monoid exceeds 20000 elements."""
    if not spot.is_complete(aut):
        aut = spot.complete(aut)
    n = aut.num_states()
    gens, _masks, valuations = extract_generators(aut, max_aps=5)
    letters: List[Transf] = [tuple(g) for g in gens]
    names = {i: "".join(("" if v else "!") + k for k, v in sorted(valuations[i].items()))
             for i in range(len(letters))}
    ident: Transf = tuple(range(n))
    monoid: Dict[Transf, str] = {ident: "1"}
    frontier: List[Transf] = [ident]
    while frontier:
        nxt: List[Transf] = []
        for t in frontier:
            for i, l in enumerate(letters):
                u = _compose(t, l)
                if u not in monoid:
                    monoid[u] = (monoid[t] + "." if monoid[t] != "1" else "") + f"[{names[i]}]"
                    nxt.append(u)
        frontier = nxt
        if len(monoid) > 20000:
            raise OverflowError("monoid > 20000")
    period, witness = max((_period(t), w) for t, w in monoid.items())
    image = next(t for t, w in monoid.items() if w == witness)
    return n, len(monoid), period, witness, image


def main(path: str) -> int:
    n, size, period, witness, image = analyze(spot.automaton(path))
    print(f"{path}: states={n} monoid_size={size} aperiodic={period == 1}")
    if period > 1:
        print(f"  GROUP element: word={witness}  period={period}  image={image}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
