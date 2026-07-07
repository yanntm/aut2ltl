"""The versioned corpus manifest and configuration list — the campaign's cases,
named and pinned, never selected ad hoc (spec §6).

A `Case` binds a stable ``case_id`` to a source automaton and its role (triptych
slot, permanent-stall specimen, alternate presentation). A `Config` (see
`sosl.experiment.run`) is one learner configuration. `e0_runs` is the ordered
(case, config) matrix the E0 validation campaign executes.

The census tier (`genaut/corpus/`) is intentionally *not* wired here yet: it is
being curated elsewhere. `census_cases` is the single guarded entry point a
later revision points at that folder; until then it returns nothing and E0 runs
the named cases alone.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from sosl.experiment.run import Config

MANIFEST_VERSION = "m4a-2026-07-08"


@dataclass(frozen=True)
class Case:
    """One named corpus case: a stable id, its source HOA (relative to the sosl
    root), the triptych slot it fills (if any), role tags, and a one-line note."""

    case_id: str
    hoa: str
    triptych: Optional[str] = None          # T1 | T2 | T3
    tags: Tuple[str, ...] = ()
    note: str = ""


# The triptych (spec §6) plus the two proven-permanent specimens (Prop. 4.4) and
# one alternate presentation of T1 (a presentation-independence metamorphic pair).
NAMED_CASES: List[Case] = [
    Case("gf_aa_parity", "samples/gf_aa_parity.hoa", triptych="T1",
         note="infinitely many aa — GF(a & Xa); parity presentation"),
    Case("gf_aa_reset", "samples/gf_aa_reset.hoa",
         tags=("presentation-alt",),
         note="T1 alternate presentation (metamorphic pair with gf_aa_parity)"),
    Case("even", "samples/even.hoa", triptych="T2",
         note="(aa)*·!a·Σ^ω — even a-block then !a; 4-state Büchi"),
    Case("evenblocks", "samples/evenblocks.hoa", triptych="T3",
         tags=("prefix-independent",),
         note="Fin(0) & Inf(1) — prefix-independent; hard for right-congruence"),
    Case("a_implies_xa", "samples/a_implies_xa.hoa",
         tags=("permanent-specimen",),
         note="a -> X a; permanent stall (Prop. 4.4), zero-cex 5-vs-4 gap"),
    Case("a_once", "samples/a_once.hoa",
         tags=("permanent-specimen",),
         note="a & X G !a; permanent stall (Prop. 4.4)"),
]


# Configuration axes the campaign sweeps.
DEFAULT = Config("default", saturation=True, eq_mode="bounded")
EXACT = Config("exact", saturation=True, eq_mode="exact")
NOSAT_BOUNDED = Config("no-sat-bounded", saturation=False, eq_mode="bounded")
NOSAT_EXACT = Config("no-sat-exact", saturation=False, eq_mode="exact")

CONFIGS: List[Config] = [DEFAULT, EXACT, NOSAT_BOUNDED, NOSAT_EXACT]


def is_permanent(case: Case) -> bool:
    """A proven-permanent-stall specimen (spec §9 P4/F5)."""
    return "permanent-specimen" in case.tags


def e0_runs() -> List[Tuple[Case, Config]]:
    """The E0 validation matrix (spec §6 E0, ordered).

    Every named case runs under ``default`` (the campaign's headline config,
    which must be SOUND everywhere). The two permanent specimens additionally run
    under ``no-sat-exact`` — the exact-mode fixture that must certify their
    stalled fixpoints (spec §9 P4). ``exact`` (saturation on) also runs on the
    specimens as the canonical cross-check."""
    runs: List[Tuple[Case, Config]] = [(c, DEFAULT) for c in NAMED_CASES]
    for c in NAMED_CASES:
        if is_permanent(c):
            runs.append((c, NOSAT_EXACT))
            runs.append((c, EXACT))
    return runs


# Expected stall class of each named case under the E2 ablation leg
# (`--no-saturation --eq-mode exact`, spec §6 E2). The two specimens are proven
# permanent (Prop. 4.4); every other named case resolves its pre-equivalence
# stall and reaches canonical (transient) or was never coarse (none).
E2_EXPECT: dict = {
    "gf_aa_parity": "transient",
    "gf_aa_reset": "transient",
    "even": "transient",
    "evenblocks": "transient",
    "a_implies_xa": "permanent",
    "a_once": "permanent",
}


def e1_runs() -> List[Tuple[Case, Config]]:
    """The E1 scaling matrix: every named case under ``default`` — E1 is a view
    of the default-config run metrics against the reference class count."""
    return [(c, DEFAULT) for c in NAMED_CASES]


def e2_runs() -> List[Tuple[Case, Config]]:
    """The E2 ablation matrix: every named case under both the canonical
    ``default`` (saturation on) and the ablation ``no-sat-exact`` leg (spec §6:
    with exact equivalence, every surviving stall is provably permanent)."""
    return ([(c, DEFAULT) for c in NAMED_CASES]
            + [(c, NOSAT_EXACT) for c in NAMED_CASES])


def case_by_id(case_id: str) -> Optional[Case]:
    """The named `Case` with this id, or ``None``."""
    for c in NAMED_CASES:
        if c.case_id == case_id:
            return c
    return None


def census_cases(folder: Optional[str] = None) -> List[Case]:
    """The census tier — guarded. Returns nothing until a folder is passed and
    the tier is deliberately enabled; the `genaut/corpus/` sweep is curated
    elsewhere and must not be pulled into E0 by default."""
    if not folder:
        return []
    root = Path(folder)
    return [Case(p.stem, str(p), tags=("census",))
            for p in sorted(root.rglob("*.hoa"))]
