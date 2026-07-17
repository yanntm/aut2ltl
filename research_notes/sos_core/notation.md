# Notation conventions (editors' note)

*Not paper text — the paper never states these rules; its notation just obeys
them. Editors keep them in mind; reusable across papers.*

One base letter per sort; decorations carry roles, never identity.

- **Sorts.** Formal letters `x, x₁, …, xₙ ∈ Σ`; concrete letters `a, b` (a
  third concrete letter `c` is tolerated in isolated examples). Finite words
  are `u`/`v` variants: the `u` family for stem-position material (prefixes,
  stems, tested words), the `v` family for loop-position material. `w` is
  reserved for ω-words — lassos — with `w = u·v^ω` the canonical shape.
  Classes: `c, d` for generic elements of the carrier `𝒞` (lowercase of the
  carrier), `s` for stem classes, `e` for idempotents; acceptance
  pairs are `(s, e)`. Maps are calligraphic (`𝒮` the stamp) or Greek (`θ` for
  isomorphisms, `λ := 𝒮|_Σ` the letter map, `π` the idempotent exponent). `^ω` means infinite repetition,
  exclusively; the idempotent power is `^π` — no algebra element ever wears
  `^ω`.
- **Automaton sorts.** States `p, q ∈ Q` — `q₀` the initial state, `p` the
  running states of a run; marks `f ∈ F`, mark sets `N ⊆ F`; `mk(q, u)` /
  `mk(q, c)` the marks a finite run collects, `mk^∞` the recurring set.
  Enriched elements act on states from the right, `q·c` — the state sort on
  the left keeps the product unambiguous.
- **Decorations.** *Prime* = counterpart: a second object of the same sort in
  the same role, typically a replacement (`u ≈ u'`, `v'`). *Indices `1, 2, …`*
  = ordered pieces of one object, where concatenation or application order
  matters (`v = v₁·v₂`, `x₁⋯xₙ`); never used for a mere pair of peers. *Index
  `0`* = ambient context material, neither counterpart nor piece (`u₀` a stem
  prefix, `v₀` a loop completion).
- **Effect.** Statements typecheck by eye: the sort and role of every symbol
  is readable from its shape. Every definition and statement still opens with
  a `Let` binder declaring each object's sort (`let u, u' ∈ Σ⁺ …`) — the
  decorations never carry information the binder does not state; they make it
  skimmable.
