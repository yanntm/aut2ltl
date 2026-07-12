# Measure, Distance, and Entropy on the Syntactic ω-Semigroup — results

The engineering answer to `sos_measure_spec.md`. Each finding `F-*` is a
checked prediction of the paper `sos_measure.md`; the paper states its
results in pure form and cites no artifact, so this report is where a claim
is tied to a regenerable machine report.

Every campaign writes its machine report under `reference/quant/` (one `.md`
+ one `.csv`, each carrying a date / git-rev / seed / corpus header and its
own regeneration command), so any number below is reproducible from that
file alone. Commands run from `sosl/`. Spot appears only inside the
independent oracles, bounded-or-skipped; a blown per-case budget is a datum,
never a wait. Each report carries the corpus it ran against in its header;
where an early campaign shows 4248 cases and a later one 6222, the corpus
grew once, between them.

**Closed work.** M1 (measure + θ-profile), M2 (the Route A oracle and laws
L1–L5), M3 (distance / shadow / essential, + the M3b biconditional), M4
(entropy) and M5 (the Markov product) are done and green corpus-wide.
Findings F-M1..F-M4 and the theory replies that accepted them, the P-M5
format ratification, and the work orders that produced all of it are frozen
in `sos_measure_experiments.md`; their machine artifacts are the
`reference/quant/m{1,2,3,4,5}_*.{md,csv}` files. The engine is
`sosl/sosl/quant/` (README = source map, `algorithm.md` = why it is
correct); its gates are `sosl/tests/quant/`, listed in that README.

**Open.** F-M5 awaits a theory verdict (below). M6 — the census campaign
E1–E4, spec §12 — is the next milestone; it fills the paper's ⟨TBD⟩ slots
and must check the two predictions registered below.

## Slot map (paper ⟨TBD⟩ → expected finding)

| paper slot | experiment | finding |
|---|---|---|
| Abstract headline number | E1 | ⟨F1⟩ |
| §4.3 pipeline demo | E4 | ⟨F4⟩ |
| §5 entropy-per-degree | E2 | ⟨F2⟩ |
| §6 (i) measure/θ-profile distributions | E1 | ⟨F1⟩ |
| §6 (ii) measure-0/1 concentration in safety rungs | E1 | ⟨F1b⟩ |
| §6 (iii) entropy distribution | E2 | ⟨F2⟩ |
| §6 (iv) distance geometry, nearest-LTL-neighbor | E3 | ⟨F3⟩ |
| §6 (v) pipeline + baseline | E4 | ⟨F4⟩ |

## Cross-gate laws M6 must check (falsifiable; assert them, don't assume them)

Both are laws between columns of the *same* run, so they hold on whatever
corpus snapshot M6 actually walks and cost nothing extra to assert — E1–E3
compute both sides anyway. No count is fixed here on purpose: the corpus is
regenerated concurrently, and a hard-coded total would only produce a false
red (or a chased edit) on the next snapshot.

**Trivial essential ⟺ `μ ∈ {0, 1}`.** If `μ(L) = 1` the complement is null
in every cylinder, so every residual measure is `1`, the residual series is
constant, and `M_x` is trivial (dually for `μ = 0`); conversely a trivial
quotient forces `ess(L) ∈ {∅, Σ^ω}`. So the E1 count of `μ ∈ {0, 1}` must
equal the E3 count of `n = 2` essential forms, row for row — and, the corpus
being complement-closed and complement sending `x` to `1 − x` pointwise (so
`≈`, its aperiodicity and its triviality are complement-invariant), that
count must split evenly between `μ = 0` and `μ = 1` up to self-complementary
entries. A mismatch convicts M1 or M3.

**`μ > 0` ⟹ `ρ = |Σ|`, exactly (uniform `p`).** For uniform `p`,
`μ(L) ≤ |pref_n(L)|/|Σ|^n` for every `n`, so `μ_p(L) > 0` forces
`h(L) = log₂|Σ|` — and in the engine this is exact, not asymptotic:
`ρ = |Σ|` requires an irreducible live block whose every row sums to `|Σ|`
(for an irreducible nonnegative matrix `ρ` reaches the max row sum only when
all row sums are equal), on which the `v₀ = 1` bracket is `[|Σ|, |Σ|]` at
iteration 0, width 0. So the E1×E2 join must contain **no row with `μ > 0`
and `ρ < |Σ|`**, and every row with `h < log₂|Σ|` must report `μ = 0`. A
violation convicts M1 or M4. The converse is *not* claimed: a `μ = 0`
language may still have maximal entropy ("finitely many `b`" has
`pref = Σ*`).

## Open findings

**F-M5 (2026-07-12, git 115e8a7cf) — the Markov product lands; the
Bernoulli embedding reconciles it with M1 corpus-wide.** Theorem 3.5
implemented as the M5 work order states it (frozen in
`sos_measure_experiments.md` §11): `mc.py` (state-labelled `Chain`, the
strict `.mc` reader/writer) and `product.py` (the chain × class product
from `(q₀, λ(ℓ(q₀)))`, its bottom SCCs, the cycle semigroup at the base
state, that semigroup's kernel, `θ_B = Val(c, k)`, and M1's transient
solver). Everything exact `Fraction`; `PARANOID` (shared with `theta`)
re-derives every `θ_B` from a second base state and a second kernel
idempotent and stayed silent throughout.

*Fixtures (exact, hand-computed).* **F-M green and discriminating**:
`Pr(a·Σ^ω) = 1` — the dropped-first-letter reading would give `1/3`, so
the word convention is now pinned by a test, not by a comment. F-N
green (`Pr((ab)^ω) = 1`, `Pr((ba)^ω) = 0`) on the 6-class alternating
monoid, and it is the fixture where the second-base-state paranoid check
bites: its single product bottom SCC spans both chain states, and the
two base states carry different cycle semigroups (`{ba}` vs `{ab}`) yet
the same verdict. F-O green (`1/3` / `2/3`), two bottom SCCs through the
linear system.

*Gates (`reference/quant/m5_product.{md,csv}` + `m5_product_oracle.csv`).*
All four green, 0 red, 0 missing, 0 budget kills, 0 skips.

| gate | scope | result |
|---|---|---|
| Bernoulli embedding `Σ_a p(a)·Pr_{M_a}(L) = μ_p(L)` | all 6222, both `p`'s, chain restarted at each of the `|Σ|` letter states | 6222/6222 byte-exact against M1 |
| complement flip `Pr_M(L) + Pr_M(L̄) = 1` | all 6222, one seeded random chain each | 6222/6222 exact |
| `.mc` reader round-trip | every chain of every gate and fixture | identical |
| Route A product-side oracle | seeded sample of 250, paired `det/*.hoa` × the same chain | 250/250 byte-equal, **0 Spot skips** |

Cost is a non-issue: median product 17 states (max 178), median 4 ms per
case (max 1198 ms) against the 15 s budget — the reachable product stays
far below the `|M|·n` bound.

*Finding against the ratified format — PRISM will not parse our label
names.* P-M5 §Syntax says label names are the alphabet's letters
*verbatim* and that the same file loads unmodified in PRISM and Storm.
Those two clauses are incompatible: our letters render as Boolean cubes
(`a`, `!a`, `a&!b`), and PRISM 4.10.1 rejects a cube inside the label
quotes — `label "a&!b" = s=0;` gives `Error: Syntax error ("&", line 9,
column 9)`. The label name must be a plain identifier. **This changes no
number in this finding** (nothing in M5 runs PRISM; the four gates are
in-engine), and it leaves the *semantic* half of P-M5 intact — the word
convention, which is the clause that actually decides the answer. Agreed
remedy (user, this session): keep `.mc` as specified, and give the E4
bench a printer that sanitizes the names PRISM refuses; the rendering
lives in one function (`mc._render`/`parse_mc`'s label check), so the
change is local and re-emits. Theory should read P-M5's "same file,
unmodified" as "same file up to label-name sanitization".

*Two notes on the M5 work order's algorithm.* (i) The cycle semigroup needs no fixpoint
iteration: the BFS over `(M-state, class)` pairs from `(q̂, [ε])` ranges
over *all* walks returning to `q̂`, so the classes it collects are
already closed under product (a concatenation of cycles at `q̂` is a
cycle at `q̂`). The code asserts the closure rather than iterating to it.
(ii) `routea`'s HOA read-off was factored into `_read_det` (letterwise
successors *and* per-edge marks) so the product-side oracle can evaluate
Emerson–Lei on the product BSCC's *edges*; M2's `route_a` was spot-checked
unchanged on rerun.

*Verdict requested.* M5 is DONE against its work order; M6 (the census
campaign, spec §12) is the next milestone, on the user's go.
