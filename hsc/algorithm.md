# hsc — algorithms

Abstract description of the kernel. Written before the code; the code is
meant to read as its transcription. Section marks `§` refer to
`research_notes/hsc_core.md`.

---

## 1. Objects

A **shape** is `V ::= 1 | ⟨A⟩ | (V_h , V_t)` — the unit sort, a leaf
importing a support algebra, or an ordered pair. Shapes are interned:
structurally equal shapes are one object with one `uid`.

The unit sort exists at one shape only and has no frontier, so no position
addresses it. It is where classification values live, and it carries three
roles that are one object: the **terminal value** `1`; the **default
classification**, acceptance — the value a word earns by reaching it; and
the base case of the **default classifier**, the continuation, whose
residual once every coordinate is consumed *is* that value. That last
identity is why classifying against the continuation reproduces the normal
form: the normal form is the special case of the quotient operator whose
classifier is the tautological one.

A **position** is a path: a tuple of bits, `0` = head, `1` = tail, read
from the root. The frontier of a shape is its leaves in path order.

A **diagram** over a shape is, by cases on the shape:

- `None` — the adjoined zero, at every shape. Never stored inside a node,
  never traversed, never a letter (§0, discipline 1).
- at `1` — the terminal `ONE`, a singleton. Over the Boolean coefficients
  it is the only nonzero value at that sort; a weighted pass replaces it by
  a coefficient without touching anything that refers to it.
- at `⟨A⟩` — a canonical, nonempty leaf code, whatever the leaf module
  says it is.
- at `(V_h,V_t)` — a `Node`: a nonempty tuple of pairs `(prime, sub)` with
  `prime` a nonzero diagram over `V_h`, `sub` a nonzero diagram over
  `V_t`, the primes pairwise disjoint **(D)** and the subs pairwise
  distinct **(F)**, sorted by the sub's uid.

**There is one diagram type, not two.** A prime over a composite head is a
diagram over that head — Theorem 6.4's internalization is the class
hierarchy, not a later test. The same recursion computes the support
algebra of a leaf shape (by delegation) and of a pair shape (by recursion).

Nodes are hash-consed on `(shape.uid, ((prime.uid, sub.uid), ...))`, so
equality is `is` and zero is absence. Leaf codes get uids from a side
table keyed on `(shape.uid, code)`; this is what gives a total order for
canonical sorting, and it is the only thing the kernel ever asks of a leaf
code besides hashability.

---

## 2. `normalize` — Theorem 5.1, operationally

```
normalize(shape, rectangles) -> Node | None
```

Input: any finite list of rectangles `(prime, sub)`, overlapping and
repeating freely. Output: the unique canonical node denoting their sum.

Construction 5.3 read literally enumerates sign-pattern cells and is
exponential. Instead, insert incrementally into a maintained disjoint
partition:

```
cells := []                                  # invariant: primes pairwise disjoint
for (p, s) in rectangles:
    if p is zero or s is zero: skip          # smash, before anything is written
    rem := p
    next := []
    for (q, t) in cells:
        if rem is zero: keep (q,t); continue
        i := meet(V_h, rem, q)
        if i is zero: keep (q,t); continue
        r := diff(V_h, q, i)                 # relative difference — tier G, no top
        if r nonzero: keep (r, t)
        emit (i, join(V_t, t, s))            # the overlap takes the joined sub
        rem := diff(V_h, rem, i)
    if rem nonzero: emit (rem, s)
    cells := next
group cells by sub uid, joining their primes                     # (F)-compression
sort by sub uid; return None if empty, else the interned node
```

The two loops are the degeneracy ledger of §5 executed: the skip is *no
zero subs*, the disjointness maintenance is **(D)**, the grouping is
**(F)**, and *no zero primes* holds because every emitted prime is a
nonempty meet or a nonempty relative difference. The all-negative cell of
Construction 5.3 — the one that would need a top — is never formed,
because `rem` is only ever *carved out of an input prime*, never out of the
ambient carrier.

`normalize`, `join` and `diff` are **mutually recursive**: normalizing at a
cut joins subs one level down, which normalizes at the next cut. This is
the kernel's central recursion; the memo tables hang off it.

---

## 3. The support algebra, uniformly

Four operations, defined at every shape, each dispatching on the shape:

| op | at `1` | at `⟨A⟩` | at `(V_h,V_t)` |
|---|---|---|---|
| `is_zero` | the diagram is `None` | code is empty (leaf decides) | the diagram is `None` — a pointer test (§6, Prop. 6.3) |
| `meet(a,b)` | `1` | leaf meet | rectangles `(p∧q, s∧t)` over all pairs, dropping zeros, then `normalize` |
| `join(a,b)` | `1` | leaf join | `normalize(a.pairs + b.pairs)` |
| `diff(a,b)` | `0` | leaf relative difference | see below |

`diff(a, b)` at a pair, per `(p,s)` of `a`: carve `p` against each `(q,t)`
of `b`, emitting `(p∧q, s∖t)` for the overlaps and `(p ∖ ⋃q, s)` for what
survives. Every step is a meet or a *relative* difference; no complement
and no top is formed at any shape, which is the point of tier G.

There is no `top` and no `complement` in the kernel. A leaf may export
them; nothing here calls them.

Emptiness at a composite shape is a pointer test *because* zero-freeness
is maintained by construction — the self-maintenance loop of Prop. 6.3.
Debug mode asserts the invariant at every `normalize`; release mode assumes
it. A release-mode failure that debug mode would have caught is by
construction a coefficient-discipline violation.

---

## 4. Homomorphisms

A homomorphism is a Python object with an `apply(shape, diagram)` and a
cache keyed on `(hom, shape.uid, diagram uid)` — the `(term_id, data_id)`
cache of the spec. Homs are frozen and hashable; terms are *not*
canonicalised (§14(v) is open), only their applications are shared.

**Local homs** address one frontier position and recurse down the spine to
it. At a pair, a path starting `0` transforms the *primes* (which are
diagrams over the head, so the recursion is the same function), a path
starting `1` transforms the *subs*.

- `Filter(path, code)` — meet the leaf at `path` with `code`. Nothing else
  changes; some primes or subs may become zero and drop out. Note the
  filter is never materialised as data: no cylinder over the other
  coordinates is built, so no top is needed. This is §4's "two faces" with
  the bridge deliberately not bought.
- `Assign(paths_to_codes)` — the parallel assign of §7.1, restricted to
  constant writes. Replace the leaf code at each listed path. This is
  memory-destructive, so previously-distinct primes may collide; the
  collision is exactly what `normalize` merges when the rewritten
  rectangles are reinserted. Nothing special is needed for it.

Both recursions rebuild bottom-up through `normalize`, so the result is
canonical by construction — "well-definedness is restored, not assumed"
(§0).

**Combinators.** `Compose(h_k, ..., h_1)` applies right to left, like `∘`.
`Sum(h_1..h_n)` joins the results — the enrichment's join. `Star(h)` is the
least fixpoint of `X ↦ d ∨ h(X)`, iterated until the root pointer stops
changing; with hash-consing that pointer test *is* the per-run certificate
of §8, and any fair schedule reaches the same fixpoint by monotonicity.

---

## 5. Measurement

- `size(d)` — per-node prime counts, summed: the §13 measure. Reported per
  level so the congruence tower is visible.
- `count(d)` — number of words denoted.
- `bill()` — leaf-call counters since the last reset. The three-factor cost
  claim of §9 is something the prototype must *measure*; the counters are
  the invoice, and they exist from the first commit so that no later claim
  is made without one.

---

## 6. `split_equiv` — the partition primitive

The one primitive the elementary layer and the quotient constructor share:

```
split_equiv(shape, d, expr) -> Partition of d
```

Partition the diagram `d` into the pieces on which `expr` takes each
realised value; zero pieces are absent, so the returned map's key set *is*
the discovered alphabet `Λ(d, expr)` of §9.

Traversal, in three movements.

**Down.** Travel to the first frontier position in `expr`'s support. A
classifier that mentions nothing in a subtree returns there in one entry
without descending: locality is the distance-zero case, and it is free.

**Across.** At a leaf, ask the leaf module to split its code by the
expression — this is where a leaf gets to be clever (an interval leaf
returning `{0,3,6,9}` as one periodic code rather than four intervals) and
where the third cost factor lives. Meeting a coordinate substitutes its
class and renormalises, so the residual stays ground and mentions only
positions not yet consumed; a consumed coordinate can never be re-queried.
Because expressions are interned, grouping head-classes by residual code
and keying the memo table on that code are the same act.

Normalisation must happen *while a residual curries*, not only when a
client writes an expression. An applied operation therefore carries the
builder that made it, and substitution rebuilds through that builder;
rebuilding through a generic constructor normalises at the wrong time,
which is to say never.

A level whose classifier mentions nothing below it does not descend, but it
still *federates*: one class is a partition too, and its kernel must be
comparable with everyone else's. Two one-class partitions arise for
different reasons and must not be conflated — one labelled by a **value**
(the terminal case; with the value `1`, acceptance) and one labelled by a
**residual expression** (a suspended computation: nothing here separates
anything, ask below). Same kernel, different labelling, which is exactly
what splitting kernel from labelling is for.

**Up.** Results federate. A partition is stored as its *kernel* — the
canonical, interned tuple of pieces — plus a labelling from residuals into
it. Two subqueries whose residual codes differ but whose realised
partitions agree are recognised here and share one kernel object, keeping
only their labellings apart. This is the retroactive repair for weak leaf
normalisation and the place the equivariant collapse appears; it is not a
code path but what the merge finds when the structure is there. The parent
then reassembles by (F)-compression.

Measured on the residue example: `(b+c) mod 3` curries to three residual
codes at the first coordinate and issues eleven subqueries below it, both
independent of the carrier's range, and the subqueries collapse onto five
kernels — one of them absorbing every residual that reaches the `<c>` sort.
The kernel count is an invariant of the classifier on the data; a leaf that
normalised its terms less would issue more subqueries to arrive at the same
kernels, which is what it means for normalisation strength to be a cost
parameter and never a soundness one.

Everything above is then a caller of this one function, distinguished only
by the codomain of `expr` and by what it does with the pieces:

| caller | codomain | tail action |
|---|---|---|
| single-variable `filter` | binary | keep the accepting piece; does not travel |
| multi-variable `filter` | binary | keep the accepting piece |
| `assign(x := e)` | value sort | rewrite `x` per piece |
| `Θ` | any declared sort | keep all pieces, labelled |
| `case` | any declared sort | apply the per-letter branch |

Consequence for the theory: Theorem 7.2 merges adjacent filters by meets,
which is canonical but anti-optimal — merging two single-variable guards
produces a two-variable guard that must now travel. The implementation
keeps guards *factored* by support and ordered by frontier position. The
theory does not care (the two are semantically equal); §14(v) should note
that the executable presentation factors where the canonical one merges.

**Not on the plate:** inverse images. Undoing a destructive assignment
needs a reachable set to move within, which is a different problem (CTL);
the interface has no absolute or relative preimage and is not expected to
grow one.
