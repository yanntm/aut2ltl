# A Calculus on the Syntactic ω-Semigroup — results

The answer to `research_notes/sos_calculus_spec.md` §8 (milestone CAL4): the
`sosl.sos.calculus` package run against the V-series, measured on the
`flat_canon` census and on the hand-built `W·L_n` family. Each finding `Fn` is a
checked prediction of the paper `research_notes/sos_calculus.md`; the paper
states the results in pure form and cites no artifact — this report is where each
claim is tied to a regenerable machine report.

Every campaign writes a machine-generated report under `reference/calculus/`
(one `.md` + one `.csv`) carrying a date / git-rev / seed / corpus header, so any
row below is reproducible from that file alone. Commands run from `sosl/`
(`cd sosl`); the census is `genaut/corpus/flat_canon/` (3938 languages, one
`.sos` invariant + its deterministic HOA `D` per language). Spot is
bounded-or-skipped; a blown per-case budget is a datum (`F2`), never a wait.

## Package — the substrate (CAL1–CAL3, product)

Engine state: `align` (the generated product), the `surgery` free fragment
(Boolean ops, complement, rooting, saturate, inverse substitution), `decide`
(emptiness / universality / inclusion / equivalence / intersection-word /
membership, all witness-carrying), `reduce` (the canonical re-quotient),
`witness`. Soundness harness 1–8 green (`tests/calculus/`, see its README).

- **F0 — the product table `align` defers.** `calculus.product.materialize`
  builds the product ω-semigroup over the reachable nodes `align` already found
  (the letter-generated subsemigroup, closed under the componentwise product),
  re-expressing each side as a pair set over one shared table, so `surgery` then
  combines two languages over *different* tables and `reduce` canonicalizes the
  result — the substrate V1b/V1c's cross-table ∩/∪ need. Gate `product_gate.py`
  (harness 5b): over every canonical cell of the aligned product, `member` of
  `reduce(a∩b)` / `reduce(a∪b)` equals the Boolean combination of the two sides,
  both carried sides are saturated, and ∩-emptiness agrees with
  `intersecting_word`. Green on 200+ sampled same-alphabet pairs across every
  alphabet stratum (`python3 -m tests.calculus.product_gate --sample 200`).

## CAL4a / V1a — the alignment-ratio distribution

Substantiates paper §3.3 (the realized-ratio datum; numbers now live in paper §8.2).
`reference/calculus/v1_align_ratio.{md,csv}` —
`python3 -m tests.calculus.v1_align --campaign` (seed 20260709; 6200 pairs
sampled within alphabet strata; `F2=0`).

- **F1 — the generated product is affordable.** Over 5000 uniform pairs the
  ratio `|nodes|/(n₁·n₂)` has median **0.174**, p95 **0.356**, max **0.593** —
  80.8% below 0.25, 98.6% below 0.5, and never at 1.0. The product is a fraction
  of its rectangular bound and never approaches it. Cold BFS median ≤ 0.4 ms.
- **F2 — related operands collapse toward the diagonal.** On 1000 (L, ¬L)
  complement-partner pairs (partner found by content hash of `reduce(¬L)`, not
  filename) the median ratio is **0.063**, well below the uniform 0.174 — the
  §3.3 prediction that a shared algebra correlates the folds.
- **F3 — the claim holds where products can grow.** On 200 pairs from the
  top-decile `|𝒞|` languages the median is **0.119** (95% below 0.25) — smaller,
  not larger, exactly where uniform sampling (dominated by small tables) could
  not test it.

## CAL4a / V1b — the operation ledger, calculus vs Spot

Substantiates paper §7.1 (the ledger rows), §8.3, and Contribution 4.
`reference/calculus/v1_ops.{md,csv}` —
`python3 -m tests.calculus.v1_ops --campaign` (first 1000 uniform pairs of V1a +
their 1550 distinct languages; 8100 rows; `F2=0`). Held-object economy: inputs
are deterministic so Spot's complement is `dualize` (not NBA complementation —
the theory row stands on [TFVT10], not these timings); per-op timings are warm
(median of 7), `align` is cold and excluded (reported align-amortized); every
wall clock carries the abstract count (`|nodes|`, cells, `|linked|`).

- **F4 — held-object operations are microsecond-scale.** Median warm times: a
  containment decision **0.0083 ms**, lasso membership **0.0002 ms**, complement
  **0.175 ms** (`P ↦ P^c` then `reduce`). The automata side is faster in raw
  wall-clock on these tiny deterministic C++ automata (dualize 0.0008 ms) — the
  ledger's argument is the *counts* and the free/normal-form structure, not the
  clock, and the summary says so.
- **F5 — normal form and heuristic sit in separate columns (trap #12).** The
  canonical intersection object (`materialize` + pointwise ∧ + `reduce`) has
  median **2.4 ms**; Spot's raw `product` is 0.0018 ms and its `postprocess`
  simplification 0.033 ms. These are never divided: one is a normal form
  (byte-comparable, canonical), the other a heuristic presentation.
- **F6 — `align` amortizes over a session.** Cold `align` (0.070 ms median) is a
  shared entry price; spread over `k` decisions on the held product the
  per-decision cost is `(align + k·op)/k` = 0.094 / 0.026 / 0.018 ms at
  `k = 1 / 5 / 10` — the §3.3 "session pays its BFS once" economy, measured.

## CAL4b / V1c — the pipeline demo

Substantiates paper §4 (the entry-price / "pay canonicity once" claim); numbers in paper §8.4.
`reference/calculus/v1_pipeline.{md,csv}` —
`python3 -m tests.calculus.v1_pipeline --campaign` (seed 20260712; 20
same-alphabet pairs, middle `|𝒞|` decile; pipeline
`E1=¬A · E2=E1∩B · E3=¬E2 · E4=E3∪A`; 80 rows; `F2=0`).

- **F7 — the entry price is a small one-time share.** Building `𝓘(L)` from the
  deterministic acceptor (`invariant_of ∘ canonical`) is a one-time
  **0.43 ms**, ~15% of the four-stage pipeline total (2.89 ms) — thereafter every
  surgery is a set operation on a held object.
- **F8 — the re-check is a byte comparison, not an equivalence test.** The
  "did my rewrite change the language" re-check every stage runs is a byte
  compare of canonical `.sos` dumps at **0.0001 ms**, against Spot's
  `equivalent_to` at **0.0039 ms** — tens of times cheaper, and the gap widens
  with automaton size while the byte compare stays linear in the dump.
- **F9 — trap #14 respected.** Every automaton is deterministic and small
  (stage `|𝒞|` 14 / 32 / 32 / 32 vs Spot states 5 / 8 / 10 / 10), so no Safra
  determinization is forced; the demo isolates the normal-form economy, not the
  exponential entry the frontier reserves.

## CAL4c / V2 — the stutter read-off vs Spot

Substantiates paper §5 (Prop 5.1 read-off) and §8.5, and a census datum for
[SωSN26]. `reference/calculus/v2_stutter.{md,csv}` —
`python3 -m tests.calculus.v2_stutter --campaign` (full sweep, 3938 languages).
Our verdict is the `.cat` `stutter:` tag (`classify`'s `λ(a)²=λ(a)` read-off);
Spot's is `is_stutter_invariant` on the paired HOA.

- **F10 — perfect agreement, zero disagreements.** The algebraic read-off and
  Spot agree on **3938 / 3938** languages; the disagreement dossier is empty.
  Spot median 0.010 ms.
- **F11 — the class counted.** **648** languages are stutter-invariant — 16.5%
  of the census, **28.9%** of the 2240 LTL-definable ones; every one is
  LTL-definable (0 non-LTL stutter-invariant), the X-free refinement of the cut.

## CAL4d / V3 — the concatenation blow-up (Prop 4.1)

Substantiates paper §4 (Proposition 4.1); numbers in paper §8.6. `reference/calculus/v3_blowup.{md,csv}`
— `python3 -m tests.calculus.v3_blowup --campaign` (per-case budget 15 s).
Deterministic `L_n` and `W·L_n` acceptors are built by hand (the known result of
the concatenation, not an implementation) and re-entered through the gate.

- **F12 — the bound holds n = 2..5.** `|𝒞(W·L_n)| = 17, 48, 127, 318` against
  the bound `2ⁿ−1 = 3, 7, 15, 31` — each above it, off acceptors of only
  `2ⁿ+1 = 5, 9, 17, 33` states; `|𝒞(L_n)| = 2n+1`. The subset construction
  resurfaces in the algebra exactly as the proof predicts.
- **F13 — the encoding trap (#9) does not weaken the proof.** Two APs give four
  valuations; the increment class carries two of them
  (`a := (¬p∧¬q)|(p∧q)`, `b := p∧¬q`, `# := ¬p∧q`), the fourth a genuine second
  increment letter rather than an alias, and Prop 4.1 survives verbatim.
- **F14 — the entry price shows as growth, not a wall.** The construction
  finished for every n (max **0.36 s** at n = 5, 33 states) — no timeout was
  needed; the enriched-monoid entry price is visible in the ~8–9× per-step time
  growth (0.7 → 4 → 36 → 320 ms) rather than a budget blow-up.

## E-CAL-EX — the running example, mechanically (spec §9.1)

Answers spec §9.1; fills paper §8.7. `reference/calculus/example_gate.md` —
`python3 -m tests.calculus.example_gate` (one shot, ~2 s, no argv). All seven
spec items green, in nine printed checks. The answer key is deliberately not
ours: both invariants are built by `sos.build.reference_of_ltl` (Spot
determinizes, `core.quotient` canonicalizes — the calculus reads off an algebra
it did not build), the 25 table cells are regenerated from the word model
`{ε, a⁺, b⁺, a⁺b⁺, dead}` rather than transcribed from the paper, classes are
located by role (identity, the two letter classes, `A·B`, `B·A`) and never by
key string, and the Wagner coordinates are checked twice — against `sos.classify`
(independent of `calculus.surgery`) and against the committed `.cat` sidecar of
the corpus row that holds the language.

- **F-EX — theory's hand computation is confirmed on every value.** 5 classes;
  the full multiplication table matches the word model; 6 linked pairs;
  `P = {(B,B), (C,B)}`; stutter read-off true; `P_A = P` and `P_B = {(B,B)}`;
  `Live = 𝒞 \ {D}`, closure adds exactly `(A,A)`, interior `= ∅`, A–S factor
  `= P ∪ {(D,A),(D,B),(D,D)}`; obligation of degree `(1, 2)`, with `classify`
  independently reporting coords `(m⁺, m⁻, n⁺, n⁻) = (0, 0, 1, 2)`;
  `𝓘(GF a)` has 3 classes with `P₂ = {(α, α)}`; the alignment generates 5 nodes
  of `5 × 3`; the intersection is empty; `a*·b^ω ⊆ FG ¬a` holds and the reverse
  fails. **The minimal counterexample is `ba·b^ω`, exactly as predicted** —
  witness verbatim `included cell=(4,2) stem=p;!p loop=p bit=1`, replaying
  positive on `FG ¬a` and negative on `a*·b^ω`. Nothing for theory to adjudicate.

- **F-EX1 — a bug on our side, found by the gate (fixed).** The hand-built
  reference that `tests/calculus/obligation_oracle.py` opened with carried only
  **4** classes: it merged `A·B` into `B`. That morphism is a legal ω-semigroup
  but it does not recognize `a*·b^ω` — it accepts `(ab)^ω`, whose loop class
  `C` is not idempotent in the true algebra (`C² = D`). Verified by `member` on
  both tables. Corrected in place to the 5-class table (now counter-signed
  against Spot by `example_gate`). **No CAL5 number moves**: the corpus sweep
  never touched the hand table, and the degree read-off is `(1, 2)` on the wrong
  algebra as well as the right one — the error was invisible to the check it sat
  in. This is why §9.1 asked for an independent construction.

- **F-EX2 — the corpus row is `2state1ap1acc_16898`, and finding it is a trap
  worth recording.** The spec's conditional `.cat` cross-check applies: the
  language *is* catalogued, at the smallest shape that emits it (2 states, 1 AP,
  1 acceptance set — a nondeterministic-or-not TGBA of exactly the shape one
  would guess), sidecar `phi: 2,sigma | coords: 0 0 1 2 | class: properly Σ₂`.
  Its coords confirm both read-offs (`max(m⁺, m⁻) = 0 ≤ 0`, degree `(1, 2)`).

  A first pass wrongly reported the language **absent**, by comparing raw `𝓘`
  dumps against the corpus files. Two things defeat that, and `corpus_row` in the
  gate now encodes both: `flat_canon` stores one file per language **up to
  renaming its symbols**, as the `B_k` orbit-min of the invariant (genaut's
  `canon_key`: `remove_free_aps` → orbit representative → dump — *not* the raw
  syntactic dump); and those canonical bytes carry the **AP's name**, which the
  corpus spells `a` and the paper spells `p`. Either mistake alone turns a
  present language into an absent one. The key function is now validated as a
  fixpoint on all 6222 rows before it is trusted to say "absent".

## V4 — the classification battery vs Spot (spec §9.2)

Answers spec §9.2; fills paper §8.5. `reference/calculus/v4_ladder.{md,csv}` —
`python3 -m tests.calculus.v4_ladder --campaign` (full sweep, 6222 languages,
per-case budget 10 s, no blown budget). Ours: the `surgery` scans on the held
invariant, warm, median of 7 (`is_safety` / `is_cosafety` — Cor 6.2;
`is_obligation` — Thm 6.6; `obligation_degree` — Prop 6.7). Spot's: the paired
deterministic HOA. **Note this run is on the 6222-row corpus, not the report-era
3938 of V1–V3** — it is the first V-number on the new corpus, and does not mix
with the others until §9.4 refreshes them.

- **F15 — the Spot surface, and why the comparison had to be built. Spot 2.14
  has no automaton-level Manna–Pnueli classifier.** `spot.is_obligation`,
  `is_persistence`, `is_recurrence` and `mp_class` are **formula-level**: the
  formula is a mandatory argument and the automaton is only an optional
  accelerator (`tl/hierarchy.hh`). `autfilt` confirms the shape of the library —
  it offers `--is-weak` / `--is-terminal` / `--is-inherently-weak`, all
  *structural*, and no `--is-safety` / `--is-obligation`. This is not a gap we
  can route around with a translation: the corpus carries an LTL bit precisely
  because **2484 of its 6222 languages are not LTL-definable**, so for those no
  formula exists to hand the classifier. The automaton-level oracle used here
  therefore needs no formula, and is language-level rather than structural:
  safety = `is_safety_automaton` (its contract is "the acceptance condition can
  be set to `true` without changing the language" — the closure fixpoint, decided
  exactly, `twaalgos/strength.hh`); co-safety = the same test on `dualize` (an
  exact complement on these deterministic complete automata, guarded by an
  explicit precondition check in the script); obligation = `minimize_wdba` +
  equivalence, which is what Spot's own `ocheck::via_WDBA` runs inside
  `is_obligation`, minus the formula. `v4_ladder.py --selftest` pins those three
  against `spot.mp_class` on eight formulas of known class (B/S/G/O/P/R) so the
  oracle's contract is a rerunnable claim and not a one-off probe.
- **F16 — perfect agreement, zero disagreements, on all three verdicts.**
  **6222/6222** on `is_safety`, on `is_cosafety`, and on `is_obligation`
  (1514 / 1514 / 3182 positives, identical on both sides); the full-triple
  agreement is 6222/6222 and the disagreement dossier is empty. No case blew the
  budget. An algebraic scan of the held invariant and a Büchi-automaton
  minimization decide the same three questions on every language in the census.
- **F17 — the rung census of `flat_canon`.** Obligation: **3182/6222 = 51.1%**.
  Split: B (safety ∧ co-safety) **84**, S (safety only) **1430**, G (co-safety
  only) **1430**, O (obligation, neither) **238**, above the obligation rung
  **3040 = 48.9%**. Two internal consistency checks pass and are printed by the
  script rather than left to the reader: co-safety is safety of the complement
  and the corpus is complement-closed, so **S = G** (1430 = 1430); and complement
  swaps the polarities of the superchain, so the degree histogram must be
  symmetric under `(n⁺, n⁻) ↦ (n⁻, n⁺)` — it is, on every entry (1430/1430,
  68/68, 40/40, 2/2, 1/1, with (0,0) and (1,1) self-paired).
- **F17b — the obligation rung is not inside LTL, and that is the point of
  F15.** Crossing the rung against the `.cat` LTL bit: **1486 of the 3182
  obligation languages (46.7%) are not LTL-definable** (S 704, G 704, O 78;
  every one of the 84 B-rows is LTL). This is as it must be — the ladder is
  topological and the LTL cut is aperiodicity, so a safety language need not be
  star-free — but it is what makes the formula-level route to Spot's classifiers
  a dead end rather than an inconvenience: on nearly half the obligation rows
  there is no formula to pass. The algebraic read-off does not notice the
  difference; it never leaves the invariant.
- **F18 — the degree stratifies the rung exactly.** Empirically the rung is a
  *function* of `obligation_degree` on all 3182 obligation rows: degree ≤ 0 in
  both coordinates ⟺ B (the 84 = 82 + 2 rows with `(0,0)`, `(-1,0)`, `(0,-1)`);
  `(1,0)` ⟺ S (1430); `(0,1)` ⟺ G (1430); everything above ⟺ O (238, the tail
  `(1,1)` 18, `(1,2)`/`(2,1)` 68 each, `(2,3)`/`(3,2)` 40 each, `(3,4)`/`(4,3)`
  2 each). The Wagner coordinates are strictly finer than the rung and no Spot
  call returns them — Spot decides the obligation rung but does not measure the
  superchain, so that column has no counterpart to disagree with.
- **F19 — the timings, stated against the trap.** Per-case median of 7, then the
  median over cases (ms): safety 0.0029 ours / 0.0007 Spot; co-safety 0.0029 /
  0.0017; obligation 0.0027 / 0.0061; degree 0.0265 ours, no counterpart. **Spot
  is faster on safety (0.25×) and co-safety (0.59×) and slower on obligation
  (2.27×)** — this is Python against C++ on tables of median 15 classes and
  automata of ≤ 9 states, so the honest reading is that both are sub-10-µs and
  the ratio corroborates the asymptotics rather than benchmarking anything: our
  scans are linear in the held table, while Spot's route builds and compares
  automata (obligation, the one that determinizes and minimizes, is the one where
  it loses). The paper should not sell a speed claim off these numbers.

## For theory — paper §8 is on the wrong corpus, and §8.5 is waiting on F15–F19

Two integration items, neither of which engineering touches (the paper is
theory's file):

1. **§8.5's V4 ⟨TBD⟩ is answered**, by F15–F19 above. The numbers are in pure
   form there; the head-to-head timing the ⟨TBD⟩ asks for is F19, and it is a
   *non-*claim — Python against C++ on microsecond-scale objects; the paper
   should not sell speed off it. The two results worth the paper's space are
   F16 (6222/6222 agreement, three verdicts, empty dossier) and F15 (Spot has no
   automaton-level Manna–Pnueli classifier at all, and translation is no escape
   because 2484 corpus languages have no formula — so the comparison had to be
   built, and what it compares against is stated exactly). F17b is the one that
   may deserve a sentence in the paper's own voice: the obligation rung is
   nearly half non-LTL, which is why the algebraic route is not a convenience.
2. **Every other corpus-derived number in §8 is stale.** They are report-era
   **3938**; the corpus is now **6222**, and V4 is the first V-number measured on
   it (so §8.5's stutter bullet and its classification bullet would otherwise sit
   side by side on different corpora — do not let them). No figure in §8 should
   be trusted, copied forward, or left in place because it looks close: each one
   needs re-sourcing from the finding here that produced it, one by one. Spec
   §9.4 is the sweep that regenerates them on the frozen corpus; until it runs,
   this report — not the paper — is the source of truth for every measured value.

## Status

All five V-experiments delivered, plus E-CAL-EX and V4. V4 is on the 6222 corpus;
V1a/V1b/V1c/V2/V3 are on the report-era 3938 and are pending the §9.4 refresh.
The remaining CAL4 line is housekeeping only. The `flat_canon` census, the seeds,
and the git revisions in each `reference/calculus/*.md` header make every finding
above regenerable.

## Status addendum (2026-07-11, theory)

The paper was restructured into ten sections (new title; results
renumbered — Prop 3.3→5.1, 3.4→4.1, 3.5→6.1, Cor 3.6/3.7→6.2/6.3,
Thm 3.10→6.6, Prop 3.11→6.7); all measured numbers now sit in paper §8
in pure form, sourced from this report unchanged. Open engineering
items are spec §9: E-CAL-EX (running-example gate), V4 (classification
battery vs Spot — fills paper §8.5's ⟨TBD⟩), CAL6 (alphabet hygiene),
and the corpus-refresh sweep (corpus moved 3938 → 6222; all §8 numbers
to be regenerated on the frozen new corpus before submission). Figure
requests: `sos_calculus_figures.md`.
