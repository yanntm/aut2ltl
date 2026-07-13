"""The TikZ backend: a placed `Figure` as a standalone `.tex` a human can edit.

The output is written to be *nudged*: every visual choice lives in one `\\tikzset`
block, each node is a named `\\node` at an explicit rounded coordinate, each arrow
is one `\\draw` between node names. Changing how the figure looks means editing one
style; changing where a node sits means editing one coordinate. Nothing is styled
inline and nothing is repeated.

The figure reads without a legend, and it draws only what the object *is*: the
whole multiplication table, one arrow per entry `M(s, c)`. Every arrow carries the
classes whose columns take it — that, not a dash pattern, is how they are told
apart — and the columns that agree on a target share one arrow (`[a],[b]`) instead
of stacking several. Derived facts get no ink of their own -- not a monochrome
cycle (a property of the drawn arrows, not an arrow of another kind), not an
idempotent (a property of the product, not a kind of class). The root, when the
figure keeps the identity, is marked the way an initial state is, with a short
incoming stub from nowhere, which is also what makes freshness visible: it is the
only arrow that enters it. An identity-eliding figure has no root and no stub.

Pure text: the placement is an input (see `layout.py`), not something computed
here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .layout import Placement
from .model import Figure, wrap

# Self-loop directions, in preference order, with the unit vector each points at.
LOOP_DIRS: Tuple[Tuple[str, Tuple[float, float]], ...] = (
    ("loop above", (0.0, 1.0)), ("loop below", (0.0, -1.0)),
    ("loop right", (1.0, 0.0)), ("loop left", (-1.0, 0.0)))
# A neighbour nearer than this (cm), in a direction's cone, crowds it out.
CROWD_CM = 2.6
# How far an anti-parallel pair of arrows bends apart (both bend left). Wide enough
# that the two labels, each sitting at its arc's midpoint, clear each other.
BEND_ANGLE = 22
# The label of an arrow that carries every column: all the (non-identity) classes.
ALL_CLASSES = r"\mathcal{C}"
# Two nodes count as sharing a row / a column when their y / x differ by less than
# this (cm) — coordinates are hand-rounded, so exact equality is too strict.
ALIGN_CM = 0.3
# A corner diagonal grazes a node when it passes within this of it (cm): the node's
# box plus a little. Only the diagonal is tested — see `_grazes`.
CLEAR_CM = 1.0
# How much steeper than the straight diagonal such an arrow leaves, in degrees.
DIAG_BEND = 20
# How far out a detour swings: the `looseness` of its bezier. Enough to clear the
# node it goes around and that node's own self-loop, not more — a wider arc buys no
# clearance and only steepens the dive back in. An anti-parallel pair of detours
# takes the two values, so the arcs do not lie on top of each other.
LOOSENESS = 1.3
LOOSENESS_FAR = 1.8
# How far under the lowest node the P caption sits (cm).
PAIRS_DROP_CM = 1.3
# Extra drop when a bottom node's self-loop hangs below it: the loop and its label
# reach further down than the node box, and the caption must clear them.
LOOP_HANG_CM = 1.4
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


def _tex_arrow_label(fig: Figure, cols: Tuple[int, ...]) -> str:
    """An arrow's label: the columns that take it, ``[a]`` or ``[a],[b·a]`` when
    several classes multiply the source to the same target. Node order, wrapped to
    `WRAP_CHARS` — the label of a full table can list every class, and a long one
    lies across whatever the arrow passes. The comma stays at the end of the line
    it breaks, so the list reads on unambiguously.

    An arrow carrying EVERY column collapses to `C`, the set of all non-identity
    classes: the longest label there is, and the least informative as a list — a
    self-loop under `C` is exactly an absorbing class, seen at a glance instead of
    counted out. Only in an eliding figure. With the identity drawn, `C` would mean
    one set on a self-loop (`[eps]` fixes every class, so every loop carries it) and
    another on an arrow that leaves its source (which can never carry it); a figure
    whose job is to be exact about the definitions does not get to be suggestive."""
    if fig.elided and set(cols) == set(fig.columns()):
        return f"${ALL_CLASSES}$"
    plain = [f"[{fig.label_of(c)}]" for c in cols]
    tex = [_tex_class(fig, c) for c in cols]
    lines = wrap(plain)
    out: List[str] = []
    for n, line in enumerate(lines):
        body = ",".join(tex[i] for i in line)
        out.append(f"${body},$" if n < len(lines) - 1 else f"${body}$")
    return r"\\".join(out)


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


def _blocked(fig: Figure, pos: Placement, src: int, dst: int) -> bool:
    """Is a node sitting ON the straight line between ``src`` and ``dst``? Only the
    aligned case counts — the two share a row or a column (to `ALIGN_CM`) and a third
    node of that row/column lies strictly between them. That is a node the arrow
    would run *through*; an arrow merely passing near one is left alone."""
    (px, py), (qx, qy) = pos[src], pos[dst]
    same_row, same_col = abs(py - qy) < ALIGN_CM, abs(px - qx) < ALIGN_CM
    if not (same_row or same_col):
        return False
    for nd in fig.nodes:
        if nd.cls in (src, dst):
            continue
        x, y = pos[nd.cls]
        if same_row and abs(y - py) < ALIGN_CM and min(px, qx) < x < max(px, qx):
            return True
        if same_col and abs(x - px) < ALIGN_CM and min(py, qy) < y < max(py, qy):
            return True
    return False


def _grazes(fig: Figure, pos: Placement, src: int, dst: int) -> bool:
    """Does the straight line from ``src`` to ``dst`` pass within `CLEAR_CM` of a
    third node, that node lying between the endpoints? Distance to the segment, not
    to the line: a node behind either end is not in the way."""
    (px, py), (qx, qy) = pos[src], pos[dst]
    ux, uy = qx - px, qy - py
    span = (ux * ux + uy * uy) ** 0.5
    if span == 0:
        return False
    for nd in fig.nodes:
        if nd.cls in (src, dst):
            continue
        vx, vy = pos[nd.cls][0] - px, pos[nd.cls][1] - py
        along = (vx * ux + vy * uy) / span
        if 0.0 < along < span and abs((ux * vy - uy * vx) / span) < CLEAR_CM:
            return True
    return False


def _diagonal(fig: Figure, pos: Placement, src: int, dst: int) -> Optional[str]:
    """The `bend` option of a CORNER DIAGONAL that would otherwise run over a node:
    an arrow from the figure's top row to its bottom row (or back), in another
    column, whose straight line grazes something on the way — in practice the node in
    the middle, which such a diagonal passes through rather than near.

    It leaves *steeper* than the diagonal, rotated `DIAG_BEND` towards the vertical,
    and so bows past the obstacle instead of across it. Rotating towards the vertical
    means bending right when the arrow descends to the right (or climbs to the left),
    left otherwise — that is the sign of `dx·dy`. An arrow from a row to the NEXT one
    is not a corner diagonal and is left alone: it has nothing to clear."""
    ys = [p[1] for p in pos.values()]
    top, bot = max(ys), min(ys)
    (px, py), (qx, qy) = pos[src], pos[dst]
    spans = ((abs(py - top) < ALIGN_CM and abs(qy - bot) < ALIGN_CM)
             or (abs(py - bot) < ALIGN_CM and abs(qy - top) < ALIGN_CM))
    if not spans or abs(px - qx) < ALIGN_CM:
        return None
    if not _grazes(fig, pos, src, dst):
        return None
    side = "right" if (qx - px) * (qy - py) < 0 else "left"
    return f"bend {side}={DIAG_BEND}"


def _detour(fig: Figure, pos: Placement, src: int, dst: int, far: bool) -> str:
    """The `to[...]` option of an arrow that must go around a node standing between
    its endpoints: a bezier that leaves the source *outward* (away from the middle of
    the figure), runs parallel to the row or column it is skipping, and dives back in
    at the target. Leaving and arriving on the same outward heading is what keeps the
    two turns gentle; `looseness` is how far out the arc swings, and an anti-parallel
    pair takes the two values so its arcs do not coincide."""
    cx = sum(p[0] for p in pos.values()) / len(pos)
    cy = sum(p[1] for p in pos.values()) / len(pos)
    (px, py), (qx, qy) = pos[src], pos[dst]
    if abs(py - qy) < ALIGN_CM:                       # a row: swing above or below
        angle = 90 if py >= cy else -90
    else:                                             # a column: swing left or right
        angle = 180 if px <= cx else 0
    loose = LOOSENESS_FAR if far else LOOSENESS
    return f"out={angle},in={angle},looseness={loose}"


def _arrows(fig: Figure) -> "List[Arrow]":
    """The drawn arrows: the figure's edges grouped by endpoint pair, so the columns
    that agree on a target share one arrow labeled ``[a],[b]`` rather than stacking
    one arrow each. Canonical order: by source node, then by least column."""
    rank = {nd.cls: i for i, nd in enumerate(fig.nodes)}
    grouped: Dict[Tuple[int, int], List[int]] = {}
    marks: Dict[Tuple[int, int], Tuple[bool, bool]] = {}
    for e in fig.edges:
        pair = (e.src, e.dst)
        grouped.setdefault(pair, []).append(e.col)
        tree, cyc = marks.get(pair, (False, False))
        marks[pair] = (tree or e.is_tree, cyc or e.is_cycle)

    out: List[Arrow] = []
    for (src, dst), cols in grouped.items():
        tree, cyc = marks[(src, dst)]
        ordered = tuple(sorted(cols, key=lambda c: rank[c]))
        out.append(Arrow(
            src=src, dst=dst, cols=ordered,
            label=",".join(fig.label_of(c) for c in ordered),
            is_tree=tree, is_cycle=cyc, is_loop=(src == dst),
            # anti-parallel pairs both bend left: that is what splits them into
            # the usual two arcs, and it is where the doubled swaps show up.
            bend=((dst, src) in grouped and src != dst)))
    out.sort(key=lambda ar: (rank[ar.src], rank[ar.cols[0]]))
    return out


@dataclass(frozen=True)
class Arrow:
    """One drawn arrow: an endpoint pair and the columns of ``M`` that share it."""

    src: int
    dst: int
    cols: Tuple[int, ...]
    label: str
    is_tree: bool
    is_cycle: bool
    is_loop: bool
    bend: bool


def tikz_of(fig: Figure, pos: Placement, provenance: str, pairs: bool = True,
            loops: Optional[Dict[int, str]] = None) -> str:
    """The standalone `.tex` of ``fig`` placed at ``pos``; ``provenance`` is the
    command that produced it, recorded as the first line. ``pairs`` adds P as a
    caption node under the drawing — the object is ``<A, P>`` and only ``A`` has a
    shape, so P is typeset, not drawn.

    ``loops`` overrides the self-loop direction of the given classes. A loop
    direction is placement, exactly like a coordinate: `_loop_dir` only guesses one,
    and a caller that already knows better (a human who placed the figure) says so
    here rather than being overruled."""
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
        r"  lbl/.style       = {font=\small, inner sep=1.5pt, fill=white,",
        r"                      align=center},   % a long class list wraps (see WRAP_CHARS)",
        r"  pairs/.style     = {anchor=north, font=\small},",
        r"]",
        "",
    ]
    for nd in fig.nodes:
        style = "class" + (",root" if nd.is_root else "")
        x, y = pos[nd.cls]
        out.append(f"  \\node[{style}] ({nd.ident}) at ({x:.1f},{y:.1f}) "
                   f"{{${_tex_class(fig, nd.cls)}$}};")

    root = fig.root()             # None when the identity is elided: no stub then
    if root is not None:
        rx, ry = pos[root.cls]
        # The stub comes from wherever the graph is not: from above when the root
        # sits on top of everything (a top-down layout), from the left otherwise.
        top = all(pos[nd.cls][1] < ry for nd in fig.nodes if not nd.is_root)
        sx, sy = (rx, ry + INIT_STUB_CM) if top else (rx - INIT_STUB_CM, ry)
        out += ["", "  % the root is the adjoined identity: a source, marked like an "
                    "initial state",
                f"  \\draw[init] ({sx:.1f},{sy:.1f}) -- ({root.ident});"]
    out.append("")

    loops = loops or {}
    rank = {nd.cls: i for i, nd in enumerate(fig.nodes)}
    for ar in _arrows(fig):
        if ar.is_loop:
            via = f"[{loops.get(ar.src) or _loop_dir(fig, pos, ar.src)}]"
        elif _blocked(fig, pos, ar.src, ar.dst):
            # a node stands between the endpoints: go around it, the back arrow of an
            # anti-parallel pair swinging wider so the two arcs stay apart
            far = ar.bend and rank[ar.src] > rank[ar.dst]
            via = f"[{_detour(fig, pos, ar.src, ar.dst, far)}]"
        elif (diag := _diagonal(fig, pos, ar.src, ar.dst)) is not None:
            via = f"[{diag}]"            # a corner diagonal that would cross a node
        elif ar.bend:                    # anti-parallel: both bend left, splitting
            via = f"[bend left={BEND_ANGLE}]"
        else:
            via = ""
        src, dst = fig.node_of(ar.src).ident, fig.node_of(ar.dst).ident
        out.append(f"  \\draw[arrow] ({src}) to{via} "
                   f"node[lbl] {{{_tex_arrow_label(fig, ar.cols)}}} ({dst});")

    if pairs:
        xs = [p[0] for p in pos.values()]
        floor = min(p[1] for p in pos.values())
        # a self-loop hanging below a bottom node, with its label, reaches further
        # down than the node does: the caption starts under whatever is lowest
        hangs = any(ar.is_loop and abs(pos[ar.src][1] - floor) < 0.1
                    and "below" in (loops.get(ar.src) or _loop_dir(fig, pos, ar.src))
                    for ar in _arrows(fig))
        low = floor - PAIRS_DROP_CM - (LOOP_HANG_CM if hangs else 0.0)
        mid = (min(xs) + max(xs)) / 2.0
        out += ["", f"  \\node[pairs] at ({mid:.1f},{low:.1f}) "
                    f"{{{_tex_lambda(fig)}}};",
                f"  \\node[pairs] at ({mid:.1f},{low - CAPTION_GAP_CM:.1f}) "
                f"{{{_tex_pairs(fig)}}};"]

    out += [r"\end{tikzpicture}", r"\end{document}", ""]
    return "\n".join(out)
