"""The layered class-machine drawing shared by FIG-1 and FIG-4.

One picture, three strata (paper §5.2):

* the **classes** of `S(L)₊¹`, keyed by their shortlex-least word;
* the **Cayley steps** `c →^x c·λ(x)`, one arrow per (class, letter), the
  letters told apart by hue *and* dash pattern; letters that agree on a class
  share one arrow, so a frozen class shows a single neutral self-loop;
* the **layers** — the SCCs of `Cay(L)`, i.e. the R-classes — as boxes, with
  the R-order between them as thick arrows, and a side tag per box naming the
  condition-(A) letter kinds and the condition-(B) width.

Everything drawn is read off the tested modules (`cayley`, `anchoring`,
`windows`); this module owns only the *placement*, which no probe can supply.
A `Layout` therefore carries coordinates and anchors, nothing semantic.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from aut2ltl.sos2ltl import anchoring, windows
from aut2ltl.sos2ltl.cayley import Cayley
from sosl.sos import Invariant

from tests.sos2ltl.figs import tikz

# On when either FIGS_TRACE or the global TRANSLATOR_TRACE_ON is set (presence;
# value ignored). Every message is built inside `if _TRACE:`, so nothing is
# computed when off.
_TRACE = "FIGS_TRACE" in os.environ or "TRANSLATOR_TRACE_ON" in os.environ

Pos = Tuple[float, float]


@dataclass
class Layout:
    """Placement for one machine: where classes sit, where decorations hang."""

    pos: Dict[int, Pos]
    tag_at: Dict[int, str] = field(default_factory=dict)     # layer -> anchor
    tag_shift: Dict[int, float] = field(default_factory=dict)  # layer -> mm
    bend: Dict[Tuple[int, int], int] = field(default_factory=dict)
    loop_at: Dict[int, str] = field(default_factory=dict)     # class -> dir
    entry_at: Dict[int, int] = field(default_factory=dict)    # class -> angle
    scale: float = 1.0


# ------------------------------------------------------------------ #
# Rendering the algebra's own names.
# ------------------------------------------------------------------ #
def letter_tex(inv: Invariant, a: int) -> str:
    trues = inv.alphabet.true_aps(a)
    return r" \land ".join(p if p in trues else rf"\lnot {p}"
                           for p in inv.alphabet.aps)


def letter_txt(inv: Invariant, a: int) -> str:
    trues = inv.alphabet.true_aps(a)
    return "&".join(p if p in trues else "!" + p for p in inv.alphabet.aps)


def class_tex(inv: Invariant, c: int) -> str:
    """The class's shortlex key as `[ε]`, `[¬a]`, `[¬a·a]`, …"""
    key = inv.keys[c]
    if not key:
        return r"[\varepsilon]"
    return "[" + r" {\cdot} ".join(letter_tex(inv, a) for a in key) + "]"


def _edge_style(inv: Invariant, a: int) -> str:
    """Solid for the letter satisfying the most atoms, dashed for its
    complement — a two-letter convention; more letters fall back to solid."""
    if inv.alphabet.size != 2:
        return "ea"
    return "ea" if inv.alphabet.true_aps(a) else "eb"


def _frozen(cay: Cayley, layer: Sequence[int], inv: Invariant) -> bool:
    return all(cay.step(c, a) == c
               for c in layer for a in range(inv.alphabet.size))


# ------------------------------------------------------------------ #
# The side tag of one layer: the (A) and (B) read-offs, verbatim.
# ------------------------------------------------------------------ #
def letter_role(cay: Cayley, layer: Sequence[int], inv: Invariant,
                a: int) -> str:
    """The role of letter `a` on `layer`, both halves of it.

    A letter may act inside the layer on some classes and exit from others; a
    tag naming only the exit would hide the in-layer action that condition (A)
    reads. The in-layer half is `reset(d)` when every class the letter keeps
    inside lands on the same `d` (a partial constant — what makes the layer
    1-anchorable), `moves` otherwise; the exit half names the classes the
    letter leaves from. A letter that never stays is a bare `exit`."""
    inside = set(layer)
    dests = {c: cay.step(c, a) for c in layer}
    stay = {d for d in dests.values() if d in inside}
    out = sorted(c for c, d in dests.items() if d not in inside)

    head = rf"\texttt{{{letter_txt(inv, a)}}}"
    if not stay:
        return head + ": exit"
    role = (rf"$\mapsto$ reset({stay.pop()})" if len(stay) == 1
            else ": moves")
    if out:
        role += r", exit@" + ",".join(str(c) for c in out)
    return f"{head} {role}" if role.startswith("$") else head + role


def layer_tag(cay: Cayley, la: anchoring.LayerAnchoring,
              rep: windows.WindowReport, inv: Invariant) -> str:
    lines: List[str] = []
    frozen = _frozen(cay, la.layer, inv)

    if rep.status == windows.TRANSIENT:
        lines.append(r"\textit{transient}")
    if frozen:
        lines.append(r"\textit{frozen}: every letter neutral")
    else:
        lines += [letter_role(cay, la.layer, inv, a)
                  for a in range(inv.alphabet.size)]

    if rep.status == windows.TRANSIENT:
        pass                                    # no law owed, no window owed
    elif la.width is None:
        lines.append(r"(A) \textit{fails at every width}")
    elif not frozen:
        lines.append(rf"(A) at $k={la.width}$")

    if rep.trivial and rep.verdict is False:
        lines.append(r"all-rejecting: $\mathrm{STAY}^\infty = \bot$")
    elif rep.trivial and rep.verdict is True:
        lines.append(r"all-accepting")
    elif rep.status == windows.PASS and rep.width:
        lines.append(rf"(B) at $k'={rep.width}$")
    return r"\\".join(lines)


# ------------------------------------------------------------------ #
def render(inv: Invariant, cay: Cayley, lay: Layout,
           committed: Sequence[int] = ()) -> str:
    anch = anchoring.analyze(cay)
    reps = [windows.analyze_layer(cay, i, k_max=3)
            for i in range(len(cay.layers))]

    body: List[str] = [rf"\begin{{scope}}[scale={lay.scale}]"]

    for c, (x, y) in sorted(lay.pos.items()):
        st = "committed" if c in committed else "cls"
        body.append(rf"  \node[{st}] (c{c}) at ({x:.2f},{y:.2f}) "
                    rf"{{${class_tex(inv, c)}$\\[-1pt]"
                    rf"\textcolor{{order}}{{\tiny {c}}}}};")

    for c, angle in sorted(lay.entry_at.items()):
        body.append(rf"  \draw[entry] ([shift=({angle}:1.05)]c{c}.{angle}) "
                    rf"-- (c{c}.{angle});")

    # Cayley steps, letters that agree on a class merged into one arrow.
    for c in sorted(lay.pos):
        groups: Dict[int, List[int]] = {}
        for a in range(inv.alphabet.size):
            groups.setdefault(cay.step(c, a), []).append(a)
        for d, letters in sorted(groups.items()):
            lbl = ", ".join(rf"\texttt{{{letter_txt(inv, a)}}}"
                            for a in letters)
            sty = (_edge_style(inv, letters[0]) if len(letters) == 1
                   else "eall")
            if _TRACE:
                print(f"[figs] step {c} -{lbl}-> {d}", file=sys.stderr)
            if d == c:
                where = lay.loop_at.get(c, "above")
                body.append(rf"  \draw[{sty}] (c{c}) edge[loop {where},"
                            rf"looseness=6] node[elab] {{{lbl}}} (c{c});")
            else:
                b = lay.bend.get((c, d), 0)
                bend = f"[bend left={b}]" if b else ""
                body.append(rf"  \draw[{sty}] (c{c}) to{bend} "
                            rf"node[elab] {{{lbl}}} (c{d});")

    # Layer boxes and their tags.
    for i, layer in enumerate(cay.layers):
        nodes = " ".join(f"(c{c})" for c in layer if c in lay.pos)
        if not nodes:
            continue
        box = "frozenbox" if _frozen(cay, layer, inv) else "layerbox"
        body.append(r"  \begin{scope}[on background layer]")
        body.append(rf"    \node[{box}, fit={nodes}, inner sep=6pt] "
                    rf"(L{i}) {{}};")
        body.append(r"  \end{scope}")
        side = lay.tag_at.get(i, "east")
        dx = lay.tag_shift.get(i, 4.0) * (-1 if side == "west" else 1)
        body.append(rf"  \node[layertag, anchor={_opp(side)}, "
                    rf"xshift={dx:.1f}mm] at (L{i}.{side}) "
                    rf"{{{layer_tag(cay, anch[i], reps[i], inv)}}};")

    for i in range(len(cay.layers)):
        for j in cay.successors[i]:
            body.append(r"  \begin{scope}[on background layer]")
            body.append(rf"    \draw[rorder] (L{i}) -- (L{j});")
            body.append(r"  \end{scope}")

    body.append(r"\end{scope}")
    return tikz.standalone(body)


def _opp(side: str) -> str:
    return {"west": "east", "east": "west",
            "north": "south", "south": "north"}[side]


__all__ = ["Layout", "class_tex", "layer_tag", "letter_txt", "render"]
