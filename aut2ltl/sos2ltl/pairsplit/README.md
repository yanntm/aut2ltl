# aut2ltl.sos2ltl.pairsplit — the SoS pair decomposition

Splits the translation problem on the invariant itself: the accepting
linked-pair set `P` partitions into saturation atoms (ω-classes), fusable by
criteria the translation exploits; the side (`P` or its free complement `P̄`)
with the fewest atoms is translated piecewise over the SAME table and the
labels recombine with `∨` (outer `¬` iff complemented). `algorithm.md` holds
the construction (atoms, the least-pairs rule, fusion criteria, verdict
inheritance); this file maps it to the code.

STATUS: doc stage — algorithm agreed first, code is its transcription.
Planned shape:

- `decompose.py` — atoms of a `PairSet` (via `sosl.sos.calculus.surgery`
  saturation), the least-pairs side choice, the fusion groupings (same loop
  class / same layer / free-AP projection per piece).
- `combinator.py` — the invariant-plane combinator: split → per-piece
  `reduce` + `remove_free_aps` → engine → `⋁` (+ `¬`). Declines poison the
  split; verdicts inherit aperiodicity (algorithm.md).
- Wiring: ONE injection seam in the sos2ltl assembly (between the bridge and
  the engine), consumed by a recipe; the engine, delegate and calculus are
  used as-is. The cascade loop half's acceptor presentation for pieces is
  the open interface point (algorithm.md "Where it sits").

Relatives: `sosl/sos/calculus/` (the primitive layer — Boolean ops on pair
sets, `reduce`, witnesses), `aut2ltl/decomp/` (the automaton-level shadows:
acceptance / scc / strength / inv).
