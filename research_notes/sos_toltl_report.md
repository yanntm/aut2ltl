# SoS → LTL — results

The answer to `research_notes/sos_toltl_experiments.md`: the `aut2ltl/sos2ltl/`
construction run against the paper's worked traces (`research_notes/sos_toltl.md`)
and evaluated over the reference bench. Each section answers one experiment id
and states the results **in force**; each finding `Fn` is a fact the census
settled (some are verdicts on spec predictions), kept under its id for
cross-reference. Open work per section sits on explicit *Remaining* lines;
the todo ledger is the spec's. History lives in git, not here.

## The bench (§3b frame)

`genaut/corpus/flat_canon/` — the flat-canonical catalogue: one deterministic
**Emerson–Lei** automaton `D` (`det/`) and one syntactic invariant `𝓘(L)`
(`sos/`) per distinct language, folded across every shape and closed under
complement. **3938 languages, 2240 LTL / 1698 non-LTL**, exactly two degenerate
(`∅`, `Σ^ω`), no non-degenerate single-word-class language. The catalogue is
exhaustive over the shapes below the tractability wall and **sampled** for the
`2state1ap2acc_parity` beyond-wall shape (present languages are real; absence
proves nothing there); the acceptance families present are generalized-Büchi
(`gba`, Inf-conjunction) and parity.

The `.sos` unit **is** the language — structurally, not by convention: `det/`
and `sos/` are 1:1 and deduplicated by the syntactic key ([SωS26 Thm 5.1],
byte-equal iff the languages are equal), so §3b's automaton-vs-language
weighting question is dissolved by the corpus rather than answered by a
convention. Each language carries a `.cat` category sidecar (its LTL cut and
**Wagner degree** `ϕ = (γ, s)`, read off `𝓘(L)` by a pure table search), and
`ϕ` is the ventilation axis throughout — the intrinsic-complexity axis in place
of per-shape rows. The per-shape *presentation* funnel (automata, not
languages) lives in `genaut/SHAPES.md`.

## Components (C1–C5, C7)

Present in `aut2ltl/sos2ltl/`: `cayley.py` (C1 — `Cay(L)`, its SCCs and DAG,
asserting SCCs = R-classes of `M` per input, paper Lemma 4.3), `anchoring.py`
(C2 — condition (A), widths `k ≤ 3` with the layer action monoid `𝒜_R` as a
by-product), `windows.py` (C3 — condition (B), the three-stage bounded tester,
F1), `readoffs.py` (C5 — λ-quotient, prefix-independence from the residuals,
complement flip; the aperiodicity read-off lives in the classifier subproject
`sosl/sosl/sos/classify/aperiodic/` and is consumed, not duplicated),
`witness/` (§4 certificate + the presentation-agnostic toggle replay + the dual
scan), `dg/` (the Diekert–Gastin baseline, E4b), and `engine.py`
(C4 — the walk+window transcription; sound, width-1 and graded strata both
live — Theorem 4.10 and Theorem 4.13 with the seam and `step_th` bricks,
F8/F15; only no-width layers and window-term gaps fall to the DG
baseline). The `translator.py`
flow: bridge `Language → 𝓘(L)`; a step-0 group scan (a certificate replayed by
membership against the *input* automaton before the absorbing `NOT_LTL`, a
failed replay declining, never verdicting); on an aperiodic invariant the
transcription engine, else the dg baseline. The bridge builds `𝓘(L)` from the
Language's base automaton (`canonical` determinizes and completes it) — the
invariant is language-canonical, independent of the seeding presentation.

The gate: `python3 -m tests.sos2ltl.e0_gate` — 29 cases, one subprocess per
case under a 15 s cap, SUCCESS. Individual probes `e0_{layers,anchoring,windows,
witness,dg,translator,canon}`, `e7_dualscan`, and the graded-band gates
`seam_gate` (the Thm 4.13 seam witness) and `engine_diff` (per-class label
grounding against the invariant, the F15 diagnostic) under `tests/sos2ltl/`.

## E0 — the triptych

C1/C2/C3/C5 + the certificate on `GF(aa)`, `Even`, `EvenBlocks`, against the
paper's hand-computed predictions ([SωS26, Table 3]):

| prediction (paper §4.3, §5.4) | run | verdict |
|---|---|:--:|
| `GF(aa)` aperiodic, 6 classes | aperiodic, 6 classes | ✓ |
| `Even`/`EvenBlocks` group: carrier `[a]`, index 1, period 2, cycle `{[a],[a·a]}` | identical, both | ✓ |
| `GF(aa)` layers `{0},{1,3},{2,4},{5}`, R-order `0 → {1,3} \| {2,4} → 5` | identical | ✓ |
| SCCs of `Cay(L)` = R-classes of `M` (paper Lemma 4.3), asserted per input | holds on every input | ✓ |
| `{1,3}`,`{2,4}` pass (A) at `k=1`; letter tables `!a↦reset(1)/reset(4)`, `a↦reset(3)/reset(2)` | identical | ✓ |
| `{5}` frozen (both letters neutral), `{0}` both exit | identical | ✓ |
| `Even`/`EvenBlocks` group layers fail (A) at every width | FAIL (mixed swap action never stabilizes) | ✓ |
| `{5}` fails (B) at `k'=1` on the width-1 conflict pair | witness `(a·!a)^ω` vs `(aa·!a)^ω`, replayed with opposite verdicts | ✓ |
| `{5}` passes (B) at `k'=2` | PASS width 2 (cap-bounded; F1) | ✓ |
| `{1,3}`,`{2,4}` as final layers all-rejecting ⟹ (B) trivial | trivial PASS width 1 (exact cycle-class closure) | ✓ |
| `GF(aa)` prefix-independent (1 residual) | `P` loop-determined: yes | ✓ |
| `Even` certificate `F₁(u=a, v=a, x=(!a)^ω, p′=2)` byte-exact | byte-exact, toggle 5/5 | ✓ |
| `EvenBlocks` certificate `F₂(u=ε, v=a, y=a·!a, p′=2)` byte-exact; linear scan all-constant first (Prop 4.2) | byte-exact, toggle 5/5; linear scan exhausted constant | ✓ |
| spec C3 cycle-length cap `⟨2·\|R\|·\|Σ_λ\|⟩` sufficient | **REFUTED** — false PASS on `EvenBlocks` layer `{6}` | ✗ F1 |

Canonicity is observed end-to-end: two presentations of `GF(aa)` (the parity
and the reset automata) bridge to the byte-identical `.sos` and synthesize the
character-identical formula (19 nodes / arena 1287 / flat 1 991 717 —
`e0_dg`).

## E1 — anchoring, by Wagner degree

Non-degenerate LTL languages (2238), ventilated by `ϕ`. `A@1` anchors at width
1; `A≤3` within the tester's `k ≤ 3`; `FAIL` layers anchoring at no `k ≤ 3`
(the (A)-tester tops out at 3, so its gap *is* the scoped-fallback stratum,
paper Props 4.11/4.14); `stemk3` languages every layer of which anchors at `k ≤ 3`;
`pfxind` prefix-independent. Built by `census_build` → `census_report`.

| `ϕ=(γ,s)` | class | langs | layers | A@1 | A≤3 | FAIL | frozen | stemk3 | pfxind |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| (1,δ) | clopen | 62 | 568 | 100% | 100% | 0 | 50.7% | 100% | 0% |
| (1,σ) | guarantee | 678 | 7263 | 63.2% | 82.5% | **716** | 20.8% | 67.7% | 0% |
| (1,π) | safety | 678 | 7263 | 63.2% | 82.5% | **716** | 20.8% | 67.7% | 0% |
| (2,σ) | Σ₂ | 4 | 19 | 100% | 100% | 0 | 68.4% | 100% | 0% |
| (2,π) | Π₂ | 4 | 19 | 100% | 100% | 0 | 68.4% | 100% | 0% |
| (ω,σ) | Gδ / DBA | 368 | 1694 | 95.6% | 100% | 0 | 61.4% | 100% | 12.0% |
| (ω,π) | Fσ / DCA | 368 | 1694 | 95.6% | 100% | 0 | 61.4% | 100% | 12.0% |
| (ω²,σ) | parity | 38 | 281 | 80.8% | 100% | 0 | 38.4% | 100% | 31.6% |
| (ω²,π) | co-parity | 38 | 281 | 80.8% | 100% | 0 | 38.4% | 100% | 31.6% |
| **POOLED** | | 2238 | 19082 | 70.6% | 86.7% | 1432 | 29.5% | 80.4% | 5.0% |

The profile is **exactly duality-symmetric** (every `σ` row equals its `π`
dual — the catalogue is complement-closed and aperiodicity / anchoring is
complement-invariant), a free cross-check on both the corpus and the tester.
Prefix-independence **climbs with degree** (0% at depth 1, 12% at ω, 31.6% at
ω²) and is nowhere the majority.

### F6 — the (A)-fallback stratum is exactly Wagner depth 1

The 1432 FAIL layers are located precisely:
**every one is at `ϕ = (1,σ)` or `(1,π)`** (guarantee / safety), 716 apiece by
duality. The clopen islands `(1,δ)`, the `(2,·)` pair, and **all** the higher
Borel degrees — `(ω,·)` DBA/DCA and `(ω²,·)` parity — anchor with **zero**
FAIL: the scoped DG
fallback's raison d'être is entirely the Wagner-degree-1 tier (safety /
guarantee languages whose entry layers resist finite-width anchoring). This is
§7's inner-frontier fraction as a measurement. The AP axis carries nothing:
every (A)-failing language is **1 AP**, none at 2 or 3 AP, and the
floor is `|𝒞| = 15` at 3 states (`3state1ap0acc_004260`, F14) — the (A)
frontier is algebra size, not alphabet width.

## E2 — window determinacy, by Wagner degree

C3 over all final-candidate layers of the non-degenerate LTL languages, same
buckets. Grades are three-valued (exact/cap-bounded PASS, UNDECIDED, FAIL) and
never pooled away:

| `ϕ=(γ,s)` | final | PASS | UND | FAIL | k′≤2 | PASSwidth |
|---|--:|--:|--:|--:|--:|--:|
| (1,δ) | 288 | 288 | 0 | 0 | 100% | {1: 288} |
| (1,σ) | 4626 | 4626 | 0 | 0 | 100% | {1: 4626} |
| (1,π) | 4626 | 4626 | 0 | 0 | 100% | {1: 4626} |
| (2,σ) / (2,π) | 15 ea | 15 | 0 | 0 | 100% | {1: 15} |
| (ω,σ) / (ω,π) | 1256 ea | 1161 | 95 | 0 | 92.4% | {1: 1146, 2: 15} |
| (ω²,σ) / (ω²,π) | 217 ea | 126 | 91 | 0 | 58.1% | {1: 123, 2: 3} |
| **POOLED** | 12516 | 12144 | 372 | 0 | 97.0% | {1: 12108, 2: 36} |

**(B) is clean catalogue-wide: 0 FAIL at every degree** — a *frame* fact: a
(B)-failing final layer needs 2 states and 2 AP at once (`G(a → F b)`, F13),
a shape the catalogue omits; the H3 minimality hunt lives at census-next
`2state2ap`.
The only 372 UNDECIDED are the frozen-final-layer node-budget stratum (F1), and
they sit entirely at `(ω,·)` and `(ω²,·)` — the DBA/parity degrees whose frozen
loop classes wander the whole algebra (depth ≤ 2 has none). The width-2 PASSes
are likewise an ω/ω² phenomenon.

### F1 — the (B) tester's cap scales with `|𝒞|`, and the verdict does not factor through the memory subgraph

The spec's provisional cap `2·|R|·|Σ_λ|` (= 4 on a singleton 1-AP layer) makes
the bounded (B) test report **PASS at `k'=3`** on `EvenBlocks`' frozen layer
`{6}` — the language whose non-LTL-ness *is* ω-power counting. The real conflict
sits one letter past the cap: `(a⁴·!a)^ω` and `(a⁵·!a)^ω` have equal recurring
3-window sets (`{aaa, aa!a, a!aa, !aaa}`) and opposite verdicts (block parity 4
vs 5). Two lessons:

1. *No cap local to the layer can work.* The verdict of a confined tail ending
   on a loop `z` at class `d` is `(d·e, e) ∈ P` with `e` the idempotent power
   of `[z]` — folded through the **whole** algebra `𝒞`, not the layer. On a
   frozen singleton layer the walk sees nothing while the loop class wanders all
   of `𝒞`; the separation lengths are governed by `|𝒞|`, so any bound in `|R|`
   and `|Σ_λ|` alone is refutable. The tester uses `2·|R|·|𝒞|` (which catches
   the `EvenBlocks` conflict), but no sufficiency theorem exists for it either.

2. *The verdict is not a function of the covering subgraph.* At `k=3` the two
   witness tails traverse **the same** strongly connected subgraph `H` of
   `G(R,c)` — identical recurring edge sets — and still disagree. So deciding
   (B) cannot enumerate subgraphs and evaluate one verdict per subgraph: the
   verdict factors through the *loop class of the covering tour*, and one
   subgraph carries tours of several loop classes (here both group phases). The
   object per subgraph `H` is its loop-class closure `{ [w] : w labels a closed
   covering walk of H }` ⊆ `𝒞`, computable by a `(node, class, covered-edges)`
   closure; (B) at width `k` holds iff, grouping across subgraphs with one
   window projection, all induced pair verdicts agree. The finiteness lives in
   `𝒞`, never in the graph. (Paper Prop 5.4(iii) and spec C3 carry both
   points.)

Implementation: stage 2 (trivial pass) is exact and polynomial (the per-class
cycle-class closure — one verdict across all proves (B) at every width); stage 3
enumerates cycle words to `2·|R|·|𝒞|` under a node budget (a conflict is an
exact FAIL with a replayable lasso pair; conflict-free complete is a cap-bounded
PASS; a tripped budget is UNDECIDED). **Open theory item:** either prove a
sufficient cap (the excision route founders on the report's own care point —
excising a repeated product state preserves the verdict but not the
recurring-window set, and a (B)-conflict is a pair of tours with *equal* window
sets), or adopt the cap-free `(node, class, covered-edges)` closure as the
normative procedure and price it. Until one is frozen a cap-bounded PASS is not
a theorem, and the tables keep the three-valued grade.

## E4-interim — the DG size ledger

The DG baseline (`sos2ltl_dg`) over the catalogue (`--use sos2ltl_dg`; the
aperiodic-only naive transcription, no engine, no simplifier): **2237
languages emitted, 0 timeout, 0 crash**, total flat-tree-carrying **DAG
3 829 657**; verification, where Spot terminates in cap, **159 TRUE, 0 FAIL,
2078 SIZE** — the SIZE rows are `FLAT_OVERFLOW`, the §3 explosion measured as
a *distribution* rather than the single `GF(aa)` exemplar (19 nodes / arena
1287 / flat 1 991 717). Group-bearing (non-LTL) inputs are declined upstream by
the aperiodicity read-off (1701 declines). The engine column (a): sound —
**0 FAIL** (F8) — where it answers (width-1 layers
and committed-accepting classes), the non-committed graded stratum declining
to DG. Its DAG is
~3× below the baseline where it does answer — the compression the paper's §6
predicts. Remaining: the full (a)-vs-(b) ledger, at M3 with the graded
engine.

## E7 — certificate validation: the dual scan and ω-blindness tiers

`dual_scan` partitions each `flat_canon/sos/*.sos` (None ⟹ aperiodic / LTL; a
`DualScan` ⟹ non-LTL certificate) and runs **both** context shapes to
completion. The certificate verifier is **membership-only and
presentation-agnostic**: a counting family validates by `2p′+1` lasso
membership queries against *any* acceptor of `L` (`witness/spot_oracle.py`
renders a `sosl.sos.Lasso` to a Spot lasso-string feeding the
acceptance-agnostic `member`), the SoS read-off surviving only as a labelled
self-check. Over the **1698 non-LTL** languages: **1490 both shapes, 100
linear-only (H5), 108 ω-only**; **every** certificate replays against its
`det/` `D` by membership (0 replay failures — the verifier holds
catalogue-wide); component lengths ≤ **6** against `|𝒞|` ≤ 121 (Theorem 4.4's
`< |𝒞|`, with margin). Ventilated by degree (`e7_ledger` → `e7_tiers`):

| `ϕ=(γ,s)` | non-LTL | both | ω-only | H5 | RI | PC-only | P-level |
|---|--:|--:|--:|--:|--:|--:|--:|
| (1,σ) / (1,π) | 678 ea | 673 | 0 | 5 | 0 | 5 | 0 |
| (ω,σ) / (ω,π) | 98 ea | 38 | 26 | 34 | 4 | 0 | 30 |
| (ω·2,σ) / (ω·2,π) | 12 ea | 12 | 0 | 0 | 0 | 0 | 0 |
| (ω²,σ) / (ω²,π) | 61 ea | 22 | 28 | 11 | 0 | 0 | 11 |
| **POOLED** | 1698 | 1490 | 108 | 100 | 8 | 10 | 82 |

Duality-symmetric. The triptych vectors: `Even` separates in **both** shapes
(linear `F₁(u=a,v=a,x=(!a)^ω,p′=2)` and ω-power `(u=ε,v=a,y=a·!a,p′=2)`, the
same family that certifies `EvenBlocks`), `EvenBlocks` is linear-all-constant
(ω-power only); neither is an H5 hit.

### F5 — ω-blind languages exist: F₂ is not always available (Proposition 4.5)

A language whose ω-power scan is **all-constant** is *ω-blind* — certifiable in
the linear shape only (an H5 hit), the dual of Proposition 4.2's
prefix-independent ⟹ linear-blind. There are **100** across the catalogue, so
spec-H5's "F₂ always available" is **REFUTED** and running both scans is
necessary, not a convenience. The symmetric 108 ω-only languages are F₁-blind —
the *theorem* side (prefix-independent ⟹ linear context constant); the 100 H5
hits are the side theory had no theorem for and leaned toward "cannot happen".

**The mechanism, Proposition 4.5 (sufficient direction, proved).** A
period-`>1` cycle `C` that is a **right ideal** (`C·𝒞¹ ⊆ C`; checking
`C·λ(Σ) ⊆ C` suffices) is closed under products, hence a finite group with a
single idempotent `e_C`; every pumped loop class `g^{m+i}·y` folds to `e_C` and
every ω-power verdict is the constant `(x·e_C, e_C) ∈ P` — unconditional
acceptance. If *every* period-`>1` cycle is a right ideal, no valid F₂ family
exists. This holds catalogue-wide with **zero** counterexamples
(`¬H5 & right-ideal = 0`).

**Smallest exhibit — `2state1ap1acc_04644`, `|𝒞| = 4`, degree (ω,σ) (DBA-proper).**
The language `L₄ = { w : |w|_{!a} = ∞ } ∪ { w : |w|_{!a} < ∞ and even }` — "if
only finitely many `!a` occur, their number is even". Non-LTL because that
parity is a group on the finite-`!a` stratum; ω-blind because every ω-power
context `(vⁿ·y)^ω` whose loop carries an `!a` has infinitely many `!a` and is
accepted unconditionally — the ω-power scan sees only constants. Only the linear
shape separates: `F₁(u=!a, v=!a, x=a^ω, p′=2)` drives the word into the
absorbing `a^ω` tail, exposing the finite-`!a` parity (samples
`(!a)^{n+1}·a^ω`, accept iff `n` odd), replaying 5/5 against `D` by membership.
Its complement (odd count) is `2state1ap1acc_16929`.

Canonical `D`:

    HOA: v1
    States: 2
    Start: 0
    AP: 1 "a"
    Acceptance: 1 Inf(0)
    --BODY--
    State: 0
    [0] 0 {0}
    [!0] 1 {0}
    State: 1
    [!0] 0 {0}
    [0] 1
    --END--

Syntactic invariant `𝓘(L₄)` (with the residual trailer — a two-state parity
residual DFA):

    SOS v1
    ap: a
    classes: 4
    0 eps
    1 !a
    2 a
    3 !a;!a
    letters: !a->1 a->2
    mult:
    0: 0 1 2 3
    1: 1 3 1 1
    2: 2 1 2 3
    3: 3 1 3 3
    accept:
    1 3
    2 2
    3 2
    3 3
    residuals: 2
    0 eps
    1 !a
    res-step:
    0: 1 0
    1: 0 1

The group is `{[!a], [!a·!a]}` (order 2, idempotent `[!a·!a]` = class 3); the
idempotents are `[a]`, `[!a·!a]`, `[ε]`. `res-step` is the parity toggle on
`!a` — the residual DFA the aperiodic reading cannot see is periodic.

### F4 — the two shapes are an asymmetry, not a duality

The global dual scan (contexts over all of `𝒞`) shows `Even` separates in
**both** shapes — the ω-power family being the very `F₂` that certifies
`EvenBlocks` — so no §4.3 remark that each specimen speaks in exactly one shape
survives globally. The clean reason: an ω-power family `u·(vⁿ·y)^ω` with `u=ε`
pumps the very start of the word, exposing a prefix-counting group to ω-power
contexts; nothing in §4 promised the dual of Proposition 4.2. So the two shapes
are an **asymmetry**: *prefix-independent ⟹ linear-blind* is a theorem (the 108
ω-only languages), while the dual blindness (the 100 H5 hits) has no
multiplicative theorem — F7. The paper states the confined claim plus
the asymmetry (§3); the layer-confined (B) statistics still see nothing of `Even`'s
group (every within-layer cycle of the group layer `{2,4}` is a pure-`a` cycle
of even length, all folding to one rejecting class).

### F7 — right-ideal is sufficient but not necessary; ω-blindness has no multiplicative characterization

The E7 mechanism cross-tab `H5 × right-ideal`: `¬H5 & RI = 0`, `H5 & RI = 8`,
`H5 & ¬RI = 92`. Proposition 4.5's prediction that all H5 hits are right-ideal
is **REFUTED** (only 8 of 100) — but its load-bearing half survives
(`¬H5 & RI = 0`, no counterexample to `right-ideal ⟹ ω-blind`, no stop-the-line
bug). The candidate exact condition, *phase-collapse* (PC — for every suffix
`y` the idempotent power `(c·y)^π` is one class independent of `c ∈ C`), is
**also refuted as a characterization**: the guards `right-ideal ⟹ PC ⟹ H5` hold
catalogue-wide (0 violations), both containments strict, and the 100 H5 split
into three tiers:

| tier | condition | langs | where (Wagner degree) |
|---|---|--:|---|
| right ideal | `C·λ(Σ) ⊆ C` | 8 | (ω,·) DBA/DCA, `\|𝒞\| ≥ 4` |
| phase-collapse only | `(c·y)^π` phase-free, `C·y ⊄ C` | 10 | (1,·) guarantee/safety, `\|𝒞\| = 6…` |
| P-level only | neither; ω-blind via `P` | 82 | (ω,·) and (ω²,·), `\|𝒞\| ≥ 9` |

The 82 P-level languages are ω-blind with PC false. **Why no multiplicative
characterization exists** — the P-level exhibit `2state1ap1acc_01681`
(`|𝒞| = 13`; smallest P-level hit `_04900`, `|𝒞| = 9`): its sole group
`C = {6, 9}` has both elements at idempotent power `6`, yet every PC-breaking
suffix `y` sends `6` and `9` to *distinct* idempotents (`y=[!a]`: `6·y↦3`,
`9·y↦11`) that are nonetheless **`P`-equivalent** — `(x·3,3) ∈ P ⇔ (x·11,11) ∈ P`
for every `x`. So `Val` is phase-constant not because the algebra collapses the
phase but because `P` cannot separate the two phase-idempotents; the same
`(𝒞, ·)` under a `P` that separated them would be ω-*visible*. The exact
ω-blindness condition is therefore inherently **acceptance-level**
(`∀ x, y : (x·(c·y)^π, (c·y)^π) ∈ P` independent of `c ∈ C` — the extractor's
own scan), and no condition on `(𝒞, ·)` alone can be necessary. The three tiers
survive as a *sufficient-condition hierarchy* of cheap certificates; both
mechanism columns stay in the ledger, guards live. Two exhibits complete the
tiers: right-ideal `2state1ap1acc_04644` (`|𝒞|=4`, F5), phase-collapse-only
`3state1ap0acc_004376` (`|𝒞|=6`, the `!a`-parity group ejected by `a` into a
region of uniform idempotent power). The mechanism probe scans ω-contexts
around **every** period-`>1` cycle, confirming a column-false H5 is genuinely
ω-blind, not a first-group scan artifact.

### F3 — classification convention at the diagonal

E0 reports layer `{5}` as "both letters neutral" while Definition 4.4's diagonal
doctrine makes a `{c↦c}`-only letter an anchor of `A(c)`. The implementation
does both: the *report kind* is identity-first (`neutral`), while `A(c)`
membership is constant-action (diagonal included). The paper fixes this as its
reporting convention (§4.2). Resolved — no divergence.

## §3 conformance and F8 — engine status: sound catalogue-wide, the graded stratum declining to DG

**Status.** `--use sos2ltl` over the catalogue, verified by the Spot oracle:
**0 verified-non-equivalent answers** (survey SUCCESS); the certificate side
and the DG fallback are likewise clean (`sos2ltl_dg`: **0 FAIL**, only
SIZE-unverified explosions). Conformance is carried by the survey oracle
itself — an in-pipeline Spot round-trip gate
(`invariant_of(import_ltl(flat))`) is *not* used: it is an unbounded outside
step that duplicates the oracle and times out on large flats.

Two engine invariants carry the soundness, each with the stratum where it
bites (F8):

**Window terms render the λ-class, never a representative.** `Ω(R,c)`'s
window positions are letter *classes*; rendering a class as its shortlex
representative's cube under-approximates. On `L = GF(a|!b)`
(`1state2ap1acc_030`, `|𝒞|=3`, degree (ω,σ)) the frozen layer's window family
has the three minimal singletons `{a&!b}, {!a&!b}, {a&b}` — the concrete
letters of the quotient letter `(a|!b)` — and
`Ω = GF(a&!b) ∨ GF(!a&!b) ∨ GF(a&b) = GF(a|!b)` exactly
(`engine.py::_Letters`). The distinction needs **≥ 2 AP** (at 1 AP a quotient
letter is a single literal or `⊤`) and floors at `|𝒞|=3`; 448 catalogue
languages sit on it.

**Committed classes short-circuit to `true`; non-committed graded layers
decline to DG.** A committed-accepting class — every linked pair whose stem is
reachable from `c` lies in `P`, so `T_c = Σ^ω` — takes `Final(c) = true`
(the `O(|𝒞|²)` read-off `_committed`), the common case on the
guarantee/safety stratum (`|𝒞| ≥ 12`, ≥ 4 states, degree (1,·) — 394
catalogue languages). A `k ≥ 2` layer carrying a non-committed class declines
(`transcribe` returns `None`, falling to the DG baseline): the Theorem 4.13
exit-chain **without the seam bricks** under-approximates near the entry — an
exit within `k` steps of the transient is certified by a `κ`-window straddling
the transient seam, which `TL_0`'s `U` cannot witness (paper §4.3). The
committed short-circuit is exact; the decline guard is necessary until the
seam bricks land.

Smallest exhibit — **`2state1ap0acc_086_c`: `|𝒞| = 12`, 4 states, 1 AP, degree
(1,σ) (properly open — guarantee).** A reach-the-accepting-sink language.
Canonical `D` (weak Büchi):

    HOA: v1
    States: 4
    Start: 1
    AP: 1 "a"
    Acceptance: 1 Inf(0)
    --BODY--
    State: 0 {0}
    [t] 0
    State: 1
    [0] 0
    [!0] 2
    State: 2
    [!0] 2
    [0] 3
    State: 3
    [!0] 1
    [0] 3
    --END--

Syntactic invariant `𝓘(L)` (12 classes, 15 accepting linked pairs — the
multi-layer structure the bricks assemble across):

    SOS v1
    ap: a
    classes: 12
    0 eps
    1 !a
    2 a
    3 !a;!a
    4 !a;a
    5 a;!a
    6 !a;!a;a
    7 !a;a;!a
    8 a;!a;!a
    9 a;!a;a
    10 !a;!a;a;!a
    11 !a;a;!a;!a
    letters: !a->1 a->2
    mult:
    0: 0 1 2 3 4 5 6 7 8 9 10 11
    1: 1 3 4 3 6 7 6 10 11 9 10 3
    2: 2 5 2 8 9 5 2 9 8 9 5 9
    3: 3 3 6 3 6 10 6 10 3 9 10 3
    4: 4 7 4 11 9 7 4 9 11 9 7 9
    5: 5 8 9 8 2 9 2 5 9 9 5 8
    6: 6 10 6 3 9 10 6 9 3 9 10 9
    7: 7 11 9 11 4 9 4 7 9 9 7 11
    8: 8 8 2 8 2 5 2 5 8 9 5 8
    9: 9 9 9 9 9 9 9 9 9 9 9 9
    10: 10 3 9 3 6 9 6 10 9 9 10 3
    11: 11 11 4 11 4 7 4 7 11 9 7 11
    accept:
    2 2
    2 6
    5 7
    5 10
    8 3
    8 8
    8 11
    9 2
    9 3
    9 6
    9 7
    9 8
    9 9
    9 10
    9 11

On this exhibit `D`'s start reads `a → sink`, so `a⁻¹L = Σ^ω`, and classes
`2 = [a]`, `5 = [a·!a]`, `8 = [a·!a·!a]` have `T_c = Σ^ω` — committed to
acceptance, so `Final(c) = true`, whence `Final(0)`'s `a`-arm `= a ∧ X true = a`
("first letter `a` ⟹ accept", correct: `a·a·a·!a·a·(!a)^ω` accepts). The layer
`{2,5,8}` is 2-anchored (`a` a partial constant onto `2`, `!a` acting
`2↦5↦8↦8`: mixed at width 1, constant at length ≥ 2), and the word
`a·a·!a·a·(!a)^ω` is the paper's §4.3 seam witness: its certifying window
`(a,a,!a) ∈ An_3(5)` opens at the entry. The exhibit declines to DG — a
correct, SIZE-unverifiable formula.

**Remaining (construction-level, M3).** Implement Theorem 4.13's graded bricks
**with the seam disjuncts `seam(c)`** (paper §4.3 — the exit-chain is
incomplete without them) and lift the decline guard for non-committed graded
layers. Do **not** implement the entry-rooted `U` variant — a disjunct
`sojourn(r) ∧ (step_κ U ⋯)` scanned from the entry is unsound (paper §4.3,
the seam remark). Gate: this section's exhibit word must accept via the root
seam disjunct. Until then, decline-to-DG is the sound guard, and the committed
short-circuit carries the guarantee/co-safety stratum exactly.

## E10 — branch factoring: guard synthesis, guard grouping, residual-indexed exits

The three renderings of spec E10, implemented and priced. All three are
exactness-preserving by the label contract (any exact label for the tail
language serves), and each is switchable (`engine.Rendering`) so the ledger
can hold the others fixed. Two structural facts underpin the numbers.

**F9 — the class memo only pays on a hash-consed AST.** `engine.py` builds a
hash-consed `spot.formula` end to end; `Final(d)` is one node, referenced at
every exit arm. A string-spliced rendering (re-parsing flats to recover a
DAG) pays *flat-tree* cost at construction time — the very explosion §3
measures on the DG baseline — and defeats the class-indexed sharing the
construction is about.

**F10 — guard grouping keys on the child, not on the target class.** Fans
group on the **child key** — the class, or the residual when indexing is on
(spec E10(1)). Keying on the target class blocks E10(2)'s residual indexing
from firing *through* the grouping: two classes with one residual stay two
arms carrying the same child. Child-keying is what turns the `⊤`-guard arc
("all exits one target") from a rarity into the common case; the two sharings
do not compose otherwise.

### The triptych of renderings on one language

`1state2ap1acc_030` = `GF(a ∨ ¬b)` (`|𝒞| = 3`, 2 AP, degree (ω,σ)) — the F8
defect-1 exhibit, prefix-independent. **Two size regimes**: the raw label, which
the paper prints for traceability of the bricks on small examples, and the
shipped label after the `hi` simplifier the `sos2ltl` recipe applies
(`Simplify(sos2ltl, "hi")`) — the size a claim is about.

| rendering | raw DAG | raw tree | **hi DAG** | hi tree |
|---|--:|--:|--:|--:|
| plain (cube guards, per-letter fans, class children) | 28 | 222 | 11 | 28 |
| + minimized guards (item 0) | 25 | 141 | 11 | 28 |
| + grouping (item 1) | 22 | 76 | 11 | 28 |
| + residual indexing (item 2) | 13 | 45 | **6** | 6 |
| **both sharings** | 7 | 7 | **6** | 6 |

Raw, the collapse to `X GF(a | !b)` needs the *composition*: neither sharing
alone reaches it (grouping stops at 22, residual at 13), because the two exit
arms have different target classes but one residual — keying the fan on the
residual merges them and the guard becomes `⊤`.

Simplified, the picture inverts and is the honest one. **Guard synthesis and
guard grouping are entirely subsumed by Spot** (all three top rows land at
DAG 11): they remove syntactic redundancy, and `X GF φ ≡ GF φ` is a rewrite
Spot does for free. **Residual indexing is not subsumed** — it is what takes the
formula to `GF(a | !b)` (DAG 6), because it identifies two *different classes*
as one tail language, a semantic fact about `P` that no formula-level simplifier
can recover. The sharings that matter after simplification are the ones the
simplifier cannot do; the others earn their keep by keeping the DAG small
enough that Spot's containment checks stay affordable (`_SIMP_FULL_LIMIT`).

### The ledger (1114 rendered languages of `flat_canon`)

`e10_ledger` → `e10_report`, keyed by language, ventilated by Wagner degree.
Of the 3938 catalogue languages: 1698 group (non-LTL, no formula), 1126 decline
to DG (the F8 guard), **1114 rendered by the engine**. Sizes summed per row,
post-`hi` (the shipped label); the raw columns are in the log.

| `ϕ=(γ,s)` | langs | hi-DAG plain | guards | +group | +residual | **all** | win |
|---|--:|--:|--:|--:|--:|--:|--:|
| (1,δ) | 62 | 457 | 457 | 457 | 457 | 457 | 1.00× |
| (1,σ) | 207 | 2913 | 2913 | 2928 | 2609 | 2618 | 1.11× |
| (1,π) | 207 | 2534 | 2534 | 2542 | 2297 | 2268 | 1.12× |
| (2,σ) / (2,π) | 4 ea | 25 / 29 | = | = | = | = | 1.00× |
| (ω,σ) | 305 | 9118 | 6943 | 5369 | 3738 | 3718 | 2.45× |
| (ω,π) | 305 | 14397 | 12916 | 8642 | 6431 | 6220 | 2.31× |
| (ω²,σ) | 9 | 337 | 329 | 297 | 176 | 176 | 1.91× |
| (ω²,π) | 9 | 690 | 516 | 417 | 303 | 303 | 2.28× |
| **POOLED** | 1114 | 30502 | 26664 | 20708 | 16067 | **15816** | **1.93×** |

Post-`hi`, the three renderings together shrink the shipped DAG **1.93×** and
the shipped flat tree **18.1×** (1 702 355 → 32 134), concentrated at degree ω
and above where the layer stacks are deep. Raw (traceability sizes, no
simplifier): DAG 38 061 → 24 579 (1.55×), tree 2 002 480 → 90 788 (22.1×).

Structure: over 5096 exit fans, classes see 8088 distinct children, residuals
7322; 51.0% of fans are single-child under class keying, 56.3% under residual
keying, and **264 fans carry a `⊤` guard** (every letter exits to one child).

At the survey level the win is invisible (total DAG 1 862 441 → 1 856 896,
0.3%): the engine renders 1114 languages, the other 1126 LTL languages decline
to the DG baseline (F8's guard), and DG's DAGs dominate the total. The E10
ledger is the honest frame — it measures the engine where the engine answers.

### F11 — the simplifier subsumes the syntactic sharings, not the semantic one

The decisive column is post-`hi`, because the `sos2ltl` recipe ships
`Simplify(sos2ltl, "hi")` and Spot rewrites cosmetic residue (`X GF φ ≡ GF φ`)
for free. Splitting the pooled win by rendering, against the `guards` baseline:

| sharing | raw DAG | hi DAG | verdict |
|---|--:|--:|---|
| guard grouping (item 1) | 1.06× | 1.29× | partly survives |
| residual indexing (item 2) | 1.34× | **1.66×** | survives |
| both | 1.52× | **1.69×** | — |

and guard synthesis (item 0) is worth `1.00×` on the raw *tree* below 2 AP:

| AP | langs | tree plain → guards | hi-DAG plain → all |
|---|--:|--:|--:|
| 0 | 2 | 1.00× | 1.00× |
| 1 | 540 | **1.00×** | 1.14× |
| 2 | 112 | 1.44× | 1.97× |
| 3 | 460 | 2.26× | **2.48×** |

Two mechanisms, only one of which the simplifier can imitate. Guard synthesis
and guard grouping remove *syntactic* redundancy — a cube union that is really
one literal, a fan arm that repeats its sibling's child — and on the E10 exhibit
Spot recovers all of it unaided (plain, guards, guards+group all land at
hi-DAG 11). Residual indexing removes a *semantic* redundancy: it identifies two
distinct classes as one tail language, a fact about `P` that no formula-level
simplifier can see, and it is what takes the exhibit to `GF(a | !b)` (hi-DAG 6).
That is why grouping's advantage grows post-`hi` (1.06× → 1.29×) only where the
DAG was large enough to defeat Spot's own containment checks
(`_SIMP_FULL_LIMIT` gates the expensive rules by tree size): the syntactic
sharings earn their keep by keeping the input *affordable* for the simplifier,
not by doing the simplifier's job. (The paper claims the post-simplifier
size, per its §8 convention.)

Cost side, unpredicted: guard minimization **never** enlarges the raw tree
(0 of 1114) but enlarges the raw **DAG** on 82 languages, all 3-AP (exhibit
`1state3ap1acc_00262`: DAG 34 → 36, tree 566 → 404). The `2^{|AP|}` concrete
cubes are a small fixed vocabulary that every guard position reuses, whereas
each minimized guard is bespoke to its letter set — fewer nodes per guard, more
distinct guards. Flat size and DAG size are optimized by opposite renderings.

### F12 — residual indexing is not monotone, and it fires on the *majority*

Two spec-E10 predictions refuted:

1. *"Residual indexing fires on a measurable minority of languages."* Classes
   are strictly finer than residuals on **1012 of 1114** rendered languages
   (90.8%) — the vast majority, not a minority. The prediction's own reasoning
   ("every non-prefix-independent language with a group-free algebra has
   candidates") is right; its quantifier was wrong.
2. *"On prefix-independent languages residual indexing degenerates (one
   residual) and the correct mechanism is the paper's Lemma 5.2 emit-directly
   rule, not the memo."* It does not degenerate — it **is** the emit-directly
   rule, discovered by the memo. The 94 prefix-independent languages get the
   *best* win of any stratum (hi-DAG 2.19× vs 1.65× for the other 1020),
   because with one residual every exit child is the label of the single
   deepest class, which is exactly the whole tail language Lemma 5.2 says to
   emit directly. The spec's requested "emit-directly column, not a
   residual-sharing win" is a distinction without a difference: same formula,
   same mechanism, reached by the memo.

The genuine cost: no rendering is **size-monotone**. Raw, residual indexing
enlarges the DAG on 12 languages and the tree on one — exhibit
`3state1ap0acc_028962` (`|𝒞| = 14`, 6 residuals, 1 AP): DAG 24 → 26, tree
85 → 86. Its fans merge *nothing* (13 distinct children by class, 13 by
residual), so the substitution buys no sharing and simply swaps each target's
own label for its residual representative's — both exact for the same tail
language, the representative's one node bigger. The representative is fixed as
*the first class built* (deepest layer), which the spec's acyclicity care point
demands; choosing the *smallest built label* of the residual would restore
monotonicity and stays acyclic. Not implemented. Post-`hi` the non-monotone
counts are 37 (guards), 13 (grouping), 11 (residual) and 7 (`+group` over
`+residual`) languages out of 1114 — the simplifier both hides some regressions
and creates others, none exceeding a few nodes against a pooled 1.93× win.

### Implementation

`guards.py` (new) renders a letter set `S ⊆ Σ` as a minimized formula over `AP`
— BDD + Minato ISOP through `aut2ltl.ltl.builders.fuse_or`, the repo's existing
guard-fusion pass, not a new minimizer. Its one hazard is canonicity: the ISOP
shape depends on the BDD variable order, which the shared process `bdd_dict`
fixes by *registration order*. `builders.register_aps` (new) pins it to the
alphabet's canonical AP order at `Guards` construction, so two presentations of
one language still render byte-identically (E0's canonicity case, green).

`readoffs.residual_partition` (new) reads the right congruence off `P` alone:
`T_c = T_d ⟺ ∀ (s,e) ∈ linked : (c·s, e) ∈ P ⟺ (d·s, e) ∈ P`, since every tail
`z·y^ω` from `c` lands on the linked pair `(c·[z]·[y]^π, [y]^π)`. This does not
consume the `.sos` residuals trailer — optional, and absent from a learner's
export — and the ledger cross-checks the two computations on every catalogue
language that carries one (0 mismatches).

Acyclicity (the spec's care point) is discharged structurally rather than by an
R-minimality argument: a residual's representative is registered only once its
layer is fully labelled, and exits point strictly down the R-order, so the
representative is always already built when an exit reaches it. The extreme case
the spec warns about — prefix-independence, one residual shared by every class —
is safe for the same reason: the single representative sits in the deepest
layer, and the root's label is never redirected into itself.

## E9 — worked-example curation, and F13: H3 exists

### F13 — `G(a → F b)` is an H3 hit: a (B)-failing final layer

`G(a → F b)` (spec E9(2)'s designated candidate — it cannot serve there)
**declines**, and the reason is not the engine: its final layer genuinely
fails condition (B) at every width — the E6/H3 hunt's first hit. Theory
status: the failure is **parked-type** — the paper's anchored parks
(Prop 5.7) capture it, expected (B̃) PASS at width 1 under the C3 park split
(spec H3, to confirm); the paper's *order beyond windows* residual witness is
H8's formula, not this one.

The specimen is committed: **`samples/fixtures/hoa/anchor/gafb_response.hoa`**
(the kanchor fixture E9(2) already names) and its canonical invariant
**`samples/fixtures/hoa/sos/gafb_response.sos`**. The two agree by construction:
bridging the fixture automaton and bridging the formula `G(a -> F b)` produce
the *byte-identical* `.sos` — the canonicity cross-check of §3b, run here as a
`cmp`.

`𝓘(L)` has 5 classes, `|AP| = 2`, `ϕ = (ω,σ)` (DBA-proper), 2 residuals, not
prefix-independent. Its final layer is `R = {2, 4}` — strongly connected,
accepting, *moving* (not frozen: `!a&b ↦ reset(2)`, `a&!b ↦ reset(4)`), which
is exactly the stratum E9(2) wants. Take the idle letter `!a&!b` (neutral on
`R`) and the two confined lassos it carries:

| lasso | anchor class | `(d·e, e)` | verdict |
|---|---|---|:--:|
| `(!a&b) · (!a&!b)^ω` | `2 = [!a&b]` | `(2, 1) ∈ P` | **accept** |
| `(!a&b · a&!b) · (!a&!b)^ω` | `4 = [!a&b·a&!b]` | `(4, 1) ∉ P` | **reject** |

Both are confined to `R`; both have recurring window set `{!a&!b}` at *every*
width `k′`. So no window set determines the verdict: the layer is
(B)-undetermined at every width, and the distinguishing datum is the *class*
(class 4 owes a `b` to an earlier `a`; class 2 owes nothing) — precisely the
"order beyond windows" phenomenon. The tester reports `FAIL` with this
witness pair at `k′ = 1, 2, 3`.

**Method notes (load-bearing, spec C3).** A conflict routinely pairs cycles at
two *different* anchor classes — this one does — so the bounded enumeration is
breadth-first (shortest cycles first; a conflict needs only short ones) under
**one node budget per anchor class**: a shared depth-first budget lets one
anchor starve the others and hides exactly this stratum. And a conflict is a
**witness pair** — two confined lassos, equal recurring window sets, opposite
verdicts — refuting (B) at that width exactly, finished search or not; only a
conflict-*free* width needs completeness to grade as a (cap-bounded) PASS.
`FAIL` means *conflicted at every tested width*.

**The catalogue tables are byte-stable** (`E1E2.txt`): **0 FAIL and 372
UNDECIDED** at every degree, the UNDECIDED entirely the
`(ω,·)`/`(ω²,·)` frozen-final-layer stratum of
F1. `G(a → F b)` is invisible to
`flat_canon` for a *frame* reason, not a tester reason: it needs **2 states and
2 AP at once**, and the catalogue enumerates `1state2ap`, `2state1ap`,
`3state1ap` — never `2state2ap`. A (B) failure therefore needs
**≥ 2 AP and ≥ 2 states** at once. The H3 minimality frontier
is a census-next axis (`2state2ap`), and the first hit is a named formula, not
a corpus id.

The failure is `k′ = ∞` (constant window at every width), not marginal. The
layer is anchored at width 1
under (A), so it isolates (B): the decline it forces is a (B) decline,
not an (A) one.

### The E9 gallery

`e9_profile` returns the spec's per-candidate tuple for any specimen — a `.sos`
id, an automaton, or an LTL formula (all keyed by the canonical invariant the
bridge builds, so presentation cannot leak in). The label stack is the engine's
own `SOS2LTL_TRACE` brick dump, captured rather than re-assembled probe-side:
a probe-side copy would drift from the engine and the figure it feeds would
stop being checkable (`sos_toltl_figures.md`, FIG-2's blocking requirement).
The hook: `[engine] layer=… brick=… class=… formula=…`,
raw formulas, simplification off, emitted child-first down the R-order — which
*is* the derivation order the label stack reads as. On `GF(aa)` it reproduces
the paper's §5.2 stack, `Final(5) = GF(a ∧ Xa)` first and `STAY = 0` on both
all-rejecting moving layers.

`e9_scan` puts the gallery's structural strata on the catalogue as *sorts*, not
hunts: it records per language whether it is a pure peel (all layers singleton,
R-depth ≥ 3, not prefix-independent), whether it carries a **live** final layer
(accepting *and* moving *and* (B)-determined *and* with exits — `STAY∞` live and
a `LEAVE` chain in the same layer), and whether any layer is graded (`k ≥ 2`).
Every row is gated on `rendered` — only a language the engine actually
transcribes can be a worked example. Over the 2240 LTL languages, 1114 render.

Smallest specimen per stratum, all paths under `genaut/corpus/flat_canon/sos/`
(tracked; each has a sibling `.cat` and a `det/` automaton):

| E9 | stratum | smallest | `\|𝒞\|` | AP | `ϕ` | simplified label |
|---|---|---|--:|--:|---|---|
| 1 | pure peel, depth 3 | `1state1ap0acc_1` | 3 | 1 | (1,π) | `Ga` |
| 1 | **pure peel, depth 4** | `1state2ap1acc_018` | **4** | 2 | (ω,σ) | `G(!b ∧ F(!a ∧ !b))` |
| 1 | pure peel, depth 7 (deepest) | `3state1ap0acc_078341` | 12 | 1 | — | — |
| 2 | **live `STAY∞` + `LEAVE`** | `2state1ap0acc_024` | **6** | 1 | (1,π) | `!a ∧ X(a ∧ G((a∨Xa) ∧ (!a∨X!a)))` |
| 4 | graded (`k = 2`) | `2state1ap0acc_086` | 12 | 1 | (1,σ) | — (declines) |

**E9(2) is answered — by a different specimen than the spec designated.**
`2state1ap0acc_024` (`|𝒞| = 6`, 219 such languages, smallest by `|𝒞|`) has the
final layer `R = {1,4}`: two classes, moving (`!a ↦ reset(1)`, `a ↦ reset(4)`),
(B)-determined trivially, accepting with a **live** `STAY∞` — the alternation
`G((a ∨ Xa) ∧ (!a ∨ X!a))` — and it has exits, so a `LEAVE` chain sits in the
same layer. That is exactly the stratum `GF(aa)` misses (its moving layers are
all-rejecting) and the one `G(a → F b)` misses the other way (its moving
accepting layer fails (B) — F13). The designated candidate cannot serve; this
one can.

**E9(1).** The depth-3 minimum `1state1ap0acc_1` is `Ga` — the safety twin of
§5.2's `F a` and just as degenerate. The useful one is the depth-4 minimum
`1state2ap1acc_018` at `|𝒞| = 4`: four singleton layers, a genuine `leave`
chain, one-line label `G(!b ∧ F(!a ∧ !b))`. Chains run to depth **7**
(`3state1ap0acc_078341`, `|𝒞| = 12`) if theory wants a long one.

**E9(4) — the graded stratum is empty of examples, and that is the finding.**
The catalogue has **952 graded languages** (some layer anchored only at `k ≥ 2`),
smallest `|𝒞| = 12` — so the F8 exhibit `2state1ap0acc_086_c` *is* the holder,
and nothing smaller exists. But **zero of the 952 render**: F8's decline guard
takes the entire graded stratum to DG. The 1126 engine declines break down as
graded 952, (A)-failing 258 (192 both), and 108 declining for neither reason —
those are the (B)-`UNDECIDED` window-term stratum of F1. So the graded engine
(M3) is not a marginal completion: it is 42.5% of the LTL catalogue.

### F14 — H2 and H4: the smallest (A)-failing and fallback-forced specimens

- **H2 = `3state1ap0acc_004260`** (`|𝒞| = 15`, **1 AP**, 3 states, `ϕ = (1,π)`
  safety; complement `_c` at `(1,σ)`). Its layers `{3,8,12}`, `{6,11,14}`,
  `{9,10,13}` are each 3 classes with both letters `mixed` — no width `k ≤ 3`
  anchors them. 258 languages (A)-fail catalogue-wide; none exists at
  2 states / 1 AP (the spec's prediction, confirmed).
- **H4 = H2** on this catalogue: the DG fallback is first forced by an
  (A)-failure at `|𝒞| = 15`, and by a graded layer at `|𝒞| = 12` — so if H4 is
  read as "must invoke the fallback *at all*", the graded stratum reaches it
  first, at `2state1ap0acc_086` (`|𝒞| = 12`).

**The AP axis carries nothing on (A).** All 258 (A)-failing
languages are 1 AP, and *no* 2-AP or 3-AP language in the catalogue has an
(A)-failing layer. The (A) frontier is driven by **states** (⟹ algebra size,
`|𝒞| ≥ 15`), not by alphabet width — the natural reading of Def 4.4,
since a mixed action needs several classes to be mixed *over*, not several
letters. The degree localisation (every FAIL at `ϕ = (1,σ)/(1,π)`, F6) is
confirmed by the exhibit's `.cat`.

## Reproduction

Every table above is machine-built and audited against a committed output under
`results/reference/flat_canon/` (its `README.md` maps each file to the command
that produced it); the report is traceable, not hand-transcribed. Re-running a
command below must reproduce its reference file. From the repo root (the `sosl`
step runs from `sosl/`). The bench is `genaut/corpus/flat_canon/` (`sos/`
invariants, `det/` automata, `.cat` categories; produced per `genaut/README.md`).
Per-run logs land in `tests/sos2ltl/logs/` and `logs/flat_canon/` (git-ignored);
the committed reference copies live in `results/reference/flat_canon/`.

**Survey reference runs (result split, sizes; engine vs DG baseline).**

    python3 -m survey --folder genaut/corpus/flat_canon/det --use sos2ltl \
        --logs logs/flat_canon/sos2ltl
    python3 -m survey --folder genaut/corpus/flat_canon/det --use sos2ltl_dg \
        --logs logs/flat_canon/sos2ltl_dg
    python3 -m survey.diff.results \
        logs/flat_canon/sos2ltl_dg/survey_*.csv logs/flat_canon/sos2ltl/survey_*.csv

**E0 / triptych.**

    python3 -m tests.sos2ltl.e0_gate                         # 29 cases, green
    python3 -m tests.sos2ltl.e7_dualscan samples/fixtures/hoa/sos/even.sos \
        --hoa samples/fixtures/hoa/sos/even.hoa --expect even

**E1 / E2 by Wagner degree.**

    python3 -m tests.sos2ltl.census_build genaut/corpus/flat_canon/sos
    python3 -m tests.sos2ltl.census_report tests/sos2ltl/logs/e12_flat_canon.jsonl

**E7 ledger + tiers, and the three tier exhibits.**

    python3 -m tests.sos2ltl.e7_ledger genaut/corpus/flat_canon/sos
    python3 -m tests.sos2ltl.e7_tiers tests/sos2ltl/logs/e7_flat_canon.jsonl
    python3 -m tests.sos2ltl.e7_mechanism_probe \
        genaut/corpus/flat_canon/sos/2state1ap1acc_04644.sos   # right-ideal, |𝒞|=4
    python3 -m tests.sos2ltl.e7_mechanism_probe \
        genaut/corpus/flat_canon/sos/3state1ap0acc_004376.sos  # phase-collapse, |𝒞|=6
    python3 -m tests.sos2ltl.e7_mechanism_probe \
        genaut/corpus/flat_canon/sos/2state1ap1acc_01681.sos   # P-level, |𝒞|=13

**F8/F15 exhibits (0 FAIL).**

    python3 -m tests.sos2ltl.engine_fails logs/flat_canon/sos2ltl/survey_*.csv   # 0 FAIL
    # window-class rendering — engine answers GF(a|!b):
    python3 -m survey --hoa genaut/corpus/flat_canon/det/1state2ap1acc_030.hoa --use sos2ltl
    # committed classes + the graded seam witness (engine renders):
    python3 -m tests.sos2ltl.seam_gate
    cat genaut/corpus/flat_canon/sos/2state1ap0acc_086_c.sos
    # the step_th refutation exhibit (per-class grounding, clean):
    python3 -m tests.sos2ltl.engine_diff \
        genaut/corpus/flat_canon/sos/3state1ap0acc_006478_c.sos

**E10 branch factoring (F9–F12).**

    python3 -m tests.sos2ltl.e10_ledger genaut/corpus/flat_canon/sos \
        --out tests/sos2ltl/logs/e10_ledger.jsonl
    python3 -m tests.sos2ltl.e10_report tests/sos2ltl/logs/e10_ledger.jsonl
    # the triptych-of-renderings exhibit, one language:
    python3 -m tests.sos2ltl.e10_ledger genaut/corpus/flat_canon/sos/1state2ap1acc_030.sos
    python3 -m tests.sos2ltl.e0_engine genaut/corpus/flat_canon/sos/1state2ap1acc_030.sos

**F13 / H3 — the (B)-failing specimen.** Both presentations are committed
(`samples/fixtures/hoa/anchor/gafb_response.hoa`, the automaton;
`samples/fixtures/hoa/sos/gafb_response.sos`, its canonical invariant).

    python3 -m tests.sos2ltl.e0_windows samples/fixtures/hoa/sos/gafb_response.sos
    python3 -m tests.sos2ltl.e9_profile samples/fixtures/hoa/anchor/gafb_response.hoa
    # canonicity: the fixture automaton and the formula bridge to one invariant
    python3 -m tests.sos2ltl.e9_profile --ltl "G(a -> F b)" \
        --dump-sos tests/sos2ltl/logs/gafb.sos --no-stack
    cmp tests/sos2ltl/logs/gafb.sos samples/fixtures/hoa/sos/gafb_response.sos
    # the (B) fix leaves the catalogue tables byte-identical to E1E2.txt:
    python3 -m tests.sos2ltl.census_build genaut/corpus/flat_canon/sos \
        --out tests/sos2ltl/logs/e12_flat_canon.jsonl
    python3 -m tests.sos2ltl.census_report tests/sos2ltl/logs/e12_flat_canon.jsonl

**E9 gallery and F14 (H2/H4).** The scan is the sort; the profile is the
per-candidate deliverable (add `--no-stack` to drop the brick dump).

    python3 -m tests.sos2ltl.e9_scan genaut/corpus/flat_canon/sos \
        --out tests/sos2ltl/logs/e9_scan.jsonl
    python3 -m tests.sos2ltl.e9_profile genaut/corpus/flat_canon/sos/2state1ap0acc_024.sos
    python3 -m tests.sos2ltl.e9_profile genaut/corpus/flat_canon/sos/1state2ap1acc_018.sos
    python3 -m tests.sos2ltl.e9_profile genaut/corpus/flat_canon/sos/1state1ap0acc_1.sos
    python3 -m tests.sos2ltl.e0_anchoring genaut/corpus/flat_canon/sos/3state1ap0acc_004260.sos
    python3 -m tests.sos2ltl.e9_profile samples/fixtures/hoa/sos/gf_aa.sos   # the FIG-2 stack

