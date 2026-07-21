# hsc/ops — algorithms

Homomorphisms: terms with a code action. Three families — local homs,
combinators, and classifier-driven homs — plus the two open questions this
package is where we will have to answer.

---

## 1. Application

A hom is a frozen, hashable object with an `_apply(shape, diagram)`, and
application is cached on `(hom, shape.uid, diagram uid)`. Terms themselves
are *not* canonicalised — see §4 — so only applications are shared, and the
cache does not care.

Every `_apply` rebuilds through `normalize`, so canonicity is restored after
each action rather than assumed to be preserved by it.

---

## 2. Local homs

A local hom addresses one frontier position. The recursion is the point:

> **A local hom at a cut is the same hom one level down**, applied to the
> primes when the path turns into the head and to the subs when it turns
> into the tail.

Recursing by re-invoking the hom, rather than by calling a helper, is what
keeps the traversal shared. A hom that recursed through a plain function
would walk the diagram's *tree unfolding* instead of its DAG, discarding
exactly the sharing that makes the representation worth having. Measured on
the philosophers: making this change turned leaf traffic from superlinear
into exactly linear in the number of philosophers, and made one full step on
a fixpoint cost zero uncached operations.

- `Filter(path, code)` — meet the leaf at `path` with `code`. No cylinder
  over the other coordinates is built, so no top is needed anywhere: the two
  faces of a support are kept apart on purpose, and the bridge between them
  is the tier-B purchase this kernel declines to make.
- `Write(path, code)` — overwrite one coordinate with a constant.
  Memory-destructive, so previously distinct primes may collide; the
  collision is precisely what re-normalisation merges, and nothing special
  is needed for it.
- `Assign(writes)` — the parallel form, the primitive. Sequential writes
  cannot express a simultaneous exchange without temporaries. With constant
  right-hand sides the writes commute, so their order is immaterial.

---

## 3. Classifier-driven homs

Each is `split_equiv` plus a decision about the pieces, and nothing here
re-implements the traversal.

- `Guard(expr)` — keep the accepting piece. Over one coordinate it does not
  travel and is the plain filter; over several it curries.
- `Put(path, expr)` — split by the value of the right-hand side, write that
  constant on each piece, re-fuse.
- `Case(expr, branches)` — quotient, act per class, re-fuse. Each branch is
  invoked **once per congruence class**, not once per element and not once
  per declared letter: the branch set is discovered, minimal and canonical.
  A letter with no branch is dropped unless a default is given; a branch
  with no realised letter is never invoked.

---

## 3b. Blocks travel; leaves get soup

*The intended architecture. The code does not do this yet: `Compose`
currently applies its parts one after another, which is n full traversals of
the diagram where this design is one.*

**`skip` is compositional.** A composition skips a level exactly when every
part does, so a block's footprint is derivable from its parts' and a block
of operations descends **as one object** for as long as it skips. Support is
not primarily a hint for a schedule; it is what decides how far a
composition travels before it has to act.

**A block parenthesises at the level it cannot skip**, splitting along the
two congruence directions: the part acting on the head goes to the *edge*,
applied to the primes; the part acting on the tail goes *down*, applied to
the subs; the node rebuilds through `normalize`. This is the node
materialising its own congruence and deferring the other, seen from the
operator side instead of the data side.

```
apply(block, shape, d):
    if every part skips this shape:  return d                    # travel through
    if shape is a leaf:              return leaf.apply_local(d, block)
    split block across the cut -> (edge parts, tail parts, crossing parts)
    for (p, s) in d.pairs:  p' = apply(edge parts, head, p)
                            s' = apply(tail parts, tail, s)
    normalize
```

Memoised on `(block, shape, diagram)`; the split is cached per
`(block, shape)`. Single-position homs are the degenerate case, a block of
one.

**A leaf is handed a maximal local block, not an opcode.** The framework's
obligation stops at delivering the whole composition whose support lies in
one leaf; what the leaf does with it is the theory's business. A BDD theory
fuses guard and update into one relation over interleaved current/next
variables and applies it with a single relational product; a finite
enumerated theory simply executes the parts. The normal form for
compositions is therefore **per theory**, and the framework must not
prescribe one.

Splitting a block is licensed by parts with disjoint support commuting —
the same independence partial-order reduction rests on. That is why §4 and
§5 below are one question and not two: the rules that let a block reorder
and fuse are the rules that let it split at a cut and travel.

A part whose support *crosses* a cut can go to neither side. That is
precisely and only where `split_equiv` fires — the genuinely non-Kronecker
case, a guard or an assign relating coordinates in different leaves. A
system whose every event is a tensor of local actions never reaches it,
which is why a Petri-net-like protocol is entirely blocks travelling and
leaves fusing, with the quotient constructor never invoked. That fragment is
the declared regime of §11, named there as exactly the one in which `Θ` is
never invoked.

---

## 4. Open: the term normal form

The calculus document canonicalises an elementary term to a strictly
alternating guarded word, merging adjacent filters by meets. That is
canonical and **anti-optimal**, and the document's framing of it
over-assumes: merging two single-coordinate guards produces a
two-coordinate guard that must now travel, where separately they never
would.

The shape of the right answer is not a canonical word but a **confluent
rewriting system** whose rules consult commutativity and the *relative
support* of operands to decide reordering. Independence of supports is the
same notion partial-order reduction uses to justify not exploring both
interleavings of independent events; here it justifies commuting, merging or
refusing to merge two terms. The reordering such a system enacts is also
what a schedule needs (§5), so these are one problem seen twice, not two.

This is the package's principal open question and it is a theory question
before it is a coding one.

---

## 5. Open: the schedule

`Star(h)` is the least fixpoint of `X ↦ d ∨ h(X)`, iterated until the root
pointer stops changing. With hash-consing that pointer test is the per-run
certificate, and monotonicity makes every fair schedule agree on the value —
so scheduling lives strictly below the semantics.

It does not live below the *cost*. Plain BFS rebuilds a fresh diagram every
round, so every round misses the caches: cost is rounds x events x |X| in
freshly built nodes. Saturation — applying each event at the lowest cut its
support touches, taking a local fixpoint there, memoised per node — is the
known answer, and with a shape tree an a-priori grouping per cut is
available that a flat variable order cannot express.

Two things must be settled first, and neither is settled in the calculus
document, which does not discuss schedules at all:

- **`support()` is a static over-approximation.** It is the complement of
  libDDD's `skip`, but `skip` is *minimal* and may be *dynamic*: an
  operation reading `tab[x]` has a static support covering all of `tab`,
  while its actual footprint depends on the data. Static support is adequate
  only while every footprint is static, which is true of everything in this
  prototype today and will not stay true.
- **Order within a cut is subtle.** Saturating the tail before the local
  level is required; filters want to be applied before moves; and the
  re-saturation of children after a crossing event fires has to terminate.

Groundwork present: `Hom.support()` and `Hom.rerooted(bit)` on every hom.
No saturation is implemented, deliberately.
