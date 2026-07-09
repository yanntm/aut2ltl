"""FIG-3 — the DG recursion: substitution tree vs memoized DAG (paper §2.3).

    python3 -m tests.sos2ltl.figs.fig3 <file.sos> [out.tex]

Prints the recursion shape of the DG induction on one `.sos` invariant — the
per-depth tallies of the substituting unfolding, the memoized node count, the
arena size, the flat formula size — and, with an output path, writes the TikZ
source of the two-panel figure: left, the recursion unfolded so each call site
gets its own copy; right, the same recursion memoized, every node built once
and *referenced* wherever the unfolding would have copied it.

Sizes come from the tested primitives (`Ast.tree_size`, `len(Ast)`); this
probe adds only the recursion *shape*, which no existing tool reports.

Set `FIGS_TRACE` (or `TRANSLATOR_TRACE_ON`) for the per-node dump.
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List, Sequence, Tuple

# `dgtrace` first: importing `aut2ltl.sos2ltl` puts the sibling `sosl` subtree
# on sys.path, so the `sosl` import below resolves.
from tests.sos2ltl.figs import dgtrace, tikz
from sosl.sos import load_invariant

# On when either FIGS_TRACE or the global TRANSLATOR_TRACE_ON is set (presence;
# value ignored). Every message is built inside `if _TRACE:`, so nothing is
# computed when off.
_TRACE = "FIGS_TRACE" in os.environ or "TRANSLATOR_TRACE_ON" in os.environ

MAX_DRAWN = 80
"""Above this many tree nodes the left panel is cut and the rest elided."""


# ------------------------------------------------------------------ #
# The tree panel: the unfolding, one node per call site.
# ------------------------------------------------------------------ #
def _tree_rows(sy: dgtrace.TracingSynth, cut: int
               ) -> List[List[Tuple[int, int]]]:
    """Levels `0..cut` as `(node id, parent slot)` rows — one entry per tree
    node, so a node reached by two call sites appears twice."""
    rows: List[List[Tuple[int, int]]] = [[(0, -1)]]
    for _ in range(cut):
        nxt: List[Tuple[int, int]] = []
        for slot, (n, _p) in enumerate(rows[-1]):
            for c in sy.children(n):
                nxt.append((c, slot))
        if not nxt:
            break
        rows.append(nxt)
    return rows


def _tree_panel(sy: dgtrace.TracingSynth, levels: Sequence[int],
                cut: int, width: float) -> List[str]:
    rows = _tree_rows(sy, cut)
    out: List[str] = [r"\begin{scope}[local bounding box=treepanel]"]
    dy = -2.0
    for d, row in enumerate(rows):
        n_row = len(row)
        for slot, (n, parent) in enumerate(row):
            x = ((slot - (n_row - 1) / 2.0) * (width / max(n_row, 1))
                 if n_row > 1 else 0.0)
            y = d * dy
            style = "dgleaf" if sy.info[n].leaf else "dgnode"
            out.append(f"  \\node[{style}] (t{d}-{slot}) at "
                       f"({x:.2f},{y:.2f}) {{{n}}};")
            if parent >= 0:
                out.append(f"  \\draw[treeedge] (t{d-1}-{parent}) -- "
                           f"(t{d}-{slot});")
    drawn = sum(len(r) for r in rows)
    below = sum(levels) - drawn
    if below > 0:
        y = len(rows) * dy
        out.append(rf"  \node[elide] at (0,{y:.2f}) {{$\vdots$\ \ "
                   rf"{tikz.num(below)} more}};")
    out.append(r"\end{scope}")
    return out


# ------------------------------------------------------------------ #
# The DAG panel: every recursion node once, duplicates become references.
# ------------------------------------------------------------------ #
def _dag_depths(sy: dgtrace.TracingSynth) -> Dict[int, int]:
    """Longest-path depth of each node from the root — the drawing row."""
    depth: Dict[int, int] = {0: 0}
    changed = True
    while changed:
        changed = False
        for p, c in sy.edges:
            d = depth.get(p, 0) + 1
            if d > depth.get(c, -1):
                depth[c] = d
                changed = True
    return depth


def _subtree_sizes(sy: dgtrace.TracingSynth) -> Dict[int, int]:
    """`sub[n]` = tree nodes the substituting recursion builds for call `n`."""
    sub: Dict[int, int] = {}

    def go(n: int) -> int:
        got = sub.get(n)
        if got is None:
            got = 1 + sum(go(c) for c in sy.children(n))
            sub[n] = got
        return got

    for n in range(len(sy.info)):
        go(n)
    return sub


def _dag_panel(sy: dgtrace.TracingSynth) -> List[str]:
    depth = _dag_depths(sy)
    rows: Dict[int, List[int]] = {}
    for n in range(len(sy.info)):
        rows.setdefault(depth.get(n, 0), []).append(n)

    out: List[str] = [r"\begin{scope}[local bounding box=dagpanel]"]
    dy = -2.0
    for d in sorted(rows):
        row = rows[d]
        for slot, n in enumerate(row):
            x = (slot - (len(row) - 1) / 2.0) * 1.55
            y = d * dy
            style = "dgleaf" if sy.info[n].leaf else "dgnode"
            out.append(f"  \\node[{style}] (d{n}) at ({x:.2f},{y:.2f}) "
                       f"{{{n}}};")

    mult: Dict[Tuple[int, int], int] = {}
    for e in sy.edges:
        mult[e] = mult.get(e, 0) + 1
    for (p, c), m in sorted(mult.items()):
        straight = depth.get(c, 0) == depth.get(p, 0) + 1
        style = "dagedge" if straight else "refedge"
        bend = "" if straight else "[bend right=20]"
        lbl = rf" node[emult] {{{m}$\times$}}" if m > 1 else ""
        out.append(rf"  \draw[{style}] (d{p}) to{bend}{lbl} (d{c});")
    out.append(r"\end{scope}")
    return out


# ------------------------------------------------------------------ #
def render(sy: dgtrace.TracingSynth, levels: Sequence[int], arena: int,
           flat: int) -> str:
    total = sum(levels)
    cut = len(levels) - 1
    while cut > 1 and sum(levels[:cut + 1]) > MAX_DRAWN:
        cut -= 1

    body: List[str] = []
    body += _tree_panel(sy, levels, cut, width=22.0)
    body.append(r"\begin{scope}[xshift=18cm]")
    body += _dag_panel(sy)
    body.append(r"\end{scope}")

    body.append(
        r"\node[panelcap] at ($(treepanel.south)+(0,-1.1)$) "
        rf"{{\textbf{{substitution: a copy per occurrence}}\\[2pt]"
        rf"{tikz.num(total)} recursion-tree nodes over "
        rf"{len(levels)} depths\\"
        rf"flat formula: {tikz.num(flat)} nodes}};")
    body.append(
        r"\node[panelcap] at ($(dagpanel.south)+(0,-1.1)$) "
        rf"{{\textbf{{memoization: a reference per occurrence}}\\[2pt]"
        rf"{len(sy.info)} recursion nodes\\"
        rf"shared arena: {tikz.num(arena)} nodes}};")
    return tikz.standalone(body)


def main(argv: List[str]) -> int:
    path = argv[0]
    with open(path) as f:
        inv = load_invariant(f.read())

    sy, ast, phi = dgtrace.trace(inv)
    levels = sy.levels()
    flat = ast.tree_size(phi)

    print(f"{path}: {len(sy.info)} recursion nodes, arena {len(ast)}, "
          f"flat tree {flat}")
    print(f"  substitution unfolding: {sum(levels)} nodes, "
          f"per depth {levels}")
    print(f"  call sites: {len(sy.edges)} ({len(set(sy.edges))} distinct)")

    if _TRACE:
        depth = _dag_depths(sy)
        sub = _subtree_sizes(sy)
        for i in sy.info:
            print(f"[figs] node {i.idx}: |S|={i.n_letters} |M|={i.n_monoid} "
                  f"target={i.target} {'base' if i.leaf else 'pivot'} "
                  f"depth={depth.get(i.idx, 0)} subtree={sub[i.idx]} "
                  f"children={sy.children(i.idx)}", file=sys.stderr)

    if len(argv) > 1:
        with open(argv[1], "w") as out:
            out.write(render(sy, levels, len(ast), flat))
        print(f"  wrote {argv[1]}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
