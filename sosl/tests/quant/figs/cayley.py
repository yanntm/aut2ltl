"""The decorated right-Cayley drawing shared by FIG-1 and FIG-3 (left).

One picture of a held invariant's right-Cayley graph, carrying the whole
measure read-off:

* the **classes**, keyed by their shortlex-least word; a class in a bottom
  SCC is double-circled, a class in the kernel wears a thick border;
* the **Cayley steps** ``c ->^x M(c, lambda(x))``, one arrow per (class,
  letter), letters told apart by hue *and* dash pattern; letters that agree
  on a class share one neutral arrow;
* the **SCC boxes** (any strongly connected component of two or more
  classes), the transient ones grey;
* per bottom SCC its **θ badge** (green 1 / red 0) on the component's
  least-keyed class, and under every class its **x-value** at the measure
  ``p`` — the value_vector entry, an exact fraction.

Everything drawn is read off the tested engine (`bottom_sccs`, `kernel`,
`theta_profile`, `value_vector`) and the calculus SCC pass; this module owns
only the *placement*, which a `Layout` supplies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

from sosl.sos import Invariant, Letter
from sosl.sos.calculus.surgery import _right_cayley_sccs
from sosl.sos.calculus.table import Table
from sosl.quant import (
    bottom_sccs,
    kernel,
    right_cayley_edges,
    theta_profile,
    value_vector,
)
from sosl.quant.chain import least_key_class

from tests.quant.figs import tikz

Pos = Tuple[float, float]


@dataclass
class Layout:
    """Placement for one Cayley drawing; carries coordinates and drawing
    hints only, never anything semantic."""

    pos: Dict[int, Pos]
    loop_at: Dict[int, str] = field(default_factory=dict)          # class -> dir
    bend: Dict[Tuple[int, int], int] = field(default_factory=dict)  # (c,d) -> deg
    theta_at: Dict[int, str] = field(default_factory=dict)         # class -> anchor
    x_at: Dict[int, str] = field(default_factory=dict)             # class -> anchor
    box_at: Dict[int, str] = field(default_factory=dict)           # scc-min -> tag anchor
    scale: float = 1.0


def _edge_style(inv: Invariant, a: int) -> str:
    if inv.alphabet.size != 2:
        return "ea"
    return "ea" if inv.alphabet.true_aps(a) else "eb"


def _sccs(inv: Invariant) -> List[List[int]]:
    comp, ncomp = _right_cayley_sccs(Table.of(inv))
    groups: List[List[int]] = [[] for _ in range(ncomp)]
    for c in range(inv.n):
        groups[comp[c]].append(c)
    return groups


def render(inv: Invariant, lay: Layout,
           p: Optional[Dict[Letter, Fraction]] = None,
           show_x: bool = True) -> str:
    bottoms = bottom_sccs(inv)
    kern = kernel(inv)
    prof = theta_profile(inv)
    x = value_vector(inv, p)
    in_bottom = {c for scc in bottoms for c in scc}
    theta_of_rep: Dict[int, bool] = {
        least_key_class(inv, scc): prof.entries[j][1]
        for j, scc in enumerate(bottoms)
    }

    body: List[str] = [rf"\begin{{scope}}[scale={lay.scale}]"]

    # nodes: double circle if bottom, thick border if kernel.
    for c, (px, py) in sorted(lay.pos.items()):
        styles = ["bottom" if c in in_bottom else "cls"]
        if c in kern:
            styles.append("kern")
        body.append(
            rf"  \node[{','.join(styles)}] (c{c}) at ({px:.2f},{py:.2f}) "
            rf"{{${tikz.class_tex(inv, c)}$\\[-1pt]"
            rf"\textcolor{{ref}}{{\tiny {c}}}}};")

    # Cayley steps: letters agreeing on a class merge into one arrow.
    edges = right_cayley_edges(inv)
    for c in sorted(lay.pos):
        groups: Dict[int, List[int]] = {}
        for a, d in enumerate(edges[c]):
            groups.setdefault(d, []).append(a)
        for d, letters in sorted(groups.items()):
            lbl = ", ".join(rf"\texttt{{{tikz.letter_txt(inv, a)}}}"
                            for a in letters)
            sty = (_edge_style(inv, letters[0]) if len(letters) == 1
                   else "eall")
            if d == c:
                where = lay.loop_at.get(c, "above")
                body.append(rf"  \draw[{sty}] (c{c}) edge[loop {where},"
                            rf"looseness=6] node[elab] {{{lbl}}} (c{c});")
            elif d in lay.pos:
                b = lay.bend.get((c, d), 0)
                bend = f"[bend left={b}]" if b else ""
                body.append(rf"  \draw[{sty}] (c{c}) to{bend} "
                            rf"node[elab] {{{lbl}}} (c{d});")

    # SCC boxes for components of two or more drawn classes.
    for grp in _sccs(inv):
        drawn = [c for c in grp if c in lay.pos]
        if len(drawn) < 2:
            continue
        nodes = " ".join(f"(c{c})" for c in drawn)
        body.append(r"  \begin{scope}[on background layer]")
        body.append(rf"    \node[sccbox, fit={nodes}, inner sep=7pt] "
                    rf"(S{min(drawn)}) {{}};")
        body.append(r"  \end{scope}")

    # θ badges and x-value annotations.
    for c in sorted(lay.pos):
        if c in theta_of_rep:
            bit = theta_of_rep[c]
            st = "thetaT" if bit else "thetaF"
            anchor = lay.theta_at.get(c, "north east")
            body.append(rf"  \node[{st}] at (c{c}.{anchor}) "
                        rf"{{{1 if bit else 0}}};")
        if show_x:
            xa = lay.x_at.get(c, "south")
            body.append(rf"  \node[xann, anchor={_opp(xa)}, yshift=-1mm] "
                        rf"at (c{c}.{xa}) {{$x={tikz.frac_tex(x[c])}$}};")

    body.append(r"\end{scope}")
    return body


def _opp(side: str) -> str:
    return {"south": "north", "north": "south",
            "east": "west", "west": "east"}.get(side, "north")


__all__ = ["Layout", "render"]
