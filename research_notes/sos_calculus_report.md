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

Substantiates paper §3.3 ("the realized ratio is a datum … over census pairs").
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

Substantiates paper §4 (the ledger rows) and Contribution 4.
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

Substantiates paper §3.4 (the entry-price / "pay canonicity once" claim).
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

Substantiates paper §3.5 (Prop 3.3 read-off) and §4, and a census datum for
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

## CAL4d / V3 — the concatenation blow-up (Prop 3.4)

Substantiates paper §3.4 (Proposition 3.4). `reference/calculus/v3_blowup.{md,csv}`
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
  increment letter rather than an alias, and Prop 3.4 survives verbatim.
- **F14 — the entry price shows as growth, not a wall.** The construction
  finished for every n (max **0.36 s** at n = 5, 33 states) — no timeout was
  needed; the enriched-monoid entry price is visible in the ~8–9× per-step time
  growth (0.7 → 4 → 36 → 320 ms) rather than a budget blow-up.

## Status

All five V-experiments delivered; the paper's measurement placeholders are
filled in pure form and cite this report's territory. The remaining CAL4 line is
housekeeping only. The `flat_canon` census, the seeds, and the git revisions in
each `reference/calculus/*.md` header make every finding above regenerable.
