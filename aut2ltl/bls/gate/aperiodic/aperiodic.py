"""
bls/gate/aperiodic/aperiodic.py — the Language LTL-definability screen.

`label_ltl_definable` takes a `Language`, reads one deterministic form of its
ω-language, decides whether an LTL formula defining it exists, and TAGS the
Language (`set_ltl_definable`) so the reading is computed once and shared.

The characterization: LTL == star-free == counter-free == the deterministic
transition monoid is APERIODIC. The screen reads `det_generic_minimal()`
(deterministic, generic acceptance, simulation-reduced and SAT-minimized when
small) — NOT a state-based (`sbacc`) form: forcing state-based acceptance
degeneralizes a generalized-Büchi condition (e.g. Inf(0)&Inf(1)&Inf(2) for
`GFa & GFb & GFc`) into a "which mark am I waiting for" counter, a spurious
cyclic group that reads as non-aperiodic on a language that IS LTL. The generic
form carries no such counter.

The verdict `(definable, conclusive)`: `definable` is the aperiodicity of the
transition monoid (True == an LTL formula exists); `conclusive` records whether
the form was SAT-minimized (the state-minimal regime). The aperiodicity oracle
is `gap/aperiodic.is_aperiodic_gens`.

LAYERING: above the floor (reads `Language`) and the gap oracle; imports neither
Cascade nor any Translator.
"""

from __future__ import annotations

import os
from typing import Optional, Tuple, TYPE_CHECKING

import spot

from aut2ltl.language import SAT_MIN_STATES
from ...generators import extract_generators
from ...gap.aperiodic import is_aperiodic_gens

if TYPE_CHECKING:
    from aut2ltl.language import Language


def _sat_min_threshold() -> int:
    """State count at/below which `det_generic_minimal()` SAT-minimizes D — the
    regime in which a non-aperiodic reading is a conclusive proof (the form is
    genuinely state-minimal); above it the verdict is only a strong hint."""
    return int(os.environ.get(SAT_MIN_STATES.env, SAT_MIN_STATES.default))


def label_ltl_definable(
    lang: "Language",
    *,
    gap_cmd: str = "gap",
    timeout: int = 30,
    max_aps: int = 5,
) -> Tuple[Optional[bool], bool]:
    """Decide and cache `(definable, conclusive)` for `lang` (idempotent: returns
    the cached tag if already set).

    `definable` is three-valued:
      * `True`  — the sbacc-free transition monoid is aperiodic: an LTL formula
        exists (a proof — see algorithm.md, Soundness).
      * `False` — the monoid carries a group: a SUSPICION of non-definability,
        never a proof; certification belongs to the witness.
      * `None`  — the oracle COULD NOT RUN (an extraction or GAP failure: too
        many APs, a GAP error/timeout). Nothing was read in either direction; the
        consumer must treat the language as it treats an uncertified suspicion —
        fence the cascade, assert nothing — rather than trust that downstream
        machinery will fail the same way.

    `conclusive` — the form was genuinely state-minimal (≤ the SAT-min
    threshold). It grades diagnosis prose only.
    """
    cached = lang.ltl_definable
    if cached is not None:
        return cached

    det = lang.det_generic_minimal()
    n_min = det.num_states()
    conclusive = n_min <= _sat_min_threshold()
    definable: Optional[bool]
    try:
        # extract_generators needs a complete deterministic automaton; completing
        # only adds a sink (an idempotent — no group), so it cannot perturb the
        # aperiodicity verdict.
        aut = spot.postprocess(det, "deterministic", "generic", "complete")
        gens, _, _ = extract_generators(aut, max_aps=max_aps)
        definable = is_aperiodic_gens(gens, gap_cmd=gap_cmd, timeout=timeout)
    except Exception:
        definable, conclusive = None, False  # oracle could not run (see docstring)

    lang.set_ltl_definable(definable, conclusive=conclusive)
    return (definable, conclusive)


__all__ = ["label_ltl_definable"]
