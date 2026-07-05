# objects — canonical algebra and membership read-off

Dev-facing notes on the two things in this module that are more than plumbing:
what makes the invariant *canonical* (so byte-equality is a sound equality
test), and how a lasso's membership is decided from the algebra alone.

## The syntactic congruence

Finite words `p, q` are congruent for `L` when they are interchangeable in both
context shapes an ω-word can put them in:

    (linear)  ∀ x, y ∈ Σ*, t ∈ Σ+ :  x.p.y.t^ω ∈ L  ⇔  x.q.y.t^ω ∈ L
    (omega)   ∀ x, y ∈ Σ*         :  x.(p.y)^ω ∈ L  ⇔  x.(q.y)^ω ∈ L

The linear shape places `p` in a finite context inside an eventually-periodic
word; the omega shape places `p` in the *period* itself. A right-congruence
(Myhill–Nerode for ω, the FDFA world) captures only a projection of this; the
omega shape is what forces the full two-sided congruence, and it is the reason a
plain right-congruence learner stalls (cf. `learn/algorithm.md`, saturation).

The quotient is a finite monoid once the empty word is adjoined as identity.

## The invariant `I(L) = (C, key, λ, M, P)`

- `C` — the finite set of congruence classes.
- `key : C → Σ*` — the **shortlex-least** word of each class. Shortlex (length
  first, then a fixed letter order) makes the representative unique and
  deterministic, hence the serialization canonical.
- `λ : Σ → C` — the class of each single letter.
- `M : C × C → C` — the class multiplication table (well-defined because `C` is
  a congruence).
- `P ⊆ C × C` — the accepting **linked pairs**: pairs `(s, e)` with
  `M(e, e) = e` (idempotent loop) and `M(s, e) = s` (stem absorbs the loop),
  such that `key(s).key(e)^ω ∈ L`.

## Membership read-off (the read-off is the whole point)

To decide a lasso `(u, v)` from `I(L)` with no automaton:

1. fold `u` and `v` to their classes via `λ` and `M`;
2. iterate the loop class to an **idempotent** `e` — by Ramsey/finiteness some
   power `[v]^k` is idempotent; take it (bounded by `|C|`);
3. set `s = [u] · e` (fold the stem, then absorb one idempotent loop);
4. accept iff `(s, e) ∈ P`.

Idempotence makes step 3 independent of *which* power was chosen, so the
verdict is well-defined. This procedure is the normative meaning of the
invariant and is what `validate/`'s acceptor check exercises against direct
automaton simulation.

## Canonical serialization (why byte-equality is sound)

Two invariants over the same `AP` denote the same language iff they are equal as
algebras up to class renaming. Canonicalization removes the renaming freedom:
re-key every class by BFS over the step relation from `[ε]` in shortlex letter
order (first word reaching a class names it), order rows/columns of `M` by class
id, and sort the linked-pair set. The serialized text is then a normal form —
byte-equality of two serializations is exactly language equality. Keeping this
property airtight is the reason canonicalization lives here and is re-applied
defensively on parse.

## The Cayley hypothesis (mid-learning) — why it is *not* an invariant

During learning no multiplication table is yet trusted, so an equivalence query
ships a weaker object: a **step** table `step(class, letter) = class` plus a
partial cache of accepting-pair verdicts. Prediction is normative and identical
on both sides (teacher and learner) to keep counterexamples meaningful:

    fold stem and loop through `step` from `[ε]`; find the least k ≤ 2n with
    fold(loop^{2k}) = fold(loop^k); answer the cached/queried bit for the pair
    (fold(stem.loop^k), fold(loop^k)).

The `k ≤ 2n` bound is the stabilization power that stands in for the idempotent
before `M` exists. Getting this semantics byte-identical on both sides is the
subtle obligation of the Cayley form.
