"""A compact human-readable rendering of a classification `Record` for a
terminal: the coordinates, the rung table, the parity/boolean lengths, and the
Wagner data (``mu``, ``sign``, ``phi`` — ``phi`` shown ``PARTIAL(mu)`` when the
derivative is unresolved).
"""
from __future__ import annotations

from .record import Record


def render_text(rec: Record) -> str:
    """A compact human-readable rendering of the record (no witnesses body)."""
    r = rec.rungs
    rungs = ",".join(name for name, on in
                     [("open", r.open), ("closed", r.closed), ("weak", r.weak),
                      ("dba", r.dba), ("dca", r.dca)] if on) or "-"
    lines = [
        f"aperiodic (LTL): {rec.aperiodic}   stutter-invariant: {rec.stutter_invariant}",
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
