"""The GraphViz backend: a `Figure` as `digraph` text.

Generic over any invariant and any alphabet. Two uses: a picture of an arbitrary
`.sos` (``dot -Tpng``), and the layout oracle whose node placement the finer
backends reuse (``dot -Tplain``, see `layout.py`). Pure text — no subprocess.

The model's classification maps onto dot attributes: the root is greyed and
dashed, an idempotent gets a double periphery, the letter picks the line dash,
a key-tree edge is thicker, a monochrome-cycle edge is drawn as two parallel
strokes (dot's ``color="c:c"``).
"""
from __future__ import annotations

from typing import List

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
        '  node [shape=ellipse, fontname="serif", margin="0.04,0.02"];',
        '  edge [fontname="serif", arrowsize=0.7];',
    ]
    if pairs:
        out += [f'  label="{pairs_label(fig)}"; labelloc="b"; labeljust="c";',
                '  fontname="serif"; fontsize=11;']
    out.append("")
    for nd in fig.nodes:
        attrs = [f'label="{nd.label}"']
        if nd.is_root:
            attrs += ['style=dashed', 'color="grey60"', 'fontcolor="grey60"']
        if nd.is_idem:
            attrs += ["peripheries=2"]
        out.append(f'  {nd.ident} [{", ".join(attrs)}];')
    out.append("")

    for layer in range(fig.layers()):
        same = [nd.ident for nd in fig.nodes if nd.layer == layer]
        out.append(f'  {{ rank=same; {" ".join(same)}; }}')
    out.append("")

    for e in fig.edges:
        attrs = [f"style={_letter_style(e.letter_index)}"]
        attrs.append("penwidth=1.6" if e.is_tree else "penwidth=0.8")
        if e.is_cycle:
            attrs.append('color="black:black"')
        src, dst = fig.node_of(e.src).ident, fig.node_of(e.dst).ident
        out.append(f'  {src} -> {dst} [{", ".join(attrs)}];')

    out.append("}")
    return "\n".join(out) + "\n"
