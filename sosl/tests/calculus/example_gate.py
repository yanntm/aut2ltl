"""E-CAL-EX: the machine counter-signature of the paper's running example.

    python3 -m tests.calculus.example_gate

The paper hand-computes, over the one-AP alphabet ``a = !p``, ``b = p``:

* ``I(a*.b^w)`` — five classes, its table, its linked pairs, its accepting set;
* the stutter read-off, the two rootings, the hulls, the obligation degree;
* ``I(GF a)`` — three classes;
* the alignment of the two, and the four verdicts read off it.

Every value is checked against a construction the calculus never sees: both
invariants come from `sos.build.reference_of_ltl` (Spot determinizes, the
quotient canonicalizes), the Wagner coordinates come from `sos.classify`, and
the predicted multiplication table is generated from the word model
``{eps, a+, b+, a+b+, dead}`` rather than transcribed.

Nine checks, one shot, no argv; ends SUCCESS.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

from sosl.sos import Invariant, Lasso
from sosl.sos.build import reference_of_ltl
from sosl.sos.calculus import (
    PairSet,
    Table,
    Witness,
    align,
    complement,
    included,
    interior,
    intersecting_word,
    intersection,
    is_obligation,
    live,
    liveness_part,
    member,
    obligation_degree,
    rooting,
    safety_closure,
)
from sosl.sos.classify import classify, is_stutter_invariant
from sosl.sos.classify.io import parse_cat
from sosl.sos.io import dump_invariant
from sosl.sos.io.serialize import render_word
from sosl.sos.minimize import remove_free_aps
from sosl.sos.relabel import canonical_relabeling

# The example, in the paper's own encoding: one AP ``p``, letter ``a`` = ``!p``
# (mask 0), letter ``b`` = ``p`` (mask 1).
L_ASTAR_BOMEGA = "(!p) U (G p)"      # a*.b^w
L_GF_A = "G F !p"                    # GF a
A_MASK, B_MASK = 0, 1

L_ASTAR_BOMEGA_CORPUS = "(!a) U (G a)"
"""The same language over the corpus's AP name: the canonical `.sos` bytes carry
the AP's *name*, so a `flat_canon` lookup must be keyed in the corpus's naming."""

CORPUS = Path(__file__).resolve().parents[3] / "genaut/corpus/flat_canon/sos"

Roles = Dict[str, int]
"""The five classes of ``I(a*.b^w)`` by their role, not by their key string."""


# --- the word model: theory's prediction, generated rather than transcribed --

def role_of(word: str) -> str:
    """The class of ``word`` in the syntactic monoid of ``a*.b^w``, read off the
    word model: the empty word is the identity, any word containing ``ba`` is
    dead, and the rest are ``a+`` / ``b+`` / ``a+b+``."""
    if not word:
        return "eps"
    if "ba" in word:
        return "D"
    if "b" not in word:
        return "A"
    if "a" not in word:
        return "B"
    return "C"


REPS = {"eps": "", "A": "a", "B": "b", "C": "ab", "D": "ba"}
"""One representative word per role — the shortest of its class."""


def roles_of(inv: Invariant) -> Roles:
    """Locate the five roles inside ``inv``'s numbering: the identity, the two
    letter classes, and the products that name ``C`` and ``D``."""
    mult = inv.mult
    a, b = inv.letter_class[A_MASK], inv.letter_class[B_MASK]
    return {
        "eps": inv.identity,
        "A": a,
        "B": b,
        "C": mult[a][b],
        "D": mult[b][a],
    }


# --- 1. the invariant of a*.b^w ---------------------------------------------

def check_algebra(inv: Invariant, roles: Roles) -> None:
    """Check 1: five classes, the multiplication table of the word model, the
    six linked pairs, and ``P = {(B,B), (C,B)}``."""
    assert len(inv.keys) == 5, f"I(a*.b^w): {len(inv.keys)} classes, expected 5"
    assert len(set(roles.values())) == 5, f"roles collide: {roles}"

    for x, cx in roles.items():
        for y, cy in roles.items():
            want = roles[role_of(REPS[x] + REPS[y])]
            got = inv.mult[cx][cy]
            assert got == want, (
                f"table: {x}.{y} = class {got} (key {inv.keys[got]}), "
                f"word model says {role_of(REPS[x] + REPS[y])}")

    table = Table.of(inv)
    want_linked = frozenset({
        (roles["A"], roles["A"]), (roles["D"], roles["A"]),
        (roles["B"], roles["B"]), (roles["C"], roles["B"]),
        (roles["D"], roles["B"]), (roles["D"], roles["D"]),
    })
    assert table.linked == want_linked, (
        f"linked pairs {sorted(table.linked)} != {sorted(want_linked)}")

    want_accept = frozenset({(roles["B"], roles["B"]), (roles["C"], roles["B"])})
    assert inv.accept == want_accept, f"P = {sorted(inv.accept)}, expected (B,B),(C,B)"
    print("  1. algebra: 5 classes, table = word model, 6 linked pairs, "
          "P = {(B,B), (C,B)}")


# --- 2. the stutter read-off -------------------------------------------------

def check_stutter(inv: Invariant, roles: Roles) -> None:
    """Check 2: both letter classes are idempotent, so the read-off is true."""
    for name in ("A", "B"):
        c = roles[name]
        assert inv.mult[c][c] == c, f"letter class {name} is not idempotent"
    assert is_stutter_invariant(inv), "stutter read-off false on a*.b^w"
    print("  2. stutter: A and B idempotent, read-off true")


# --- 3. the rootings ---------------------------------------------------------

def check_rootings(table: Table, p: PairSet, roles: Roles) -> None:
    """Check 3: ``a^-1 L = L`` and ``b^-1 L = {b^w}``."""
    by_a = rooting(table, p, roles["A"])
    assert by_a == p, f"P_A = {sorted(by_a)}, expected P"
    by_b = rooting(table, p, roles["B"])
    want = frozenset({(roles["B"], roles["B"])})
    assert by_b == want, f"P_B = {sorted(by_b)}, expected {{(B,B)}} (= b^w)"
    print("  3. rootings: P_A = P, P_B = {(B,B)} = {b^w}")


# --- 4. the hulls ------------------------------------------------------------

def check_hulls(table: Table, p: PairSet, roles: Roles) -> None:
    """Check 4: ``Live = C \\ {D}``, the safety closure adds exactly ``(A,A)``,
    the interior is empty, and the Alpern-Schneider liveness factor is
    ``P + {(D,A), (D,B), (D,D)}``."""
    want_live = frozenset(c for c in range(table.n) if c != roles["D"])
    got_live = live(table, p)
    assert got_live == want_live, f"Live = {sorted(got_live)}, expected all but D"

    hull = safety_closure(table, p)
    assert hull == p | {(roles["A"], roles["A"])}, (
        f"safety_closure adds {sorted(hull - p)}, expected exactly (A,A)")

    inner = interior(table, p)
    assert inner == frozenset(), f"interior = {sorted(inner)}, expected empty"

    live_part = liveness_part(table, p)
    want_lp = p | {(roles["D"], roles["A"]), (roles["D"], roles["B"]),
                   (roles["D"], roles["D"])}
    assert live_part == want_lp, (
        f"liveness_part = {sorted(live_part)}, expected P + the D-pairs")
    assert intersection(table, hull, live_part) == p, "A-S decomposition broken"
    print("  4. hulls: Live = C \\ {D}, closure adds (A,A), interior empty, "
          "liveness = P + {(D,A), (D,B), (D,D)}")


# --- 5. the obligation degree ------------------------------------------------

def corpus_row(inv: Invariant) -> Optional[Path]:
    """The `flat_canon` file holding ``inv``'s language, or ``None``. The
    catalogue keeps one file per language **up to renaming its symbols**, stored
    as the ``B_k`` orbit-min of its invariant (genaut's `canon_key`:
    `remove_free_aps` -> orbit representative -> dump). Those bytes *are* the
    file, so the lookup is a text match against the key — mind the AP name, it is
    part of the canonical bytes."""
    if not CORPUS.is_dir():
        return None
    key = dump_invariant(canonical_relabeling(remove_free_aps(inv))[1])
    for path in sorted(CORPUS.glob("*.sos")):
        if path.read_text() == key:
            return path
    return None


def check_obligation(table: Table, inv: Invariant, p: PairSet) -> None:
    """Check 5: an obligation of degree ``(1, 2)``, cross-checked twice — against
    the Wagner coordinates `sos.classify` derives from the invariant, and against
    the `.cat` sidecar of the corpus row holding this language (obligation iff
    ``max(m+, m-) <= 0``; the degree is then ``(n+, n-)``)."""
    assert is_obligation(table, p), "a*.b^w is not an obligation"
    degree = obligation_degree(table, p)
    assert degree == (1, 2), f"obligation_degree = {degree}, expected (1, 2)"

    rec = classify(inv)
    coords = (rec.m_plus, rec.m_minus, rec.n_plus, rec.n_minus)
    assert max(rec.m_plus, rec.m_minus) <= 0, f"classify coords {coords}: not an obligation"
    assert (rec.n_plus, rec.n_minus) == degree, (
        f"classify coords {coords} disagree with degree {degree}")
    print(f"  5. obligation: degree (n+, n-) = (1, 2); classify coords "
          f"(m+ m- n+ n-) = {coords} agree")

    # The same language over the corpus's own AP name, so the canonical bytes match.
    row = corpus_row(reference_of_ltl(L_ASTAR_BOMEGA_CORPUS))
    if row is None:
        print("     (corpus row: none found -- .cat cross-check SKIPPED)")
        return
    cat = parse_cat((row.parent / (row.stem + ".cat")).read_text())
    assert cat["coords"] == coords, f"{row.name}: .cat coords {cat['coords']} != {coords}"
    print(f"     corpus row {row.name}: .cat coords {cat['coords']} agree "
          f"(the answer key the calculus never sees)")


# --- 6. the invariant of GF a ------------------------------------------------

def check_gfa(inv2: Invariant) -> Tuple[Table, PairSet, int]:
    """Check 6: three classes (identity counted in), and ``P2 = {(alpha, alpha)}``
    where ``alpha`` is the class of the words containing an ``a`` — every cell
    whose loop class is ``alpha`` accepts, and no other."""
    assert len(inv2.keys) == 3, f"I(GF a): {len(inv2.keys)} classes, expected 3"
    alpha = inv2.letter_class[A_MASK]
    assert inv2.accept == frozenset({(alpha, alpha)}), (
        f"P2 = {sorted(inv2.accept)}, expected {{(alpha, alpha)}}")
    table2 = Table.of(inv2)
    for c, d in table2.cells():
        assert table2.val(inv2.accept, c, d) == (d == alpha), (
            f"cell ({c},{d}): verdict disagrees with 'the loop contains an a'")
    print("  6. I(GF a): 3 classes, P2 = {(alpha, alpha)}, every a-loop cell accepts")
    return table2, inv2.accept, alpha


# --- 7. the alignment and its four verdicts ----------------------------------

def show(w: Witness) -> str:
    """The witness as ``stem . loop^w``, in the alphabet's own letters."""
    return f"{render_word(w.alphabet, w.stem)} . ({render_word(w.alphabet, w.loop)})^w"


def check_align(table: Table, p: PairSet, table2: Table, p2: PairSet) -> None:
    """Check 7: 5 nodes out of 5 x 3, empty intersection, ``a*.b^w <= FG !a``,
    and the reverse inclusion refuted by ``ba.b^w``."""
    aligned = align(table.language(p), table2.language(p2))
    assert aligned.n == 5, f"align: {aligned.n} nodes, expected 5"
    assert (aligned.size_a, aligned.size_b) == (5, 3), "align: side sizes moved"
    print(f"  7. align: {aligned.n} nodes of 5 x 3, ratio {aligned.ratio:.4f} (= 5/15)")

    shared, w_shared = intersecting_word(aligned)
    assert not shared and w_shared is None, (
        f"a*.b^w and GF a share a word: {show(w_shared)}" if w_shared else "")
    print("  8. intersection: EMPTY, no witness")

    # FG !a is the complement of GF a -- free, on the same table.
    fg_not_a = complement(table2, p2)
    fwd, w_fwd = included(align(table.language(p), table2.language(fg_not_a)))
    assert fwd and w_fwd is None, "a*.b^w <= FG !a should HOLD"

    rev, w_rev = included(align(table2.language(fg_not_a), table.language(p)))
    assert not rev and w_rev is not None, "FG !a <= a*.b^w should FAIL"
    print(f"  9. inclusion: a*.b^w <= FG !a HOLDS; the reverse FAILS on "
          f"{show(w_rev)}  [{w_rev.render()}]")

    want = Lasso((B_MASK, A_MASK), (B_MASK,))          # ba . b^w
    assert w_rev.lasso == want, (
        f"F-EX: minimal counterexample is {show(w_rev)}, theory predicted ba . (b)^w")

    # The counterexample replays: in FG !a, out of a*.b^w.
    assert member(table2, fg_not_a, want), "counterexample not in FG !a"
    assert not member(table, p, want), "counterexample is in a*.b^w"
    print("     counterexample replays: in FG !a, not in a*.b^w")


def main() -> int:
    inv = reference_of_ltl(L_ASTAR_BOMEGA)
    inv2 = reference_of_ltl(L_GF_A)
    print(f"E-CAL-EX  a*.b^w = {L_ASTAR_BOMEGA}   GF a = {L_GF_A}   "
          f"(a = !p, b = p; both invariants built by Spot + quotient)")

    roles = roles_of(inv)
    table, p = Table.of(inv), inv.accept
    print("  roles: " + ", ".join(
        f"{name}={render_word(inv.alphabet, inv.keys[c]) or 'eps'}"
        for name, c in roles.items()))

    check_algebra(inv, roles)
    check_stutter(inv, roles)
    check_rootings(table, p, roles)
    check_hulls(table, p, roles)
    check_obligation(table, inv, p)
    table2, p2, _ = check_gfa(inv2)
    check_align(table, p, table2, p2)

    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
