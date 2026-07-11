# aut2ltl.sos2ltl.cascade — the decomposition fallback (source map)

The per-layer delegate below the walk+window engine (spec E11, paper
§6): a layer the engine cannot transcribe — no anchoring width (stem
side), or no window/config width determining its verdict (loop side) —
descends to a Krohn–Rhodes cascade through the `aut2ltl.bls` machinery
the portfolio's peelers already floor on. The construction is
`algorithm.md` in this folder; the machine descent replaces the two DG
calls of the architecture's steps 3(b) and 4.

## Modules

- **`machine.py`** — the shared seam: a scoped deterministic
  transformation machine (states, per-letter images) from a layer —
  the totalized `A_R` (stem) or the tail-restricted acceptor (loop) —
  handed to the bls gap bridge (`decompose_gens` / `decompose_aut`),
  returning a `CascadeHolder` plus the height / per-level ledger
  record.
- **`stem.py`** — Prop 4.14 with the cascade extractor: the exit
  disjunction `⋁_c reach_to(ι_R, C_c, θ_c)` over the reach family,
  children labels supplied by the engine's memo.
- **`loop.py`** — the acceptance term `W(R)` / `Ω(R, r)` off the
  scoped acceptor's decomposition: lifted acceptance, `Fin(C)`
  combination per acceptance class (the existing bls member assembly).

Probes live in `tests/sos2ltl/` (worked instances, the E11 ledger);
they gate through the conformance gate — on the loop branch the gate
is the only correctness authority.

## Layering

This subpackage is the **single sanctioned import point** of
`aut2ltl.bls` inside `aut2ltl.sos2ltl` (the parent's "imports nothing
from bls" rule moves here: everything *else* in sos2ltl still imports
nothing from bls). Consumed from bls: `gap` (the SgpDec bridge),
`cascade` (`Cascade`, `CascadeHolder`, config analysis), `operators`
(the reach family, `Fin`), and the acceptance members' assembly.
GAP resolution is the bridge's own: a bare `gap` on `PATH`
(`deps/env.sh` puts the tree's `opt/gap/bin` first).
