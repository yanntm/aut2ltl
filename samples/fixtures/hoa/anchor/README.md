# anchor — fixtures for the anchored SCC read-off

Hand-written HOA automata exercising `aut2ltl/anchor` (see its `algorithm.md`):
components whose phase is **anchored-recoverable** (anchors partition, loop letters
shared freely — preconditions P1 + P2) but **not input-deterministic** (the full
entry labels `I(s)` overlap), so the retired `partscc` / `daisystardet` read-offs
decline and only the anchored one applies. Unlike the sibling `hoa/<set>/` folders,
these are not generated from an `ltl/` list.

- `gafb_response.hoa` — the minimal DBA of `G(a → Fb)`; terminal SCC whose two
  states share the idle letter `!a & !b` on their self-loops. The `algorithm.md`
  worked example.
