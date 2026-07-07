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
