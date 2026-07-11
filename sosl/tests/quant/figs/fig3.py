"""FIG-3 — the kernel group and the phase contrast, on F-D (paper §3.4).

    python3 -m tests.quant.figs.fig3 SRC.sos [OUT.tex]

Two panels side by side. Left: the right-Cayley graph of the nine-class
invariant of "some ``a`` at infinitely many even positions", its SCCs
boxed, the unique bottom SCC ``K = {fold(aa), fold(baa)}`` double-circled
and thick-bordered, tagged ``≅ ℤ/2`` and ``θ = 1``. Right: the phase
contrast, every verdict computed by `Table.val` — the non-kernel idempotent
``e' = fold(ba)`` splits the ``R``-equivalent stems ``fold(b)``, ``fold(bb)``
(``1`` vs ``0``), while the kernel loop ``k = fold(aa)`` merges them
(``1`` and ``1``); the lasso names and the re-bracketing are the paper's.
Called without an output path it prints the four verdicts.
"""
from __future__ import annotations

import sys

from sosl.sos import load_invariant
from sosl.sos.calculus import Table
from sosl.quant import kernel, kernel_idempotent, theta_profile

from tests.quant.figs import cayley, tikz

# canonical F-D ids: 6 = fold(aa) = k, 8 = fold(baa) = m, 4 = fold(ba) = e',
# 1 = fold(b), 3 = fold(bb).
LAYOUT = cayley.Layout(
    pos={0: (0.0, 4.4),
         1: (-4.6, 2.6), 3: (-2.1, 2.6),
         2: (2.1, 2.6), 5: (4.6, 2.6),
         4: (-4.6, 0.3), 7: (-2.1, 0.3),
         6: (1.8, -2.0), 8: (4.3, -2.0)},
    bend={(1, 3): 24, (3, 1): 24, (2, 5): 24, (5, 2): 24,
          (4, 7): 24, (7, 4): 24, (6, 8): 24, (8, 6): 24,
          (4, 8): 10},
    theta_at={6: "north"},
)

RX = 7.4            # right panel origin


def draw(src: str) -> str:
    inv = load_invariant(open(src).read())
    tab = Table.of(inv)
    k = kernel_idempotent(inv)
    b, bb = tab.fold((0,)), tab.fold((0, 0))       # fold(b), fold(bb)  (mask 0 = b)
    ba = tab.fold((0, 1))                           # fold(ba)  -> e'
    aa = tab.fold((1, 1))                           # fold(aa)  -> k
    assert aa == k and tab.idem(ba) == ba

    body = cayley.render(inv, LAYOUT, show_x=False)

    # K box annotations (the group and its verdict).
    body.append(rf"  \node[scctag, anchor=west] at (5.4,-2.0) "
                rf"{{$K \cong \mathbb{{Z}}/2$\\$\theta_K = 1$}};")
    body.append(rf"  \node[scctag] at (3.05,-3.2) "
                rf"{{the unique bottom SCC = the kernel}};")

    # ---- right panel: the phase contrast, verdicts via Val ---------------
    def badge(bit: bool) -> str:
        st = "thetaT" if bit else "thetaF"
        return rf"\tikz\node[{st}]{{{1 if bit else 0}}};"

    v_b_e = tab.val(inv.accept, b, ba)
    v_bb_e = tab.val(inv.accept, bb, ba)
    v_b_k = tab.val(inv.accept, b, aa)
    v_bb_k = tab.val(inv.accept, bb, aa)
    assert (v_b_e, v_bb_e, v_b_k, v_bb_k) == (True, False, True, True)

    y = 3.9
    body.append(rf"  \node[vrow,font=\small\bfseries] at ({RX},{y}) "
                rf"{{Phase contrast \;($\mathrm{{Val}}$ read-offs)}};")
    y -= 0.85
    body.append(rf"  \node[vrow] at ({RX},{y}) "
                rf"{{$e' = \mathrm{{fold}}(ba)$ \; (non-kernel idempotent)}};")
    y -= 0.7
    body.append(rf"  \node[vrow] at ({RX},{y}) "
                rf"{{$\mathrm{{Val}}(\mathrm{{fold}}(b),\,e') = $ {badge(v_b_e)} "
                rf"\quad $b\cdot(ba)^\omega \in L$}};")
    y -= 0.7
    body.append(rf"  \node[vrow] at ({RX},{y}) "
                rf"{{$\mathrm{{Val}}(\mathrm{{fold}}(bb),\,e') = $ {badge(v_bb_e)} "
                rf"\quad $bb\cdot(ba)^\omega \notin L$}};")
    y -= 0.6
    body.append(rf"  \node[vnote] at ({RX},{y}) "
                rf"{{$R$-equivalent stems, split verdict: "
                rf"$\mathrm{{Val}}(\cdot,e')$ is not $R$-invariant}};")
    y -= 1.0
    body.append(rf"  \node[vrow] at ({RX},{y}) "
                rf"{{$k = \mathrm{{fold}}(aa)$ \; (kernel idempotent)}};")
    y -= 0.7
    body.append(rf"  \node[vrow] at ({RX},{y}) "
                rf"{{$\mathrm{{Val}}(\mathrm{{fold}}(b),\,k) = $ {badge(v_b_k)} "
                rf"\qquad $\mathrm{{Val}}(\mathrm{{fold}}(bb),\,k) = $ {badge(v_bb_k)}}};")
    y -= 0.6
    body.append(rf"  \node[vnote] at ({RX},{y}) "
                rf"{{$u\cdot(aa)^\omega = (u{{\cdot}}a)\cdot(aa)^\omega$: "
                rf"the kernel forgets the phase}};")

    # a light divider between the panels.
    body.append(r"  \draw[cut] (6.9,-3.3) -- (6.9,4.5);")
    return tikz.standalone(body)


def report(src: str) -> None:
    inv = load_invariant(open(src).read())
    tab = Table.of(inv)
    b, bb = tab.fold((0,)), tab.fold((0, 0))
    ba, aa = tab.fold((0, 1)), tab.fold((1, 1))
    print(f"F-D: {inv.n} classes; kernel {sorted(kernel(inv))}, "
          f"k = {kernel_idempotent(inv)} = fold(aa) = {aa}")
    print(f"  theta {theta_profile(inv).entries}")
    print(f"  e' = fold(ba) = class {ba} (idempotent: {tab.idem(ba) == ba})")
    print(f"  Val(fold(b),e')  = {tab.val(inv.accept, b, ba)}   "
          f"Val(fold(bb),e') = {tab.val(inv.accept, bb, ba)}")
    print(f"  Val(fold(b),k)   = {tab.val(inv.accept, b, aa)}   "
          f"Val(fold(bb),k)  = {tab.val(inv.accept, bb, aa)}")


def main() -> None:
    src = sys.argv[1]
    if len(sys.argv) > 2:
        open(sys.argv[2], "w").write(draw(src))
        print(f"wrote {sys.argv[2]}")
    else:
        report(src)


if __name__ == "__main__":
    main()
