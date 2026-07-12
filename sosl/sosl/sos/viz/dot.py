"""The GraphViz backend: a `Figure` as `digraph` text.

Generic over any invariant and any alphabet. Two uses: a picture of an arbitrary
`.sos` (``dot -Tpng``), and the layout oracle whose node placement the finer
backends reuse (``dot -Tplain``, see `layout.py`). Pure text — no subprocess.

The model's classification maps onto dot attributes: the root gets an incoming
stub from nowhere (an initial-state marker — and the only arrow that may enter
it), an idempotent gets a double periphery, the letter picks the line dash and
labels the arrow, a key-tree edge is thicker, and a monochrome-cycle edge is
drawn as two parallel strokes (dot's ``color="c:c"``).
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .model import Figure

# Rank/node separation, in inches: the ~2.2cm x ~1.4cm grid the figures want.
RANKSEP_IN = 0.87
NODESEP_IN = 0.55

# The dash pattern per letter index; cycled if the alphabet is larger.
LETTER_STYLE = ("solid", "dashed", "dotted", "bold")


def _letter_style(index: int) -> str:
    """The dot line style of the letter at display index ``index``."""
    return LETTER_STYLE[index % len(LETTER_STYLE)]


def pairs_label(fig: Figure) -> str:
    """The accepting pairs as one plain-text line, ``P = { ([b],[b]), … }``."""
    inner = ", ".join(f"([{s}],[{e}])" for s, e in fig.pairs())
    return f"P = {{ {inner} }}" if inner else "P = { }"


def dot_of(fig: Figure, name: str = "cayley", pairs: bool = True) -> str:
    """The `digraph` for ``fig``: layered left-to-right by key length (one
    ``rank=same`` group per BFS layer), nodes and edges in the figure's canonical
    order, so the text is a deterministic function of the invariant. ``pairs``
    puts P under the drawing as the graph title (the object is ``<A, P>``; only
    ``A`` has a shape, so P is a caption)."""
    out: List[str] = [
        f"digraph {name} {{",
        "  rankdir=LR;",
        f"  ranksep={RANKSEP_IN}; nodesep={NODESEP_IN};",
        '  node [shape=box, style=rounded, fontname="serif", margin="0.06,0.03"];',
        '  edge [fontname="serif", fontsize=10, arrowsize=0.7];',
    ]
    if pairs:
        out += [f'  label="{pairs_label(fig)}"; labelloc="b"; labeljust="c";',
                '  fontname="serif"; fontsize=11;']
    out.append("")
    for nd in fig.nodes:
        attrs = [f'label="{nd.label}"']
        if nd.is_idem:
            attrs += ["peripheries=2"]
        out.append(f'  {nd.ident} [{", ".join(attrs)}];')
    root = next(nd for nd in fig.nodes if nd.is_root)
    out += ['  _init [shape=none, label="", width=0.02, height=0.02];',
            f"  _init -> {root.ident};",   # the root, marked like an initial state
            ""]

    for layer in range(fig.layers()):
        same = [nd.ident for nd in fig.nodes if nd.layer == layer]
        out.append(f'  {{ rank=same; {" ".join(same)}; }}')
    out.append("")

    for (src, dst), letters in grouped(fig).items():
        marks = [e for e in fig.edges if (e.src, e.dst) == (src, dst)]
        attrs = [f'label="{",".join(fig.naming.names[i] for i in letters)}"',
                 f"style={_letter_style(letters[0])}" if len(letters) == 1
                 else "style=solid",
                 "penwidth=1.6" if any(e.is_tree for e in marks) else "penwidth=0.8"]
        if any(e.is_cycle for e in marks):
            attrs.append('color="black:black"')
        a, b = fig.node_of(src).ident, fig.node_of(dst).ident
        out.append(f'  {a} -> {b} [{", ".join(attrs)}];')

    out.append("}")
    return "\n".join(out) + "\n"


def grouped(fig: Figure) -> Dict[Tuple[int, int], List[int]]:
    """The figure's edges by endpoint pair, each with the display indices of the
    letters that take it. Letters that agree on a target share one arrow, labeled
    with all of them (``a,b``), rather than stacking one arrow per letter."""
    out: Dict[Tuple[int, int], List[int]] = {}
    for e in fig.edges:
        out.setdefault((e.src, e.dst), []).append(e.letter_index)
    return out
