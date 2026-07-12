"""The TikZ backend: a placed `Figure` as a standalone `.tex` a human can edit.

The output is written to be *nudged*: every visual choice lives in one `\\tikzset`
block, each node is a named `\\node` at an explicit rounded coordinate, each arrow
is one `\\draw` between node names. Changing how the figure looks means editing one
style; changing where a node sits means editing one coordinate. Nothing is styled
inline and nothing is repeated.

The figure reads without a legend, and it draws only what the object *is*. Every
arrow carries its letter as a label — that, not a dash pattern, is how letters are
told apart — and the letters that agree on a target share one arrow (`a,b`)
instead of stacking two. Derived facts get no ink of their own -- not a monochrome
cycle (a property of the drawn arrows, not an arrow of another kind), not an
idempotent (a property of the product, not a kind of class). The root is
marked the way an initial state is, with a short incoming stub from nowhere, which
is also what makes freshness visible: it is the only arrow that enters it.

Pure text: the placement is an input (see `layout.py`), not something computed
here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .layout import Placement
from .model import Figure

# Self-loop directions, in preference order, with the unit vector each points at.
LOOP_DIRS: Tuple[Tuple[str, Tuple[float, float]], ...] = (
    ("loop above", (0.0, 1.0)), ("loop below", (0.0, -1.0)),
    ("loop right", (1.0, 0.0)), ("loop left", (-1.0, 0.0)))
# A neighbour nearer than this (cm), in a direction's cone, crowds it out.
CROWD_CM = 2.6
# How far an anti-parallel pair of arrows bends apart (both bend left).
BEND_ANGLE = 15
# How far under the lowest node the P caption sits (cm).
PAIRS_DROP_CM = 1.3
# Length of the initial-state stub pointing into the root (cm).
INIT_STUB_CM = 0.9
# Vertical gap between the lambda line and the P line (cm).
CAPTION_GAP_CM = 0.75


def _tex_key(fig: Figure, key: Tuple[int, ...]) -> str:
    """The math body of a display key: letters joined by ``{\\cdot}``, the identity
    as ``\\varepsilon``. No ``$`` — the caller places it."""
    if not key:
        return r"\varepsilon"
    names = [fig.naming.names[i] for i in key]
    escaped = [n.replace("!", r"\lnot ").replace("&", r"\wedge ") for n in names]
    return r"{\cdot}".join(escaped)


def _tex_class(fig: Figure, cls: int) -> str:
    r"""A class as it is written everywhere in the figure: ``[a{\cdot}b]``. Nodes
    and arrows alike name classes, never letters, so both wear the brackets."""
    return f"[{_tex_key(fig, fig.node_of(cls).key)}]"


def _tex_arrow_label(fig: Figure, letters: Tuple[int, ...]) -> str:
    """An arrow's label: the class each of its letters names, ``[a]`` or ``[a],[b]``
    when several letters take the same step. Aliases (letters of one class) collapse
    to the single class they name — the lambda line says which letters those were."""
    seen: List[str] = []
    for i in letters:
        tex = _tex_class(fig, fig.letter_class(i))
        if tex not in seen:
            seen.append(tex)
    return ",".join(seen)


def _tex_lambda(fig: Figure) -> str:
    """The letter map as one line: ``λ : a ↣ [a], b ↣ [b]``. The arrow itself
    carries the fact — a tail arrow when λ is injective (every letter names a class
    of its own), a plain maplet when it is not and some letters are aliases."""
    arrow = r"\rightarrowtail" if fig.lambda_injective() else r"\mapsto"
    items = [rf"{','.join(names)} {arrow} {_tex_class(fig, cls)}"
             for names, cls in fig.lambda_map()]
    return rf"$\lambda:\; " + r",\;\; ".join(items) + "$"


def _tex_pairs(fig: Figure) -> str:
    """The accepting pairs as one math line, ``P = \\{([b],[b]), …\\}``."""
    items = [rf"({_tex_class(fig, s)},{_tex_class(fig, e)})"
             for s, e in fig.pair_classes()]
    body = r",\; ".join(items) if items else r"\emptyset"
    return rf"$P = \{{\, {body} \,\}}$" if items else r"$P = \emptyset$"


def _loop_dir(fig: Figure, pos: Placement, cls: int) -> str:
    """The `loop <dir>` option for the self-loop at ``cls``, pointed away from the
    node's neighbours: the four directions are scored by how many other nodes
    crowd their cone, and the least-crowded wins (ties by the preference order)."""
    x, y = pos[cls]
    scored: List[Tuple[int, int, str]] = []
    for rank, (opt, (dx, dy)) in enumerate(LOOP_DIRS):
        crowd = 0
        for other in fig.nodes:
            if other.cls == cls:
                continue
            ox, oy = pos[other.cls]
            vx, vy = ox - x, oy - y
            dist = (vx * vx + vy * vy) ** 0.5
            if dist < CROWD_CM and (vx * dx + vy * dy) > 0.5 * dist:
                crowd += 1
        scored.append((crowd, rank, opt))
    return sorted(scored)[0][2]


def _arrows(fig: Figure) -> "List[Arrow]":
    """The drawn arrows: the figure's edges grouped by endpoint pair, so the two
    letters that agree on a target share one arrow labeled ``a,b`` rather than
    stacking two. Canonical order: by source node, then by least letter."""
    rank = {nd.cls: i for i, nd in enumerate(fig.nodes)}
    grouped: Dict[Tuple[int, int], List[int]] = {}
    marks: Dict[Tuple[int, int], Tuple[bool, bool]] = {}
    for e in fig.edges:
        pair = (e.src, e.dst)
        grouped.setdefault(pair, []).append(e.letter_index)
        tree, cyc = marks.get(pair, (False, False))
        marks[pair] = (tree or e.is_tree, cyc or e.is_cycle)

    out: List[Arrow] = []
    for (src, dst), letters in grouped.items():
        tree, cyc = marks[(src, dst)]
        out.append(Arrow(
            src=src, dst=dst, letters=tuple(sorted(letters)),
            label=",".join(fig.naming.names[i] for i in sorted(letters)),
            is_tree=tree, is_cycle=cyc, is_loop=(src == dst),
            # anti-parallel pairs both bend left: that is what splits them into
            # the usual two arcs, and it is where the doubled swaps show up.
            bend=((dst, src) in grouped and src != dst)))
    out.sort(key=lambda ar: (rank[ar.src], ar.letters[0]))
    return out


@dataclass(frozen=True)
class Arrow:
    """One drawn arrow: an endpoint pair and the letters that share it."""

    src: int
    dst: int
    letters: Tuple[int, ...]
    label: str
    is_tree: bool
    is_cycle: bool
    is_loop: bool
    bend: bool


def tikz_of(fig: Figure, pos: Placement, provenance: str,
            pairs: bool = True) -> str:
    """The standalone `.tex` of ``fig`` placed at ``pos``; ``provenance`` is the
    command that produced it, recorded as the first line. ``pairs`` adds P as a
    caption node under the drawing — the object is ``<A, P>`` and only ``A`` has a
    shape, so P is typeset, not drawn."""
    out: List[str] = [
        f"% {provenance}",
        "% Generated by sosl.sos.viz. Every visual choice is in the \\tikzset below:",
        "% edit a style to restyle, edit a coordinate to move a node.",
        r"\documentclass[tikz,border=4pt]{standalone}",
        r"\usepackage{amssymb}",   # \rightarrowtail, for an injective lambda
        r"\usetikzlibrary{arrows.meta,shapes.misc}",
        r"\begin{document}",
        r"\begin{tikzpicture}[",
        r"  class/.style     = {draw, thin, rounded corners=2pt, inner sep=3pt,",
        r"                      minimum width=10mm, minimum height=7mm},",
        r"  root/.style      = {},          % the root needs no ink: the init stub says it",
        r"  init/.style      = {semithick, -{Stealth[length=4pt,width=3pt]}},",
    ]
    out += [
        r"  arrow/.style     = {thin, -{Stealth[length=4pt,width=3pt]}},",
        r"  lbl/.style       = {font=\small, inner sep=1.5pt, fill=white},",
        r"  pairs/.style     = {anchor=north, font=\small},",
        r"]",
        "",
    ]
    for nd in fig.nodes:
        style = "class" + (",root" if nd.is_root else "")
        x, y = pos[nd.cls]
        out.append(f"  \\node[{style}] ({nd.ident}) at ({x:.1f},{y:.1f}) "
                   f"{{${_tex_class(fig, nd.cls)}$}};")

    root = next(nd for nd in fig.nodes if nd.is_root)
    rx, ry = pos[root.cls]
    # The stub comes from wherever the graph is not: from above when the root
    # sits on top of everything (a top-down layout), from the left otherwise.
    top = all(pos[nd.cls][1] < ry for nd in fig.nodes if not nd.is_root)
    sx, sy = (rx, ry + INIT_STUB_CM) if top else (rx - INIT_STUB_CM, ry)
    out += ["", "  % the root is the adjoined identity: a source, marked like an "
                "initial state",
            f"  \\draw[init] ({sx:.1f},{sy:.1f}) -- ({root.ident});", ""]

    for ar in _arrows(fig):
        if ar.is_loop:
            via = f"[{_loop_dir(fig, pos, ar.src)}]"
        else:
            via = f"[bend left={BEND_ANGLE}]" if ar.bend else ""
        src, dst = fig.node_of(ar.src).ident, fig.node_of(ar.dst).ident
        out.append(f"  \\draw[arrow] ({src}) to{via} "
                   f"node[lbl] {{${_tex_arrow_label(fig, ar.letters)}$}} ({dst});")

    if pairs:
        xs = [p[0] for p in pos.values()]
        low = min(p[1] for p in pos.values()) - PAIRS_DROP_CM
        mid = (min(xs) + max(xs)) / 2.0
        out += ["", f"  \\node[pairs] at ({mid:.1f},{low:.1f}) "
                    f"{{{_tex_lambda(fig)}}};",
                f"  \\node[pairs] at ({mid:.1f},{low - CAPTION_GAP_CM:.1f}) "
                f"{{{_tex_pairs(fig)}}};"]

    out += [r"\end{tikzpicture}", r"\end{document}", ""]
    return "\n".join(out)
