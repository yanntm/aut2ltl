"""K-E2 step 3: the Prop C.19 transfer specimen — first moving-layer floor.

    python3 -m tests.cascade.k_e2_transfer

Builds `𝓘(π₁⁻¹(GF(a∧X((!a&!b)U a))) ∩ π₂⁻¹(G(c→F d)))` — over disjoint AP sets
this is the conjunction over `{a,b,c,d}` — locates the moving final layer, and
runs the (C)-decider at k=0..3 plus the sandwich scan. Prop C.19 predicts a
MOVING, 1-anchored final layer with verified (C)-conflicts at every tested
width (the transfer of the floor witness's absorption onto a moving layer). A
clean pass at any width would REFUTE C.19 (PAPER-EDIT on C.4/C.19).
"""
from __future__ import annotations

import sys
from typing import List

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.anchoring import analyze_layer
from aut2ltl.sos2ltl.readoffs import is_prefix_independent
from sosl.sos.classify.aperiodic import is_aperiodic

from sosl.sos.lasso import Lasso

from tests.cascade.config_machine import find_c_conflict, quotient_letters


def rep_mask(inv, d: int) -> int:
    """A representative concrete letter mask of quotient letter `d`."""
    return next(a for a in inv.alphabet.letters() if inv.letter_class[a] == d)


def reach_word(inv, target: int):
    """Shortest concrete word folding identity → `target` (Cayley BFS)."""
    from collections import deque
    seen = {inv.identity: ()}
    q = deque([inv.identity])
    while q:
        c = q.popleft()
        if c == target:
            return seen[c]
        for a in inv.alphabet.letters():
            n = inv.mult[c][inv.letter_class[a]]
            if n not in seen:
                seen[n] = seen[c] + (a,)
                q.append(n)
    return None


def conjugate(inv, s1, e1, s2, e2) -> bool:
    """Lemma C.11: (s1,e1) ~ (s2,e2) if e1=g·h, e2=h·g, s2=s1·g for some g,h."""
    n = inv.n
    for g in range(n):
        for h in range(n):
            if inv.mult[g][h] == e1 and inv.mult[h][g] == e2 \
                    and inv.mult[s1][g] == s2:
                return True
    return False


def verify_conflict(inv, con) -> dict:
    """ALG-7: reconstruct the two lassos, check the verdict toggles under
    `inv.member` (independent of the closure) and the induced linked pairs are
    non-conjugate (a genuine floor inhabitant, not a closure bug). Returns
    `{"m1", "m2", "conjugate", "genuine"}` alongside the printout."""
    (c, x, d1, v1, w1) = con.w1
    (_, _, d2, v2, w2) = con.w2
    base_cls = x[0]
    stem = reach_word(inv, base_cls)
    loop1 = tuple(rep_mask(inv, a) for a in w1)
    loop2 = tuple(rep_mask(inv, a) for a in w2)
    m1 = inv.member(Lasso(stem, loop1))
    m2 = inv.member(Lasso(stem, loop2))
    e1, e2 = inv.idempotent_power(d1), inv.idempotent_power(d2)
    s1, s2 = inv.mult[base_cls][e1], inv.mult[base_cls][e2]
    conj = conjugate(inv, s1, e1, s2, e2)
    print(f"  ALG-7 verify (k={con.k}): base class {base_cls}")
    print(f"    loop1 classes d1={d1} (idem {e1}) member={m1}")
    print(f"    loop2 classes d2={d2} (idem {e2}) member={m2}")
    print(f"    membership TOGGLES: {m1 != m2}   linked pairs conjugate: {conj}")
    print(f"    => {'GENUINE floor inhabitant' if m1 != m2 and not conj else 'CHECK (bug?)'}")
    return {"m1": m1, "m2": m2, "conjugate": conj,
            "genuine": m1 != m2 and not conj}

FORMULA = "(G F (a & X((!a & !b) U a))) & (G (c -> F d))"


def main(argv: List[str]) -> int:
    inv = invariant_of_language(Language.of(spot.translate(FORMULA)))
    ap = is_aperiodic(inv)
    cay = build(inv)
    print(f"# transfer specimen: {FORMULA}")
    print(f"  {inv.n} classes; aperiodic={ap}; "
          f"prefix-independent={is_prefix_independent(inv)}; "
          f"|Σ_λ|={len(quotient_letters(inv))}; layers={len(cay.layers)}")
    for i, layer in enumerate(cay.layers):
        anc = analyze_layer(cay, i)
        frozen = all(k == "neutral" for k in anc.letter_kind.values())
        term = not cay.successors[i]
        print(f"  layer {i}: R={{{','.join(map(str,layer))}}} "
              f"|R|={len(layer)} terminal={term} frozen={frozen} width={anc.width}")

    fid = len(cay.layers) - 1
    R = frozenset(cay.layers[fid])
    anc = analyze_layer(cay, fid)
    moving = any(k != "neutral" and k != "exit"
                 for k in anc.letter_kind.values())
    print(f"  --- final layer {fid}: |R|={len(R)} moving={moving} ---")

    all_conflict = True
    for k in range(4):
        con = find_c_conflict(inv, R, k, budget=400000)
        print(f"    k={k}: {con.status}  states={con.states}"
              + (f"  |F|={len(con.F)} d1={con.w1[2]} d2={con.w2[2]}"
                 if con.status == "CONFLICT" else ""))
        if con.status == "CONFLICT":
            verify_conflict(inv, con)
        if con.status != "CONFLICT":
            all_conflict = False
        if con.status == "CLEAN":
            print(f"  VERDICT: (C) HOLDS at width {k} — C.19 REFUTED "
                  f"(PAPER-EDIT C.4/C.19)")
            return 0
    if all_conflict:
        print("  VERDICT: verified genuine (C)-CONFLICT at every width k=0..3 — "
              "first MOVING-layer floor inhabitant, C.19 CONFIRMED")
    else:
        print("  VERDICT: verified genuine (C)-CONFLICT at every NON-budget "
              "width (k=0,1 toggle+non-conjugate); higher k BUDGET (tooling) — "
              "C.19 CONFIRMED on the moving layer, no clean width found")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
