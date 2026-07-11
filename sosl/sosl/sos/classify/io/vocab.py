"""The Wagner vocabulary: naming a degree ``ϕ = (γ, s)`` and ordering degrees.

Pure, `sosl`-import-free helpers shared by the `.cat` writer and by report
aggregators that read `.cat` text without ever classifying. The dictionary keys
are ``(gamma, sign)`` exactly as `sosl.sos.classify.Record.phi` renders them.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

Phi = Tuple[str, str]
"""``(gamma-string, sign-string)`` as `Record.phi` renders them."""

# The C§7–8 dictionary: the Wagner degree of a language named as its class. Keyed
# by (gamma, sign); complement-side rows are named as the dual.
_READING: Dict[Phi, str] = {
    ("0", "sigma"): "empty — trivial open",
    ("0", "pi"): "universal — trivial closed",
    ("1", "delta"): "clopen — properly Δ₁",
    ("1", "sigma"): "properly open — guarantee",
    ("1", "pi"): "properly closed — safety",
    ("2", "delta"): "properly Δ₂",
    ("2", "sigma"): "properly Σ₂",
    ("2", "pi"): "properly Π₂",
    ("omega", "sigma"): "properly Gδ — DBA-proper",
    ("omega", "pi"): "properly Fσ — DCA-proper",
    ("omega*2", "sigma"): "one Rabin pair — σ side",
    ("omega*2", "pi"): "one Rabin pair — π side",
    ("omega^2", "sigma"): "parity {0,1,2} — proper",
    ("omega^2", "pi"): "co-parity {0,1,2} — proper",
    ("omega+1", "delta"): "self-dual, one derivation (Fork)",
}

_SIGN_RANK = {"delta": 0, "sigma": 1, "pi": 2, "PARTIAL": 3}
_SIGN_GLYPH = {"sigma": "σ", "pi": "π", "delta": "δ", "PARTIAL": "PARTIAL"}


def class_reading(phi: Phi) -> str:
    """The class name of a Wagner degree; a generic label when off the table."""
    return _READING.get(phi, f"degree ({phi[0]}, {phi[1]})")


def _gamma_terms(gamma: str) -> Tuple[Tuple[int, int], ...]:
    """Parse a rendered ordinal ``γ`` into descending ``(exponent, coefficient)``
    terms — a tuple that orders as the ordinal. ``PARTIAL(...)`` sorts above every
    resolved degree. Handles ``0``, finite ints, ``omega``, ``omega*c``,
    ``omega^e``, ``omega^e*c``, and ``+``-sums (spaceless, as `Ordinal`
    renders)."""
    if gamma.startswith("PARTIAL"):
        return ((999, 1),)
    if gamma == "0":
        return ()
    out: List[Tuple[int, int]] = []
    for part in gamma.split("+"):
        if part.startswith("omega"):
            rest, exp, coeff = part[len("omega"):], 1, 1
            if rest.startswith("^"):
                rest = rest[1:]
                exp_s, _, coeff_s = rest.partition("*")
                exp = int(exp_s)
                coeff = int(coeff_s) if coeff_s else 1
            elif rest.startswith("*"):
                coeff = int(rest[1:])
            out.append((exp, coeff))
        else:
            out.append((0, int(part)))
    return tuple(out)


def degree_sort_key(phi: Phi) -> Tuple:
    """Weakest-first Wagner order on ``ϕ = (γ, s)``: by the ordinal ``γ``, then
    the sign ``δ < σ < π``."""
    return (_gamma_terms(phi[0]), _SIGN_RANK.get(phi[1], 9))


def phi_pretty(phi: Phi) -> str:
    """``ϕ`` for display: ``(ω, σ)``, ``(ω·2, π)``, ``(ω², σ)``, ``(1, δ)``, …"""
    g = phi[0].replace("omega^2", "ω²").replace("omega*2", "ω·2").replace("omega", "ω")
    return f"({g}, {_SIGN_GLYPH.get(phi[1], phi[1])})"
