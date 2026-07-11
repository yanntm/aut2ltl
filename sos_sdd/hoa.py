"""Spot `twa_graph` → `Automaton` digest (the parser half of C2).

The digest is exactly what the graph holds — states, AP order, mark
count and the acceptance formula carried verbatim (no postprocess, no
renumbering), each edge condition rendered as irredundant DNF cubes
(minato-isop), one `Transition` per cube.

Obtaining the graph is the caller's business, via the standard APIs:
`spot.automaton(path)` for inputs already in the deterministic complete
form D (the corpus `det/` tiers), `sosl.sos.build.import_hoa` /
`canonical` to normalize anything else. The engine's pipeline is defined
over D, so a nondeterministic or incomplete graph is refused loudly."""

from typing import List

import buddy
import spot

from .model import Automaton, Transition


def _cube_str(cube_bdd: "spot.bdd", aut: "spot.twa_graph") -> str:
    """One isop cube as the digest's literal string (`a&!b`, or `1`)."""
    f = spot.bdd_to_formula(cube_bdd, aut.get_dict())
    if f.kind() == spot.op_tt:
        return "1"
    lits = list(f) if f.kind() == spot.op_And else [f]
    out: List[str] = []
    for lit in lits:
        if lit.kind() == spot.op_Not:
            out.append("!" + lit[0].ap_name())
        else:
            out.append(lit.ap_name())
    return "&".join(out)


def digest_twa(aut: "spot.twa_graph", name: str) -> Automaton:
    """The digest of a Spot automaton already in the form D, verbatim."""
    if not spot.is_universal(aut):
        raise ValueError(f"{name}: nondeterministic input "
                         "(normalize via sosl.sos.build.canonical first)")
    if not spot.is_complete(aut):
        raise ValueError(f"{name}: incomplete input "
                         "(normalize via sosl.sos.build.canonical first)")
    trans: List[Transition] = []
    for e in aut.edges():
        isop = spot.minato_isop(e.cond)
        marks = frozenset(e.acc.sets())
        cube = isop.next()
        while cube != buddy.bddfalse:
            trans.append(Transition(e.src, _cube_str(cube, aut), e.dst, marks))
            cube = isop.next()
    dig = Automaton(name=name,
                    ap=tuple(p.ap_name() for p in aut.ap()),
                    states=aut.num_states(),
                    init=aut.get_init_state_number(),
                    marks=aut.num_sets(),
                    acceptance=str(aut.get_acceptance()),
                    trans=tuple(trans))
    dig.validate()
    return dig
