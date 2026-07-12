"""FIG-1 — kernel vs `Aut`: the two-level structure of Theorem 3.1.

Two panels over the 2-AP minterm square, both entirely data-driven from the
fixtures and `sosl.sos.symmetry` (SY1); the probe hard-codes *placement* only.

  Left  (Example A, `GF a` = FIX_A): the square colored by λ-fiber; the flip
        σ_b as green arrows *within* each fiber (`λ∘σ_b = λ`, the kernel
        read-off); the flip σ_a crossing fibers, whose candidate must go to
        the table and there fails.
  Right (Example B, `GF a ∧ GF b` = FIX_B): λ injective (four singleton
        fibers); the 5-class multiplication table; the swap's ρ = (A B) as
        green arrows with P = {(C,C)} fixed; σ_a's forced images up to the
        one cell where ρ(A·B) ≠ ρ(A)·ρ(B), red-crossed.

Run without an output path to print the read-offs (the cheapest number check);
with a path, it writes the `.tex` the Makefile rasterizes.

    python3 -m tests.symmetry.figs.fig1 [out.tex]
"""
from __future__ import annotations

import sys
from typing import Dict, List, Optional, Tuple

from tests.symmetry import fixtures
from sosl.sos.invariant import Invariant
from sosl.sos.symmetry.sigma import (
    SignedPerm, apply_perm, in_kernel, is_symmetry, inert_aps)

from . import tikz


# --------------------------------------------------------------------------
# read-offs (data; no placement)
# --------------------------------------------------------------------------

def _sigma_action(inv: Invariant, s: SignedPerm) -> Dict[int, int]:
    """The letter map `m ↦ σ(m)` on every minterm mask."""
    return {a: s(a) for a in inv.alphabet.letters()}


def _forced_rho(inv: Invariant, s: SignedPerm) -> Dict[int, int]:
    """The forced class map ρ read off `λ∘σ`: ρ(λ(m)) = λ(σ(m)). Defined on the
    classes in the image of λ (a candidate automorphism, before any table
    check); the identity is fixed."""
    rho: Dict[int, int] = {inv.identity: inv.identity}
    for m in inv.alphabet.letters():
        rho[inv.letter_class[m]] = inv.letter_class[s(m)]
    return rho


def _is_failure(inv: Invariant, rho: Dict[int, int], x: int, y: int) -> bool:
    """Whether the cell (x, y) witnesses `ρ(x·y) ≠ ρ(x)·ρ(y)` (all three of
    x, y, x·y in ρ's domain)."""
    xy = inv.mult[x][y]
    return xy in rho and rho[xy] != inv.mult[rho[x]][rho[y]]


def _failure_cell(inv: Invariant, swap_rho: Dict[int, int],
                  flip_rho: Dict[int, int]) -> Optional[Tuple[int, int]]:
    """The cell the paper narrates: the product `A·B` of the two classes the
    *swap* automorphism exchanges (its non-fixed pair), which the *flip*'s
    forced map breaks. Ties the two panels together and is fully read off the
    two candidate maps. Falls back to the first failing cell in id order if the
    swap's own pair happens not to fail (asserted not to happen on FIX_B)."""
    moved = sorted(x for x in swap_rho if swap_rho[x] != x)
    if len(moved) == 2:
        x, y = moved
        if _is_failure(inv, flip_rho, x, y):
            return (x, y)
    for x in sorted(flip_rho):
        for y in sorted(flip_rho):
            if _is_failure(inv, flip_rho, x, y):
                return (x, y)
    return None


# --------------------------------------------------------------------------
# left panel — Example A, the kernel
# --------------------------------------------------------------------------

# minterm-square placement: columns by AP `a` (¬a left, a right), rows by AP
# `b` (b top, ¬b bottom). Keyed by mask, computed from the alphabet below.
def _square_pos(inv: Invariant, x0: float) -> Dict[int, Tuple[float, float]]:
    """A position per minterm mask: AP index 0 sets the column, AP index 1 the
    row. Two APs exactly (asserted by the caller)."""
    pos: Dict[int, Tuple[float, float]] = {}
    for m in inv.alphabet.letters():
        trues = inv.alphabet.true_aps(m)
        col = 1 if inv.alphabet.aps[0] in trues else 0
        row = 1 if inv.alphabet.aps[1] in trues else 0
        pos[m] = (x0 + 2.4 * col, 2.4 * row)
    return pos


def _panel_a(inv: Invariant, x0: float) -> List[str]:
    aps = inv.alphabet.aps
    assert len(aps) == 2, "FIG-1 left panel is the 2-AP square"
    ai = 0  # AP `a`
    bi = 1  # AP `b`
    sig_b = SignedPerm.polarity_flip(2, bi)
    sig_a = SignedPerm.polarity_flip(2, ai)
    pos = _square_pos(inv, x0)
    lc = inv.letter_class
    # the two fat fibers, by class
    fibers: Dict[int, List[int]] = {}
    for m in inv.alphabet.letters():
        fibers.setdefault(lc[m], []).append(m)

    out: List[str] = []
    out.append(rf"\node[hdr] at ({x0 + 1.2:.2f}, 3.5) {{Example A: $GF\,a$}};")
    # fiber hulls (drawn behind the vertices)
    out.append(r"\begin{scope}[on background layer]")
    for c, masks in fibers.items():
        style = "fibF" if c == lc[max(inv.alphabet.letters())] else "fibN"
        nodes = " ".join(f"(mA{m})" for m in masks)
        # placeholder fit needs the nodes to exist; declare invisible anchors
        for m in masks:
            xx, yy = pos[m]
            out.append(rf"\coordinate (mA{m}) at ({xx:.2f}, {yy:.2f});")
        out.append(rf"\node[{style}, fit={nodes}, inner sep=9pt] "
                   rf"(fibbox{c}) {{}};")
    out.append(r"\end{scope}")
    # fiber tags (the class each fiber maps to)
    for c, masks in fibers.items():
        lbl = tikz.class_tex(inv, c)
        out.append(rf"\node[tag, anchor=south] at (fibbox{c}.north) "
                   rf"{{$\lambda^{{-1}}({lbl})$}};")
    # minterm vertices
    for m in inv.alphabet.letters():
        xx, yy = pos[m]
        out.append(rf"\node[mint] (mv{m}) at ({xx:.2f}, {yy:.2f}) "
                   rf"{{${tikz.minterm_tex(inv, m)}$}};")
    # σ_b — green arrows within fibers (kernel), one per swapped pair
    act_b = _sigma_action(inv, sig_b)
    seen: set = set()
    for m, mm in act_b.items():
        if m == mm or (mm, m) in seen:
            continue
        seen.add((m, m if m < mm else mm))
        within = lc[m] == lc[mm]
        sty = "perm" if within else "permd"
        out.append(rf"\draw[{sty}] (mv{m}) -- (mv{mm});")
    out.append(rf"\node[ktag, anchor=north] at ({x0 + 1.2:.2f}, -0.9) "
               rf"{{$\lambda\circ\sigma_b=\lambda$\\(in $K$: read-off)}};")
    # σ_a — crossing fibers, must go to the table and there fails
    act_a = _sigma_action(inv, sig_a)
    seen = set()
    for m, mm in act_a.items():
        if m == mm or (mm, m) in seen:
            continue
        seen.add((m, m if m < mm else mm))
        out.append(rf"\draw[permd] (mv{m}) to[bend left=12] (mv{mm});")
    out.append(rf"\node[fail, anchor=north] at ({x0 + 1.2:.2f}, -1.9) "
               rf"{{$\sigma_a$ crosses fibers:\\candidate $\to$ table, "
               rf"$\rho(P)\neq P$}};")
    return out


# --------------------------------------------------------------------------
# right panel — Example B, the automorphism
# --------------------------------------------------------------------------

def _panel_b(inv: Invariant, x0: float) -> List[str]:
    aps = inv.alphabet.aps
    assert len(aps) == 2, "FIG-1 right panel is the 2-AP square"
    swap = SignedPerm.transposition(2, 0, 1)
    sig_a = SignedPerm.polarity_flip(2, 0)
    lc = inv.letter_class
    n = inv.n
    out: List[str] = []
    out.append(rf"\node[hdr] at ({x0 + 2.4:.2f}, 3.5) "
               rf"{{Example B: $GF\,a\wedge GF\,b$}};")

    # -- the injective square (four singleton fibers) --------------------
    pos = _square_pos(inv, x0)
    for m in inv.alphabet.letters():
        xx, yy = pos[m]
        c = lc[m]
        out.append(rf"\node[mint] (mB{m}) at ({xx:.2f}, {yy + 0.0:.2f}) "
                   rf"{{${tikz.minterm_tex(inv, m)}\!\mapsto\!"
                   rf"{tikz.class_tex(inv, c)}$}};")
    out.append(rf"\node[tag, anchor=north] at ({x0 + 1.2:.2f}, -0.6) "
               rf"{{$\lambda$ injective: $K$ trivial}};")

    # -- the 5-class multiplication table --------------------------------
    rho = _forced_rho(inv, swap)          # the symmetric swap ρ = (A B)
    rho_a = _forced_rho(inv, sig_a)       # the failing flip σ_a
    fail = _failure_cell(inv, rho, rho_a)
    tx = x0 + 4.2
    ty = 2.6
    cell = 0.92
    # header row / column: class keys
    for j in range(n):
        out.append(rf"\node[celltab] at ({tx + (j + 1) * cell:.2f}, "
                   rf"{ty:.2f}) {{${tikz.class_tex(inv, j)}$}};")
        out.append(rf"\node[celltab] at ({tx:.2f}, "
                   rf"{ty - (j + 1) * cell:.2f}) {{${tikz.class_tex(inv, j)}$}};")
    out.append(rf"\node[celltab, text=ref] at ({tx:.2f}, {ty:.2f}) "
               rf"{{$\cdot$}};")
    # body cells
    for i in range(n):
        for j in range(n):
            v = inv.mult[i][j]
            cx = tx + (j + 1) * cell
            cy = ty - (i + 1) * cell
            out.append(rf"\node[celltab] at ({cx:.2f}, {cy:.2f}) "
                       rf"{{${tikz.class_tex(inv, v)}$}};")
    out.append(rf"\node[hdr, anchor=south] at ({tx + 3 * cell:.2f}, "
               rf"{ty + 0.5:.2f}) {{multiplication table $M$}};")

    # accepting pair P fixed by the swap — double-ring the (C,C) cell
    for (s, e) in sorted(inv.accept):
        if rho.get(s) == s and rho.get(e) == e:
            cx = tx + (e + 1) * cell
            cy = ty - (s + 1) * cell
            out.append(rf"\node[draw=accept, line width=1pt, circle, "
                       rf"inner sep=1pt, minimum size=6mm] at "
                       rf"({cx:.2f}, {cy:.2f}) {{}};")
    # swap arrows on the header (rows/cols A ↔ B)
    ab = [(x, y) for x, y in rho.items() if x != y]
    if ab:
        x, y = ab[0]
        out.append(rf"\draw[perm] ({tx:.2f}, {ty - (x + 1) * cell:.2f}) "
                   rf"to[bend right=30] ({tx:.2f}, {ty - (y + 1) * cell:.2f});")
        out.append(rf"\node[permlab, anchor=east] at "
                   rf"({tx - 0.5:.2f}, {ty - (x + 1.5) * cell:.2f}) "
                   rf"{{$\rho=({tikz.class_tex(inv, x)}\,{tikz.class_tex(inv, y)})$}};")
    # the failing flip σ_a: red-cross the offending cell
    if fail is not None:
        i, j = fail
        cx = tx + (j + 1) * cell
        cy = ty - (i + 1) * cell
        d = 0.36
        out.append(rf"\draw[xfail, line width=1.1pt] "
                   rf"({cx - d:.2f}, {cy - d:.2f}) -- ({cx + d:.2f}, {cy + d:.2f});")
        out.append(rf"\draw[xfail, line width=1.1pt] "
                   rf"({cx - d:.2f}, {cy + d:.2f}) -- ({cx + d:.2f}, {cy - d:.2f});")
        prod = inv.mult[i][j]
        out.append(
            rf"\node[fail, anchor=north] at ({tx + 3 * cell:.2f}, "
            rf"{ty - (n + 1.4) * cell:.2f}) {{$\sigma_a$: "
            rf"$\rho({tikz.class_tex(inv, i)}\!\cdot\!{tikz.class_tex(inv, j)})"
            rf"=\rho({tikz.class_tex(inv, prod)})"
            rf"\neq\rho({tikz.class_tex(inv, i)})\!\cdot\!"
            rf"\rho({tikz.class_tex(inv, j)})$\\dies on one cell, "
            rf"no keying pass}};")
    return out


# --------------------------------------------------------------------------
# assembly + provenance print
# --------------------------------------------------------------------------

def _facts(A: Invariant, B: Invariant) -> List[str]:
    sb = SignedPerm.polarity_flip(2, 1)
    sa = SignedPerm.polarity_flip(2, 0)
    swap = SignedPerm.transposition(2, 0, 1)
    rho_swap = _forced_rho(B, swap)
    rho_a = _forced_rho(B, SignedPerm.polarity_flip(2, 0))
    fail = _failure_cell(B, rho_swap, rho_a)
    return [
        f"FIX_A |C|={A.n} P={sorted(A.accept)} inert={sorted(inert_aps(A))}",
        f"  σ_b in_kernel={in_kernel(A, sb)} is_symmetry={is_symmetry(A, sb)}",
        f"  σ_a is_symmetry={is_symmetry(A, sa)}",
        f"FIX_B |C|={B.n} P={sorted(B.accept)} inert={sorted(inert_aps(B))}",
        f"  swap is_symmetry={is_symmetry(B, swap)}",
        f"  σ_a is_symmetry={is_symmetry(B, sa)} first_mult_failure={fail}",
    ]


def build(out_tex: Optional[str]) -> None:
    A = fixtures.load("FIX_A")
    B = fixtures.load("FIX_B")
    for line in _facts(A, B):
        print(line)
    if out_tex is None:
        return
    body = _panel_a(A, 0.0) + _panel_b(B, 6.0)
    with open(out_tex, "w") as fh:
        fh.write(tikz.standalone(body))
    print(f"wrote {out_tex}")


def main() -> None:
    build(sys.argv[1] if len(sys.argv) > 1 else None)


if __name__ == "__main__":
    main()
