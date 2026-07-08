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
    """One corpus case: a stable id, its source HOA (relative to the sosl root),
    an optional precomputed reference `.sos` (the census fast path), the triptych
    slot it fills (if any), role tags, and a one-line note."""

    case_id: str
    hoa: str
    sos: Optional[str] = None               # precomputed reference .sos, if any
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


# Census location (relative to the sosl root) and the shapes SHAPES.md marks
# "deferred" — heavy `kept`/`langs` counts run separately from the main sweep.
CENSUS_ROOT = "../genaut/corpus"
DEFERRED_SHAPES = frozenset({"1state3ap1acc", "2state2ap0acc", "3state1ap0acc"})


def census_cases(det_folder: str) -> List[Case]:
    """Every canonical automaton under a `corpus/det/<shape>/` folder as a `Case`,
    each paired with its precomputed `corpus/sos/<shape>/*.sos` reference (the
    fast path). The shape name is carried as a tag so runs can group by shape."""
    root = Path(det_folder)
    shape = root.name
    cases: List[Case] = []
    for p in sorted(root.rglob("*.hoa")):
        cand = Path(str(p).replace("/det/", "/sos/")).with_suffix(".sos")
        sos = str(cand) if cand.exists() else None
        cases.append(Case(p.stem, str(p), sos=sos, tags=("census", shape)))
    return cases


def census_shapes(
    corpus_root: str = CENSUS_ROOT,
    shapes: Optional[List[str]] = None,
    include_deferred: bool = False,
) -> List[Case]:
    """The census cases across shapes under ``corpus_root/det/``. With ``shapes``
    given, exactly those; otherwise every built shape, minus `DEFERRED_SHAPES`
    unless ``include_deferred``. The tractable non-deferred set spans the whole
    LTL frontier (SHAPES.md: not-LTL first appears at `2state1ap0acc`)."""
    det = Path(corpus_root) / "det"
    if not det.is_dir():
        return []
    available = sorted(d.name for d in det.iterdir() if d.is_dir())
    if shapes is not None:
        chosen = [s for s in available if s in set(shapes)]
    elif include_deferred:
        chosen = available
    else:
        chosen = [s for s in available if s not in DEFERRED_SHAPES]
    out: List[Case] = []
    for s in chosen:
        out.extend(census_cases(str(det / s)))
    return out


# The flat, complement-closed catalogue (one file per language up to AP
# relabeling, closed under complement — genaut `flatten.py --canon`). Unlike the
# per-shape census tiers, `det/` and `sos/` are a single flat pool; the shape is
# the filename prefix and is not needed here (no shape ventilation).
FLAT_CANON_ROOT = "../genaut/corpus/flat_canon"


@dataclass(frozen=True)
class Category:
    """A language's `.cat` category, read off its syntactic invariant `𝓘(L)`:
    the LTL-definability cut and the Wagner degree `ϕ = (γ, s)` with its class
    name (genaut `gen/categorize.py`; one `.cat` per language)."""

    ltl: bool
    phi: str                                # e.g. "1,pi"  (γ, side)
    cls: str                                # human class name


def load_category(sos_path: str) -> Optional[Category]:
    """Parse the `.cat` sidecar next to ``sos_path`` (same basename), or
    ``None`` if absent. Format: ``CAT v1`` then ``ltl:`` / ``phi:`` / ``class:``
    lines (``coords:`` is ignored — recomputable from ``phi``)."""
    cat = Path(sos_path).with_suffix(".cat")
    if not cat.exists():
        return None
    ltl = True
    phi = ""
    cls = ""
    for line in cat.read_text().splitlines():
        if line.startswith("ltl:"):
            ltl = line.split(":", 1)[1].strip() == "yes"
        elif line.startswith("phi:"):
            phi = line.split(":", 1)[1].strip()
        elif line.startswith("class:"):
            cls = line.split(":", 1)[1].strip()
    return Category(ltl=ltl, phi=phi, cls=cls)


def flat_canon_cases(corpus_root: str = FLAT_CANON_ROOT) -> List[Case]:
    """Every language of the flat, complement-closed catalogue as a `Case`,
    each paired with its precomputed `sos/*.sos` reference (the fast path). The
    `.cat` category is not carried on the `Case` — load it with
    `load_category(case.sos)` where a run needs the LTL/Wagner cut."""
    det = Path(corpus_root) / "det"
    if not det.is_dir():
        return []
    cases: List[Case] = []
    for p in sorted(det.glob("*.hoa")):
        cand = Path(corpus_root) / "sos" / (p.stem + ".sos")
        sos = str(cand) if cand.exists() else None
        cases.append(Case(p.stem, str(p), sos=sos, tags=("flat_canon",)))
    return cases
