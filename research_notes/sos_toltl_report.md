# SoS → LTL — results

The answer to `research_notes/sos_toltl_experiments.md`: the `aut2ltl/sos2ltl/`
construction run against the paper's worked traces (`research_notes/sos_toltl.md`)
and evaluated over the reference bench. Each section answers one experiment id;
each finding `Fn` is either a refuted prediction (with the paper/spec edit it
triggers) or a mechanism the census settles.

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
asserting SCCs = R-classes of `M` per input, Lemma 5.3), `anchoring.py`
(C2 — condition (A), widths `k ≤ 3` with the layer action monoid `𝒜_R` as a
by-product), `windows.py` (C3 — condition (B), the three-stage bounded tester,
F1), `readoffs.py` (C5 — λ-quotient, prefix-independence from the residuals,
complement flip; the aperiodicity read-off lives in the classifier subproject
`sosl/sosl/sos/classify/aperiodic/` and is consumed, not duplicated),
`witness/` (§4 certificate + the presentation-agnostic toggle replay + the dual
scan), `dg/` (the Diekert–Gastin baseline, E4b), and `engine.py`
(C4 — the walk+window transcription; sound, with the graded stratum deferred to
the DG baseline, F8). The `translator.py`
flow: bridge `Language → 𝓘(L)`; a step-0 group scan (a certificate replayed by
membership against the *input* automaton before the absorbing `NOT_LTL`, a
failed replay declining, never verdicting); on an aperiodic invariant the
transcription engine, else the dg baseline. The bridge builds `𝓘(L)` from the
Language's base automaton (`canonical` determinizes and completes it) — the
invariant is language-canonical, independent of the seeding presentation.

The gate: `python3 -m tests.sos2ltl.e0_gate` — 27 cases, one subprocess per
case under a 15 s cap, SUCCESS. Individual probes `e0_{layers,anchoring,windows,
witness,dg,translator,canon}` and `e7_dualscan` under `tests/sos2ltl/`.

## E0 — the triptych

C1/C2/C3/C5 + the certificate on `GF(aa)`, `Even`, `EvenBlocks`, against the
paper's hand-computed predictions ([SωS26, Table 3]):

| prediction (paper §4.3, §5.4) | run | verdict |
|---|---|:--:|
| `GF(aa)` aperiodic, 6 classes | aperiodic, 6 classes | ✓ |
| `Even`/`EvenBlocks` group: carrier `[a]`, index 1, period 2, cycle `{[a],[a·a]}` | identical, both | ✓ |
| `GF(aa)` layers `{0},{1,3},{2,4},{5}`, R-order `0 → {1,3} \| {2,4} → 5` | identical | ✓ |
| SCCs of `Cay(L)` = R-classes of `M` (Lemma 5.3), asserted per input | holds on every input | ✓ |
| `{1,3}`,`{2,4}` pass (A) at `k=1`; letter tables `!a↦reset(1)/reset(4)`, `a↦reset(3)/reset(2)` | identical | ✓ |
| `{5}` frozen (both letters neutral), `{0}` both exit | identical | ✓ |
| `Even`/`EvenBlocks` group layers fail (A) at every width | FAIL (mixed swap action never stabilizes) | ✓ |
| `{5}` fails (B) at `k'=1` on the Lemma-5.2 edge pair | witness `(a·!a)^ω` vs `(aa·!a)^ω`, replayed with opposite verdicts | ✓ |
| `{5}` passes (B) at `k'=2` | PASS width 2 (cap-bounded; F1) | ✓ |
| `{1,3}`,`{2,4}` as final layers all-rejecting ⟹ (B) trivial | trivial PASS width 1 (exact cycle-class closure) | ✓ |
| `GF(aa)` prefix-independent (1 residual) | `P` loop-determined: yes | ✓ |
| `Even` certificate `F₁(u=a, v=a, x=(!a)^ω, p′=2)` byte-exact | byte-exact, toggle 5/5 | ✓ |
| `EvenBlocks` certificate `F₂(u=ε, v=a, y=a·!a, p′=2)` byte-exact; linear scan all-constant first (Prop 4.2) | byte-exact, toggle 5/5; linear scan exhausted constant | ✓ |
| spec C3 cycle-length cap `⟨2·\|R\|·\|Σ_λ\|⟩` sufficient | **REFUTED** — false PASS on `EvenBlocks` layer `{6}` | ✗ F1 |

Canonicity is observed end-to-end: two presentations of `GF(aa)` (the parity
and the reset automata) bridge to the byte-identical `.sos` and synthesize the
character-identical formula (19 nodes / arena 1287 / flat 4 357 185).

## E1 — anchoring, by Wagner degree

Non-degenerate LTL languages (2238), ventilated by `ϕ`. `A@1` anchors at width
1; `A≤3` within the tester's `k ≤ 3`; `FAIL` layers anchoring at no `k ≤ 3`
(the (A)-tester tops out at 3, so its gap *is* the scoped-fallback stratum,
Prop 5.21/5.24); `stemk3` languages every layer of which anchors at `k ≤ 3`;
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

Spec E1 predicted "a large majority pass (A) at `k=1`" and left H2 ("first
(A)-failing hit ⟨TBD⟩") open. The 1432 FAIL layers are located precisely:
**every one is at `ϕ = (1,σ)` or `(1,π)`** (guarantee / safety), 716 apiece by
duality. The clopen islands `(1,δ)`, the `(2,·)` pair, and **all** the higher
Borel degrees — `(ω,·)` DBA/DCA and `(ω²,·)` parity — anchor with **zero**
FAIL. So H2's `⟨TBD⟩` is filled by *complexity, not shape*: the scoped DG
fallback's raison d'être is entirely the Wagner-degree-1 tier (safety /
guarantee languages whose entry layers resist finite-width anchoring). This is
§7's inner-frontier fraction as a measurement. No refutation of a paper claim
(the stratum is predicted to exist); it fixes the empirical column and pins the
frontier to a degree. The FAIL floor needs **≥ 2 AP** (no 1-AP language fails).

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

**(B) is clean catalogue-wide: 0 FAIL at every degree** — the H3 hunt (smallest
(B)-failing final layer) stays empty even at 2 AP; a positive (B)-failure
witness still awaits, the spec's "≥ 2 AP" necessary but not shown sufficient.
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
   `𝒞`, never in the graph. **Paper 5.15(iii) and spec C3 patched.**

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
the aperiodicity read-off (1701 declines). The engine column (a) is provisional
now sound (F8): the engine answers where it is provably exact (width-1 layers
and committed-accepting classes) and declines the non-committed graded stratum
to DG, so column (a) is smaller than the full census but **0 FAIL**. Its DAG is
~3× below the baseline where it does answer — the compression the paper's §6
predicts; the full (a)-vs-(b) ledger awaits the graded engine's return.

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
multiplicative theorem — F7. **Paper §4.3 corrected** to the confined claim plus
the asymmetry; the layer-confined (B) statistics still see nothing of `Even`'s
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

E0 reports layer `{5}` as "both letters neutral" while Definition 5.4's diagonal
doctrine makes a `{c↦c}`-only letter an anchor of `A(c)`. The implementation
does both: the *report kind* is identity-first (`neutral`), while `A(c)`
membership is constant-action (diagonal included). The paper states the overlap
(`A(c) ∩ L(c)` = diagonals) but not the reporting convention; harmless, worth
one sentence in §5.2 if the letter tables become paper material.

## §3 conformance and F8 — engine soundness restored; the graded stratum deferred to DG

Spec §3 mandates a conformance gate: every emitted formula `φ` must have
`𝓘(L(φ))` byte-equal to the input `𝓘`, a mismatch being *a stop-the-line bug in
the engine, never a statistic*. Implemented as a Spot round-trip
(`invariant_of(import_ltl(flat))` — Spot translating the emitted formula string,
then a fresh algebra closure), that gate was an **unbounded outside step**: it
exploded on some inputs (15 s survey timeouts) and merely duplicated the survey
oracle's own equivalence check, so it is removed and the engine formula ships
directly. The removal **surfaced** what §3's gate had been converting silently
into declines.

**The measurement.** `--use sos2ltl` over the catalogue, verified by the Spot
oracle. Removing the gate exposed **842 verified non-equivalent (FAIL)** answers,
**every one `sos2ltl.engine`** — the walk+window transcription (C4), never the
certificate side and never the DG fallback (`sos2ltl_dg` has **0 FAIL**, only
SIZE-unverified explosions). These were two distinct engine defects, **both now
resolved**: the engine is sound catalogue-wide (**0 FAIL**, survey SUCCESS),
trading coverage for soundness on one stratum (defect 2). Per §3 the FAILs were
stop-the-line bugs, not statistics — and are now closed.

**Defect 1 — the window term rendered one representative, not the class (fixed,
−448).** A window word is built from λ-class representatives, and `Ω(R,c)`'s
`⋁_S ⋀_{w∈S} GF ŵ` rendered each window position as the representative's single
cube rather than the whole class it names. On `L = GF(a|!b)` (`1state2ap1acc_030`,
`|𝒞|=3`, degree (ω,σ)) the frozen absorbing accepting layer's window family is
upward-closed with three minimal singletons `{a&!b}, {!a&!b}, {a&b}` — the three
concrete letters of the quotient letter `(a|!b)` — so `Ω = GF(a&!b) ∨ GF(!a&!b) ∨
GF(a&b) = GF(a|!b)`; the engine emitted only `GF(!a&!b)` (the class's shortlex
key), under-approximating. The construction is sound (no paper edit): every window
position now renders as the full λ-class letter-set (`engine.py::_Letters`), and
`Ω` reduces to `L` exactly. This fault needed **≥ 2 AP** (at 1 AP a quotient
letter is a single literal or `⊤`, so representative and class coincide and the
truncation is invisible — the 2-AP switch-on of F6) and floored at `|𝒞|=3`; the
fix clears all 448 such cases.

**Defect 2 — committed-accepting layers not collapsed to `true` (fixed by §6.3
short-circuit + a decline guard).** The remaining 394 were uniformly **`|𝒞| ≥ 12`,
≥ 4 states, degree (1,σ)/(1,π)** — the guarantee/safety stratum, over **1 AP** so
not a rendering fault. They are **terminal committed-accepting layers**: from
such a class every continuation is accepted (tail language `T_c = Σ^ω`, i.e.
every linked pair whose stem is reachable from `c` lies in `P`), so the exact
`Final(c)` is `true` — but the graded Theorem-5.23 exit-chain fails to collapse
it, under-approximating.

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
("first letter `a` ⟹ accept", correct: `a·a·a·!a·a·(!a)^ω` accepts). The engine's
graded `Final(2)` was not `true`, so it rejected that witness — a 2-anchored
layer (`a` a partial constant onto `2`, `!a` acting `2↦5↦8↦8`: mixed at width 1,
constant at length ≥ 2) whose graded Theorem-5.23 exit-chain must reduce to
`true` here but did not.

**The cure (implemented, `engine.py`; construction sound, no paper edit).** Two
parts, per theory's §6.3 strength-stratification reading:

- *Committed short-circuit.* A committed-accepting class — the `O(|𝒞|²)`
  read-off `_committed`: every linked pair whose stem is reachable from `c` in
  `Cay(L)` lies in `P` — takes `Final(c) = true` directly, in place of the walk
  brick. On the guarantee/safety stratum this is the common case.
- *Decline-to-DG guard.* A `k ≥ 2` (graded) layer carrying any non-committed
  class **declines** (`transcribe` returns `None`, falling through to the DG
  baseline) rather than emit the Theorem-5.23 exit-chain, whose exact collapse
  is not yet proven. The exhibit now declines to DG — a correct,
  SIZE-unverifiable formula, no longer FAIL.

The result is **0 verified-non-equivalent answers catalogue-wide** (survey
SUCCESS, E0 green): faithful-or-NOK restored. The cost is coverage — a
non-committed graded layer now falls to DG instead of the compact engine
formula.

**Remaining work.** Repair the graded Theorem-5.23 exit-chain so it collapses
exactly, then lift the decline guard and return the graded engine to service.
Theory localizes the residual to the graded `TL_0` exit disjunction failing to
reduce `G a ∨ (a U (!a ∧ X φ))` when the child `φ` is `true`; the bottom-up walk
on the exhibit (`Final(9) = true` at the absorbing sink, then `Final(8)`,
`Final(5)`, `Final(2)`, each ⊨-equivalent to `true`) pins the broken brick. Until
the collapse is exact and assertable, decline-to-DG is the sound guard.

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

    python3 -m tests.sos2ltl.e0_gate                         # 27 cases, green
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

**F8 exhibits (0 FAIL after the fixes).**

    python3 -m tests.sos2ltl.engine_fails logs/flat_canon/sos2ltl/survey_*.csv   # 0 FAIL
    # defect 1 (window class) — now exact, engine answers GF(a|!b):
    python3 -m survey --hoa genaut/corpus/flat_canon/det/1state2ap1acc_030.hoa --use sos2ltl
    # defect 2 (committed-accepting layer) — engine declines, DG answers:
    python3 -m survey --hoa genaut/corpus/flat_canon/det/2state1ap0acc_086_c.hoa --use sos2ltl
    cat genaut/corpus/flat_canon/det/2state1ap0acc_086_c.hoa
    cat genaut/corpus/flat_canon/sos/2state1ap0acc_086_c.sos
