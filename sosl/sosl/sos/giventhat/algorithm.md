# giventhat — the interval, one level above the code

Dev-facing notes: read this to *change* the package; read `README.md` to *use*
it. The specification of record is `research_notes/sos_giventhat_spec.md`
(milestones GT1–GT5, gates, traps); the normative math is
`research_notes/sos_giventhat.md`, on top of the calculus paper
`research_notes/sos_calculus.md` [SωSC26] and [DPT25] for the automata-side
original. Where code and paper disagree: stop and report (spec §8/§10), never
reconcile silently.

The whole package rests on one sentence (paper Prop 3.1): **on the
materialized product table, `P_max \ P_min = P_K^c`, and the legal `B`s are
exactly `P_min ⊔ (a union of conjugacy classes of linked pairs outside
`P_K`)`.** Every structure here reifies that sentence, and `given_that`
asserts it at runtime on every construction — if it fires, the bug is
upstream (align / materialize / saturate), never here.

## 1. Why the product must be materialized

`Aligned` is decision-only: it exposes the two verdict maps on a common node
set but no multiplication table, so no surgery can run on it. The endpoints
are *cross-table Boolean combinations* (`∩` and `∪` of one side with the
complement of the other), which only exist once `materialize` has built the
product `Table` and carried **both** pair sets onto it (`pairs_a = P_¬φ`,
`pairs_b = P_K`). One align + one materialize is the entire product-priced
cost of `given_that`; everything after is `O(|linked|)` set algebra plus one
`conjugacy_classes` pass.

## 2. The freedom classes

`P_K` is saturated (a carried side of `materialize` is a language), so every
conjugacy class of the product's linked pairs is entirely inside or entirely
outside it — `given_that` asserts the dichotomy while filtering. The classes
outside are the freedom `F`: on them `K` says nothing, and a legal `B` picks
one verdict bit per class; on the classes inside `P_K` the verdict is `¬φ`'s,
non-negotiable. `conjugacy_classes` (in `calculus.surgery`, commissioned by
this package) partitions `linked` deterministically — pairs processed in the
key discipline order, each class `saturate` of its least representative,
classes in discovery order — so `Interval.freedom` and the `choose` /
`decompose` index space are stable across runs.

## 3. The endpoint symmetry

`k_settles_phi` is `is_empty(P_min)`; `k_refutes_phi` is
`is_empty(complement(P_max))`. The second is deliberately **not** a separate
universality scan: on the automata side universality is exponential on TGBA,
and the paper's claim (§3) is that on the invariant the two checks are the
same scan on complementary pair sets — the code exhibits the symmetry (spec
trap #4). Both inherit the calculus witness discipline: the first satisfying
cell of the normative scan order is the *globally* minimal lasso, replayable
against any independent oracle.

## 4. `choose` / `decompose`

`choose(iv, S) = P_min ∪ ⋃_{i∈S} freedom[i]` is saturated and inside the
interval *by Prop 3.1* — asserted anyway under `check=True` (the default;
campaigns may pass `check=False`). `decompose` inverts it by intersecting
`q \ P_min` against each freedom class: all-in or all-out (a straddle would
convict Prop 3.1, asserted), remainder empty. Laws the gate holds:
`choose(∅) = P_min`, `choose(range(bits)) = P_max`,
`decompose(choose(S)) = S`, monotonicity in `S`.
