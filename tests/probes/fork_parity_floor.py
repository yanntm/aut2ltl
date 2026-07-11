"""Where does `Fork` sit in the max-even parity shape family?

    python3 tests/probes/fork_parity_floor.py

`Fork = (a & GFa) | (!a & FG!a)` is the smallest derivative-regime language
(sos_classification.md §5); its natural acceptance `Inf(0) | Fin(1)` is a
*min*-even two-colour parity condition, while the genaut census enumerates
`parity max even c` (gen/build.py). This probe asks Spot for Fork's minimal
deterministic **max-even** parity form — states and colour count — i.e. the
first census shape `<n>state1ap<c>acc_parity` that can hold a Fork-shaped
language at all. Prints the postprocessed automaton's header data.
"""
from __future__ import annotations

import signal

import spot

FORK = "(a & GFa) | (!a & FG!a)"


def main() -> int:
    signal.alarm(15)
    aut = spot.translate(FORK)
    for mode in ("parity max even", "parity"):
        p = spot.postprocess(aut, mode, "deterministic", "complete")
        acc = p.get_acceptance()
        print(f"{mode:16s}: states = {p.num_states()}, "
              f"colours = {p.num_sets()}, acc = {acc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
