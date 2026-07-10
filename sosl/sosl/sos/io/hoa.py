"""hoa — a canonical HOA serialization of an ω-automaton.

`aut.to_str("hoa")` is not a normal form. Two things it leaves to Spot make the
bytes depend on the build rather than on the automaton:

* **Acceptance reading.** The printer re-declares state-based acceptance whenever
  it can, *even when the automaton's `state_acc` property was deliberately
  cleared*. Acceptance belongs on the edges (Spot stores it there in every case),
  so the `"t"` option is not a preference; without it a terminal language is
  written `state-acc`.
* **AP order.** The `AP:` line lists the atomic propositions in the automaton's
  registration order, and transitions reference them by *index*. Two Spot builds
  that register `a` and `b` in different orders emit different bytes for the same
  automaton — the corpus has both.

`dump_hoa` fixes both: the APs are re-registered in name order onto a copy (a
real permutation, carried by the shared bdd dict, not a rewrite of the `AP:`
line), and the acceptance is forced onto the edges. The result is a function of
the automaton alone.

Not to be confused with `survey.normalize.names.normalize_hoa`, which rewrites
the `AP:` line's *names* in index order. That is a sound dedup **key** — it
collapses name variants — and an unsound **normal form**: applied to two automata
that differ by an AP permutation it maps both to the same text, silently
relabelling one of them. A key answers "are these the same up to renaming"; a
normal form must not change what the file denotes.

State numbering is left alone. Renumbering states topologically would make these
bytes an isomorphism invariant, which is a stronger claim than the `spot_det`
tier wants: that tier counts *distinct deterministic presentations*, and
presentations differing only by state numbering are distinct to it.

Nothing here assumes the automaton is deterministic, complete, or a canonical
`D`. Serialization normalizes a presentation; obtaining the presentation worth
serializing is the caller's business (`build.importer.canonical`). An export that
silently determinized would be doing the caller's algorithm behind their back,
and an import that did so could not read back what it wrote.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import spot

if TYPE_CHECKING:  # pragma: no cover - annotation only
    pass


def ap_canonical(aut: "spot.twa_graph") -> "spot.twa_graph":
    """A copy of `aut` whose atomic propositions are registered in name order.

    Built on a **fresh** bdd dictionary, because the order the HOA printer
    indexes is the dictionary's variable order, not the automaton's AP list:
    re-registering onto the source's own dictionary reorders the list and emits
    the same bytes. Each edge condition is therefore carried across as a formula
    and rebuilt against the new dictionary, where the variable numbers follow the
    names.
    """
    res = spot.make_twa_graph(spot.make_bdd_dict())
    for p in sorted(aut.ap(), key=lambda f: f.ap_name()):
        res.register_ap(p)
    res.new_states(aut.num_states())
    res.set_init_state(aut.get_init_state_number())
    res.copy_acceptance_of(aut)
    src = aut.get_dict()
    for e in aut.edges():
        cond = spot.formula_to_bdd(spot.bdd_to_formula(e.cond, src), res.get_dict(), res)
        res.new_edge(e.src, e.dst, cond, e.acc)
    res.prop_copy(aut, spot.twa_prop_set.all())
    return res


def dump_hoa(aut: "spot.twa_graph") -> str:
    """`aut` as canonical HOA: APs in name order, acceptance on the transitions.

    Idempotent, and invariant under the order in which Spot happened to register
    the atomic propositions.
    """
    return ap_canonical(aut).to_str("hoa", "t")
