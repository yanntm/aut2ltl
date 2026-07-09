"""FIG-2 — the label stack as a derivation (paper §5.2).

    python3 -m tests.sos2ltl.figs.fig2 <file.sos> [out.tex]

Replays the engine's own brick dump — the `SOS2LTL_TRACE` lines of
`aut2ltl.sos2ltl.engine` — and lays it out as a derivation: one block per
layer, in the order the R-order descent builds them (children first), each
line one brick the engine emitted, tagged with the rule that produced it.
Nothing here rebuilds a brick; the formulas are the engine's, simplification
off, transcribed from its trace.

Two presentation devices, both driven by the data:

* **Naming.** A brick that repeats a formula already introduced — a child
  layer's `Final(c)`, or the current layer's `step` / `leave(c)` — prints
  that name in place of the subterm. The substitution is structural (on the
  hash-consed formula, not on its text), so a name stands exactly where the
  engine shares a node; the panel is the label DAG, not its unfolding.
  Boolean subterms are never named: a bare literal reads better than a name.
* **Order.** Layers are drawn deepest-first, as the engine builds them.
  R-incomparable layers are ordered by their least class — placement, not
  semantics.

The rendering is the *plain* one (`Rendering(residual=False)`): the root's
exit fan is drawn as the fan. The engine's default rendering keys exit
children by residual, which on a prefix-independent language collapses that
fan to a single `X Final(·)` of the deepest layer — the label of the whole
language — and the derivation's last step would then show nothing.

With an output path the two-column TikZ panel is written: left, the R-order
descent as a miniature of the FIG-1 diamond with the layer under construction
lit and its children shaded; right, the bricks that layer contributes.
"""
from __future__ import annotations

import contextlib
import io
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from aut2ltl.sos2ltl import anchoring, engine
from aut2ltl.sos2ltl.cayley import Cayley, build
from sosl.sos import Invariant, load_invariant

from tests.sos2ltl.figs import tikz
from tests.sos2ltl.figs.machine import Pos

_TRACE = "FIGS_TRACE" in os.environ or "TRANSLATOR_TRACE_ON" in os.environ

_LINE = re.compile(
    r"^\[engine\] layer=(\d+) brick=(\S+)(?: class=(\d+))? formula=(.*)$")

# The mini-diamond's class coordinates (cm), a scaled-down FIG-1: transient
# root on top, the two mirrored moving layers side by side, frozen below.
MINI: Dict[int, Pos] = {0: (0.0, 0.0),
                        1: (-1.00, -0.90), 3: (-0.45, -0.90),
                        2: (0.45, -0.90), 4: (1.00, -0.90),
                        5: (0.0, -1.80)}

ROW = 0.60          # cm between two brick lines
GAP = 0.75          # cm between two layer blocks
COL_TEXT = 2.6      # cm: the brick column
COL_RULE = 13.2     # cm: the rule tag column


# ------------------------------------------------------------------ #
# The engine's dump, read back.
# ------------------------------------------------------------------ #
@dataclass(frozen=True)
class Brick:
    """One line of the engine's trace, its formula re-read by Spot."""

    layer: int
    brick: str
    cls: Optional[int]
    formula: "spot.formula"


def dump(inv: Invariant, rend: engine.Rendering) -> List[Brick]:
    """Transcribe `inv` with the trace on; the bricks, in emission order.

    The trace is the engine's published interface — one structured line per
    brick on stderr. Re-reading each formula with Spot's parser is a print
    round-trip, so a `Brick` carries what the engine built, not a copy of the
    engine's assembly."""
    import spot

    was, engine._TRACE = engine._TRACE, True
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            phi = engine.transcribe(inv, rend=rend)
    finally:
        engine._TRACE = was
    assert phi is not None, "engine declined: there is no label stack to draw"

    out: List[Brick] = []
    for line in err.getvalue().splitlines():
        m = _LINE.match(line)
        assert m, f"unparsed trace line: {line}"
        layer, brick, cls, f = m.groups()
        out.append(Brick(int(layer), brick, None if cls is None else int(cls),
                         spot.formula(f)))
    return out


# ------------------------------------------------------------------ #
# Names: the shared subterms, printed as the paper prints them.
# ------------------------------------------------------------------ #
class Names:
    """A structural formula → name map, applied outermost-first.

    A named formula is replaced wherever it occurs as a subterm, so the printed
    line shows a reference where the engine shares a node: the panel is the
    label DAG, not its unfolding. Names ride on fresh atomic propositions,
    swapped for their TeX at print time. The propositions are opaque
    lowercase-alphabetic tokens: a leading capital would re-parse as a
    temporal operator, and a trailing digit prints as a LaTeX subscript, which
    the swap would then miss."""

    def __init__(self) -> None:
        self._tex: Dict[str, str] = {}
        self._ap: Dict["spot.formula", "spot.formula"] = {}

    def add(self, f: "spot.formula", tex: str) -> None:
        """Name `f`, unless it is boolean: a literal reads better than a name,
        and its letters recur in every brick."""
        import spot
        if f.is_boolean():
            return
        tok = "nm" + "abcdefghijklmnopqrstuvwxyz"[len(self._tex)]
        self._ap[f] = spot.formula.ap(tok)
        self._tex[tok] = tex

    def latex(self, f: "spot.formula", hide: Sequence["spot.formula"] = ()
              ) -> str:
        """`f` in LaTeX, its named subterms replaced. `hide` drops names — a
        brick must not be printed as its own name."""
        table = {g: ap for g, ap in self._ap.items() if g not in hide}

        def go(g: "spot.formula") -> "spot.formula":
            named = table.get(g)
            return named if named is not None else g.map(go)

        out = go(f).to_str("latex")
        for ap, tex in self._tex.items():
            out = out.replace(rf"\mathit{{{ap}}}", tex)
        return out


def _final_tex(c: int) -> str:
    return rf"\mathsf{{Final}}({c})"


def _exit_targets(cay: Cayley, layer: Sequence[int]) -> List[int]:
    """The classes one Cayley step below `layer` — the children its exit fans
    reach, and the only labels its bricks can name."""
    inside = set(layer)
    return sorted({cay.step(c, a)
                   for c in layer for a in range(cay.inv.alphabet.size)}
                  - inside)


# ------------------------------------------------------------------ #
# One layer's block: the bricks it contributes, and how each was made.
# ------------------------------------------------------------------ #
@dataclass
class Row:
    name: str       # TeX of the brick's name, e.g. `\mathsf{leave}(3)`
    body: str       # TeX of its formula, names substituted
    rule: str       # the rule that produced it


def _rule(la: anchoring.LayerAnchoring, brick: str, c: Optional[int]) -> str:
    if brick == "window":
        return r"window $\Omega$"
    if brick == "sojourn":
        return "sojourn"
    if brick == "step":
        return "step"
    if brick == "committed":
        return "committed"
    assert brick == "leave" and c is not None
    if not la.exits[c]:
        return "no exit"
    return "exit fan" if not la.stutter[c] else "leave"


def _kind(cay: Cayley, layer: Sequence[int]) -> str:
    lets = range(cay.inv.alphabet.size)
    if all(cay.step(c, a) == c for c in layer for a in lets):
        return "frozen, terminal"
    if not any(cay.step(c, a) in set(layer) for c in layer for a in lets):
        return "transient"
    return "moving"


def _block(cay: Cayley, anch: Sequence[anchoring.LayerAnchoring],
           layer_id: int, bricks: Sequence[Brick],
           finals: Dict[int, "spot.formula"]) -> Tuple[str, str, List[Row]]:
    """The header, the note, and the rows of one layer, and `finals` extended
    with the layer's own labels.

    The names a block may use are exactly the labels of the classes its exit
    fans reach — `finals` restricted to the layer's exit targets — plus the
    scaffolding it builds itself (`step`, each `leave(c)`), introduced as the
    rows that define them are printed. `STAY` and `LEAVE` get no row: they are
    the two disjuncts of `Final`, and the single fact their formulas carry
    that `Final` hides — whether the confinement branch survived — is the
    note."""
    import spot
    la = anch[layer_id]
    by: Dict[Tuple[str, Optional[int]], "spot.formula"] = {
        (b.brick, b.cls): b.formula for b in bricks}
    layer = sorted(la.layer)

    names = Names()
    for t in _exit_targets(cay, layer):
        names.add(finals[t], _final_tex(t))

    rows: List[Row] = []
    win = by[("window", None)]
    if win != spot.formula.ff():
        rows.append(Row(rf"\Omega(R_{{{layer_id}}})", names.latex(win),
                        _rule(la, "window", None)))
    for c in layer:
        if ("sojourn", c) in by:
            rows.append(Row(rf"\mathsf{{sojourn}}({c})",
                            names.latex(by[("sojourn", c)]),
                            _rule(la, "sojourn", c)))
    if ("step", None) in by:
        step = by[("step", None)]
        rows.append(Row(r"\mathsf{step}", names.latex(step),
                        _rule(la, "step", None)))
        names.add(step, r"\mathsf{step}")

    for c in layer:
        if ("leave", c) not in by:
            continue
        rows.append(Row(rf"\mathsf{{leave}}({c})",
                        names.latex(by[("leave", c)], hide=[by[("leave", c)]]),
                        _rule(la, "leave", c)))
    for c in layer:
        if ("leave", c) in by:
            names.add(by[("leave", c)], rf"\mathsf{{leave}}({c})")

    # No `hide` here: when a class's confinement branch is `⊥`, its `Final`
    # *is* its `leave`, and printing the name says so.
    for c in layer:
        committed = ("committed", c) in by
        f = by[("committed", c)] if committed else by[("Final", c)]
        rule = ("committed" if committed
                else r"$\mathrm{STAY}^\infty \lor \mathrm{LEAVE}$")
        rows.append(Row(_final_tex(c), names.latex(f), rule))
        finals[c] = f

    kind = _kind(cay, layer)
    live = any(by.get(("STAY", c), spot.formula.ff()) != spot.formula.ff()
               for c in layer)
    if kind == "transient":
        note = r"no infinite sojourn: $\mathrm{STAY}^\infty = \bot$"
    elif live:
        note = r"$\mathrm{STAY}^\infty$ live"
    else:
        note = (r"all-rejecting as a final layer: "
                r"$\mathrm{STAY}^\infty = \bot$")
    head = (rf"layer $R_{{{layer_id}}} = \{{"
            + ",".join(str(c) for c in layer) + rf"\}}$ --- {kind}")
    return head, note, rows


def derivation(inv: Invariant, cay: Cayley, rend: engine.Rendering
               ) -> List[Tuple[int, str, str, List[Row]]]:
    """The whole stack, deepest layer of the R-order first; R-incomparable
    layers by least class. Every block's names are already defined when it is
    printed — that is what "assembled child-first" means."""
    anch = anchoring.analyze(cay)
    bricks = dump(inv, rend)
    order = sorted(range(len(cay.layers)),
                   key=lambda i: (_depth(cay, i), min(cay.layers[i])))
    finals: Dict[int, "spot.formula"] = {}
    out: List[Tuple[int, str, str, List[Row]]] = []
    for i in order:
        mine = [b for b in bricks if b.layer == i]
        head, note, rows = _block(cay, anch, i, mine, finals)
        out.append((i, head, note, rows))
    return out


def _depth(cay: Cayley, i: int) -> int:
    """Longest R-order path out of layer `i` — 0 at a terminal layer."""
    best = 0
    for j in cay.successors[i]:
        best = max(best, 1 + _depth(cay, j))
    return best


# ------------------------------------------------------------------ #
# The drawing: the mini-diamond, and the blocks beside it.
# ------------------------------------------------------------------ #
def _mini(cay: Cayley, live: int, done: Sequence[int], y: float,
          tag: str) -> List[str]:
    """The R-order diamond, this step's layer lit, its children shaded."""
    out: List[str] = [rf"\begin{{scope}}[shift={{(0,{y:.2f})}}, "
                      rf"local bounding box=m{tag}]"]
    for c, (x, cy) in sorted(MINI.items()):
        out.append(rf"  \node[minicls] (m{tag}c{c}) at ({x:.2f},{cy:.2f}) "
                   rf"{{{c}}};")
    for i, layer in enumerate(cay.layers):
        style = ("minilive" if i == live
                 else "minidone" if i in done else "minibox")
        nodes = " ".join(f"(m{tag}c{c})" for c in layer)
        out.append(r"  \begin{scope}[on background layer]")
        out.append(rf"    \node[{style}, fit={nodes}, inner sep=1.6pt] "
                   rf"(m{tag}L{i}) {{}};")
        out.append(r"  \end{scope}")
    for i in range(len(cay.layers)):
        for j in cay.successors[i]:
            out.append(r"  \begin{scope}[on background layer]")
            out.append(rf"    \draw[miniorder] (m{tag}L{i}) -- (m{tag}L{j});")
            out.append(r"  \end{scope}")
    out.append(r"\end{scope}")
    return out


def render(cay: Cayley,
           blocks: Sequence[Tuple[int, str, str, List[Row]]]) -> str:
    body: List[str] = []
    y = 0.0
    done: List[int] = []
    for live, head, note, rows in blocks:
        top = y
        body.append(rf"\node[blockhead] at ({COL_TEXT:.2f},{y:.2f}) "
                    rf"{{{head}}};")
        body.append(rf"\node[blocknote] at ({COL_RULE:.2f},{y:.2f}) "
                    rf"{{{note}}};")
        for r in rows:
            y -= ROW
            body.append(rf"\node[brick] at ({COL_TEXT:.2f},{y:.2f}) "
                        rf"{{${r.name} \;=\; {r.body}$}};")
            body.append(rf"\node[rulelab] at ({COL_RULE:.2f},{y:.2f}) "
                        rf"{{{r.rule}}};")
        body += _mini(cay, live, done, (top + y) / 2.0 + 0.8, f"{live}")
        done.append(live)
        y -= GAP
    return tikz.standalone(body)


# ------------------------------------------------------------------ #
def main(argv: List[str]) -> int:
    path = argv[0]
    with open(path) as f:
        inv = load_invariant(f.read())
    cay = build(inv)
    blocks = derivation(inv, cay, engine.Rendering(residual=False))

    print(f"{path}: {len(blocks)} layers, "
          f"{sum(len(b[3]) for b in blocks)} bricks")
    for _live, head, note, rows in blocks:
        print(f"  {head}  [{note}]")
        for r in rows:
            print(f"    {r.name} = {r.body}   ({r.rule})")

    if _TRACE:
        for b in dump(inv, engine.DEFAULT):
            print(f"[figs] default rendering: L{b.layer} {b.brick} "
                  f"c={b.cls} {b.formula}", file=sys.stderr)

    if len(argv) > 1:
        with open(argv[1], "w") as out:
            out.write(render(cay, blocks))
        print(f"  wrote {argv[1]}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
