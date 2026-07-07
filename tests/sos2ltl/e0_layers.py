"""C1 + C5 read-offs on one `.sos` invariant (E0 sanity probe).

    python3 -m tests.sos2ltl.e0_layers <file.sos> [--expect gfaa|even|evenblocks]

Prints the Cayley layer structure (R-classes in topological order, with the
R-order edges), the λ-quotient blocks, prefix-independence, and the absorbing
classes. The Lemma 5.3 assertion (SCCs = R-classes) runs inside `build` on
every input. With ``--expect``, asserts the triptych predictions of
`research_notes/sos_toltl_experiments.md` E0.
"""
from __future__ import annotations

import sys
from typing import List

# aut2ltl.sos2ltl first: its package init puts the sibling `sosl` subtree on
# sys.path (no editable install needed), so the `sosl` import below resolves.
from aut2ltl.sos2ltl.cayley import build
from sosl.sos import load_invariant
from aut2ltl.sos2ltl.readoffs import (
    absorbing_classes,
    is_prefix_independent,
    letter_quotient,
)


def main(argv: List[str]) -> int:
    path = argv[0]
    expect = argv[2] if len(argv) > 2 and argv[1] == "--expect" else None
    with open(path) as f:
        inv = load_invariant(f.read())

    cay = build(inv)
    print(f"{path}: {inv.n} classes, {len(cay.layers)} layers")
    for i, layer in enumerate(cay.layers):
        succ = ", ".join(str(j) for j in cay.successors[i]) or "-"
        members = " ".join(str(c) for c in layer)
        print(f"  layer {i}: classes {{{members}}} -> {succ}")
    blocks = letter_quotient(inv)
    print(f"  lambda blocks: {sorted(tuple(b) for b in blocks.values())}")
    pi = is_prefix_independent(inv)
    absorbing = absorbing_classes(inv)
    print(f"  prefix-independent: {pi}   absorbing: {list(absorbing)}")

    if expect == "gfaa":
        assert [set(l) for l in cay.layers] == [{0}, {1, 3}, {2, 4}, {5}], cay.layers
        assert pi is True
        assert absorbing == (5,), absorbing
    elif expect == "even":
        assert pi is False
    elif expect == "evenblocks":
        assert pi is True
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
