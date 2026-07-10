# SoS Quantitative (Measure / Distance / Entropy) — Implementation Specification

**Status (2026-07-11).**

| item | state |
|---|---|
| **M1: θ-profile + measure + fixture/flip gate (§1–§6)** | **OPEN — the current work order; do this first, alone, end to end** |
| M2 = QNT2: Route A oracle + full metamorphic harness (§8) | LATER — needs M1 |
| M3 = QNT1c: distance on aligned tables (§9) | LATER — needs M1 |
| M4 = QNT3: entropy (§10) | LATER — independent of M2/M3 |
| M5 = QNT4: the Markov product `Pr_M(L)` (§11) | LATER — needs M1+M2 |
| M6 = QNT5: census campaign + pipeline demo (§12) | LAST |
| MDPs, semiring-valued `Val`, Hausdorff dimension, performance work | **NON-GOALS** (§13) |

An implementer starting cold for M1 reads: §0–§6 of this file, nothing
else, then works the order of §2. Do not read `docs/HISTORY.md`. Do not
start M2–M6.

**Normative math.** `research_notes/sos_measure.md` (the paper):
Lemmas 3.1–3.3, Theorem 3.4, and the §4.1 algorithm are what M1
implements. Where this spec and the paper disagree, the paper wins and
the disagreement is a bug to report in `sos_measure_report.md`.

## 0. Ground rules (read first, they are all mandatory)

- **Package**: new code goes in `sosl/sosl/sos/quant/` (create it, with
  `__init__.py`). Test scripts go in `sosl/tests/quant/`. Logs go in
  `sosl/tests/quant/logs/` (create; never `/tmp`).
- **Layering (hard)**: `sosl.sos.quant` imports `sosl.sos` and
  `sosl.sos.calculus` and NOTHING else in the repo — never `sosl.learn`,
  `sosl.teacher`, `sosl.experiment`, `tests.*`. Do not modify any
  existing file outside `sosl/sosl/sos/quant/` and `sosl/tests/quant/`.
- **Reuse, don't re-derive.** The invariant object, its `.sos` reader,
  `fold`, `idem`, `Val`, the linked-pair enumeration, and the complement
  surgery all exist. Find them under `sosl/sosl/sos/` (`invariant.py`,
  `io/`, `calculus/table.py`, `calculus/surgery.py`) — grep for `idem`,
  `Val`, `complement`, `linked`. If a right-Cayley SCC pass already
  exists (the obligation read-off uses one — grep `scc` under
  `calculus/`), reuse it; only if absent, implement Tarjan locally in
  `quant/`.
- **Numbers are `fractions.Fraction`, end to end.** No `float` anywhere
  in M1. No numpy. No Spot. No subprocess.
- **Type every signature** (params + return), `from __future__ import
  annotations` allowed; follow the typing style of the calculus package.
- **Tests are placed scripts** run as `python3 -m tests.quant.<name>`
  from `sosl/`, one input per invocation where a corpus is walked
  (argv = one `.sos` path), ≤15s per case; a blown budget is a finding
  to report, not something to code around.
- **Files stay under ~500 LOC.** Split by the module layout of §2.
- Every public function gets a context-free docstring: what the
  function computes on its own inputs — not who calls it, not the
  campaign it serves.

## 1. M1 scope — one sentence

From a held invariant `𝓘 = (𝒞, λ, M, P)`: compute the **θ-profile**
(one canonical bit per bottom SCC of the right-Cayley graph) and the
**measure** `μ_p(L)` as an exact `Fraction`, certificate included;
prove it on three hand-computed fixtures and one corpus-wide exact law.
Nothing else — no distance, no entropy, no Markov chains, no Spot
oracle, no census columns.

## 2. M1 work order (do the steps in this order)

1. `quant/chain.py` — bottom SCCs of the right-Cayley graph (§3.1).
2. `quant/kernel.py` — one kernel idempotent of `S` (§3.2).
3. `quant/theta.py` — the θ-profile (§3.3).
4. `quant/measure.py` — the linear system and `measure()` (§3.4).
5. `tests/quant/fixtures.py` — the three fixtures of §4, exact
   expected values, plus the in-engine paranoid checks of §5.
6. `tests/quant/flip_gate.py` — the corpus-wide flip law (§6).
7. One machine report `reference/quant/m1_measure.{md,csv}` and one
   finding row appended to `research_notes/sos_measure_report.md`
   (regeneration command included). Stop; hand back.

## 3. M1 algorithms (explicit)

Notation: classes are whatever id type the invariant uses; `[ε]` is the
adjoined identity (the io layer knows it); `S = 𝒞 \ {[ε]}` as a vertex
set (every non-identity class is the fold of some nonempty word, and no
nonempty word folds to `[ε]` — assert this by checking `λ(a) ≠ [ε]` for
all `a`).

### 3.1 `chain.py`

```python
def right_cayley_edges(inv: Inv) -> dict[C, list[C]]      # c -> [M(c, λ(a)) for a in Σ]
def bottom_sccs(inv: Inv) -> list[frozenset[C]]
```

SCCs of the graph on ALL of `𝒞` (including `[ε]`); a bottom SCC is one
with no edge leaving it. Return them sorted by their least class key
(shortlex on `key(c)` — the invariant carries the keys; this fixed
order is what makes the θ-profile canonical). Assert: `[ε]` is in no
bottom SCC (its SCC is the singleton `{[ε]}` with no return edge);
at least one bottom SCC exists.

### 3.2 `kernel.py`

```python
def kernel_idempotent(inv: Inv) -> C
```

Build the two-sided Cayley graph on `S` only: edges `c → M(λ(a), c)`
AND `c → M(c, λ(a))` for every `a ∈ Σ`. Compute its SCCs; keep the
*sink* SCCs (no edge leaving). **Assert exactly one sink** — it is the
kernel `K` (unique minimal two-sided ideal); two sinks mean a corrupted
table: raise, do not continue. Take `t` = the least-keyed element of
`K`, return `k := idem(t)` (reuse the existing `idem`). Assert
`M(k, k) = k` and `k ∈ K`.

### 3.3 `theta.py`

```python
@dataclass(frozen=True)
class ThetaProfile:
    entries: tuple[tuple[str, bool], ...]   # (least class key of the SCC, θ) in §3.1 order

def theta_profile(inv: Inv) -> ThetaProfile
```

For each bottom SCC `C`: pick its least-keyed class `c`, compute
`θ_C := Val(c, k)` with `k` from §3.2 — reuse the existing `Val`
(`Val(c, k) = ((M(c, k), k) ∈ P)`; `k` is idempotent so `idem(k) = k`).
One lookup per component.

### 3.4 `measure.py`

```python
@dataclass(frozen=True)
class MeasureResult:
    value: Fraction
    profile: ThetaProfile
    absorption: tuple[tuple[str, Fraction], ...]  # per bottom SCC, §3.1 order

def uniform(inv: Inv) -> dict[Letter, Fraction]
def measure(inv: Inv, p: dict[Letter, Fraction] | None = None) -> MeasureResult
```

Validate `p` (every letter present, every value `> 0`, sum `== 1` —
exact Fraction comparisons); default `uniform`. Let `theta[C]` be the
§3.3 bits. Let `transient` = classes in no bottom SCC. Unknowns `x_c`
for `c ∈ transient`; for each transient `c`, the equation

```
x_c  =  Σ_{a ∈ Σ} p(a) · rhs(M(c, λ(a)))
rhs(c') = x_{c'}            if c' transient
        = θ_{C(c')}         if c' lies in bottom SCC C(c')
```

i.e. move the unknown terms left, the constant terms right, and solve
the `|transient| × |transient|` system by plain Gaussian elimination
over `Fraction` (write it by hand, ~40 lines; no library). The matrix
is nonsingular — from every transient class a bottom SCC is reachable —
so a zero pivot after full row-search is an assertion failure, not a
case to handle. `value = x_[ε]`. Also compute, for the certificate,
the absorption probability of each bottom SCC (same system with
boundary 1 on that SCC, 0 on the others — or solve once with vector
right-hand sides, implementer's choice; assert the absorptions sum to
1 exactly).

Complement note (needed by §6): `measure` must accept an invariant
whose `P` was flipped by the existing calculus complement surgery
WITHOUT any reduce — nothing in §3.1–§3.4 assumes the table is
syntactic-minimal. Do not call `reduce` anywhere in M1.

## 4. M1 fixtures (hand-checked ground truth; exact equality required)

Build these three invariants in-test (construct the object directly, or
write three tiny `.sos` files under `tests/quant/`; whichever the io
layer makes easier). Alphabet `Σ = {a, b}` in all three. Classes are
named by their shortlex key.

**F-A: L = "infinitely many a's".** Classes `[ε]`, `A` (key `a`:
words containing an `a`), `B` (key `b`: nonempty all-`b` words).
`λ(a) = A`, `λ(b) = B`. Table: `A·A = A·B = B·A = A`, `B·B = B`
(identity rows/columns for `[ε]`). `P = {(A, A)}`.
Expected: bottom SCCs = `[{A}]`; kernel `K = {A}`, `k = A`;
θ-profile `[("a", 1)]`; `μ = 1` — for uniform `p` AND for
`p(a) = 1/3` (exactly `Fraction(1)`).

**F-B: L = "finitely many a's".** Same table; `P = {(A, B), (B, B)}`
(the complement's accepting linked pairs). Expected: θ-profile
`[("a", 0)]`; `μ = 0` under both `p`'s. (Also obtainable from F-A by
the complement surgery — assert both routes give byte-equal results.)

**F-C: L = a·Σ^ω ("first letter a").** Classes `[ε]`, `A` (key `a`:
words starting `a`), `B` (key `b`: words starting `b`). `λ(a) = A`,
`λ(b) = B`. Table: `A·x = A`, `B·x = B` for `x ∈ {A, B}`.
`P = {(A, A), (A, B)}`. Expected: bottom SCCs = `[{A}, {B}]`; the
kernel is ALL of `S = {A, B}` (single sink SCC of the two-sided graph
— check this is what §3.2 finds), so `k ∈ {A, B}` — **assert the
θ-profile is the same for both choices** (this exercises paper
Lemma 3.3): `[("a", 1), ("b", 0)]`. `μ = 1/2` uniform;
`μ = 1/3` for `p(a) = 1/3`. Absorption: `[("a", p(a)), ("b", p(b))]`.

If any fixture disagrees with the code, the code is wrong until proven
otherwise; if you believe the fixture itself is wrong, STOP and report
in `sos_measure_report.md` — that is a finding against the paper.

## 5. M1 in-engine paranoid checks

Behind a module-level flag `PARANOID: bool = True` (leave it on in M1;
the census pass may later sample it):

- θ recomputed from a *different* class of the same bottom SCC agrees
  (paper Lemma 3.3(1)).
- θ recomputed with `k' := idem(t')` for a *different* `t'` in the
  kernel (when `|K| > 1`) agrees (paper Lemma 3.3(2)).
- `Σ_C absorption(C) = 1` exactly.
- `[ε]` transient; profile length = number of bottom SCCs.

Each failure raises with the invariant's identifying key in the
message.

## 6. M1 gate: the flip law, corpus-wide

`tests/quant/flip_gate.py`, argv = one `.sos` path from
`genaut/corpus/flat_canon/`; a driver mode `--list` may emit the file
list for a shell loop, but the measurement path handles ONE file per
invocation. For the given invariant: load, `measure` under uniform
`p`; complement via the existing calculus flip (no reduce); `measure`
again; **check `μ(L) + μ(¬L) == 1` exactly** and that the two
θ-profiles are pointwise negations. Write one CSV row per case
(`name, n, n_bottom_sccs, mu_num, mu_den, ok, ms`) under
`tests/quant/logs/`, aggregate into `reference/quant/m1_measure.{md,csv}`
with the date / git-rev / corpus header used by `reference/calculus/`
reports (copy that header shape).

**M1 is DONE when:** fixtures F-A/F-B/F-C pass exactly (both `p`'s);
the flip gate is green on the full census (any red row = stop and
report); the report files exist with the regeneration command; no
float, no Spot, no reduce, layering respected. Then hand back for
review — do not begin M2.

---

## 7. Later milestones — reference only (do NOT start these in M1)

## 8. M2 (QNT2) — Route A oracle + full metamorphic harness

Independent measure via the exit acceptor: exit `𝓘 → NBA` (existing
calculus exit), determinize through Spot (bounded-or-skipped, budget
per case; a skip is a datum, never a wait), then the classical BSCC
analysis on the deterministic automaton with the same hand-rolled
`Fraction` solver. Laws beyond the flip: modularity
`μ(L₁∪L₂) + μ(L₁∩L₂) = μ(L₁) + μ(L₂)` on aligned pairs; inclusion ⟹
`μ` monotone; trichotomy `p`-freeness under 3 random full-support
rational `p`; obligation cross-check (θ vs the stem-`R`-class verdict
of the calculus paper's Thm 3.10 on obligation-band census entries).

## 9. M3 (QNT1c) — distance

`d_p(L₁, L₂)`: align (calculus), `xor` the carried pair sets, run M1's
`measure` on the aligned table. Return `Fraction` plus the aligned
xor's θ-profile (all-zero ⟺ null disagreement — paper §4.2).
Pseudometric laws sampled: symmetry exact, triangle on sampled
triples, `d_p(L, L) = 0`.

## 10. M4 (QNT3) — entropy

Paper Prop 5.1: `A` = letter-count matrix on `Live × Live` (`Live`
from `calculus.surgery`), `h = log₂ ρ(A)`. Float quarantine: `ρ` via
power iteration with Collatz–Wielandt bracketing until the enclosure
is `< 1e-9` wide; report `(h_lo, h_hi)`; certificate = the `Live`
submatrix. Laws: `h(∅) = 0` convention; `h ≤ log₂|Σ|`; monotone under
inclusion on aligned pairs; `h(cl(L)) = h(L)` asserted on the
submatrices (exact structural equality), not on floats.

## 11. M5 (QNT4) — the Markov product

Paper Thm 3.5. Chain reader (`.mc` sidecar, CSV-shaped, no JSON — fix
the format with the corpus keeper first). Product chain on reachable
`states(M) × 𝒞`; bottom SCCs; per component `B`: base state `q̂` =
least occurring in `B`; cycle semigroup `T` = folds of labels of
`M`-cycles at `q̂`, computed by BFS over `(M-state, class)` pairs from
`(q̂, [ε])`, collecting the class at each return to `q̂`, iterated to a
fixpoint; kernel of `T` by the two-sided sink routine of §3.2
parameterized by generator set; `θ_B := Val(c, k)` for the least
`(q̂, c) ∈ B`; linear system over the product. Cross-checks: a
one-state `M` emitting all letters reproduces M1 exactly; `θ_B` from a
different base state agrees; Route A product-side on small chains.

## 12. M6 (QNT5) — the census campaign

Machine reports under `reference/quant/` (one `.md` + one `.csv` per
experiment, date / git-rev / seed / corpus header; `.cat`/CSV sidecar
columns, no JSON). E1 measure+θ-profile columns (distribution per
Wagner degree / safety band); E2 entropy column; E3 distance geometry
sampled per alphabet slice (diameter, clustering, nearest-LTL-neighbor
per non-LTL language); E4 pipeline demo (one spec, a family of chains,
baseline = Route A route; wall-clock + spec-side artifact stability).
Per-case budget 15s; blown budget is a datum. Every number destined
for the paper lands first as a finding row in `sos_measure_report.md`
with its regeneration command.

## 13. Non-goals

- **MDPs / schedulers**: refused (branching wall, paper §4.3).
- **Semiring-valued `Val`**: future work, paper §7 last paragraph.
- **Hausdorff dimension**: not until entropy has landed.
- **Performance work of any kind**: census sizes are small; exactness
  and replayability outrank speed everywhere.
