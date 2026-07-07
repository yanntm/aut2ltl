"""Rendering a classification `Record` as a flat dict (JSON) and as text.

The dict is the spec section 1 output record: the coordinates, the rung table,
the parity/boolean lengths, the Wagner data (``mu``, ``sign``, ``gamma`` — the
last shown as ``PARTIAL(mu)`` when the derivative is unresolved), ``phi``, and
the witnesses. ``render_text`` is the same content for a terminal.
"""
from __future__ import annotations

from typing import Dict

from .record import Record


def record_to_dict(rec: Record) -> Dict:
    """The flat JSON-friendly record of spec section 1."""
    g = rec.phi[0]
    return {
        "aperiodic": rec.aperiodic,
        "m_plus": rec.m_plus, "m_minus": rec.m_minus,
        "n_plus": rec.n_plus, "n_minus": rec.n_minus,
        "rungs": {
            "open": rec.rungs.open, "closed": rec.rungs.closed,
            "weak": rec.rungs.weak, "dba": rec.rungs.dba, "dca": rec.rungs.dca,
        },
        "boolean_level": rec.boolean_level,
        "parity_length": rec.parity_length,
        "co_parity_length": rec.co_parity_length,
        "mu": str(rec.mu),
        "sign": rec.sign,
        "gamma": None if rec.gamma is None else str(rec.gamma),
        "gamma_partial": rec.gamma_partial,
        "phi": [g, rec.sign],
        "witnesses": rec.witnesses,
    }


def render_text(rec: Record) -> str:
    """A compact human-readable rendering of the record (no witnesses body)."""
    r = rec.rungs
    rungs = ",".join(name for name, on in
                     [("open", r.open), ("closed", r.closed), ("weak", r.weak),
                      ("dba", r.dba), ("dca", r.dca)] if on) or "-"
    lines = [
        f"aperiodic (LTL): {rec.aperiodic}",
        f"chains   (m+, m-): ({rec.m_plus}, {rec.m_minus})",
        f"superchn (n+, n-): ({rec.n_plus}, {rec.n_minus})",
        f"rungs: {rungs}",
        f"parity length: {rec.parity_length}   co-parity: {rec.co_parity_length}"
        + (f"   boolean level: {rec.boolean_level}" if rec.boolean_level is not None else ""),
        f"mu = {rec.mu}   sign = {rec.sign}",
        f"phi = ({rec.phi[0]}, {rec.phi[1]})"
        + ("   [PARTIAL: derivative needed]" if rec.gamma_partial else ""),
    ]
    return "\n".join(lines)
