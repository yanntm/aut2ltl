"""FIG-3 — the DG formula: substitution tree vs memoized DAG (paper §2.3).

    python3 -m tests.sos2ltl.figs.fig3 <file.sos> [out.tex]

Prints the shape of the DG induction on one `.sos` invariant — the recursion's
per-depth tallies, the formula arena, its flat unfolding — and, with an output
path, writes the TikZ source of the two-panel figure. Both panels draw the
*formula*, as an operator over slots (`formulaview`): right, the hash-consed
arena, where a subterm used twice is one node with two in-arcs; left, the same
slice expanded as a substituting recursion would write it, one copy per
occurrence.

The arena cannot be drawn whole, and on `GF(aa)` its top is wide rather than
deep — a seven-way disjunction of conjunctions of nine to nineteen conjuncts,
94 arcs onto 36 distinct children. The figure draws the *pattern*, under a
width discipline that spends its arcs on sharing and states every elision in
place:

* **`∧` / `∨` are associative-commutative**, so their arcs carry no slot
  label — position in an `∧` means nothing — and the node carries an arity
  badge (`⋀ ·12`) instead. Only `X` / `U` / `XU` arcs name their slots.
* **The root's `KEEP` cheapest disjuncts are drawn** (fewest slots first);
  the rest are one `⋯ n more` node, their width already stated by the root's
  own arity badge.
* **Arcs are drawn for sharing.** Under a drawn node, every child that two or
  more of the root's disjuncts reference gets an arc to a handle `ψᵢ` — one
  box per distinct subtree, reused wherever referenced. One unshared child per
  node is drawn as a representative; the rest are the node's `+k private`
  line.
* **Every handle carries its in-degree** (`ψ₃ ×5`: five of the seven disjuncts
  reference it), so the sharing the cut did not draw is still counted.

The handles are exactly the fresh propositions of the paper's §6 definitional
rendering; each carries an arena/flat size badge, which is where the explosion
actually lives.

Sizes come from the tested primitives (`Ast.tree_size`, `len(Ast)`); the
recursion tallies from `dgtrace`. Only the coordinates below are the figure's
own.

Set `FIGS_TRACE` (or `TRANSLATOR_TRACE_ON`) for the per-handle dump.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Sequence, Set

# `dgtrace` first: importing `aut2ltl.sos2ltl` puts the sibling `sosl` subtree
# on sys.path, so the `sosl` import below resolves.
from tests.sos2ltl.figs import dgtrace, formulaview as fv, tikz
from tests.sos2ltl.figs.machine import letter_txt
from aut2ltl.sos2ltl.dg.formulas import Ast
from sosl.sos import load_invariant

_TRACE = "FIGS_TRACE" in os.environ or "TRANSLATOR_TRACE_ON" in os.environ

KEEP = 3
"""How many of the root's disjuncts are drawn; the rest are elided."""

XS = (-4.2, 0.0, 4.2)
"""Where the drawn disjuncts sit on the DAG panel."""


# ------------------------------------------------------------------ #
# The cut: which nodes are drawn, which collapse into a handle.
# ------------------------------------------------------------------ #
@dataclass
class Cut:
    """The drawn slice of the arena.

    `kept` are the root's drawn disjuncts, in the root's own slot order;
    `drawn[p]` are the children of `p` that earn an arc — every shared one,
    plus one unshared representative — and `private[p]` counts the children
    that do not. `uses[c]` is `c`'s in-degree over *all* the root's disjuncts,
    drawn or not: the sharing the arcs cannot show. `handles` lists the drawn
    children in first-encounter order: the boxes `ψ₁ … ψₙ`."""

    root: int
    kept: List[int]
    elided: int                       # root disjuncts not drawn
    drawn: Dict[int, List[int]]       # parent -> its drawn children
    private: Dict[int, int]           # parent -> count of elided children
    uses: Dict[int, int]              # child -> in-degree over all disjuncts
    handles: List[int]

    def psi(self, h: int) -> str:
        return rf"\psi_{{{self.handles.index(h) + 1}}}"

    @property
    def arcs(self) -> int:
        return sum(len(v) for v in self.drawn.values())


def _in_degree(view: Dict[int, fv.Head], parents: Sequence[int]
               ) -> Dict[int, int]:
    """How many of `parents` reference each child (a parent using a child in
    two slots counts once — it is one reference to one node)."""
    uses: Dict[int, int] = {}
    for p in parents:
        for c in {c for _s, c in view[p].slots}:
            uses[c] = uses.get(c, 0) + 1
    return uses


def cut(view: Dict[int, fv.Head], root: int, keep: int) -> Cut:
    """Cheapest-first at the root; below it, an arc to every child two drawn
    parents share, plus one unshared representative per parent.

    The arcs are decided among the *drawn* parents — an arc the figure cannot
    draw would say nothing — while a handle's badge counts its references
    among *all* the root's disjuncts, which is the sharing the cut hides."""
    tops = [c for _s, c in view[root].slots]
    kept = sorted(tops, key=lambda c: (len(view[c].slots), c))[:keep]
    kept.sort(key=tops.index)

    uses = _in_degree(view, tops)
    here = _in_degree(view, kept)

    drawn: Dict[int, List[int]] = {}
    private: Dict[int, int] = {}
    handles: List[int] = []
    for p in kept:
        keepers: List[int] = []
        skipped = 0
        rep = False                 # one unshared representative per node
        for c in dict.fromkeys(c for _s, c in view[p].slots):
            if here[c] > 1:
                keepers.append(c)
            elif not rep:
                rep = True
                keepers.append(c)
            else:
                skipped += 1
        drawn[p] = keepers
        private[p] = skipped
        for c in keepers:
            if c not in handles:
                handles.append(c)
    return Cut(root, kept, len(tops) - len(kept), drawn, private, uses,
               handles)


# ------------------------------------------------------------------ #
# Labels.
# ------------------------------------------------------------------ #
def _inline(tex: str) -> str:
    """A head shrunk to one line of a handle box: the display-size `⋁`/`⋀` of
    a wide node overprints the line above it."""
    return tex.replace(r"\bigvee", r"\lor").replace(r"\bigwedge", r"\land")


def _arity(head: fv.Head) -> str:
    """An AC node states its width instead of numbering its slots."""
    return rf"\;{{\cdot}}{len(head.slots)}" if head.ac and len(head.slots) > 2 \
        else ""


def _op(view: Dict[int, fv.Head], cut_: Cut, p: int) -> str:
    """A drawn operator node: its head, its arity if it is AC, and how many of
    its children the cut dropped — an elision the node states itself."""
    h = view[p]
    lost = cut_.private[p]
    tail = (rf"\\[-2pt]{{\tiny\itshape $+{lost}$ private}}" if lost else "")
    return rf"${h.tex}{_arity(h)}${tail}"


def _slot_label(view: Dict[int, fv.Head], p: int, c: int) -> str:
    """The slots of `p` that `c` fills. An AC parent has none to give: the
    position of a conjunct in a conjunction carries no information."""
    if view[p].ac:
        return ""
    return "node[slot] {" + ",".join(f"${s}$" for s, ch in view[p].slots
                                     if ch == c) + "}"


def _handle(ast: Ast, view: Dict[int, fv.Head], cut_: Cut, h: int,
            letters: Sequence[str]) -> str:
    """A cut subtree's box: its name and in-degree, the operator it heads — so
    the node can still be read — and its arena/flat sizes."""
    dag = len(fv.reachable(ast, h, letters))
    return (rf"${cut_.psi(h)}$ {{\scriptsize$\times${cut_.uses[h]}}}"
            rf"\\[-2pt]{{\tiny ${_inline(view[h].tex)}{_arity(view[h])}$}}"
            rf"\\[-1pt]{{\tiny\textcolor{{order}}{{{dag} / "
            rf"{tikz.num(ast.tree_size(h))}}}}}")


# ------------------------------------------------------------------ #
# The two panels.
# ------------------------------------------------------------------ #
def _dag_panel(ast: Ast, view: Dict[int, fv.Head], cut_: Cut,
               letters: Sequence[str]) -> List[str]:
    out: List[str] = [r"\begin{scope}[local bounding box=dagpanel]"]
    root = view[cut_.root]
    out.append(rf"  \node[opnode] (droot) at (0,0) "
               rf"{{${root.tex}{_arity(root)}$}};")

    for p, x in zip(cut_.kept, XS):
        out.append(rf"  \node[opnode] (dp{p}) at ({x:.2f},-2.6) "
                   rf"{{{_op(view, cut_, p)}}};")
        out.append(rf"  \draw[dagedge] (droot) -- "
                   rf"{_slot_label(view, cut_.root, p)} (dp{p});")
    out.append(rf"  \node[elide] (delide) at (7.8,-2.6) "
               rf"{{$\cdots$ {cut_.elided} more\\disjuncts}};")
    out.append(r"  \draw[refedge] (droot) -- (delide);")

    step = 1.8
    x0 = -(len(cut_.handles) - 1) * step / 2.0
    for k, h in enumerate(cut_.handles):
        out.append(rf"  \node[ophandle] (dh{h}) at ({x0 + k * step:.2f},-6.2) "
                   rf"{{{_handle(ast, view, cut_, h, letters)}}};")

    seen: Set[int] = set()
    for p in cut_.kept:
        for h in cut_.drawn[p]:
            # The first arc into a handle builds it; every later one is the
            # reference a substituting recursion would have copied.
            style = "dagedge" if h not in seen else "refedge"
            seen.add(h)
            out.append(rf"  \draw[{style}] (dp{p}) -- "
                       rf"{_slot_label(view, p, h)} (dh{h});")
    out.append(r"\end{scope}")
    return out


def _tree_panel(ast: Ast, view: Dict[int, fv.Head], cut_: Cut,
                letters: Sequence[str]) -> List[str]:
    """The same slice, one node per occurrence: every reference of the DAG
    panel becomes a copy, at the depth the DAG referenced it."""
    out: List[str] = [r"\begin{scope}[local bounding box=treepanel]"]
    root = view[cut_.root]
    step = 1.8
    width = (cut_.arcs - 1) * step
    out.append(rf"  \node[opnode] (troot) at (0,0) "
               rf"{{${root.tex}{_arity(root)}$}};")

    x = -width / 2.0
    for p in cut_.kept:
        kids = cut_.drawn[p]
        px = x + (len(kids) - 1) * step / 2.0
        out.append(rf"  \node[opnode] (tp{p}) at ({px:.2f},-2.6) "
                   rf"{{{_op(view, cut_, p)}}};")
        out.append(rf"  \draw[dagedge] (troot) -- "
                   rf"{_slot_label(view, cut_.root, p)} (tp{p});")
        for h in kids:
            out.append(rf"  \node[ophandle] (t{p}h{h}) at ({x:.2f},-6.2) "
                       rf"{{{_handle(ast, view, cut_, h, letters)}}};")
            out.append(rf"  \draw[dagedge] (tp{p}) -- "
                       rf"{_slot_label(view, p, h)} (t{p}h{h});")
            x += step
    out.append(rf"  \node[elide] (telide) at ({width / 2 + 1.8:.2f},-2.6) "
               rf"{{$\cdots$ {cut_.elided} more\\disjuncts}};")
    out.append(r"  \draw[refedge] (troot) -- (telide);")
    out.append(r"\end{scope}")
    return out


# ------------------------------------------------------------------ #
def render(ast: Ast, view: Dict[int, fv.Head], cut_: Cut,
           letters: Sequence[str], flat: int) -> str:
    body: List[str] = []
    body += _tree_panel(ast, view, cut_, letters)
    body.append(r"\begin{scope}[xshift=32cm]")
    body += _dag_panel(ast, view, cut_, letters)
    body.append(r"\end{scope}")

    body.append(
        r"\node[panelcap] at ($(treepanel.south)+(0,-1.0)$) "
        rf"{{\textbf{{substitution: a copy per occurrence}}\\[2pt]"
        rf"{cut_.arcs} copies of {len(cut_.handles)} subterms, "
        rf"in this slice alone\\"
        rf"flat formula: {tikz.num(flat)} nodes}};")
    body.append(
        r"\node[panelcap] at ($(dagpanel.south)+(0,-1.0)$) "
        rf"{{\textbf{{hash-consing: a reference per occurrence}}\\[2pt]"
        rf"{len(cut_.handles)} boxes, {cut_.arcs} in-arcs\\"
        rf"shared arena: {tikz.num(len(ast))} nodes}};")
    return tikz.standalone(body)


def main(argv: List[str]) -> int:
    path = argv[0]
    with open(path) as f:
        inv = load_invariant(f.read())

    sy, ast, phi = dgtrace.trace(inv)
    levels = sy.levels()
    flat = ast.tree_size(phi)
    letters = [letter_txt(inv, a) for a in range(inv.alphabet.size)]
    view = fv.reachable(ast, phi, letters)
    cut_ = cut(view, phi, KEEP)
    nodes = 1 + len(cut_.kept) + len(cut_.handles)

    print(f"{path}: {len(sy.info)} recursion nodes, arena {len(ast)}, "
          f"flat tree {flat}")
    print(f"  substitution unfolding: {sum(levels)} nodes, "
          f"per depth {levels}")
    print(f"  call sites: {len(sy.edges)} ({len(set(sy.edges))} distinct)")
    print(f"  formula view: {len(view)} nodes reachable from the root; "
          f"root {'AC' if view[phi].ac else 'ordered'}, "
          f"{len(view[phi].slots)} slots")
    print(f"  drawn: {len(cut_.kept)} disjuncts ({cut_.elided} elided), "
          f"{len(cut_.handles)} handles, {cut_.arcs} arcs, "
          f"{sum(cut_.private.values())} private children elided")
    print(f"  budget: DAG {nodes} nodes / {cut_.arcs} arcs, "
          f"tree {1 + len(cut_.kept) + cut_.arcs} nodes")

    if _TRACE:
        for k, h in enumerate(cut_.handles):
            print(f"[figs] psi{k + 1} = arena node {h}: {view[h].tex} "
                  f"uses={cut_.uses[h]} "
                  f"dag={len(fv.reachable(ast, h, letters))} "
                  f"flat={ast.tree_size(h)}", file=sys.stderr)

    if len(argv) > 1:
        with open(argv[1], "w") as out:
            out.write(render(ast, view, cut_, letters, flat))
        print(f"  wrote {argv[1]}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
