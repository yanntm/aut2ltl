# SoS → LTL — Status Report

Where the `aut2ltl/sos2ltl/` implementation stands against the plan in
`research_notes/sos_toltl_experiments.md` (the normative experiment
contract) and the paper `research_notes/sos_toltl.md` (whose worked traces
are predictions the tool must reproduce). Ledger style: one row per
finding; a refuted prediction is a paper edit, recorded here with the edit
it triggered.

## Milestones (spec §6)

- **M1 — C1 + C2 + C3 + C5 + certificate, E0 gate.** Components landed and
  E0-green: `cayley.py` (C1), `anchoring.py` (C2), `windows.py` (C3),
  `readoffs.py` (C5 minus the ladder rung — deferred to the classifier
  subproject, whose position `sosl/sosl/sos/classify/` now exists with
  Band 1 implemented), `witness/` (§4 certificate + toggle replay).
  **M1 closed:** the E1/E2 census tables landed (see the E1/E2 section) via
  the `SOS2LTL_CENSUS` recipe side channel over the 1-AP `genaut` shapes.
- **The DG baseline (E4b's engine).** Ported to consume the invariant
  natively (`aut2ltl/sos2ltl/dg/`, from the running `bls/definability/dg`
  implementation; `morphism.py`'s `Alg` dropped — the `.sos` value is
  already canonical). On `GF(aa)`: 19 recursion nodes, arena (DAG) 1287,
  **flat tree 1 991 717** — the §3 explosion measured on a six-class
  algebra — Spot-equivalent to `GF(a ∧ Xa)`; group-bearing inputs are
  refused upstream by the aperiodicity read-off.
- **The Translator.** `aut2ltl/sos2ltl/translator.py` — bridge
  (`Language → 𝓘(L)` via the reference construction, capped into a
  decline), step-0 group scan, certificate replayed against the *input
  automaton* before the absorbing `NOT_LTL` (a failed replay declines,
  never verdicts), dg synthesis on the aperiodic side. End-to-end on the
  triptych HOAs: `gf_aa_parity` → OK, Spot-equivalent to `GF(a ∧ Xa)`;
  `even` → NOT_LTL, witness `p=2 u=[a] v=[a] x=[cycle{!a}]`; `evenblocks`
  → NOT_LTL, witness `p=2 u=[] v=[a] y=[a; !a]`.
- **Canonicity (dg algorithm.md layer 8), confirmed.** Two different
  presentations of `GF(aa)` — the parity and the reset automata — bridge
  to the byte-identical `.sos` and synthesize the character-identical
  formula (4 357 185 chars flat; 19 nodes, arena 1287 as a DAG).
- **M2 — C4 walk+window engine.** Not started; next construction step.

The gate: `python3 -m tests.sos2ltl.e0_gate` — 21 cases, one subprocess
per case under a 15 s cap (the classifier cases run from the `sosl`
subproject root), currently SUCCESS. Individual probes: `e0_layers`,
`e0_anchoring`, `e0_windows`, `e0_witness`, `e0_dg`, `e0_translator`,
`e0_canon` under `tests/sos2ltl/`, and `tests/sosl/classify_aperiodic`
in the sosl subproject.

## E0 — the triptych, predictions vs runs

| prediction (spec E0 / paper §4.3, §5.4) | run | verdict |
|---|---|:--:|
| `GF(aa)` aperiodic, 6 classes | aperiodic, 6 classes | ✓ |
| `Even`/`EvenBlocks` group: carrier `[a]`, index 1, period 2, cycle `{[a],[a·a]}` | identical, both | ✓ |
| `GF(aa)` layers `{0},{1,3},{2,4},{5}`, R-order `0 → {1,3} \| {2,4} → 5` | identical | ✓ |
| SCCs of `Cay(L)` = R-classes of `M` (Lemma 5.3), asserted per input | holds on all inputs so far | ✓ |
| `{1,3}`,`{2,4}` pass (A) at `k=1`; letter tables `!a↦reset(1)/reset(4)`, `a↦reset(3)/reset(2)` | identical | ✓ |
| `{5}` frozen (both letters neutral), `{0}` both exit | identical | ✓ |
| `Even`/`EvenBlocks` group layers fail (A) at every width | FAIL (mixed swap action never stabilizes) | ✓ |
| `{5}` fails (B) at `k'=1` on the Lemma-5.2 edge pair | witness found IS `(a·!a)^ω` vs `(aa·!a)^ω`, replayed with opposite verdicts | ✓ |
| `{5}` passes (B) at `k'=2` | PASS width 2 (cap-bounded; see F1) | ✓ |
| `{1,3}`,`{2,4}` as final layers all-rejecting ⟹ (B) trivial | trivial PASS width 1 (exact cycle-class closure) | ✓ |
| `GF(aa)` prefix-independent (1 residual) | `P` loop-determined: yes | ✓ |
| `Even` certificate `F₁(u=a, v=a, x=(!a)^ω, p′=2)` byte-exact | byte-exact, toggle 5/5 | ✓ |
| `EvenBlocks` certificate `F₂(u=ε, v=a, y=a·!a, p′=2)` byte-exact; linear scan all-constant first (Prop 4.2) | byte-exact, toggle 5/5; linear scan exhausted constant | ✓ |
| spec C3 cycle-length cap `⟨2·\|R\|·\|Σ_λ\|⟩` sufficient | **REFUTED** — false PASS on `EvenBlocks` layer `{6}` | ✗ F1 |

## Findings

### F1 — the (B) tester's cap must scale with `|𝒞|`, and the verdict does not factor through the memory subgraph

**The incident.** With the spec's provisional cap `2·|R|·|Σ_λ|` (= 4 on a
singleton layer over one AP), the bounded (B) test on `EvenBlocks`' frozen
layer `{6}` enumerated all cycle words to length 4, found the `k'=1` and
`k'=2` conflicts, found no `k'=3` conflict, and reported **PASS at
`k'=3`** — on the language whose non-LTL-ness is precisely ω-power
counting. The real conflict sits one letter past the cap:
`(a⁴·!a)^ω` and `(a⁵·!a)^ω` have equal recurring 3-window sets
(`{aaa, aa!a, a!aa, !aaa}`) and opposite verdicts (block parity 4 vs 5).

**The theory content, for reintegration.** Two separate lessons:

1. *No cap local to the layer can work.* The verdict of a confined tail
   ending on a loop `z` at class `d` is `(d·e, e) ∈ P` with `e` the
   idempotent power of `[z]` — and `[z]` is folded through the **whole**
   algebra `𝒞`, not through the layer. On a frozen singleton layer the
   walk sees nothing while the loop class wanders all of `𝒞`; the lengths
   at which loop classes separate are governed by `|𝒞|`, so any bound in
   `|R|` and `|Σ_λ|` alone is refutable. The implementation now uses
   `2·|R|·|𝒞|` (which does catch the `EvenBlocks` conflict), but no
   sufficiency theorem exists for that bound either — see the open item.

2. *The verdict is not a function of the covering subgraph.* In the
   memory-graph reading of Proposition 5.15(ii)/(iii): at `k = 3` the two
   witness tails traverse **the same** strongly connected subgraph `H` of
   `G(R, c)` — identical recurring edge sets — and still disagree. So
   deciding (B) cannot enumerate subgraphs and evaluate "the" verdict per
   subgraph: the verdict factors through the *loop class of the covering
   tour*, and one subgraph carries tours of several loop classes (here,
   both phases of the group). The object to compute per subgraph `H` is
   its loop-class closure `{ [w] : w labels a closed covering walk of H }`
   — a subset of `𝒞`, computable by a `(node, class, covered-edge-set)`
   closure — and (B) at width `k` holds iff, grouping across subgraphs
   with one window projection `S`, all induced pair verdicts agree. The
   finiteness of the check lives in `𝒞`, never in the graph. The paper's
   5.15(iii) said "verdicts factoring through loop classes" without
   flagging that a single subgraph mixes loop classes; the spec's C3 then
   read it as a per-cycle-set comparison with a layer-local cap. Both
   texts patched (paper 5.15(iii); spec C3).

**Implementation semantics now.** Stage 2, the trivial pass, is exact and
polynomial: the per-class cycle-class sets `{ m : (d, m) reachable from
(d, [ε]) in the (position, word-class) product }` — one verdict across all
of them proves (B) at every width. Stage 3 enumerates cycle words to
`2·|R|·|𝒞|` under a node budget: a conflict is an exact **FAIL** with a
replayable lasso pair; conflict-free with the enumeration complete is a
cap-bounded **PASS**; a tripped budget is **UNDECIDED**. On the triptych:
`GF(aa)` `{5}` PASS at `k'=2`; `EvenBlocks` `{6}` FAIL at `k'=1,2,3` with
the block-parity witnesses; `EvenBlocks`' larger non-final layers
UNDECIDED (budget) — honest, and immaterial to the certificate side.

**Open theory item.** Either prove a sufficient cap (candidate:
tours whose `(position in R, word class)` product trajectory repeats a
state can be excised *without shrinking the window set* below the target —
needs care exactly because excision can drop windows), or adopt the
cap-free `(node, class, covered-edge-set)` closure as the normative
procedure and price it. Until one is frozen, a cap-bounded PASS is not a
theorem and E2's tables should carry the PASS/UNDECIDED distinction.

### F2 — `Even`'s group is invisible to (B): the two context shapes split exactly as §4.3 says

All four of `Even`'s layers pass (B) trivially — every within-layer cycle
of the group layer `{2,4}` is a pure-`a` cycle of even length, all folding
to the same class, all rejecting. The ω-power side has nothing to say on
`Even` (its certificate is linear), just as the linear side has nothing to
say on `EvenBlocks` (Prop 4.2). The §4.3 duality of the two specimens is
visible in the (B) statistics alone, before any certificate is extracted.

### F3 — classification convention at the diagonal (definitional, no edit yet)

E0 predicts layer `{5}` reports "both letters neutral", while Definition
5.4's diagonal doctrine makes a `{c↦c}`-only letter an anchor of `A(c)`
("it names its class"). The implementation does both: the *report kind* is
identity-first (`neutral`), while `A(c)` membership is constant-action
(diagonal included). The paper states the overlap (`A(c) ∩ L(c)` =
diagonals) but not the reporting convention; harmless today, worth one
sentence in §5.2 if the letter tables become paper material.

## E1 / E2 — the 1-AP census

**Provenance.** The six 1-AP `genaut` shapes (`1state1ap{0,1,2,3}acc`,
`2state1ap{0,1}acc`), 981 inputs, driven through `--use sos2ltl` under
`survey` (per-input isolation + 15 s cap). The recipe carries an env-gated
side channel (`SOS2LTL_CENSUS` → `aut2ltl/sos2ltl/census.py`): one JSON
record per input, printed *early* (right after the group scan, before
synthesis) so the (A)/(B) statistics persist even when a later emit blows
the cap. Reproduce:

    SOS2LTL_CENSUS=…/census_1ap.jsonl python3 -m survey \
        --folder genaut/corpus/1state1ap0acc … --folder genaut/corpus/2state1ap1acc \
        --use sos2ltl --no-verify --logs …
    python3 -m tests.sos2ltl.census_report …/census_1ap.jsonl

Run: 981 inputs, **891 LTL / 90 not-LTL**, 0 declined / 0 timeout / 0 crash;
all 981 records captured (E1/E2 restrict to the 891 aperiodic specimens).

### E1 — condition (A), 891 LTL specimens, 2898 layers

| metric | census | spec E1 prediction | verdict |
|---|---|---|:--:|
| layers anchoring at `k = 1` | 2796/2898 (96.5%) | "large majority pass (A) at `k=1`" | ✓ |
| (A)-width histogram | `{1: 2796, 2: 102}` — no `k=3`, no FAIL | — | ✓ (stronger: `k ≤ 2` everywhere) |
| languages fully stem-transcribable at `k ≤ 3` | 891/891 (100%) | (deliverable) | ✓ |
| frozen layers | 1478/2898 (51.0%) | "frozen layers are common" | ✓ |
| prefix-independent languages | 535/891 (60.0%) | — | — |

The 102 width-2 layers are the graded-engine stratum (Thm 5.23 fires); no
1-AP layer reaches width 3 and none (A)-fails.

### E2 — condition (B), 1921 final-candidate layers

| metric | census | spec E2 prediction | verdict |
|---|---|---|:--:|
| status split | `{PASS: 1834, UNDECIDED: 87}` — **zero FAIL** | "(B) holds at `k' ≤ 2` on all 1-AP census; failures need ≥ 2 AP" | ✓ |
| PASS width histogram | `{1: 1793, 2: 41}` (trivial 1554) | — | ✓ (no `k'=3`) |
| determined at `k' ≤ 2` | 1834/1921 (95.5%) | — | all PASSes ≤ 2 |

No (B)-failure anywhere on the 1-AP census — the "failures need ≥ 2 AP"
clause is unfalsified here (its positive witness awaits the 2-AP shapes,
E6/H3). The 41 `k'=2` PASSes are the `GF(aa)`-style frozen final layers
(`{5}`, F1). The **87 UNDECIDED** are enumeration-guard gaps (F1's node
budget), not conflicts — a stratum-statistics hole, immaterial to the
no-failure claim; each carries a conflict-free width but no PASS theorem.

**Both E1 and E2 predictions confirmed, and stronger than stated:** on the
1-AP census `k ≤ 2` / `k' ≤ 2` covers everything that is decided, and
nothing (A)- or (B)-fails.

## Deviations from the spec (implementation placement)

- The aperiodicity read-off (spec C5's first item) lives in
  `sosl/sosl/sos/classify/aperiodic/` — the classifier subproject's
  position (`sos_classifier_spec.md` §3.1's first primitive), consumed by
  `sos2ltl`, not duplicated in it. The ladder rung (C5's "rung from `P`")
  is deferred to that subproject: nothing in M1/M2 consumes it.
- C3's per-stem quantification collapses per layer: `R` is strongly
  connected, so every `(d, cycle)` is reachable from every `c ∈ R` — one
  test per layer, recorded once, not `|R|` times.

---

## Theory review of the M1 report (2026-07-07)

**M1 is accepted.** The E0 gate is the family discipline doing its job:
every §4.3/§5.4 prediction confirmed byte-exact, canonicity observed
end-to-end (two presentations → one `.sos` → one formula), and F1 is the
report channel working as designed — a refuted prediction that became a
paper edit (Prop 5.15(iii)) plus one live open item. That item — no
sufficiency theorem for the `2·|R|·|𝒞|` cap — is on the theory desk; the
current leaning is to freeze the cap-free `(node, class, covered-edges)`
closure as the *normative* (B) procedure (priced, with the bounded
enumeration kept as a cheap first stage), because the excision route
founders exactly on the report's own care point: excising a repeated
product state preserves the verdict but not the recurring-window set, and
a (B)-conflict is a pair of tours with *equal* window sets. Until that
lands, every table keeps the three-valued PASS grade, as this report
already does.

**The census under-declares its bench.** "Six 1-AP shapes, 981 inputs" is
a provenance note, not a frame declaration. What the E1/E2 section must
state, and the spec now demands (§3b): the enumeration axes and whether
the sweep is exhaustive over them; determinism and completeness of the
inputs; and — first-class — the **acceptance family** behind the `acc`
counts. The construction's contract is deterministic Emerson–Lei input;
if this run exercised only generalized-Büchi-style Inf sets, the tables
are Büchi-flavored and must say so, and the parity corpora already
promoted to `genaut/corpus/` join the bench at the next run (arbitrary EL
is the census-next axis). Also explain the frame's asymmetry — 0–3
acceptance sets at one state against 0–1 at two states: budget or
principle?

**Ventilate, dedupe, and quarantine the bottom.** Three reporting debts
on E1/E2, none touching the findings' substance. (i) Per-shape rows:
pooled percentages over six shapes hide where the width-2 layers and the
87 UNDECIDEDs live. (ii) Both weightings: the census counts automata, and
automata sharing a byte-identical canonical `.sos` are one language —
percentages weighted by presentation multiplicity contradict the very
canonicity this report confirms two sections earlier; report automaton-
and language-weighted counts side by side. (iii) The degenerate line:
empty and universal specimens (one word class, `P` empty or full) pass
everything trivially and can only inflate the 96.5% / 95.5% headlines and
the frozen-layer count; give them their own line per shape and restate
the headline figures without them.

**Sizes: two ledgers are runnable today, no C4 needed.** (i) E4-interim —
the DG baseline over the 891 LTL specimens: DAG nodes, flat size or
`FLAT_OVERFLOW`, by `|𝒞|` and per shape, with size-bucket histograms; the
paper's §3/§6 needs the explosion as a *distribution*, not the single
`GF(aa)` exemplar (19 nodes / arena 1287 / flat 1 991 717). (ii) E7,
pulled forward to M1.5 — the witness ledger over the 90 non-LTL
specimens: component lengths against the Theorem-4.4 bounds, and the
**dual scan** — record for every specimen whether the linear scan and the
ω-power scan *each* find a non-constant pattern, not merely which fired
first under the scan order; a specimen whose ω-power side is all-constant
is an H5 hit, and a census with none is the first real evidence toward
"F₂ always available".

**The precursors have a rendezvous, and it should be early.** daisy
(self-loop peel) and kanchor (SCC peel) are exactly what E3 exists to
cross-test, and E3 needs no new engine. Two directed questions for the
early pass: does kanchor's peel go through on the census reference forms
at all (per-SCC passing widths, failure modes), and does daisy's
applicability coincide with the width-1 park stratum — frozen layers, (B)
at `k' = 1` — as the theory says it should? Any census instance where the
algebra needs a *larger* width than some automaton form comes back to the
paper immediately.

**The pair split gets an experiment id.** C7 had no milestone and its
decompositions no experiment — fixed: E8, assigned with C7 to M3. The
OR-split by final layer is the sanctioned granularity; the split per
accepting pair is what §5.6(1)'s guard warns against (pieces can climb
the Wagner ladder while staying LTL) — but the guard is a prediction, and
E8 measures it: re-canonicalize every final-layer piece and every
single-pair piece, record the read-offs, count the ladder climbs. The
AND-split search reports its factored-vs-`IRREDUCIBLE` fractions on the
same pass.

Spec revisions issued in `sos_toltl_experiments.md`, revision line
2026-07-07: §3b census reporting discipline; E1/E2 table requirements;
E4-interim; E7 dual scan + pull-forward; E3 directed questions; E8/C7;
milestone M1.5.

### Addendum (2026-07-08) — the census unit is the language

Portfolio-path data on the single shape `2state1ap1acc` (Inf-only
acceptance — which also answers the family question for this shape: the
run was Büchi-flavored): 759 LTL answers collapse to at most 73 distinct
formula structures (md5 on strings — a proxy; the byte-identical
canonical `.sos` is the normative key, distinct strings can be one
language), with 43.6% of all answers the universal language `1` and the
top 10 structures covering 80%. Automaton-weighted statistics on this
shape are therefore ~90% presentation noise, and the degenerate stratum
alone is over two-fifths of it. Consequence — spec §3b upgraded from
"report both weightings" to: the census unit *is* the distinct `.sos`;
automaton counts survive as presentation multiplicity, a deliverable in
its own right and a free canonicity cross-check (every presentation of
one `.sos` must yield identical read-offs, certificates and formulas; a
divergence is a stop-the-line bug). E1/E2 percentages are re-keyed
accordingly at M1.5 — keep running the full automaton census, key the
tables by language. The portfolio's formulas on these shapes are also
adopted as E4(c)'s standing readability yardstick: per language,
`GFa` / `!a & G(!a | X!a)`-class output is the bar the transcription
should approach. (One row to explain in the next report: the "1
gated/unprintable string" among the 759 — printer artifact or encoding
bug, either way one line, and whether its language deduplicates away.)

---

## M1.5 — in progress (2026-07-08)

Census-independent parts first (the genaut census is being regenerated by a
parallel track; E1/E2 re-key, E4-interim, E3, and the full E7 ledger consume
it and wait). Landed on the triptych + fixtures below; the census sweeps run
when the new census lands.

### The certificate verifier is membership-only, presentation-agnostic

A counting family is a *portable* non-LTL certificate: validation is
"membership toggles with `n mod p′`", i.e. `2p′+1` lasso membership queries
against **any** acceptor of `L`. The verifier side holds no algebra and is
not tethered to the SoS-derived automaton — the client's own presentation
answers. Implemented as an oracle bridge (`witness/spot_oracle.py`): a
`sosl.sos.Lasso → Spot lasso-string` renderer feeding `verifier.check.member`
(Spot lasso-intersection, acceptance-agnostic), so `toggles(family, oracle)`
replays against the input HOA directly. The SoS read-off (`witness.val`)
survives only as a labelled self-check, never the trust anchor. Spot is a
lazy import kept out of the pure `witness/` core. Proven presentation-faithful
on the triptych: a family replays against its own language's automaton and
correctly **fails** against the wrong one (`Even`'s linear family toggles on
`even.hoa`, is constant on `evenblocks.hoa`). This is E7's verifier tier,
ready for the non-LTL census when it lands.

### E7 dual scan (theory's ask): both context shapes run to completion

`witness/extract.py` refactored into `_scan_linear` / `_scan_omega` (each the
first separating family of its shape, or `all-constant`), with `dual_scan`
running **both** to completion and `extract_family` = first-of-two (historical
scan order, behavior byte-identical — E0 gate green at 27 cases, the three
`e7_dualscan` cases now wired in). `DualScan.h5_hit` is the H5 read-off:
ω-power all-constant ⟹ a linear-only certificate.

### F4 — the dual scan (global) refutes F2's parenthetical: `Even` speaks in *both* shapes

**The incident.** F2 recorded "the ω-power side has nothing to say on Even
(its certificate is linear), just as the linear side has nothing to say on
EvenBlocks (Prop 4.2)." The global dual scan (contexts ranging over all of
`𝒞`) says otherwise for `Even`: **both** shapes separate — linear
`F₁(u=a, v=a, x=(!a)^ω, p′=2)` **and** ω-power `(u=ε, v=a, y=a·!a, p′=2)` —
and both replay against `even.hoa` by membership. So `Even` is *not* ω-blind
and *not* an H5 shape. `EvenBlocks` is confirmed linear-**all-constant**
(ω-power only) — H5's *dual*, not an H5 hit. Neither triptych specimen is an
H5 hit (ω-power all-constant); that hunt is genuinely for the census.

**The distinction, for theory to adjudicate.** F2's *main* claim is about the
**layer-confined (B)** tester (within `Even`'s group layer `{2,4}`), where "the
ω-power side has nothing to say" may still hold. The dual scan is the
**global** certificate scan, which uses contexts outside the layer. Read
globally, F2's parenthetical — and any §4.3 remark that each specimen speaks
in exactly one shape — is refuted for `Even`; read as layer-confined, there is
no tension. **No paper edit made:** §4.3's duality remark is flagged for
theory to decide whether it is a confined or global statement. If global, it
needs `Even`'s two-shape availability folded in (only `EvenBlocks` is
single-shape).

### Theory adjudication of F4 (2026-07-08)

**Confined — and the global refutation is correct and welcome.** F2's
main claim stands untouched: the layer-confined (B) statistics see
nothing of `Even`'s group. The parenthetical, read globally, is refuted
for a clean reason: an ω-power family `u·(vⁿ·y)^ω` with `u = ε` pumps
the very start of the word, so a prefix-counting group is exposed to
ω-power contexts — nothing in §4 ever promised the dual of
Proposition 4.2. The finding is an *asymmetry*, not a duality:
prefix-independent ⟹ linear-blind is a theorem; the dual blindness has
no theorem, and `Even` refutes the naive symmetry — speaking in both
shapes, via the very family that certifies `EvenBlocks`. The paper's
§4.3 remark, which the M1 fold-in edit had written in its global
reading (importing F2's parenthetical), is corrected to the confined
claim plus the asymmetry; §4.1's H5 paragraph now records that the
triptych offers no witness; spec E7 gains the triptych dual-scan
vectors. Net effect on H5: sharpened — one more data point toward "F₂
always available", with the census the judge.

### Interim (2026-07-08) — E7 verifier tier landed; the regenerated census is open

**Landed (commit, census-independent):** the E7 dual scan and the
presentation-agnostic certificate verifier — the two parts of M1.5 that
needed only the triptych and fixtures. `witness/extract.py` now splits into
`_scan_linear`/`_scan_omega` with `dual_scan` running both shape scans to
completion (`DualScan.h5_hit` = ω-power all-constant); `extract_family` is
first-of-two, behavior byte-identical. `witness/spot_oracle.py` renders a
`sosl.sos.Lasso` into a Spot lasso-string and replays a family through
`verifier.check.member` — membership only, no algebra on the verifier side,
against *any* acceptor the client holds; the SoS read-off (`witness.val`)
survives only as a labelled self-check. E0 gate green at 27 cases (the three
`e7_dualscan` triptych cases wired in); the oracle is proven
presentation-faithful (a family toggles against its own language's automaton,
is constant against the wrong one). This is the E7 verifier tier, ready to run
the moment the census is available — which it now is.

**The regenerated census (`genaut/corpus/`, three tiers, per its README).**
`tgba/<tag>/` is the raw presentation census (many encodings per language);
`det/<tag>/` is the canonical automaton `D` (deterministic, complete,
transition-based, generic acceptance, HOA) — one per language; `sos/<tag>/`
is the syntactic invariant `𝓘(L)` (`.sos`) — one per language. `det/` and
`sos/` are **1:1 and deduplicated by the syntactic key**, so §3b's "the unit
is the language" is now *structural*, not something we impose: `corpus/sos/`
**is** the language census (~15k distinct languages across the bench), and
`corpus/det/` supplies the matching input automaton for the membership-only
verifier. Each tier folder's `census.md` carries the presentation
multiplicity (the `tgba → det` collapse) that §3b wants reported alongside —
it is measured for us, not re-derived. The frame is declared by the tag:
state/AP/acceptance-set count plus the acceptance **family** (bare tag =
`gba` generalized-Büchi default; `_parity` suffix = parity), so the parity
corpora the spec asked to add to the bench are present (`*_parity` shapes).

**Consumption plan (now unblocked).** The algebra-side experiments read
`corpus/sos/` (the language unit, no dedup on our side): E1/E2 re-key, the E7
dual-scan ledger over the non-LTL languages, the algebra half of E3.
`corpus/det/` is the acceptor for E7's membership replay and the automaton
side of E4/E3. `census.md` supplies each table's presentation-multiplicity
column. First run: the E7 dual-scan ledger — `dual_scan` partitions each
`corpus/sos/*.sos` (None ⟹ aperiodic/LTL, `DualScan` ⟹ non-LTL certificate),
and the non-LTL rows carry the two-column dual scan, `h5_hit`, component
lengths against the Theorem-4.4 bounds, and the `corpus/det/` replay.

### F5 — the census refutes "F₂ always available": H5 hits exist at the smallest shape

**The prediction.** Spec E7/H5: "a census with none [no ω-power-all-constant
specimen] is evidence toward 'F₂ always available'"; the dual scan looks for
the dual of Proposition 4.2's blindness, a non-LTL language certifiable in the
**linear** shape only.

**The run** (`tests/sos2ltl/e7_ledger.py` over `corpus/sos/2state1ap1acc`,
gba/Inf, deterministic-EL canonical `D` as the acceptor; the language census,
1:1 per §3b): 129 languages, 82 LTL / 47 non-LTL. All 47 non-LTL certificates
replay against `D` by membership only — the presentation-agnostic verifier
holds across the shape (0 replay failures). Dual-scan split: **34 both shapes,
9 linear-only (H5), 4 ω-power-only.** Component lengths ≤ 4 against `|𝒞|` ≤ 15
(Theorem 4.4's `< |𝒞|` holds with margin).

**REFUTED.** Nine H5 hits at 2 states / 1 AP — the ω-power scan is
*all-constant* (exact: it is read off the syntactic invariant `𝓘(L)`, which
`corpus/sos` *is*), the linear certificate `F₁` replays against `D`. One
confirmed witness settles §4.1's existence question **negatively**: F₂ (the
ω-power certificate) is *not* always available.

**The exhibit (smallest H5 witness, `|𝒞| = 4`).** `2state1ap1acc_04644`, the
language `L₄ = { w : |w|_a = ∞ } ∪ { w : |w|_a < ∞ and even }` — "*if only
finitely many `a` occur, their number is even*". Non-LTL because that parity
is a group on the finite-`a` stratum; H5 because **every** ω-power context
`(vⁿ·y)^ω` whose loop carries an `a` has infinitely many `a` and so is
accepted unconditionally — the ω-power scan sees only constants. Only the
linear shape separates: `F₁(u=a, v=a, x=(!a)^ω, p′=2)` drives the word into
the absorbing `(!a)^ω` tail, exposing the finite-`a` parity (samples
`a^{n+1}·(!a)^ω`, accept iff `n` odd). Replays 5/5 against the canonical `D`
by membership. Its `|𝒞| = 4` twin `…_16929` is the complement (odd count),
pattern `(T,F)`; the `_parity` shape yields the identical two languages.

Canonical automaton `D` (deterministic, complete, transition-based Büchi):

    HOA: v1
    States: 2
    Start: 0
    AP: 1 "a"
    Acceptance: 1 Inf(0)
    --BODY--
    State: 0
    [!0] 0 {0}
    [0] 1 {0}
    State: 1
    [0] 0 {0}
    [!0] 1
    --END--

Syntactic invariant `𝓘(L₄)` in full (`.sos`, with the residual trailer —
`tests/sos/build_sos.py --residuals`, a two-state parity residual DFA):

    SOS v1
    ap: a
    classes: 4
    0 eps
    1 !a
    2 a
    3 a;a
    letters: !a->1 a->2
    mult:
    0: 0 1 2 3
    1: 1 1 2 3
    2: 2 2 3 2
    3: 3 3 2 3
    accept:
    1 1
    2 3
    3 1
    3 3
    residuals: 2
    0 eps
    1 a
    res-step:
    0: 0 1
    1: 1 0

The group is `{[a], [a·a]}` (order 2 under `·[a]`); `[!a]` and the two group
powers are the three idempotents; `res-step` is the parity toggle on `a`, the
residual DFA the aperiodic reading cannot see is periodic.

**The symmetric reading.** The 4 ω-power-only languages are F₁-blind — the
direction theory already has as a *theorem* (prefix-independent ⟹ linear
context constant). The 9 H5 hits are the direction theory had *no* theorem for
and leaned toward "cannot happen"; it happens. So **neither** context shape is
universally available (34 both / 9 F₁-only / 4 F₂-only), and running *both*
scans — the dual scan itself — is necessary, not a convenience. F4's asymmetry
becomes: each blindness occurs, one by theorem and one by census witness.

**Sweep (every shape bar the excluded ~11k `2state2ap0acc`).** H5 hits total
**26**: 9 in `2state1ap1acc` and 9 in its `_parity` twin (same languages, min
`|𝒞| = 4`), 8 in `3state1ap0acc` (min `|𝒞| = 6`); none below `|𝒞| = 4`.
Non-LTL languages occur **only** at ≥ 2 states — every 1-state shape (through
3 AP / 3 acc, gba and parity) is entirely LTL, as expected (a single state
cannot carry a counting group). `2state1ap0acc` has 6 non-LTL, all two-shape
(0 H5). Every non-LTL certificate across the whole sweep replays against its
`D` (0 failures — the presentation-agnostic verifier holds census-wide). The
F₁-blind (ω-only) direction appears only in `2state1ap1acc` (4) — the
prefix-independent theorem stratum. Only `2state2ap0acc` remains unrun.

**Paper edit flagged, not made** (per F4's handling): §4.1's H5 paragraph
should record the negative settlement and cite the `|𝒞| = 4` exhibit above;
the extractor's two-shape scan earns a "necessary" note. Awaiting theory.
