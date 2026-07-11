# Cascade ladder — Experimentation Specification

This document is the interface between the section draft
(`research_notes/bls_cascade.md`) and the implementation sessions: the
draft's ⟨TBD⟩s cite the `K-` ids below, every derivation printed in the
draft is a *prediction* the tool must reproduce, and results come back as
findings in **`research_notes/bls_cascade_report.md`** (to be created by
the first engineering session — contract in §0). Experiment ids are
namespaced `K-` to avoid collision with `sos_toltl_spec.md`'s
C/E/H/M series, whose assets this spec consumes.

**Where things stand — THREAD PARKED.** The note is the standalone
companion [Cas26]; the main paper's §6 imports its slim core. K-E0 is
COMPLETE (K-F1..F6); K-E1, K-E2, K-E3 and K-E7 are COMPLETE **on the
current corpus** (6 222 languages, Wagner ω³/ω⁴ — K-F7..K-F10, K-F12;
data in `reference/cascade/`); K-E4's worked example is gated (K-F11).
**Migrated:** K-E5 and K-E6 are subsumed by `sos_toltl_spec.md`
**E11** (the decomposition fallback); K-E4's production wiring is the
toltl thread's census-regeneration item. **Parked here** (reopen only
if the floor cartography becomes a paper): K-E8 (padded-block floor
certificates + the (B̃)-strictness probe) and the k=2 pass on K-E1's
640 budget-open layers.

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

## 1. Objects consumed (all exist — see `sos_toltl_spec.md` §1–§2)

- The invariant `𝓘(L) = (𝒞, λ, M, P)` in `.sos` format; the census with
  ground truth; the triptych and fixtures.
- **C1** (Cayley builder): `Cay(L)`, SCC decomposition = layers, R-order.
- **C2** ((A)-tester): per-layer letter classification
  (`neutral | reset(t) | mixed`), passing widths, and the layer action
  monoid `𝒜_R` as a by-product.
- **C3** ((B)-tester): the bounded window-determinacy stages and its
  census output table — the source of the `undecided` layers (K-E1's
  input; 8 786 readings over 2 114 languages) and of Table 3's
  semantics, which K-C1's (B)-mode must match.
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

### K-E1 — (C) on the (B)-undecided stratum — COMPLETE (K-F7/K-F12); one pass open

*Outcome (extended corpus; data `reference/cascade/k_series.md`):* the
old-cut hypothesis ("all frozen, zero conflicts") was a frame
artifact. Of the 8 786 undecided layers, 6 610 decide at k ≤ 2
(6 105/346/159), 505 of them after a k=0 conflict; the 2 176 heavy
layers resolve into 1 021 genuine (C)@0-conflicts (806 aperiodic),
263 persisting at k=1 (246 aperiodic), 118 ladder-rescued, 640
budget-open — every conflict ALG-7-verified. The floor track is
inhabited in-frame (K-F12, type specimen
`2state2ap1acc_parity_3772037665`).

*Remaining run:* the **k=2 pass on the 640 budget-open layers**
(`k_e1_verify <id> <layer> 2`, sharded; consider `--cores 4
--timeout 300` and/or a raised `find_c_conflict` budget — cone growth
saturates 10⁶ states at k=1 already). Extend `reference/cascade/` and
`k_series.md` with the result: each row lands as CONFLICT (feeds
K-E8), CLEAN (ladder rescue at k=2), or BUDGET (stays open).

*(Original procedure, kept for reference: ALG-1..6 per layer, entries
= all `c ∈ R`, widths ascending, stop at first passing width; CSV
columns as in `k_e1_cluster.csv`; CONFLICT → ALG-7; BUDGET → record
which coordinate blew.)*

### K-E2 — the floor map — COMPLETE (K-F9; steps 1–2 subsumed by K-F7/K-F12)

*Question (revised):* C.12 is refuted (Theorem C.12′); the scan now
measures how far the floor extends and whether any failure mechanism
beyond zero absorption exists (draft C.4's mechanisms paragraph).
*Outcome:* steps 1–2 are answered on the extended corpus by
K-F7/K-F12 (the floor-track stratum is inhabited in-frame; the
`2state2ap` shape is in the frame and populated); step 3 confirmed
Prop C.19 (K-F9, the moving-layer transfer specimen); step 4's ALG-7
discipline is now inlined in `k_e1_verify`. Every-width promotion of
the in-frame conflicts moves to **K-E8**.

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

### K-E3 — one-sidedness statistics (scope of Cor C.8/C.9) — COMPLETE (K-F10); recount open

*Outcome (extended corpus):* over the 74 (C)-decided final layers with
a ≥ 2-class collected family: 16 upward / 16 downward / 28 both / 14
neither — the up/down tie is structural (complement-closed catalogue).
The "predominantly upward" prediction is NOT supported at the raw
level. Cor C.9 gating stratum: **0**; prefix-independent languages:
1 104/1 104 with frozen final layers — now **Theorem C.9′** on paper
(prefix-independence ⟹ frozen singleton terminal layers, proved
unconditionally; the census is its confirmation, not its evidence).

*Remaining run:* the rung-stratified recount — cross-tabulate the
74-layer one-sidedness with the ladder rung of `P|_R` (the strength
stratification read-off); the precise E3/C.8 prediction lives at the
recurrence rung, and only this recount can still support or refute it.

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

### K-E5 — DG vs manufactured cascade on the (A)-fallback stratum — MIGRATED

*Subsumed by `sos_toltl_spec.md` E11 (stem half); kept below for
reference only.*

*Hypothesis* (draft C.5, stem side): on the (A)-failing languages
(stratum recount on the current corpus is step 0's first duty),
holonomy cascade + finite-word reach beats DG-on-`𝒜_R`, and cascade
heights sit far below `2^{|R|}`.

0. *Preflight (cheap, reported separately):* recount the (A)-failing
   stratum on the current corpus, then for each of its failing
   layers, record whether it is a final candidate (has an
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

### K-E7 — sandwich scan (the absorption map; C.17 refuted on paper) — COMPLETE (K-F8)

*Outcome (extended corpus):* both positive controls green; over the
6 610 decided layers: absorption 14 050 pairs / group 7 387 /
non-splitting `other` 3 076, **verdict-splitting `other` = 0** — no
third mechanism; the conflict stratum shows the same dichotomy from
the failing side (K-F12). The scan stays enabled by default in every
K-E1-machinery run (including the open k=2 pass).

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

### K-E6 — the fallback's worked instance + prophetic cross-check — MIGRATED

*Step 1 is subsumed by `sos_toltl_spec.md` E11 (loop half, worked
instance). Step 2 (the prophetic `A_S` cross-check) stays with this
note's open problem; parked. Kept below for reference.*

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

### K-E8 — floor certificates: the padded-block scan (Theorem C.12″) — PARKED

*Feeds only this note's K-F12 every-width claim, not the main paper;
run when the floor cartography reopens.*

*Statement scanned* (draft Theorem C.12″): on a frozen singleton layer
`{z}`, pick a pad letter `s ∈ Σ_z` and let `σ := π([s])` (ALG-3). For
a block set `B` (non-empty words over `Σ_z`) and a covering sequence
`w₁ … w_r` of `B`, let `ε(w₁…w_r) := π([w₁]·σ·[w₂]·σ ⋯ [w_r]·σ)`
(plain `M`-products). **Two covering sequences of the same `B` whose
`Val(z, ·)` verdicts differ certify that `{z}` fails (C) at every
width** — a floor inhabitant outright. The check consumes only the
multiplication table and `P`: no cone, no closure, no budget.

*(a) Certificate scan.*
```
for each CONFLICT layer (id, layer) in k_e1w_conflicts_k1.csv   # the 263 first,
        then the 1021 k=0 conflicts, then k=2 output as it lands:
    require R = {z} frozen singleton (every within-layer letter neutral);
        count and skip the rest (they go to a Theory follow-up)
    for s in Σ_z:
        σ := π([s])
        pass 1: blocks = single quotient letters, B ⊆ Σ_z \ {s}, |B| ∈ {1, 2}
        pass 2 (only if no hit): blocks of length 2 over Σ_z, |B| ≤ 2
        for each B, enumerate covering sequences of length ≤ |B| + 1
            (e.g. B = {a,b}: (a,b), (b,a), (a,a,b), (a,b,b), …);
            compare all pairs: ε via M-products, verdicts via Val(z, ε)
        verdict split ⟹ CERTIFICATE: emit (id, layer, s, B, seq, seq′, ε, ε′)
            and stop for this layer
```
*Cost:* table products only — trivially local, no cluster. *Output
CSV:* `id, layer, aperiodic, certified, s, B, seq, seq', time`; lands
in `reference/cascade/` + a `k_series.md` section.
*Expected:* the type specimen `2state2ap1acc_parity_3772037665`
certifies (its conflict is the `a·s^*·a` shape; mandatory positive
control — if it does not certify with pass-1 blocks, widen to pass 2
before concluding anything). The headline number is **how many of the
246 aperiodic k=1-persisters certify**.
*Decision:* certified count → `PAPER-EDIT` on the draft's K-F12
paragraphs ("N of the 246 are floor inhabitants outright"). A
persister that does NOT certify under both passes is a Theory specimen
— either a longer-block certificate exists or a genuinely different
every-width mechanism does; dump its idempotent loop classes and
verdicts at `z` for hand analysis.

*(b) (B̃) strictness at the rescue width* (Lemma C.5(i), the moving
witness). Frozen-singleton rescues are automatic witnesses and already
on paper (`GF(aa)`, K-F6 + Lemma C.10 — degenerate). The open hunt is
a **moving** layer (C)-determined at a width where (B̃) fails: over
the ladder-rescued conflict layers (118 CLEAN-at-k=1 rows of
`k_e1w_conflicts_k1.csv`, plus pass-1's 505 k=0-conflict-but-decided
layers), restrict to *moving* layers and run the (B̃)/window decider
at the rescue width. Any FAIL row is the witness — report it
prominently (`PAPER-EDIT`: C.5(i)'s remark gets its non-degenerate
witness). All-PASS is also data: (B̃) and (C) coincide at the rescue
width on every census moving layer — record and move on.

## 5. Dependency graph

```
K-E0 ──▶ K-E1 ──▶ K-E2      (ALG-5/6/7: one machinery)
           │        │
           │        └─ K-E7  (sandwich scan: piggybacks on every
           │                  K-E1/K-E2 run — enable by default)
           ├──▶ K-E3         (same enumeration, extra classification)
           ├──▶ K-E4         (first emitter; conformance-gated)
           └──▶ K-E8         (table-only: consumes K-E1's conflict CSVs)
K-E5                         (independent: bls bridge plumbing)
K-E6                         (independent; promoted — the fallback's
                              worked instance, C.5)
```
