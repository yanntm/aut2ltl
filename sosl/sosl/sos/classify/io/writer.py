"""Rendering a classification `Record` as a `.cat` sidecar, and the batch writer
that emits one beside every `.sos` in a folder.

The read-off is a pure table search — no automaton, no Spot.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..record import classify
from .vocab import class_reading

if TYPE_CHECKING:
    from ..record import Record

from ... import load_invariant


def cat_text(rec: "Record") -> str:
    """Render a classification `Record` as a `.cat` body — see
    `sosl.sos.classify.io.reader` for the field grammar."""
    g, s = rec.phi
    ltl = "yes" if rec.aperiodic else "no"
    stutter = "invariant" if rec.stutter_invariant else "sensitive"
    coords = (rec.m_plus, rec.m_minus, rec.n_plus, rec.n_minus)
    return (f"CAT v1\nltl: {ltl}\nstutter: {stutter}\nphi: {g},{s}\n"
            f"coords: {coords[0]} {coords[1]} {coords[2]} {coords[3]}\n"
            f"class: {class_reading((g, s))}\n")


def write_cats(sos_dir: str) -> int:
    """Classify every `.sos` in ``sos_dir`` and write a sibling `.cat`; return
    the count. Iterates in sorted name order for byte-stable output. Overwrites
    an existing sidecar."""
    n = 0
    for fname in sorted(f for f in os.listdir(sos_dir) if f.endswith(".sos")):
        with open(os.path.join(sos_dir, fname)) as fh:
            rec = classify(load_invariant(fh.read()))
        with open(os.path.join(sos_dir, fname[:-4] + ".cat"), "w") as fh:
            fh.write(cat_text(rec))
        n += 1
    return n
