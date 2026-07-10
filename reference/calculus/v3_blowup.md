# V3 — Prop 3.4 blow-up: |𝒞(W·L_n)| ≥ 2^n − 1

- date: 2026-07-10
- git: d0329a3c3
- per-case budget: 15 s (the construction, not Spot)

Directly built deterministic Emerson–Lei automata; `|𝒞|` via `invariant_of ∘ canonical`. Encoding (trap #9): the increment class carries two letters `a := (¬p∧¬q)|(p∧q)`, with `b := p∧¬q`, `# := ¬p∧q` — Prop 3.4 survives verbatim.

| n | classes(L_n) | classes(W·L_n) | bound 2^n−1 | W·L_n states | construct ms |
|---|---|---|---|---|---|
| 2 | 5 | 17 | 3 | 5 | 0.73 |
| 3 | 7 | 48 | 7 | 9 | 4.03 |
| 4 | 9 | 127 | 15 | 17 | 35.86 |
| 5 | 11 | 318 | 31 | 33 | 364.31 |

Every finished row satisfies the bound `|𝒞(W·L_n)| ≥ 2^n − 1`, so the syntactic semigroup blows up exponentially even though the automaton stays at ≤ 2^n + 1 states.
