"""The `.cat` category sidecar: LTL cut + Wagner degree, per language.

A `genaut/corpus/flat_canon/sos/<id>.cat` records a language's *category* — the
LTL / non-LTL cut and the Wagner degree `ϕ = (γ, s)` — read off its syntactic
invariant `𝓘(L)` (`genaut/gen/categorize.py`, a pure table search). One `.cat`
per language covers both its `.sos` and its `det/` HOA. This module is the
read side: `load_cat` parses one sidecar, and `PHI_ORDER` fixes the
weakest-to-strongest degree order the E1/E2/E7 tables ventilate by — replacing
the old per-shape rows now that `flat_canon` is a single cross-shape catalogue.

    CAT v1
    ltl: yes
    phi: 1,sigma
    coords: 0 0 0 1
    class: properly open — guarantee
"""
from __future__ import annotations

import os
from typing import Dict, List, NamedTuple, Optional


class Cat(NamedTuple):
    ltl: bool          # aperiodic 𝓘(L) — LTL-definable
    phi: str           # the Wagner degree key, e.g. "1,sigma" (see PHI_ORDER)
    klass: str         # the human class name, e.g. "properly open — guarantee"


# Weakest-to-strongest, matching flat_canon/STUDY.md's Wagner-degree profile:
# ordinal depth γ then side (σ before π; the self-dual δ with its γ). The list
# also gives each degree a short table label.
PHI_ORDER: List[str] = [
    "0,sigma", "0,pi",            # trivial: empty / universal
    "1,delta",                    # clopen — properly Δ₁
    "1,sigma", "1,pi",            # properly open (guarantee) / closed (safety)
    "2,sigma", "2,pi",            # properly Σ₂ / Π₂
    "omega,sigma", "omega,pi",    # properly Gδ (DBA) / Fσ (DCA)
    "omega*2,sigma", "omega*2,pi",  # one Rabin pair, σ / π side
    "omega^2,sigma", "omega^2,pi",  # parity / co-parity {0,1,2}
]

PHI_LABEL: Dict[str, str] = {
    "0,sigma": "(0,σ)", "0,pi": "(0,π)", "1,delta": "(1,δ)",
    "1,sigma": "(1,σ)", "1,pi": "(1,π)", "2,sigma": "(2,σ)", "2,pi": "(2,π)",
    "omega,sigma": "(ω,σ)", "omega,pi": "(ω,π)",
    "omega*2,sigma": "(ω·2,σ)", "omega*2,pi": "(ω·2,π)",
    "omega^2,sigma": "(ω²,σ)", "omega^2,pi": "(ω²,π)",
}


def phi_rank(phi: str) -> int:
    """Sort key placing `phi` in the weakest-to-strongest order (unknown last)."""
    return PHI_ORDER.index(phi) if phi in PHI_ORDER else len(PHI_ORDER)


def load_cat(path: str) -> Optional[Cat]:
    """Parse one `.cat` sidecar, or None if it is absent."""
    if not os.path.exists(path):
        return None
    ltl: bool = False
    phi = ""
    klass = ""
    with open(path) as f:
        for line in f:
            if line.startswith("ltl:"):
                ltl = line.split(":", 1)[1].strip() == "yes"
            elif line.startswith("phi:"):
                phi = line.split(":", 1)[1].strip()
            elif line.startswith("class:"):
                klass = line.split(":", 1)[1].strip()
    return Cat(ltl=ltl, phi=phi, klass=klass)


def cat_for(sos_dir: str, lang_id: str) -> Optional[Cat]:
    """The category of language `lang_id`, from `<sos_dir>/<lang_id>.cat`."""
    return load_cat(os.path.join(sos_dir, lang_id + ".cat"))
