"""Where the nodes go: a placement (class id -> (x, y) in centimetres).

Two engines. `layered` is pure and deterministic: BFS layer = column, shortlex
rank within the layer = row. `by_dot` shells out to the GraphViz `dot` binary and
harvests the coordinates it computed (``-Tplain``), which untangles the crossings
a naive layering leaves — this is the one impure module of the package, and the
only place a subprocess is run.

Coordinates are rounded to one decimal: a placement is meant to land in a text
file a human then nudges by hand.
"""
from __future__ import annotations

import shutil
import subprocess
from typing import Dict, List, Tuple

from .dot import dot_of
from .model import Figure

Placement = Dict[int, Tuple[float, float]]  # class id -> (x, y) in cm

COL_CM = 2.2   # column (layer) separation
ROW_CM = 1.4   # row separation within a layer
IN_TO_CM = 2.54
DOT_TIMEOUT_S = 10.0


def layered(fig: Figure) -> Placement:
    """The naive layering: column = BFS layer, row = shortlex rank within the
    layer, each layer centred vertically on 0. Deterministic, no external tool;
    crossings are not avoided."""
    by_layer: Dict[int, List[int]] = {}
    for nd in fig.nodes:                       # fig.nodes is in shortlex order
        by_layer.setdefault(nd.layer, []).append(nd.cls)
    pos: Placement = {}
    for layer, members in by_layer.items():
        top = (len(members) - 1) / 2.0
        for row, cls in enumerate(members):
            pos[cls] = (round(layer * COL_CM, 1), round((top - row) * ROW_CM, 1))
    return pos


def by_dot(fig: Figure) -> Placement:
    """The coordinates GraphViz computes for `dot.dot_of(fig)`, in centimetres.

    Runs ``dot -Tplain``, whose output gives one ``node <name> <x> <y> …`` line
    per node with x/y in inches. Raises RuntimeError if `dot` is absent, fails, or
    does not place every node. The emitted figure never contains dot's own
    drawing — only the placement is taken."""
    if shutil.which("dot") is None:
        raise RuntimeError("GraphViz `dot` not on PATH (use the `layered` engine)")
    proc = subprocess.run(                      # no P caption: it would shift the
        ["dot", "-Tplain"], input=dot_of(fig, pairs=False),   # bounding box, and
        capture_output=True, text=True, timeout=DOT_TIMEOUT_S)  # only nodes matter
    if proc.returncode != 0:
        raise RuntimeError(f"dot -Tplain failed: {proc.stderr.strip()}")

    by_ident = {nd.ident: nd.cls for nd in fig.nodes}
    pos: Placement = {}
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "node" and parts[1] in by_ident:
            x, y = float(parts[2]) * IN_TO_CM, float(parts[3]) * IN_TO_CM
            pos[by_ident[parts[1]]] = (round(x, 1), round(y, 1))
    missing = [nd.ident for nd in fig.nodes if nd.cls not in pos]
    if missing:
        raise RuntimeError(f"dot placed no coordinates for {missing}")
    return pos


def place(fig: Figure, engine: str = "dot") -> Placement:
    """The placement under ``engine`` (``"dot"`` or ``"layered"``)."""
    if engine == "dot":
        return by_dot(fig)
    if engine == "layered":
        return layered(fig)
    raise ValueError(f"unknown layout engine {engine!r} (dot | layered)")
