"""Reading a `.cat` classification sidecar back into a flat dict.

`.cat` is the serialization of a language's classification: a small text sidecar
next to each `.sos`, one line per read-off. The reader is pure text — a report
aggregator uses it without pulling the classifier.

`.cat` format:

    CAT v1
    ltl: yes|no
    stutter: invariant|sensitive
    phi: <gamma>,<sign>          e.g. omega,sigma  omega*2,pi  omega^2,sigma
    coords: <m+> <m-> <n+> <n->
    class: <dictionary reading>
"""
from __future__ import annotations

from typing import Dict


def parse_cat(text: str) -> Dict:
    """Read a `.cat` body into ``{ltl: bool, stutter_invariant: bool,
    phi: (γ, s), coords: (m+,m-,n+,n-), class: str}``. Inverse of
    `sosl.sos.classify.io.cat_text` up to the class label."""
    fields: Dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line and not line.startswith("CAT"):
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip()
    g, _, s = fields["phi"].partition(",")
    return {
        "ltl": fields["ltl"] == "yes",
        "stutter_invariant": fields["stutter"] == "invariant",
        "phi": (g, s),
        "coords": tuple(int(x) for x in fields["coords"].split()),
        "class": fields.get("class", ""),
    }
