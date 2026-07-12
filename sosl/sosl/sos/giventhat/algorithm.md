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

## 5. The ladder (`ladder.py`): one lemma, one hull per rung

Every "does the interval contain a member of class 𝒦" question is one
instance of paper Lemma 4.1: when 𝒦 is intersection-closed with
`linked ∈ 𝒦` (a Moore family on the finite lattice of saturated pair sets),
its closure operator `ρ_𝒦` decides existence —

    𝒦 ∩ [P_min, P_max] ≠ ∅   ⟺   ρ_𝒦(P_min) ⊆ P_max,

and `ρ_𝒦(P_min)` is then the least member. Dually a union-closed 𝒦 with
`∅ ∈ 𝒦` is decided by its kernel `κ_𝒦` on `P_max`, greatest member
`κ_𝒦(P_max)`. Each rung is one hull:

- **safety** — `ρ` = `safety_closure` (CAL5); **co-safety** — `κ` =
  `interior`. Both one `O(n²)` liveness scan.
- **obligation** — 𝒦 = the `R`-class-constant verdicts `B_θ` (paper
  Prop 4.3). An `R`-class is *forced to 1* by a `P_min` stem, *forced to 0*
  by a linked stem outside `P_max`; a member exists iff no class is forced
  both ways, least member θ = forced₁, greatest θ = ¬forced₀. `R`-classes
  come from `r_classes` in `calculus.surgery` (the SCC pass `is_obligation`
  already runs, promoted — never a second Tarjan).
- **recurrence** — 𝒦 = the chain-condition sets: no linked stem `s` with
  loops `f ≤_H e`, `Val(s,e) = 1`, `Val(s,f) = 0`. The H-order on
  idempotents is `classify.primitives`' (`leq_h_idem`, one implementation
  in the repo); `h_below` is its ladder-shaped view. `ρ` = `rec_hull`: the
  Horn rule "(s,e) ∈ Q, f ≤_H e, f a loop of s ⟹ (s,f) ∈ Q" alternated
  with `saturate` to the joint least fixpoint — the Horn rule alone does
  not yield a language (spec trap #10).
- **persistence** — the mirror chain condition, decided with **no new
  machinery**: `B ∈ [P_min, P_max]` is a persistence iff `B^c ∈
  [P_max^c, P_min^c]` is a recurrence (paper Prop 4.4), so the test is
  `rec_hull(P_max^c) ⊆ P_min^c` and the greatest member is
  `rec_hull(P_max^c)^c` — one complement flip.

**Witness convention.** Every `exists_*` returns
`(bool, Optional[PairSet], Optional[Witness])`. On yes the pair set is the
canonical member — least for the Moore rungs (safety, obligation,
recurrence), greatest for the kernel rungs (co-safety, persistence). On no
the `Witness` is the refusal certificate: the first hull pair pushed past
the constraining endpoint, in the key discipline order, rendered as its
canonical lasso — a behavior every rung member must accept and the interval
forbids (or dually).

**Orientation.** The read-offs `is_recurrence` / `is_persistence`
transcribe the paper's §2 chain conditions (`m⁺ ≤ 0` resp. `m⁻ ≤ 0`); the
paper hand-checked the orientation on four examples and the corpus rung
oracle (`ladder_gate.py`) is the deciding instance — a consistent flip is a
paper correction (report F5), not a silent reconciliation. The oracle
compares two *paths*, not two codebases: the violation scan here vs the
chain DP behind the `.cat` coordinates, both over the shared
`classify.primitives` H-order (duplicating the primitive was judged not
worth the maintenance cost — decision 2026-07-11).

## 6. The quotient engine (`quotient.py`): one theorem, one hull

`Interval` fixes the *language* bounds `[P_min, P_max]`; the engine adds the
missing dimension — the *table*. A `Quotient` is a monoid congruence `π` of the
product table `T`, presented as the quotient table `T/π` (canonically keyed by
`Table.of_raw` — the one shortlex BFS, never a second) plus the class map
`π : T → T/π`. Two constructors: `congruence(T, seeds)` closes a set of seed
identifications under a **letter** worklist (letters suffice by the same
induction `reduce`'s refinement runs), and `syntactic_congruence(T, q)` lifts
`reduce.syntactic_blocks` (paper Prop 4.1's `π_L`) into a `Quotient`. Both go
through `_from_blocks`, which induces the quotient product from block
representatives and asserts `[ε]`'s block is a singleton (trap #8).

The whole engine is **paper Prop 4.2**: for any `π`,

    hull(π, Q) = pullback(π, saturate_{T/π}(forced(π, Q)))

is the least `π`-recognizable superset of `Q`. Two orientation traps live in
that one line. `forced` renormalizes each image pair through the **quotient's**
idempotent (`linked_pair_of` on `T/π`) — inserting the raw image is unsound
(trap #3); and `saturate` runs on the **quotient**, only then `pullback` —
pulling back first and saturating on `T` is a different, wrong set (trap #15).
Hence `admits(π, iv)` is exactly `hull(π, P_min) ⊆ P_max`, `least_member` is
that hull, and `greatest_member` is its de Morgan dual. Stutter invariance is
one seed set (`M(ℓ,ℓ) ∼ ℓ`), so `stutter.py` is a thin instance — and its
verdict is YES/UNKNOWN, never NO, because the least stutter superset can leave
the table (paper Thm 5.7, trap #11).

## 7. The greedy (`simplify.py`): merge while it admits

The operation searches the lattice of congruences, scored by `|𝒞|`. From each
admissible seed it repeatedly merges **two blocks of the current quotient** and
re-closes *on the quotient*, composing the map back to `T` (`compose`) rather
than re-closing from `T` each round (trap #9); it keeps the admissible merge
that collapses the most classes, ties broken by the merged blocks' keys
(determinism is mandatory). When no merge admits, it reads off the least and
greatest recognized members. The global answer is the class-count `argmin` over
every recorded member **and** the three reference points `P_¬φ / P_min / P_max`,
so "never worse than the best reference" holds by construction — `π_{¬φ}` is
always an admissible seed (its own language witnesses it), which is what makes
the contract free (paper §4.6; asserted as A3).

Two laws stay on at every emission: Prop 3.1 (inherited from `Interval`) and the
[DPT25] soundness identity `B ∩ P_K = P_min` (spec §6.3). Constrained mode
(`opts.require`, paper Lemma 5.2) alternates `hull_π` with a rung's closure
operator to a joint least fixpoint — built from the GT2 hulls, no new machinery;
only the Moore rungs (grow-from-`P_min`) are wired, the kernel rungs need the
dual and are refused. **Honesty:** exact minimization is conjectured NP-hard
(paper Conj 4.5); this is a heuristic with an exact test inside it, and the
reported `|𝒞|` is *achieved*, never *minimal* (trap #15).
