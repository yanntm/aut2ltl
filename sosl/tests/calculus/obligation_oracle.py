"""CAL5 gate: the obligation read-offs against the `.cat` sidecars.

    python3 -m tests.calculus.obligation_oracle DIR [LIMIT] [SEED]

The corpus is its own oracle here — no Spot. The sidecars carry the Wagner
coordinates ``(m+, m-, n+, n-)`` computed by the classification engines, an
answer key the calculus never sees:

- `is_obligation` must be true exactly when ``max(m+, m-) <= 0`` — the language
  has no chain of length 1 (a ``-1`` coordinate means the polarity has no chain
  at all, the empty/universal convention, and still counts as obligation);
- on every obligation row, `obligation_degree` must equal the sidecar
  ``(n+, n-)``.

Before the sweep, the worked reference of the calculus paper (Prop 3.11 /
[CP97, Ex. 10]): the hand-built invariant of ``a*.b^omega`` is an obligation of
degree ``(n+, n-) = (1, 2)``.

``LIMIT`` caps the sweep to a random sample (default 0 = the whole directory).
Ends SUCCESS.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import List, Tuple

from sosl.sos import Alphabet, Invariant, load_invariant
from sosl.sos.calculus import Table, is_obligation, obligation_degree
from sosl.sos.classify.io import parse_cat


def astar_bomega() -> Invariant:
    """The syntactic invariant of ``a*.b^omega`` (letter ``a`` = mask 0, ``b`` =
    mask 1, one AP): five classes ``[eps]``, A = ``a+``, B = ``b+``, C = ``a+b+``
    and D = dead (an ``a`` after a ``b``, absorbing); the accepting pairs are
    ``(B, B)`` and ``(C, B)``. ``A.B = C`` is a class of its own: merging it into
    B would accept ``(ab)^omega``, which is not in the language.
    `tests.calculus.example_gate` counter-signs this table against Spot."""
    inv = Invariant(
        alphabet=Alphabet.of(["p"]),
        keys=((), (0,), (1,), (0, 1), (1, 0)),
        letter_class=(1, 2),
        mult=((0, 1, 2, 3, 4),
              (1, 1, 3, 3, 4),
              (2, 4, 2, 4, 4),
              (3, 4, 3, 4, 4),
              (4, 4, 4, 4, 4)),
        accept=frozenset({(2, 2), (3, 2)}),
        identity=0,
    )
    inv.validate()
    return inv


def check_reference() -> None:
    """Prop 3.11's worked case: ``a*.b^omega`` has theta-path A(0) > B(1) > D(0),
    so ``n+ = 1`` and ``n- = 2``."""
    inv = astar_bomega()
    table = Table.of(inv)
    assert is_obligation(table, inv.accept), "a*.b^omega is an obligation"
    degree = obligation_degree(table, inv.accept)
    assert degree == (1, 2), f"a*.b^omega: degree {degree} != (1, 2)"
    print("  reference a*.b^omega: obligation, degree (n+, n-) = (1, 2)")


def check_case(path: Path) -> Tuple[bool, bool]:
    """One corpus row: `(is obligation, sidecar had the coordinates)`."""
    coords = parse_cat(path.with_suffix(".cat").read_text())["coords"]
    m_plus, m_minus, n_plus, n_minus = coords
    inv = load_invariant(path.read_text())
    table = Table.of(inv)
    ours = is_obligation(table, inv.accept)
    expected = max(m_plus, m_minus) <= 0
    assert ours == expected, (
        f"{path.name}: is_obligation {ours}, but sidecar m = ({m_plus}, {m_minus})"
    )
    if ours:
        degree = obligation_degree(table, inv.accept)
        assert degree == (n_plus, n_minus), (
            f"{path.name}: obligation_degree {degree} != sidecar ({n_plus}, {n_minus})"
        )
    return ours, True


def main(argv: List[str]) -> int:
    directory = Path(argv[1])
    limit = int(argv[2]) if len(argv) > 2 else 0
    seed = int(argv[3]) if len(argv) > 3 else 0
    check_reference()

    paths = sorted(p for p in directory.glob("*.sos")
                   if p.with_suffix(".cat").exists())
    assert paths, f"no .sos with .cat sidecar under {directory}"
    if limit and limit < len(paths):
        paths = sorted(random.Random(seed).sample(paths, limit))
    obligations = 0
    for done, path in enumerate(paths, start=1):
        ob, _ = check_case(path)
        obligations += ob
        if done % 500 == 0:
            print(f"  ... {done}/{len(paths)}")
    print(f"{directory}: {len(paths)} rows checked, {obligations} obligations "
          f"(is_obligation == [max(m+, m-) <= 0] on all; degree == sidecar (n+, n-))")
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
