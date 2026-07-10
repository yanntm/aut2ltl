# Cascade ladder — Experimentation Specification

This document is the interface between the section draft
(`research_notes/bls_cascade.md`) and the implementation sessions: the
draft's ⟨TBD⟩s cite the `K-` ids below, every derivation printed in the
draft is a *prediction* the tool must reproduce, and results come back as
findings in **`research_notes/bls_cascade_report.md`** (to be created by
the first engineering session — contract in §0). Experiment ids are
namespaced `K-` to avoid collision with `sos_toltl_experiments.md`'s
C/E/H/M series, whose assets this spec consumes.

**Where things stand:** K-E0 ran (findings K-F1–K-F3 in the report):
step 5 confirmed, steps 1–3 refuted the draft's floor-witness model
(profile monoid vs. syntactic quotient), steps 4/6 pending. The paper
edit the decision rule demanded has landed — draft banner, C.3–C.7
(Conjecture C.12/C.17 refuted, Theorem C.12′, Prop C.19), main paper
§5.1/§8 — and this spec is synced to it: **K-E1–K-E5 are unblocked**
under the revised predictions below.

---

## 0. The report contract (`bls_cascade_report.md`)

Create the report on first landing a result; thereafter it is the ledger.

- **Current-state only**: done/todo delineated, no narrative of how a
  result was reached; git holds history.
- **Every finding carries**: an id (`K-F1`, `K-F2`, …), a one-line claim,
  status (`CONFIRMED | REFUTED | BUDGET | BLOCKED`), the exact command
  line, and pointers **only to git-tracked files** — the probe script
  under `tests/`, and the machine-generated output it produced
  (`tests/**/logs/...`, committed, or regenerable by the cited command).
  No numbers without a pointer; no pointers outside git.
- **Reproduce before correcting**: to amend a number, first rerun the
  cited command and show the discrepancy.
- **A refuted prediction is a paper edit**, flagged in the report as
  `PAPER-EDIT:` with the section draft location — not a footnote.
- House rules from `CLAUDE.md` apply to every run: ≤ 15 s per example,
  single-input argv, one invocation per case; a blown timeout is a
  finding (`BUDGET`); logs never to `/tmp`; language comparisons report
  containment direction + witness word; Spot bounded-or-skipped;
  `python3 -m survey --folder samples/validation` must end SUCCESS before
  any code lands.

## 1. Objects consumed (all exist — see `sos_toltl_experiments.md` §1–§2)

- The invariant `𝓘(L) = (𝒞, λ, M, P)` in `.sos` format; the census with
  ground truth; the triptych and fixtures.
- **C1** (Cayley builder): `Cay(L)`, SCC decomposition = layers, R-order.
- **C2** ((A)-tester): per-layer letter classification
  (`neutral | reset(t) | mixed`), passing widths, and the layer action
  monoid `𝒜_R` as a by-product.
- **C3** ((B)-tester): the bounded window-determinacy stages and its
  census output table — the source of the 372 `undecided` layers (K-E1's
  input) and of Table 3's semantics, which K-C1's (B)-mode must match.
- The `aut2ltl/bls` package: GAP/SgpDec holonomy bridge
  (`aut2ltl/bls/gap`, `decompose_aut`), the reach-formula family
  (`aut2ltl/bls/operators/`), `Fin` (`fin.py`) — consumed by K-E5.
- The conformance gate (rebuild `𝓘` from an emitted formula,
  byte-compare) — consumed by K-E4.

## 2. Definitions the implementer needs (self-contained)

All from `bls_cascade.md`; restated here so no paper-reading is required.

- **Layer** `R`: an SCC of `Cay(L)` (a set of class ids). **Within-layer
  step**: `q·a := M(q, λ(a))`, *defined* iff the result is in `R`.
- **Quotient letters** `Σ_λ`: the distinct values of `λ`; each carries
  the set of concrete letters mapping to it (needed only at
  formula-rendering time, K-E4).
- **Letter roles at `q ∈ R`** (from C2): `St(q)` = letters with
  `q·a = q`; `An(q)` = letters whose within-layer action is a partial
  constant onto `q` (diagonal case `a ∈ St(q) ∩ An(q)` allowed);
  `1-anchored` = every letter's within-layer action is a partial
  identity or partial constant.
- **Config machine** `M_k(R)`, entry `c ∈ R`: nodes `(q, m)` with
  `q ∈ R`, `m` a word over `Σ_λ` of length ≤ `k`; built by ALG-1.
- **Edge**: `e = ((q, m), a)` with `|m| = k` and `q·a` defined.
- **Verdict oracle**: `Val(s, d) := [ (M(s, π(d)), π(d)) ∈ P ]` where
  `π(d)` is the unique idempotent among the powers of `d` (ALG-3).
- **Condition (C) at width `k`** (Def C.4): for every entry `c ∈ R`, any
  two tails confined to `R` from `c` with equal recurring `M_k`-edge
  sets have equal verdicts. Decision procedure: ALG-5 — equivalently,
  every *collected covered-set* is verdict-uniform.
- **Condition (B) at width `k`**: same with the recurring edge set
  replaced by its window projection (the set of `k`-windows of the
  edges' endpoint nodes) — one extra grouping step over ALG-5's output;
  must agree with C3 on C3's decided cases (a K-E0 assertion).

## 3. Algorithms (normative — implement exactly, then optimize)

**ALG-1 (cone build).** Input `(𝓘, R, c, k)`.
```
frontier := {(c, ε)}; nodes := {(c, ε)}; edges := ∅
while frontier nonempty:
    pop (q, m)
    for a in Σ_λ:
        q' := M(q, λ(a));  if q' ∉ R: continue
        m' := last k letters of m·a
        if |m| = k: edges += ((q, m), a)          # full-memory edges only
        if (q', m') ∉ nodes: add to nodes & frontier
```
Output: `nodes`, full-memory `edges`, successor map. `k = 0` ⟹ `m = ε`
everywhere and `edges` are the within-layer Cayley edges.

**ALG-2 (entry stems).** Fixpoint on pairs `(node, s ∈ 𝒞)`:
```
seed (c-node, c); propagate ((x, s), a) ↦ (x·a, M(s, λ(a))) along cone edges.
EntrySt(x) := { s : (x, s) reached }.
```

**ALG-3 (idempotent power).** `π(d)`: compute powers `d, d², …` by
`M`-multiplication until the first repeat; among the closed cycle's
elements return the unique `x` with `M(x, x) = x` (assert exactly one).

**ALG-4 (walk reconstruction).** Every explored state in ALG-5 stores one
parent pointer `(prev-state, letter)`; a collected state unwinds to a
concrete letter word. Needed only when a witness must be printed (K-E2).

**ALG-5 (unified closure — the core; the paper's loop-class closure with
a covered-set coordinate).** Input: cone from ALG-1, per entry `c`.
```
for each full-memory node x:                    # the base
    states := {(x, 1, ∅)}                        # (current node, class ∈ 𝒞∪{1}, covered ⊆ edges)
    explore: ((y, d, F), e = (y, a)) ↦ (y·a-node, M(d, λ(a)), F ∪ {e})
             under a node budget B (default 10⁶ states per base; a hit is BUDGET, never a pass)
    collect CL(x) := { (F, d) : state (x, d, F) reached, d ≠ 1 }   # closed walks at x
```
Facts to assert (cheap, every run): each collected `F` is strongly
connected as an edge set; `CL(x)` is closed under
`(F₁,d₁),(F₂,d₂) ↦ (F₁∪F₂, M(d₁,d₂))` — this closure rule may be used to
*saturate* instead of raw exploration (much faster), but only after a
small-case cross-check that saturation and raw exploration collect the
same sets (a K-E0 assertion).

**ALG-6 (decision).** From ALG-5's output over all bases and entries:
```
VerdictSet(F) := { Val(s, d) : x a base with (F, d) ∈ CL(x), s ∈ EntrySt(x) }
(C) at width k  ⟺  every collected F has |VerdictSet(F)| = 1, no BUDGET
(B) at width k  ⟺  grouping F's by window projection, each group's union is a singleton
```
A mixed `F` (`|VerdictSet(F)| ≥ 2`) is a **(C)-conflict**: dump
`(F, bases, entry classes, loop classes, verdicts)` and go to ALG-7.

**ALG-7 (conflict triage — K-E2 only).**
```
1. From the mixed F pick (x, d₁) with verdict 1 and (x', d₂) with verdict 0
   (prefer same base x = x'; if bases differ, extend one walk through the
   other's base inside F — F is strongly connected).
2. Reconstruct (ALG-4): entry word u (from c to x), loop words w₁, w₂
   with classes d₁, d₂. Emit lassos u·w₁^ω, u·w₂^ω.
3. Independent verification: fold both lassos through 𝓘 (the membership
   rule) AND model-check against the source acceptor of L; expected: one
   accepted, one rejected. Any disagreement = closure bug, stop.
4. Conjugacy check (Lemma C.11): pairs (s₁,e₁) = (M(M(c,[u]),π(d₁)), π(d₁)),
   (s₂,e₂) likewise for d₂; scan all (g,h) ∈ 𝒞²: e₁ = M(g,h), e₂ = M(h,g),
   s₂ = M(s₁,g). If conjugate: closure bug (conjugate pairs cannot split
   verdicts), stop. If non-conjugate: a genuine candidate — escalate.
```

## 4. Experiments

### K-E0 — gate: the two witnesses (extends H8) — RAN, expectations revised

*Status:* steps 1–3 and 5 ran (K-F1–K-F3). The original expectations
for steps 1–3 encoded the profile-monoid hand model and were refuted;
the draft is revised (C.3's worked witness is `G(a → F b)`; the floor
witness is C.4's refutation instance and C.5's fallback instance). The
expectations below are the revised ones; steps 4 and 6 remain to run.

1. Build `𝓘(GF(a ∧ X((!a∧!b) U a)))`; run C1/C2. **Expect** (revised;
   = K-F2's observation): **seven** classes, prefix-independent;
   layers `{unit} | {[s]} | {(b,·,0) pair} | {(a,·,0) pair} | {z}`;
   final layer the frozen singleton `{z}` (every quotient letter
   neutral); the unflagged pairs moving and 1-anchored with the
   completion edge an *exit* (their confined verdicts constantly
   rejecting).
2. ALG-1 at `k = 0`: on `{z}` one node, three self-loop edges; on each
   unflagged pair, five within-layer edges (the completion edge
   absent).
3. ALG-5/6 on `{z}`: **expect** (C) fails at `k = 0` (mixed `F`s:
   `{a,b}` and `{a,b,s}`) and at `k = 1`; `k = 2` may be `BUDGET` —
   acceptable, Theorem C.12′ settles every width on paper. Run K-E7's
   sandwich scan on the same output: **expect** it dumps the
   absorption failure `e·e′·e = z <_J e` (`e` an unflagged idempotent
   profile, `e′ = z`) — the aperiodic positive control (draft C.4) —
   and on `EvenBlocks`' frozen layer at `k = 2..3` the group failure
   `f·z·f = z <_J f`: the scan must detect *both* mechanisms, or it is
   not testing anything.
4. Cross-check ALG-6's (B)-mode against C3 on this layer and on the
   triptych's frozen layers (`GF(aa)` at `k = 2`): **expect** agreement
   with Table 3 semantics wherever C3 decided.
5. `G(a → F b)` — **CONFIRMED** (K-F1): (C) at width 0 on the final
   layer `{2, 4}`, six edges, plain (B) failing at width 0; accepting
   family "an edge at class `2` is covered", upward-closed, minimal
   sets `{(2,s)}`, `{(2,b)}`, `{(2,a),(4,b)}`; Prop 5.7 data unchanged.
6. Assert the saturation/raw-exploration agreement (ALG-5) on all of the
   above.

*Decision.* The original rule fired (steps 1–3 mismatch → `PAPER-EDIT`
on C.3; K-E1–K-E5 stopped). The edit has landed and the gate is
re-opened; steps 4 and 6 complete it. A mismatch against the *revised*
expectations is a new `PAPER-EDIT`.

### K-E1 — (C) on the (B)-undecided stratum

*Hypothesis (revised):* the 372 layers C3 left `undecided` (budget
gaps, Table 3) are all frozen final layers, where (C) at `k` is
exactly (B) at `k+1` (Lemma C.10) — so the run's value is procedural,
not logical: dropping the grouping step relieves the budget, and the
piggybacked K-E7 scan maps absorption. Expect decisions where the
budget was the binder; any `CONFLICT` is a new floor inhabitant, not a
C.12 falsifier (C.12 is already refuted — Theorem C.12′).

*Input:* C3's census output table, rows with status `undecided`.
*Run:* ALG-1..6 per layer, entries = all `c ∈ R`, widths `k = 0..3`,
budget as in §3; stop at first passing width.
*Output CSV columns:* `language id, layer id, |𝒞|, |R|, |Σ_λ|, C3
status, (C) width | CONFLICT | BUDGET, #collected F, max states, time`.
*Decision:* `CONFLICT` rows → ALG-7 then K-E2 escalation. Pass rows →
coverage numbers for the draft's C.7 §8-bullet. `BUDGET` rows → record
which coordinate blew (`F`-count vs state count) — sizing data for the
width growth on frozen layers.

### K-E2 — the floor map (was: C.12 falsification — settled on paper)

*Question (revised):* C.12 is refuted (Theorem C.12′); the scan now
measures how far the floor extends and whether any failure mechanism
beyond zero absorption exists (draft C.4's mechanisms paragraph).

1. *Frozen layers* (class coordinate trivial — (C) at `k` = (B) at
   `k+1`): all frozen final layers of the census, widths ascending under
   a stated budget.
2. *Beyond the frame:* the `2state2ap` enumeration (shared with the
   existing census-next H6/smallest-H3 work — reuse its generation,
   aperiodic invariants only), moving final layers included, `k = 0..3`.
3. *The transfer specimen* (Prop C.19): build
   `𝓘(π₁⁻¹(GF(a ∧ X(s U a))) ∩ π₂⁻¹(G(c → F d)))` over the product
   alphabet. **Expect** a *moving*, 1-anchored final layer
   `{(z,2), (z,4)}` with verified (C)-conflicts at every tested width
   — the first moving-layer floor inhabitant, confirming the transfer.
4. Every conflict through ALG-7 (expect verified toggles and
   non-conjugate pairs — on the known specimens these are *not*
   closure bugs). Persistence across budgeted widths is recorded with
   the Lemma C.13(i) projection signature.

*Output:* per candidate the full ALG-7 dump + lassos + verification
transcript; otherwise scanned-clean statistics per stratum.
*Decision:* a conflict whose K-E7 signature is *not* zero absorption
(no saturated coordinate) is the interesting find — a third mechanism
— and a `PAPER-EDIT` on C.4's mechanisms paragraph. A clean step 3
(no conflict on the transfer specimen) refutes Prop C.19 →
`PAPER-EDIT` on C.4/C.19.

### K-E3 — one-sidedness statistics (scope of Cor C.8/C.9)

Over every final layer where (B) or (C) passed at `k ≤ 3` (census +
K-E1 output): during ALG-6, restrict to collected `F` spanning ≥ 2
classes; test monotonicity of the verdict under `F ⊆ F′` (pairwise scan
per entry). Classify `upward | downward | neither`; cross-tabulate with
the ladder rung of `P|_R` (the strength stratification read-off) and
count the languages meeting all of Cor C.9's hypotheses
(prefix-independent, terminal 1-anchored final layer with anchors,
upward-closed, parked verdicts rejecting) — the guaranteed-Π₂ stratum.
*Prediction:* recurrence-rung layers predominantly `upward`; the C.9
count may well be **zero** — the revised draft suspects
prefix-independence forces the final layer frozen (C.3's ⟨TBD⟩). A
non-zero count settles that question negatively and hands C.9 its
first instance — report any hit prominently.

### K-E4 — config normal form emitter + conformance

Implement in the window engine, decision data from K-E1's machinery:

```
pin(m): fold m left-to-right; state ∈ {ID, CONST(t)}:
    letter constant onto t′ ⟹ CONST(t′);  letter identity ⟹ unchanged.
A_e, e = ((q,m),a):
    pin = CONST(q):  m̂ ∧ X^k â
    pin = ID:        An(q) ∧ X( St(q) U (m̂ ∧ X^k â) )
    pin = CONST(q′≠q): assert-fail (unreachable config)
  where m̂ = ⋀_i X^{i-1} (letter-set formula of m_i), letter sets rendered
  per the existing λ-preimage synthesis (§2.1 convention), â likewise.
Ω(R,c): if accepting family upward-closed (K-E3 data):
            ⋁_{F minimal accepted} ⋀_{e∈F} GF A_e
        else exact-set: one disjunct per accepted F:
            ⋀_{e∈F} GF A_e ∧ ⋀_{e∈E_cone∖F} FG ¬A_e
        plus parks  ⋁_d F( An(d) ∧ X( G St(d) ∧ Ω_d ) )  — Ω_d from the
        existing Prop 5.4 emitter on the frozen restriction ({d}, St(d)) —
        plus the entry park ( G St(c) ∧ Ω_c ).
```

*Run on:* `G(a → F b)`, then every layer K-E1 decided. **Expected on
`G(a → F b)`** (revised, C.3):
`( GF A_{(2,a)} ∧ GF A_{(4,b)} ) ∨ F( b ∧ X G St(2) ) ∨ G St(2)` with
the `k = 0` carried atoms `A_{(2,a)} = b ∧ X((b∨s) U a)`,
`A_{(4,b)} = a ∧ X((a∨s) U b)`; equivalent to the Prop 5.7 width-1
output (report containment both ways + witness if not syntactically
equal). **Expected on the floor witness**: the canonical emitter must
*not* fire — no (C) width exists (Theorem C.12′), the layer routes to
the C.5 fallback, and an emission here is a bug. (The
`GF(a ∧ X(s U a))` emission survives on the *presentation-side*
pendency machine — that is K-E6's item, not this emitter's.)
*Gate:* the conformance gate on every emitted formula; Spot bounded.
Zero verified-non-equivalent. Sizes (final DAG, flat, modal depth, until
depth) recorded against the DG-fallback output the same languages took.

### K-E5 — DG vs manufactured cascade on the (A)-fallback stratum

*Hypothesis* (draft C.5, stem side): on the 258 (A)-failing languages
(1 432 layers), holonomy cascade + finite-word reach beats DG-on-`𝒜_R`,
and cascade heights sit far below `2^{|R|}`.

0. *Preflight (cheap, reported separately):* for each of the 1 432
   failing layers, record whether it is a final candidate (has an
   internal cycle — some run can stay forever). The draft's C.5 asserts
   none is; a final (A)-failing layer would also need the loop-side
   fallback and is a `PAPER-EDIT` on that sentence.
1. Per failing layer (C2 output): totalize the within-layer machine with
   an absorbing exit sink; feed it to the SgpDec bridge
   (`decompose_aut`); record the cascade height and per-level state
   counts.
2. Emit each `ψ_{r→c}` with the reach family in its finite-word variant
   — [BLS22, Rem 2]: weak next `X̃ψ := ¬X¬ψ` substituted inside `wsolid`
   only, strong `X` elsewhere (the in-repo operators are the
   infinite-word forms; this substitution is the only change).
3. Assemble through Prop 4.14's `SAFE`/insertion wrapper unchanged;
   conformance-gate the assembled label.
4. Ledger vs the DG route on the same layers: height, DAG size, flat
   size, depth, wall time; the two 3-class floor specimens worked in
   full in the report.

*Decision:* selects the fallback — cascade wins ⟹ it replaces DG at
step 3(b) of the architecture (`PAPER-EDIT` on §5.4 via C.7); DG wins ⟹
C.5's stem half is demoted to a remark.

### K-E7 — sandwich scan (the absorption map; C.17 refuted on paper)

*Statement scanned* (draft C.4): the sandwich identities
`e·e′·e J e`, `e′·e·e′ J e′` for idempotent loop classes at a common
anchored node with equal cyclic window data. C.17 is **refuted on
paper** (Theorem C.12′; the floor witness fails the identity by zero
absorption at every width), so the scan is a *map*, not a
falsification: it measures where aperiodic failures live and whether
any mechanism beyond absorption and group cancellation appears. Two
positive controls are mandatory: the floor witness's frozen layer
(absorption, `e·z·e = z <_J e`) and `EvenBlocks` (group,
`f·z·f = z <_J f`). ALG-5's output is exactly
the realizable instance set: within one collected group `(x, F)` —
common base node `x = (q, m)` (so common suffix `ω = m`), common covered
set `F` (so equal cyclic data, `W = F`'s windows) — the loop classes
`{d : (F, d) ∈ CL(x)}` are the candidates.

*Procedure.* Piggybacks on any K-E1/K-E2 run:
```
for each base x, each collected F:
    E_id := { d : (F, d) ∈ CL(x), M(d, d) = d }        # idempotents only
    for each pair e ≠ e′ in E_id:
        s  := M(M(e, e′), e);   s' := M(M(e′, e), e′)
        if s = e and s' = e′:  PASS
        else:
            test J-equivalence of s with e (and s' with e′):
                J(a, b) ⟺ a ∈ S·b·S and b ∈ S·a·S — decide by the
                two-sided reachability closure on the table
                (fixpoint over left/right multiplications)
            if J holds but equality fails: BUG — contradicts aperiodic
                localization (Lemma C.16); check the input is aperiodic,
                else fix the closure; stop.
            if J fails: sandwich failure — dump
                (invariant, layer, k, x, F, e, e′, s, s'), reconstruct
                witness loops (ALG-4), record whether the verdicts
                Val(·, e), Val(·, e′) actually differ over EntrySt(x)
                (they need not — the identity is stronger than (C);
                flag which), and classify the mechanism: absorption
                (s sits J-below both e and e′ — a saturated zero-like
                class) vs group vs other.
```
*Output:* pass/fail counts per stratum (frozen / moving, per width),
failures classified by mechanism; every failure fully dumped.
*Decision:* both positive controls must be detected, or the scan is
broken. A failure classified `other` — neither absorption nor group —
is the finding: `PAPER-EDIT` on C.4's mechanisms paragraph. Verdict-
differing failures are (C)-conflicts and also feed K-E2's floor map.

*Cost note:* `O(|E_id|²)` table products per `(x, F)` group — negligible
against ALG-5 itself; run it by default in every K-E1/K-E2 invocation.

### K-E6 — the fallback's worked instance + prophetic cross-check
(promoted from optional: C.5 is load-bearing by C.4's no-go)

1. *Presentation-side config run* (draft C.5's worked paragraph): build
   the pendency machine for the floor witness (two states, "last
   non-`s` letter was an `a`", Büchi on the completion transition) and
   run ALG-1/5/6 on it — the six-edge closure of K-F1, on this machine
   instead of a canonical layer. **Expect**: (C) at width 0, accepting
   family upward-closed with single minimal set `{(A, a)}`, emission
   `GF(a ∧ X((a∨s) U a))` ≡ `GF(a ∧ X(s U a))`; conformance-gate it.
   This is the fallback's first end-to-end instance: the data the
   canonical walk provably cannot carry (Theorem C.12′), carried by a
   two-state presentation.
2. *Prophetic cross-check:* build the chains-expansion automaton `A_S`
   ([CM03, §6.3]) for the floor witness's invariant: states
   (linked-pair conjugacy classes × strict R-chains), the unique runs
   of the two §5.1 lasso families, loop languages restricted to the
   final layer. **Expect**: accepting recurrence coincides with the
   completion-transition recurrence of step 1's machine; `A_S`
   counter-free (instance check of the prophetic note's Theorem 1).
   Feeds the prophetic transcription problem's first worked instance —
   the open problem's main candidate route (C.4, C.5).

## 5. Dependency graph

```
K-E0 ──▶ K-E1 ──▶ K-E2      (ALG-5/6/7: one machinery)
           │        │
           │        └─ K-E7  (sandwich scan: piggybacks on every
           │                  K-E1/K-E2 run — enable by default)
           ├──▶ K-E3         (same enumeration, extra classification)
           └──▶ K-E4         (first emitter; conformance-gated)
K-E5                         (independent: bls bridge plumbing)
K-E6                         (independent; promoted — the fallback's
                              worked instance, C.5)
```
