# SOSG serialization format — proposition (v1)

A canonical, complete, text serialization of the syntactic ω-semigroup of a regular
ω-language `L`, together with the acceptance data that recovers `L` from it. The core
sections are a **complete language invariant** (Theorem 5.1 of `sos_constructed.md`):
two languages over the same `AP` are equal iff their cores are byte-identical after the
canonical keying below. An optional residuals section carries the right-congruence for
consumers that want an FDFA-shaped object; it does not participate in the equality test.

This is a *proposition* — contents and semantic constraints, one worked example. No
concrete grammar is fixed here; the token layout of the example is illustrative, the
constraints are normative.

## The canonical ordering (the spine everything references)

All canonicity flows from one declared order. A file **must** fix it and derive the
rest:

1. **`AP` order.** The atomic propositions are listed in the **canonical order** —
   lexicographic by proposition name — `a₁ < … < a_k`. This is a *convention*, not a
   free choice: the declaration merely echoes it, so that two files produced
   independently for the same `L` are byte-identical rather than equal-up-to-a-chosen-
   order. Everything below is then a function of `L` alone.
2. **Letter order.** A letter is a subset `σ ⊆ AP` (`Σ = 2^AP`). Letters are ordered by
   their characteristic tuple `(χ_σ(a₁), …, χ_σ(a_k))` lexicographically, with
   `absent (0) < present (1)`. (For a single `a`: `!a < a`.)
3. **Shortlex on words.** Finite words are ordered shortest-first, ties broken
   left-to-right by letter order. The empty word `ε` is least.
4. **Class keys and ids.** Each `S(L)₊¹`-class is keyed by its **shortlex-least
   representative word**. Classes are listed, and given ids `0,1,…`, in the shortlex
   order of their keys — so id `0` is always `[ε]`, the identity.
5. **Linked-pair order.** A linked pair is a pair of class ids `(s, e)`; pairs are
   ordered lexicographically by `(s, e)`.

Two automata for the same `L` produce the same keys, hence the same ids, hence the same
core bytes — this is what makes the file an invariant rather than a dump.

## Core sections (the invariant)

Membership of any ultimately-periodic word, hence `L`, is determined by these alone.

- **Header.** Format tag and version.
- **`ap`.** The atomic propositions in their declared order (constraint 1). Fixes the
  whole ordering.
- **`classes`.** Count, then one line per class: `id  key`, where `key` is the
  shortlex-least word (`;`-joined letters, `ε` = empty). Listed in id order = key order
  (constraint 4). *(No idempotency flag: `e` is idempotent iff `mult(e,e)=e`, derived.)*
- **`letters`.** For each letter `σ` in letter order (constraint 2), the class id of the
  one-letter word `σ`. This is the generator action; it need not be the class whose key
  is `σ`.
- **`mult`.** The `|classes|×|classes|` multiplication table of `S(L)₊¹`, rows and
  columns in id order; entry `(i,j)` is the class of `rep_i·rep_j`. This is the full
  semigroup — the ω-structure (infinite power, mixed product) is *not* stored, being the
  standard linked-pair completion: `π(s)` is `s` iterated to idempotence in this table,
  and a linked pair `(s,e)` addresses `u·z^ω` with reps `⟦u⟧∈s`, `⟦z⟧∈e`.
- **`accept`.** The **saturated** set of accepting linked pairs: *every* `(s,e)` with
  `e` idempotent, `s·e = s`, and `u·z^ω ∈ L` for its reps — listed, in linked-pair order
  (constraint 5). Saturation is required: membership of an arbitrary `u·z^ω` is decided
  by folding to `(s,e)` and testing presence directly, so the reader never computes
  conjugacy. `L` and its complement share every section but this one.

**Completeness.** To test `u·z^ω`: fold `u`, `z` to class ids through `letters`+`mult`;
compute `e = z` iterated to idempotence; set `s = u·e`; accept iff `(s,e) ∈ accept`.
Regular ω-languages agree iff they agree on ultimately-periodic words, so the core
decides `L`.

## Optional section — `residuals`

The core determines membership but not, cheaply, the **right congruence**
`u ∼ v ⟺ u⁻¹L = v⁻¹L` — the leading (derivative) automaton an FDFA consumer wants. When
present, `residuals` supplies it as a deterministic automaton over `Σ`:

- **Contents.** A count; one line per residual class `id  key`, keyed by the
  shortlex-least prefix word reaching that residual (so id `0` is `ε`, the residual `L`
  itself); and a derivative table `residual × Σ → residual`, rows in residual-id order,
  columns in letter order.
- **Constraint.** It is the minimal DFA of `∼` (Myhill–Nerode for residuals), so it is
  itself canonical when produced — no free choice beyond the `AP` order already fixed.
  It is a standalone derivative automaton; a consumer builds an FDFA by pairing it as the
  leading automaton with progress read off the core.

**Byte-identity semantics.** Language equality is decided on the **core only** (header
through `accept`). The `residuals` section is optional: a file with it and a file without
it both faithfully represent the same `L` and are *not* required to be byte-equal to each
other. When two files both carry `residuals`, those sections are byte-equal iff the cores
are (both being functions of `L`). Equality tooling compares cores and ignores an absent
or present residuals block.

## Worked example — `𝓘(GF(aa))`

`L = GF(a ∧ Xa)` over `AP = {a}`, so letters `!a < a`. Computed from a run-parity
2-state form (`|EM¹| = 10`); the identical core results from a minimal reset form
(`|EM¹| = 7`), the automata being non-isomorphic.

```
SOSG v1
ap: a
classes: 6
0  eps
1  !a
2  a
3  !a;a
4  a;!a
5  a;a
letters: !a->1  a->2
mult:
     0 1 2 3 4 5
  0  0 1 2 3 4 5
  1  1 1 3 3 1 5
  2  2 4 5 2 5 5
  3  3 1 5 3 5 5
  4  4 4 2 2 4 5
  5  5 5 5 5 5 5
accept:
  5 5
```

Reading it: `[a·a]` (id `5`) is two-sided absorbing ("contains `aa`"); every power cycle
has period `1`, so `S(L)₊¹` is aperiodic — `L` is LTL. The one accepting linked pair
`(5,5)` says `u·z^ω ∈ L` iff the recurring loop `z` contains an `aa`. To test, e.g.,
`(a·!a)^ω`: `z = a·!a` folds to class `4`; `4` iterated — `4·4 = 4` — is already
idempotent, `e = 4`; `s = ε·4 = 4`; `(4,4) ∉ accept`, so rejected (correct — isolated
`a`'s, no `aa`).

`GF(aa)` is prefix-independent, so its optional residuals section is a single state:

```
residuals: 1
0  eps
res-mult:
     !a a
  0  0  0
```

For contrast, a language with structure on the finitary side — `Even` — would carry a
four-residual derivative automaton here (the parity pair, the accepting and rejecting
sinks), while its core `accept` block would list the three accepting pairs into its
absorbing accept class. The residuals block never changes the equality verdict; it only
hands the finite-word/learning consumer the leading automaton for free.

## Dropped / derived (recorded, not stored)

- **idempotency** of a class — `mult(e,e)=e`.
- **the ω-semigroup structure** (infinite power `π`, mixed product) — the linked-pair
  completion of the tabulated `S(L)₊¹`.
- **conjugacy** of linked pairs — never needed by a reader, because `accept` is
  saturated.
- **class representatives beyond the key** — any word's class is folded through
  `letters`+`mult`.
