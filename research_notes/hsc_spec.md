# HSC — Implementation Direction

*Companion to `hierarchical-shape-calculus` (draft 1). Despite the filename,
this is not a specification: it is a line of implementation — architecture,
concrete representations, an interchange syntax, and ordered milestones with
acceptance gates. Section references (§) point into the calculus document.
Target language: Python. Performance is explicitly not a goal of the
prototype; the products are the API, the measured cost model, and the
falsification of the document's claims.*

---

## 0. Orientation

The three disciplines are implementation decisions already:

| discipline | in code |
|---|---|
| `0` adjoined, never a citizen (§0.1) | the null child is `None`; no node stores, iterates, or hashes it |
| `id` free (§0.1) | the no-op is not an object; empty compositions vanish at construction |
| naming window (§0.2) | hash-consing; equality is a pointer test |
| partition window (§0.2) | partition refinement over leaf codes |
| per-run certificates (§0.3) | memo tables, residual-novelty checks, step counters |

The kernel is standard hash-consed decision-diagram engineering. The one
genuinely new component is Θ's curried residual transport (§9); it is also
the only research contribution, so it is the right place for the risk and
the instrumentation to live.

---

## 1. Core representations

**Shapes.** Interned binary trees over leaf-module references:
`Shape = LeafRef(module) | Pair(Shape, Shape) | Unit`. Positions are
frontier paths (bit strings). Two structurally equal shapes are one object.

**Diagrams.** A node is a frozen, canonically sorted tuple of
`(prime_code, sub_id)` pairs, unique-tabled (a weak dict keyed on that
tuple plus the shape id). Consequences, by construction:

- equality is `is`; zero is *absence* (Python `None`), never a node;
- (F)-compression at build time is "group pairs by sub pointer, join their
  primes";
- (D) and zero-freeness are constructor preconditions, checked in debug
  mode, assumed in release mode — Prop 6.3 says positive coefficients keep
  them true without semantic tests, and the debug assertion is the test of
  that proposition.

**Leaf codes.** Whatever the leaf module says, but hashable and canonical:
the kernel only ever compares them (naming window) or hands them back to
their module (partition window).

**Coefficients.** A `Semiring` protocol: `zero, one, add, mul, eq`,
plus declared flags `zerosumfree`, `entire`. The kernel refuses instances
without both flags (§1); `Bool` is the default; `Nat` is the second
instance and exists to prove nothing outside the leaves changes (§14 (vi)).
Weights live on subs per Theorem 5.1's gauge: primes Boolean, values
quantitative.

**The one central function.**

```
normalize(pairs: list[(prime, sub)]) -> Node | None
```

Theorem 5.1 operationally. Implementation note, against a naive reading of
Construction 5.3: do **not** enumerate sign-pattern cells (exponential);
insert rectangles incrementally into a maintained disjoint partition —
split via leaf `meet`/`diff` (tier G), then merge equal subs by pointer.
Same canonical result, apply-style complexity. Everything else in the
kernel is the classical apply/cache architecture around this function:
`meet`, `join` (recursive, memoized on node-id pairs), `filter` as
meet-with-recanonicalization, `+` on data as `join`, `apply(term, data)`
memoized on `(term_id, data_id)`, `star` as a fixpoint loop whose per-run
certificate is a residual-novelty check.

---

## 2. The Leaf interface

One ABC; its methods are the tier ledger of §2 verbatim. A leaf declares
its tier and implements up to it; the kernel calls only what the operation
at hand consumes (the interface ledgers of §5/§6 say which).

```
class Leaf:
    # tier E
    def code(self, raw) -> Code
    def eq(self, a, b) -> bool            # on codes
    def is_empty(self, a) -> bool
    # tier J
    def join(self, a, b) -> Code
    # tier G
    def meet(self, a, b) -> Code
    def diff(self, a, b) -> Code          # relative difference, no top
    # tier B (optional)
    def top(self) -> Code
    def complement(self, a) -> Code
    # maps (§2.3), per exported map f
    def pushforward(self, f, a) -> Code                   # image-computable
    def weighted_pushforward(self, f, a) -> WeightedCode  # fiber-computable (optional)
    def rel_preimage(self, f, a, b) -> Code   # f⁻¹(a) ∩ b (optional, per map)
    # terms (§2.4)
    def normalize_term(self, expr) -> Expr    # canonical codes for curried classifiers
```

Rules of the house:

- Unimplemented tiers raise `TierError`. This turns the interface ledger
  into a runtime discipline: if an operation demands a tier the leaf did
  not declare, the exception names the theorem being violated.
- There is **no absolute preimage** in the interface. `rel_preimage` is the
  operation (§2.3, §7.2); tier-B leaves may implement it with `b = top()`
  internally, but the signature carries the relativizer always.
- `normalize_term` strength is a declared property, and a *cost* property
  only (§2.4): under-normalization causes redundant Θ subqueries, cleaned
  by the semantic merge; it never causes wrong answers.
- Every leaf method is call-counted. The three-factor bill of §9
  (residuals × distance × class-code size) is a claim the prototype must
  *measure*, not assume; the counters are the invoice.

---

## 3. Interchange syntax

SMT-flavored s-expressions. The analogy is architectural, not cosmetic:
leaves are theories. `declare-leaf` is `declare-sort` plus a tier
signature; each leaf module registers the function symbols legal in its
guards, assigns, and classifiers, plus its rewrite rules — exactly an SMT
theory plugin. The reader is ~40 lines; the evaluator dispatches head
symbols to leaf modules.

Indicative surface (frozen only by the first implementation, not by this
document):

```
(declare-leaf Fork (enum free tk))
(declare-leaf St   (enum T HL E))
(declare-leaf Nat  (intervals))
(declare-shape Ph1 (pair (F1 Fork) (S1 St)))
(declare-shape V   (pair (pair Ph1 Ph2) (pair Ph3 Ph4)))

(define-op takeL1
  (seq (assign (S1 HL) (F1 tk))
       (filter (and (= S1 T) (= F1 free)))))

(define-op step (sum takeL1 takeR1 drop1 ...))
(define-data X0 (word (T free) (T free) (T free) (T free)))
(define-data X  (star step X0))

(theta X (mod (+ b c) 3))
(case X (mod (+ b c) 3) ((0 opA) (1 opB) (2 opC)))
(check-empty (apply (filter (deadlocked)) X))
(size X)          ; per-node prime counts — the §13 measure
(bill)            ; leaf-call counters since last reset — the §9 invoice
```

Design intents: `seq` composes right-to-left like the document's `∘`;
`assign` is the parallel form natively (the vector primitive of §7.1);
guards are leaf-registered expressions, so the guard language grows with
the leaf catalog and the core never learns arithmetic; everything is
generatable by programs, which matters if clients include them.

---

## 4. The shadow oracle — build it first

Definition 4.2 is the test architecture. Over tiny carriers (2–4 element
leaves), a behavior is a brute-force dict from words to values: ~30 lines.
Then **every** kernel operation, every leaf, every Θ is property-tested
against brute force on randomized small instances (`hypothesis` is the
right tool). The shadow-vs-mechanism split of §4 becomes literal: the
shadow is the referee, the calculus is the contestant, and the scary
components — Θ's semantic merge, `rel_preimage`, weighted pushforward —
ship with an independent judge. No kernel code is merged before its oracle
test exists.

Properties worth encoding beyond raw agreement: canonicity (normalize is
idempotent and order-insensitive), the degeneracy ledger (no zero subs, no
zero primes, (D), (F) hold on every constructed node), Prop 6.3
(zero-freeness never needs a semantic test over positive semirings — run
with the debug assertions on), 9.2 (Θ's alphabet is minimal: refining any
returned letter changes nothing, merging any two changes the answer).

---

## 5. Leaf modules, in build order

1. **EnumLeaf** — explicit finite sets. Tier B trivially; absolute
   preimages free; `normalize_term` is evaluation. Alone, it runs Ex1 end
   to end and exercises the entire kernel. First, because it isolates
   kernel bugs from leaf bugs.
2. **IntervalLeaf** — finite unions of intervals over ℕ/ℤ, plus a small
   linear-arithmetic rewriter (enough to send `(mod (+ 3 c) 3)` to
   `(mod c 3)`). Runs Ex2. First leaf where relative-vs-absolute preimage
   and class-naming cost (§9's third factor) actually bite; the measured
   bill on Ex2 is this milestone's deliverable.
3. **RegularLeaf** — recognizable languages, minimal DFAs as canonical
   codes; product/union/difference; concatenation and left-quotient as
   exported maps (push/pop). The paradigm infinite case (§2); yields
   queues. Hopcroft minimization is ~150 lines, or wrap an existing
   library.
4. **BddLeaf** — wrapped `dd` package or a minimal ROBDD. Deliberately
   fourth, and not as the workhorse (internal nodes already generalize
   BDDs): its purpose is the **internalization test** — pack a subtree's
   Boolean diagrams into an imported leaf per Theorem 6.4 and verify the
   calculus eats its own output, i.e. that a re-boxed white box is
   indistinguishable from a black one.
5. **Nat semiring pass** — not a leaf: switch the coefficient instance
   under Ex1/Ex2 and confirm nothing changes outside the leaves and the
   weighted pushforward (§14 (vi) as a regression suite; Θ over Ex2 counts
   representations).

---

## 6. Θ — the hard 20%

Mechanism 9.3, as code. The traveling classifier is a normalized ground
term, suffix-supported by construction (meeting a coordinate substitutes
its class and calls `normalize_term`; a consumed coordinate cannot recur).
Per node:

1. group head-primes by normalized residual code — the residual cache is
   keyed on that code, so dedup *is* cache sharing across contexts;
2. one recursive subquery per distinct code, on demanded tails only
   (demand-driven; nothing is computed bottom-up on spec);
3. on return, merge partitions with equal underlying kernels, recording
   finite relabeling tables (the retroactive semantic merge — the
   completeness backstop for weak `normalize_term`);
4. assemble by (F)-compression at the cut.

Expectations to hold the implementation to: the equivariant collapse is
**not a code path** — it is what the merge discovers (Ex2 must come out as
one kernel plus three relabel tables without any mod-specific logic in the
kernel); `case` invokes each branch once per congruence class (9.2(ii)),
observable in the call counters; the tautological instance (classifier =
continuation) reproduces `normalize` bit-for-bit — a mandatory test, since
§9 claims the normal form is a special case of Θ.

Anticipated redesign: `normalize_term`'s signature will be renegotiated
between the traversal and the leaf rewriter (context argument or not) —
plan for it to change twice; keep the seam thin.

---

## 7. Milestones, with gates

Ordered checkpoints; each gate is an executable fact, not a date.

- **M0 — shadow.** Brute-force behaviors over enum leaves; the property
  harness runs. *Gate:* a deliberately wrong `normalize` is caught.
- **M1 — kernel.** Shapes, unique table, `normalize`, meet/join/filter,
  apply, star-with-certificate; EnumLeaf. *Gate:* Ex1 end to end — four
  primes at every cut, deadlock reachable with filter provenance, sizes
  linear when scaled to 8/16 philosophers.
- **M2 — syntax.** Reader + evaluator + `size`/`bill` introspection.
  *Gate:* Ex1 expressed entirely in the s-expr surface, no Python.
- **M3 — Θ.** Curried transport per §6 above. *Gate:* `#eaters` discovers
  `{0,1,2}` from `⟨ℕ⟩`; tautological Θ ≡ `normalize`.
- **M4 — intervals.** IntervalLeaf + rewriter. *Gate:* Ex2 — three
  residuals independent of range, merge finds one kernel + three tables,
  measured bill matches the three-factor prediction; `rel_preimage`
  passes the mod-2 representability test that the absolute form fails.
- **M5 — regular.** RegularLeaf; a bounded producer/consumer over an
  unbounded queue. *Gate:* per-element certificates observable — an
  infinite leaf algebra, every touched class finitely coded.
- **M6 — closure & weights.** Internalization test (BddLeaf); Nat pass.
  *Gate:* Theorem 6.4 exercised; Ex2 counts representations with no kernel
  change.
- **M7 — a stranger's leaf.** Someone (or some session) not holding this
  document's context adds a leaf from the ABC docstring alone. *Gate:*
  they succeed without reading the kernel. This is the real test of
  "algebra agnostic."

Sequencing over scheduling: M1 before M3 (kernel bugs must not be
attributable to Θ), M4 before any claim about the bill (enum leaves make
every cost trivially cheap), M0 before everything.

---

## 8. Design decisions taken here (so the code need not relitigate)

- **Cross-coordinate assigns are compiled, not primitive.** An assign
  reading here and writing there goes through structural maps to co-locate
  or a `case` on the read-classifier — which is what the calculus says
  anyway (§7's assigns are leaf-local plus structural maps). The prototype
  restriction is principled.
- **No term-level canonical forms yet.** Obligation §14 (v) is open;
  operation *terms* therefore do not perfectly dedupe — only their
  applications do, and the `(term_id, data_id)` cache does not care.
- **Scheduling of `∗` is out of scope** (§8): any fair worklist; the
  certificate is the residual-novelty check, and two schedules agreeing on
  Ex1 is a test, not a feature.
- **Debug/release split carries the theory.** Debug mode asserts the
  degeneracy ledger and zero-freeness on every constructor; release mode
  assumes them, which is exactly Prop 6.3's promise. A failure in release
  mode that debug mode would have caught is, by construction, a
  coefficient-discipline violation — the diagnosis is free.

---

## 9. Use cases this should grow toward

Ordered by how specifically they need *this* framework rather than a flat
BDD/SDD:

- **Compositional reachability / model checking.** Hierarchical systems —
  components, protocol stacks — where the shape mirrors the architecture
  and no global variable order exists. Ex1 writ large; the native habitat.
- **Parameterized & infinite-state verification.** Queues, channels,
  token-passing via RegularLeaf: regular-model-checking territory, with
  the hierarchy supplying the system decomposition flat approaches lack.
- **Knowledge compilation over mixed domains.** Weighted counting on
  Boolean-plus-arithmetic structure, past where bit-blasting stops.
- **Provenance & factorized query results.** Provenance semirings
  (`ℕ[X]`) are positive in exactly §1's sense, so the algebra-agnostic
  layer yields why-provenance for free; the congruence tower is a
  factorized representation of a relation, with per-query Θ as its
  interface.
- **Program analysis.** Abstract domains (intervals first) as leaves; the
  diagram is the disjunctive completion; `rel_preimage` is backward
  analysis, billed in the same currency as Θ.
- **Configuration / product lines.** Feature bits plus numeric attributes;
  "discovered, not declared" is the difference between a configurator and
  a combinatorial declaration nobody maintains.

---

## 10. What the prototype is for

Three products, in order: an API a stranger can extend (M7 is the proof);
a measured cost model (the §9 bill as printed invoices on Ex1/Ex2, either
confirming the three factors or handing §14 (iii) a counterexample, both
outcomes valuable); and pressure on the open obligations — Θ's
implementation is a draft of the transport lemma's induction, and wherever
the code needs a case the lemma statement lacks, the document iterates.
The prototype is an instrument pointed at the theory, not a delivery.
