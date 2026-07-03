"""Shared preamble of the dg probes: from ONE HOA file to the canonical
quotient algebra (`aut2ltl/bls/definability/dg/morphism.Alg`), carrying the
intermediate oracle objects the probes display.

Not a probe itself — import it from a sibling script in this directory.
"""
from __future__ import annotations

from typing import List, NamedTuple, Optional

import spot

from aut2ltl.language import Language
from aut2ltl.bls.extract import extract_generators
from aut2ltl.bls.definability.witness.enriched import letter_elems
from aut2ltl.bls.definability.witness.support import valuation_to_letter
from aut2ltl.bls.definability.oracle.closure import close, Monoid
from aut2ltl.bls.definability.oracle.profile import Profile, profile
from aut2ltl.bls.definability.oracle.quotient import Group, find_group
from aut2ltl.bls.definability.oracle.refine import refine
from aut2ltl.bls.definability.oracle.residuals import state_classes
from aut2ltl.bls.definability.dg.morphism import Alg, build


class DgData(NamedTuple):
    """The pipeline's stations, deterministic form to frozen algebra."""
    aut: "spot.twa_graph"       # the completed deterministic form D
    names: List[str]            # letter names, alphabet order
    init: int                   # initial state of D
    mon: Monoid                 # the closed enriched monoid EM^1(D)
    cls: List[int]              # element -> congruence class (oracle ids)
    group: Optional[Group]      # a group in the quotient, None iff aperiodic
    alg: Alg                    # the canonical frozen algebra


def quotient_of_hoa(path: str, cap: int = 20000) -> Optional[DgData]:
    """Run the oracle pipeline on one HOA file and freeze the algebra.

    Returns `None` when the closure blows `cap`. The algebra is built even
    on a group-bearing quotient (`group` is then set) — callers decide
    whether to refuse it.
    """
    lang = Language.of(spot.automaton(path))
    det = lang.det_generic_minimal()
    aut = spot.postprocess(det, "deterministic", "generic", "complete")
    _gens, _masks, valuations = extract_generators(aut)
    names: List[str] = [valuation_to_letter(v) for v in valuations]
    init: int = aut.get_init_state_number()

    letters = letter_elems(aut, valuations)
    mon: Optional[Monoid] = close(letters, aut.num_states(), cap)
    if mon is None:
        return None

    st_cls = state_classes(aut)
    lin = [tuple(st_cls[st] for (st, _m) in el) for el in mon.elems]
    acc = aut.acc()
    prof: List[Profile] = [profile(acc, el) for el in mon.elems]
    cls: List[int] = refine(mon, list(zip(lin, prof)))
    alg: Alg = build(mon, cls, prof, names, init)
    return DgData(aut=aut, names=names, init=init, mon=mon, cls=cls,
                  group=find_group(mon, cls), alg=alg)


def print_d_line(data: DgData) -> None:
    """The one-line description of the deterministic form."""
    print(f"D        : {data.aut.num_states()} states, letters {data.names}, "
          f"init {data.init}, acc {data.aut.get_acceptance()}")
