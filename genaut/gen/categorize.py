"""Categorize each language of a `sos/` tier — write a `.cat` sidecar next to
every `.sos`, recording the language's classification (the *category*).

A `.cat` carries the language's **definability cut** (LTL / non-LTL) and its
**Wagner degree** `ϕ = (γ, s)` with the `(m⁺, m⁻, n⁺, n⁻)` chain/superchain
coordinates and the human-readable class name — the full read-off of the
syntactic invariant `𝓘(L)` (`sosl.sos.classify`), a pure table search, no
automaton and no Spot call. One `.cat` per language: it is a property of the
*language*, so the single sidecar in `sos/` covers both the `.sos` and the
`det/` HOA of the same basename (no second copy under `det/`).

    python3 genaut/gen/categorize.py                 # -> corpus/flat_canon/sos/*.cat
    python3 genaut/gen/categorize.py <sos-folder>    # any tier's sos/ dir

The Wagner vocabulary (class names, weakest-first ordering, the `.cat` parser)
lives here as pure top-level helpers so a report aggregator can import it
without pulling the classifier (`flat_study.py` reads the `.cat` text and never
classifies). Writing the sidecars is the only step that imports `sosl`.

`.cat` format (v1):

    CAT v1
    ltl: yes|no
    phi: <gamma>,<sign>          e.g. omega,sigma  omega*2,pi  omega^2,sigma
    coords: <m+> <m-> <n+> <n->
    class: <dictionary reading>
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
_DEFAULT = os.path.join(_REPO, "genaut", "corpus", "flat_canon", "sos")

Phi = Tuple[str, str]           # (gamma-string, sign-string) as `sosl` renders them

# The C§7–8 dictionary: the Wagner degree of a language named as its class. Keyed
# by (gamma, sign) exactly as `Record.phi` renders them (`sigma`/`pi`/`delta`,
# `omega`, `omega*2`, `omega^2`, …). Complement-side rows are named as the dual.
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
    """Parse a rendered ordinal `γ` into descending `(exponent, coefficient)`
    terms — a tuple that orders as the ordinal. `PARTIAL(...)` sorts above every
    resolved degree. Handles `0`, finite ints, `omega`, `omega*c`, `omega^e`,
    `omega^e*c`, and `+`-sums."""
    if gamma.startswith("PARTIAL"):
        return ((999, 1),)
    if gamma == "0":
        return ()
    out: List[Tuple[int, int]] = []
    for part in gamma.split(" + "):
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
    """Weakest-first Wagner order on `ϕ = (γ, s)`: by the ordinal `γ`, then the
    sign `δ < σ < π`."""
    return (_gamma_terms(phi[0]), _SIGN_RANK.get(phi[1], 9))


def phi_pretty(phi: Phi) -> str:
    """`ϕ` for display: `(ω, σ)`, `(ω·2, π)`, `(ω², σ)`, `(1, δ)`, …"""
    g = phi[0].replace("omega^2", "ω²").replace("omega*2", "ω·2").replace("omega", "ω")
    return f"({g}, {_SIGN_GLYPH.get(phi[1], phi[1])})"


def parse_cat(text: str) -> Dict:
    """Read a `.cat` body into `{ltl: bool, phi: (γ, s), coords: (m+,m-,n+,n-),
    class: str}`. Inverse of `cat_text` up to the class label."""
    fields: Dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line and not line.startswith("CAT"):
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip()
    g, _, s = fields["phi"].partition(",")
    return {
        "ltl": fields["ltl"] == "yes",
        "phi": (g, s),
        "coords": tuple(int(x) for x in fields["coords"].split()),
        "class": fields.get("class", ""),
    }


def cat_text(rec: "object") -> str:
    """Render a classification `Record` as a `.cat` body (format v1)."""
    g, s = rec.phi                                        # type: ignore[attr-defined]
    ltl = "yes" if rec.aperiodic else "no"               # type: ignore[attr-defined]
    coords = (rec.m_plus, rec.m_minus, rec.n_plus, rec.n_minus)  # type: ignore[attr-defined]
    return (f"CAT v1\nltl: {ltl}\nphi: {g},{s}\n"
            f"coords: {coords[0]} {coords[1]} {coords[2]} {coords[3]}\n"
            f"class: {class_reading((g, s))}\n")


def write_cats(sos_dir: str) -> int:
    """Classify every `.sos` in `sos_dir` and write a sibling `.cat`; return the
    count. Loads the invariant and runs the read-off — the only `sosl`-importing
    step (kept lazy so the vocabulary helpers above import Spot-free)."""
    if os.path.join(_REPO, "sosl") not in sys.path:
        sys.path.insert(0, os.path.join(_REPO, "sosl"))
    from sosl.sos import load_invariant                   # noqa: E402
    from sosl.sos.classify import classify                # noqa: E402

    n = 0
    for fname in sorted(f for f in os.listdir(sos_dir) if f.endswith(".sos")):
        with open(os.path.join(sos_dir, fname)) as fh:
            rec = classify(load_invariant(fh.read()))
        with open(os.path.join(sos_dir, fname[:-4] + ".cat"), "w") as fh:
            fh.write(cat_text(rec))
        n += 1
    return n


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    sos_dir = argv[0] if argv else _DEFAULT
    n = write_cats(sos_dir)
    print(f"wrote {n} .cat sidecars in {sos_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
