"""viz — the Cayley graph of an invariant, as a picture. Re-exports; see README.md.

The figure model (`model`) classifies the algebra once; the backends (`dot`,
`tikz`) render it; `layout` places it; `render` calls the external tools. CLI:
``python3 -m sosl.sos.viz <file.sos> -o <out.dot|.tex|.pdf|.png>``.
"""
from .dot import dot_of
from .layout import Placement, layered, place
from .model import Edge, Figure, Naming, Node, figure_of
from .tikz import tikz_of

__all__ = [
    "Figure",
    "Node",
    "Edge",
    "Naming",
    "figure_of",
    "Placement",
    "place",
    "layered",
    "dot_of",
    "tikz_of",
]
