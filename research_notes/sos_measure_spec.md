# SoS Quantitative (Measure / Distance / Entropy) — Implementation Specification

**Status (2026-07-10).**

| item | state |
|---|---|
| QNT1: the engine — θ-profile, measure, distance (§2–§4) | **OPEN** |
| QNT2: the soundness harness (§5) | **OPEN** |
| QNT3: entropy (§6) | **OPEN** |
| QNT4: the Markov product `Pr_M(L)` (§7) | **OPEN** |
| QNT5: the census campaign + pipeline demo (§8) | **OPEN** — blocked on QNT1–QNT4 |
| MDPs, semiring-valued `Val`, Hausdorff dimension | **NON-GOALS** (§9) |

An implementer starting cold reads: this header, §1, the section for the
component at hand, and §5 before trusting any number. Revision history
lives in git and `docs/HISTORY.md`, not here.

**Normative math.** `research_notes/sos_measure.md` (the paper): the
generic-verdict theorem (Thm 3.4, Lemmas 3.1–3.3), the product form
(Thm 3.5), the algorithm (§4.1), the pseudometric (§4.2), entropy
(Prop 5.1). Where this spec and the paper disagree, the paper wins and
the disagreement is a bug to report. Results flow back through
`research_notes/sos_measure_report.md` only; the paper cites no artifact.

**One-line goal.** A package `sosl/sosl/sos/quant/` computing, from a held
invariant `𝓘 = (𝒞, λ, M, P)`: the θ-profile, `μ_p(L)` exactly over `ℚ`,
`d_p(L₁, L₂)` on an aligned table, `h(L)`, and `Pr_M(L)` for a labeled
Markov chain — each with a replayable certificate.

**Layering law (hard).** `sosl.sos.quant` imports `sosl.sos` and
`sosl.sos.calculus` (it consumes `align`, `xor`-surgery, `Live`, the SCC
pass) and NOTHING else in the repo. Never `sosl.learn`, `sosl.teacher`,
`tests.*`. Pure functions over invariant objects; no mutation of inputs.

**Typing.** Every public function fully annotated (params + return), house
rule. Probabilities are `fractions.Fraction` end to end in QNT1/QNT4;
floats appear only in QNT3 (entropy), clearly quarantined.

---

## 1. Objects

- **Bernoulli measure**: `p : Σ → Fraction`, all values `> 0`, summing
  to 1. Default: uniform. Constructor validates both conditions.
- **Right-Cayley chain**: the DFA `c →a c·λ(a)` on `𝒞` weighted by `p`.
  Never materialize a stochastic matrix separately from `M`/`λ` — the
  table *is* the chain.
- **θ-profile**: ordered list of `(bottom SCC key, θ ∈ {0,1})`, the SCC
  keyed by its shortlex-least class key (canonical — profile equality
  must be a value equality).
- **Labeled Markov chain `M`** (QNT4): finite states, transitions
  `(q, a, q', prob ∈ Fraction > 0)`, out-probabilities summing to 1 per
  state, initial distribution. Reader for a small text format to be fixed
  with the corpus keeper (`.mc` sidecar, CSV-shaped, no JSON — house
  rule).

## 2. QNT1a — θ-profile

Algorithm (paper §4.1 steps 1–3):

1. Bottom SCCs of the right-Cayley graph: Tarjan/Kosaraju over the
   `n·|Σ|` edge list. (If `sosl.sos.calculus` already exposes the SCC
   condensation from the obligation read-off, REUSE it — do not re-derive.)
2. Kernel idempotent `k`: unique bottom SCC of the *two-sided* Cayley
   graph — edges `c → M(λ(a), c)` AND `c → M(c, λ(a))`, `a ∈ Σ`, on
   `𝒞 \ {[ε]}` — then `k := idem(t)` for any `t` in it. Assert: the
   bottom SCC of the two-sided graph is unique (kernel uniqueness); a
   second one is a table corruption, fail loudly.
3. Per bottom SCC `C`, pick the keyed representative `c` and set
   `θ_C := Val(c, k)`.

Certificate: `(key(c), key(k), θ_C)` per component — a replay needs only
`fold`, `idem`, and `P`.

**Law checks (cheap, assert in-engine):** `k·k = k`; `c·k` lands in `C`
(closedness); recomputing `θ_C` from a *different* `c' ∈ C` and from
`k' := idem(t')` for a different kernel element agrees (Lemma 3.3 made
executable — this is the single most valuable assertion in the package;
keep it on under `--paranoid`, sample it under default).

## 3. QNT1b — measure

Paper §4.1 step 4: unknowns `x_c` for transient `c`, equations
`x_c = Σ_a p(a)·x_{c·λ(a)}` with bottom-SCC classes substituted by their
`θ`. Solve over `Fraction` (fraction-free Gaussian elimination or
`sympy`-free hand-rolled — no numpy floats). `μ_p(L) = x_{[ε]}`.

- Output: `Fraction`, plus the certificate (θ-profile + the solved
  vector).
- Complexity guard: `n ≤` census sizes (double digits) — cubic exact
  arithmetic is nothing; do NOT optimize.
- API shape: `measure(inv, p=None) -> MeasureResult` (`Fraction` value,
  θ-profile, certificate); `theta_profile(inv) -> Profile` exposed
  separately (it is `p`-free and cheaper — census wants it standalone).

## 4. QNT1c — distance

`d_p(L₁, L₂)`: align (calculus), `xor` the carried pair sets (free
surgery), run §3 on the aligned table. Return `Fraction` plus the
aligned xor's θ-profile (all-zero ⟺ null disagreement — paper §4.2).
Do not reduce before measuring (measure is invariant under reduce; a
`--paranoid` check may verify that on samples).

## 5. QNT2 — the soundness harness (before any number is believed)

Gates under `sosl/tests/quant/`, runnable one-input-per-invocation,
≤15s each, logs under `tests/quant/logs/`.

**Oracle (Route A).** Independent measure via the exit acceptor: exit
`𝓘 → NBA` (existing calculus exit), determinize through Spot
(bounded-or-skipped, budget per case; a skip is a datum, never a wait),
then the classical BSCC analysis [CY95-shaped] on the deterministic
automaton with the SAME hand-rolled `Fraction` linear solver. The oracle
shares no code with QNT1 except the solver — acceptable; if the solver
worries you, cross-check it once against hand-computed 3-state cases.

**Metamorphic laws (exact, corpus-wide):**

1. `μ(L) + μ(¬L) = 1` — complement is the free flip; this must hold to
   the exact Fraction.
2. `μ(L₁ ∪ L₂) + μ(L₁ ∩ L₂) = μ(L₁) + μ(L₂)` on aligned pairs.
3. `L₁ ⊆ L₂` (calculus scan) ⟹ `μ(L₁) ≤ μ(L₂)`.
4. θ-profile is `p`-free: recompute `μ` under 3 random full-support
   rational `p`; the {0, 1, interior} trichotomy must not move.
5. `d_p` pseudometric: symmetry exact; triangle inequality on sampled
   triples; `d_p(L, L) = 0`.
6. Absorption sanity: `Σ_C Pr[absorption in C] = 1` exactly.
7. Obligation cross-check: on obligation-band census entries
   (`is_obligation` read-off), `θ_C` must agree with the stem-`R`-class
   verdict of the calculus paper's Thm 3.10.

**Gate discipline.** As in the calculus package: a red law is a
stop-the-line finding against the *paper*, reported in the report file
with the invariant key and the replay command, before any fix.

## 6. QNT3 — entropy

Paper Prop 5.1: `A` = letter-count matrix on `Live × Live` (`Live` from
`calculus.surgery`), `h = log₂ ρ(A)`.

- Float quarantine: `ρ` via power iteration with certified bracketing
  (Collatz–Wielandt bounds give rigorous lower/upper enclosures from any
  positive vector; iterate until the bracket is `< 1e-9` wide). Report
  `(h_lo, h_hi)`; the certificate is the `Live` submatrix.
- Laws: `h(∅) = 0` convention; `h ≤ log₂|Σ|`; monotone under inclusion
  on aligned pairs; `h(cl(L)) = h(L)` — closure via the calculus hull
  surgery, an EXACT structural law (same `Live`), assert equality of the
  submatrices, not of floats.

## 7. QNT4 — the Markov product

Paper Thm 3.5. Product chain on reachable `states(M) × 𝒞`; bottom SCCs;
per component `B`: base point `(q̂, ĉ)` = keyed-least in `B`; cycle
semigroup `T` by BFS over pairs `(state of B, class in 𝒞)` from
`(q̂, [ε])` following `B`-internal edges, collecting classes at returns
to `q̂`, closed under the collection's products (it is closed by
construction of the BFS — assert idempotence of the collection step);
kernel of `T` by the two-sided reachability *within `T`* (T is a set of
classes with multiplication from `M` — reuse the §2.2 kernel routine
parameterized by generator set); `θ_B := Val(c, k)` for the keyed
`(q̂, c) ∈ B`; linear system over the product. Cross-checks:

- one-state `M` emitting all letters reproduces QNT1b exactly;
- `θ_B` recomputed from a different base point `q̂'` agrees (Thm 3.5's
  well-definedness, made executable);
- oracle: Route A product-side on small chains.

## 8. QNT5 — the campaign (fills the paper's §6 ⟨TBD⟩ slots)

Machine reports under `reference/quant/` (one `.md` + one `.csv` per
experiment, date / git-rev / seed / corpus header; `.cat`/CSV sidecar
columns, no JSON). Census: `genaut/corpus/flat_canon/`. Experiments:

- **E1 — measure + θ-profile columns**, full census: distribution per
  Wagner degree and per safety-progress band; the measure-0/1
  concentration question.
- **E2 — entropy column**, full census: distribution per degree; the
  full-entropy concentration question.
- **E3 — distance geometry**, sampled per alphabet slice: diameter,
  clustering by degree, nearest-LTL-neighbor for each non-LTL language
  (ties into the frontier story).
- **E4 — the pipeline demo**: one spec, a family of chains, `Pr_M(L)`
  per chain; baseline = the same queries through Spot-side
  determinization + the oracle solver; report wall-clock and the
  canonicity dividend (spec-side artifact stability across the family).

Per-case budget 15s, blown budget is a datum. Every number destined for
the paper lands first as a finding row in `sos_measure_report.md` with
its regeneration command.

## 9. Non-goals

- **MDPs / schedulers**: refused (branching wall, paper §4.3).
- **Semiring-valued `Val`**: future work, paper §7 last paragraph.
- **Hausdorff dimension**: not until entropy has landed and a source is
  in library.
- **Performance work of any kind**: census sizes are small; exactness
  and replayability outrank speed everywhere.
