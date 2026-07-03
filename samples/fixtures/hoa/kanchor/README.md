# kanchor — fixtures for the graded (k-window) anchored read-off

Hand-written HOA automata exercising `aut2ltl/kanchor` (see its
`algorithm.md`): components whose phase is **not** recoverable from the last
letter (anchor's P1/P2 fail) but **is** recoverable from the last k adjacent
letters modulo stuttering — plus the negative exhibits no window width can
anchor. The k = 1 fixtures live in the sibling `hoa/anchor/` folder.

- `gf_a_xa.hoa` — the minimal DBA of `GF(a & Xa)`, the `algorithm.md` worked
  example: k = 1 fails P1 (states 1 and 2 share the anchor `a`) and P2
  (state 2's loop `a` fires state 1's anchor); the pair windows partition,
  every sojourn collapses to `⊤`, the park drops by `Stay₂ = Enter₂`, and
  the label is exactly `GF(a & Xa)` with no simplifier involved.
- `promoted_stay.hoa` — the state-based automaton of
  `G((a & F!a) | (!b R !a))`: k = 1 fails P1, the pairs pass, and two
  self-loops are promoted (`a` at state 0, `!a & b` at state 2). The
  promoted edges carry the label: state 2's staying pairs re-fire its own
  promoted entry, so the `GF` accepts the run parked there and the park
  terms drop, while the promoted law row legislates the position after a
  stay.
- `promoted_q0_park.hoa` — a promoted loop at `q0` (`a & b`) on a k = 2
  component whose `q0` carries every color: the word reading `a & b` at
  position 0 and then parking on the residual idle `!a & !b` is accepted
  only through the truncated rows the promoted edge contributes — the
  0-step start law `a & b → X sojourn(q0)` and the 0-step park
  `a & b ∧ XG(!a & !b)`; position 0 has no predecessor pair, so no full
  window can see that entry.
- `gf_a_xa_nd.hoa` — the natural 2-state NBA of `GF(a & Xa)`: state 0 reads
  `a` and may stay or move — in-component nondeterminism from a single
  source, which no window width resolves; kanchor declines at every level
  (the deterministic sibling `gf_a_xa.hoa` anchors at k = 2).
- `gf_aaaa_nd.hoa` — the same shape one size up, the 4-state NBA of
  `GF(a & Xa & XXa & XXXa)`: declines at every level; its deterministic
  form is a 5-state counter chain needing a 4-letter window, beyond the
  k ≤ 2 ladder (algorithm.md, layer 12 — form dependence).
