# SoS Quantitative (Measure / Distance / Entropy) — Implementation Specification

**Status (2026-07-11).**

| item | state |
|---|---|
| **M1: θ-profile + measure + fixture/flip gate (§1–§6)** | **DONE (2026-07-11)** — `sosl/sosl/quant/` (placement provisional), fixtures exact, flip gate 4248/4248 green, `reference/quant/m1_measure.{md,csv}`, finding F-M1 |
| M2 = QNT2: Route A oracle + metamorphic harness (§8) | **OPEN — the current work order; §8 is self-contained** |
| M3 = QNT1c: distance on aligned tables (§9) | LATER — needs M1 |
| M4 = QNT3: entropy (§10) | LATER — independent of M2/M3 |
| M5 = QNT4: the Markov product `Pr_M(L)` (§11) | LATER — needs M1+M2 |
| M6 = QNT5: census campaign + pipeline demo (§12) | LAST |
| MDPs, semiring-valued `Val`, Hausdorff dimension, performance work | **NON-GOALS** (§13) |

An implementer starting cold for M2 reads: §0 and §8 of this file, plus
the §2 module map for what M1 provides. Do not read `docs/HISTORY.md`.
Do not start M3–M6. (§1–§6 remain the normative description of the M1
engine they would be extending.)

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

## 7. Milestone sections — M5 (§11) is the work order; §8–§10 are DONE (F-M2, F-M3, F-M4+M3b, accepted); §12 reference only

## 8. M2 (QNT2) — Route A oracle + metamorphic harness

The ground rules of §0 stand (exact `Fraction`s in every verdict path,
placed scripts, one input per invocation, ≤15s per case, ~500 LOC
files, context-free docstrings, layering), with one relaxation: **Spot
is allowed in M2 for parsing and acceptance read-out only** — never for
construction, always bounded-or-skipped; a skip is a datum, never a
wait. New code continues in the M1 package (`quant/`), new tests in
`tests/quant/`.

### 8.1 Scope — one sentence

An independent measure oracle on each census language's paired
deterministic automaton, plus four exact laws that test θ where the
flip law is blind (see the F-M1 theory reply in
`sos_measure_report.md`), corpus-wide.

### 8.2 Work order

1. `quant/routea.py` — the oracle (§8.3).
2. `tests/quant/oracle_gate.py` — law L1, one corpus `.sos` per
   invocation (its `det/` mate found by basename).
3. `tests/quant/law_gate.py` — laws L2–L4 on sampled aligned pairs
   (argv = two `.sos` paths), law L5 on obligation-band rows (argv =
   one `.sos` path).
4. Machine report `reference/quant/m2_oracle.{md,csv}` (date / git-rev
   / seed / corpus header) and finding row(s) in
   `sos_measure_report.md`, regeneration commands included. Stop; hand
   back.

### 8.3 Route A (the oracle)

Substrate: the corpus pairs every `sos/X.sos` with `det/X.hoa` — a
deterministic, **complete** automaton with Emerson–Lei acceptance on
transitions, same basename ⟺ same language. On it, under a
full-support rational `p` on the letter masks:

- The automaton states are the chain states; `δ(q, a)` is unique, so
  the transition probability `q → q'` is the exact `Fraction`
  `Σ { p(a) : δ(q, a) = q' }`.
- Bottom SCCs of that chain (the BSCCs), same pass shape as §3.1.
- A run absorbed in a BSCC `B` a.s. traverses **every** edge of `B`
  infinitely often (finite irreducible chain, every edge positive), so
  the run accepts iff the EL condition evaluates true on the mark set
  of `B`'s edges: `Inf(m)` ⟺ `m` occurs on some `B`-edge, `Fin(m)` ⟺
  it occurs on none. One evaluation per BSCC (Spot exposes the parsed
  acceptance condition; evaluate it on the mark set, e.g.
  `acc.accepting(marks)`).
- The §3.4 transient system with these BSCC bits as boundary;
  `μ_A = x_{init}`. Reuse the M1 solver — do not write a second one.

Spot's role ends at parsing the HOA and exposing the acceptance
formula. A parse failure or blown budget is a recorded skip.
Assert the HOA's AP set matches the invariant's alphabet.

### 8.4 The laws

- **L1 — oracle agreement (corpus-wide):** `measure(𝓘(X)).value ==
  μ_A(det/X.hoa)` exactly, under uniform `p` AND one fixed skewed `p`
  (`p(a) ∝ 1 + rank(a)`, normalized; rank = letter mask value). Per
  file, both `p`'s in one invocation.
- **L2 — modularity (sampled aligned pairs):** on one aligned table,
  `μ(P₁|P₂) + μ(P₁&P₂) == μ(P₁) + μ(P₂)` exactly (free surgeries `|`
  and `&`; `measure` runs on the aligned, non-reduced table — M1
  supports this by construction).
- **L3 — monotonicity (same aligned pairs):** if the calculus
  `included` says `L₁ ⊆ L₂` then `μ(L₁) ≤ μ(L₂)`.
- **L4 — trichotomy `p`-freeness:** 3 random full-support rational
  `p` per file, fixed seed recorded in the report header: the
  0 / interior / 1 trichotomy of `μ_p` equals the profile read-off
  (all-0 / mixed / all-1) for every `p`.
- **L5 — obligation cross-check:** on census rows whose `.cat` sidecar
  lies in the obligation band: for every bottom SCC `C`, `θ_C` equals
  the constant stem verdict of `C`'s linked stems (the calculus
  paper's Thm 3.10, made numerical) — an independent θ check that
  needs no automaton at all.

Sampling for L2/L3: the first-1000-uniform-pairs precedent of
`reference/calculus/v1_*`; one pair per invocation.

### 8.5 M2 is DONE when

L1 is green (or skipped-with-datum, skip rate reported) on the full
census under both `p`'s; L2–L5 green on their samples; the report
files exist with regeneration commands; any red row = stop and report.
Then hand back — do not begin M3/M4.

Fixture additions (F-D, F-E) — promote the paper's two worked examples,
hand-verified there: **F-D** = "some `a` at infinitely many even
positions" (paper §3.4 example: 8 non-identity classes `(p, E)`,
kernel `≅ ℤ/2`, `k = fold(aa)`, `μ = 1` for every full-support `p`;
also assert the *negative control*: for the non-kernel idempotent
`e' = fold(ba)`, `Val(fold(b), e') = 1 ≠ 0 = Val(fold(bb), e')` — the
engine must NOT use non-kernel idempotents). **F-E** = "`b` occurs and
the first `b` is at an even position" (paper §4.1 example: 5 classes,
kernel spans two bottom SCCs, `μ = p_b/(1−p_a²)`: exactly
`Fraction(2, 3)` at uniform, `Fraction(3, 4)` at `p_a = 1/3`).

## 9. M3 (QNT1c) — distance + the measure shadow

`d_p(L₁, L₂)`: align (calculus), `xor` the carried pair sets, run M1's
`measure` on the aligned table. Return `Fraction` plus the aligned
xor's θ-profile (all-zero ⟺ null disagreement — paper §4.2).
Pseudometric laws sampled: symmetry exact, triangle on sampled
triples, `d_p(L, L) = 0`.

**Shadow surgery** (paper Prop 4.1): `shadow(inv) -> Inv` replaces the
pair set by `P_sh := {(s, e) ∈ linked : s ∈ D}`, `D` = union of the
θ=1 bottom SCCs (M1 already computes both ingredients), then `reduce`.
Laws, all exact:

- `d_p(L, shadow(L)) = 0` (aligned xor-profile all-zero), on fixtures
  and corpus samples;
- idempotence: `shadow(shadow(L))` byte-equal `shadow(L)`;
- `p`-freeness: shadow bytes identical under 3 random full-support `p`
  (trivially true — the construction never reads `p`; assert anyway);
- **F-F (positive)**: `shadow` of F-A ("infinitely many `a`'s") is
  byte-equal to the reduced invariant of `Σ*·a·Σ^ω` ("some `a`
  occurs") — build the latter as a fixture (three classes: `[ε]`;
  absorbing `T = fold(a)`; `B = fold(b)`; `P = {(T, T), (T, B)}`);
- **F-G (negative control, do NOT "fix" it)**: over `{a, b}`,
  `L = Σ*·b·Σ^ω` vs `Σ^ω`: their `d_p` is `0` (aligned xor-profile
  all-zero — the difference is `{a^ω}`) YET their reduced shadows are
  byte-DIFFERENT (`shadow(L) = L`, `shadow(Σ^ω) = Σ^ω`). Shadow
  equality is sufficient for `d_p = 0`, not necessary (paper §4.2
  warning); an implementation that makes F-G "pass" by equating the
  shadows is wrong.

**Essential form** (paper Thm 4.4): `essential(inv, p=uniform) -> Inv`
and `ltl_up_to_null(inv, p=uniform) -> bool`. Algorithm: solve for the
full vector `x` (M1 solver; extend by `θ_C` on bottom classes);
compute the congruence `≈` on `𝒞` by direct pair testing —
`c ≈ c'` iff `x(M(w, M(c, z))) == x(M(w, M(c', z)))` for ALL
`w, z ∈ 𝒞` including the identity (`O(n⁴)` exact Fraction
comparisons; census sizes make this nothing); build the quotient
table and letter map; bottom SCCs of the quotient; **assert** `x̄` is
constant `0` or `1` on each quotient-bottom SCC (paper Thm 4.4(2) —
a violation is a stop-the-line finding); `D̄` = the value-1 ones; pair
set `{(s̄, ē) linked : s̄ ∈ D̄}`; reduce. `ltl_up_to_null` =
aperiodicity of the quotient monoid (reuse the calculus aperiodicity
scan — grep `aperiodic` under `calculus/`/`classify/`). Laws and
fixtures:

- `d_p(L, essential(L)) = 0` and `essential(essential(L))` byte-equal
  `essential(L)`, fixtures + corpus samples;
- **measure-independence (paper Prop 4.5, executable)**:
  `essential(inv, uniform)` byte-equal `essential(inv, p_a = 1/3)` on
  fixtures and corpus samples — the `p` parameter provably does not
  matter; a byte difference here is a stop-the-line finding against
  Prop 4.5, not something to normalize away;
- **F-H (the repair)**: `essential(Σ*·b·Σ^ω)` and `essential(Σ^ω)`
  are byte-EQUAL (both `= Σ^ω`'s invariant) — exactly where F-G's
  shadows differ;
- **F-I**: on F-E ("first `b` at even position"): `≈` merges `[ε]`
  with the neutral class `A₀` and nothing else, the quotient retains
  `{1̄, A₁} ≅ ℤ/2`, `essential(F-E)` is byte-equal to (reduced) F-E
  itself, and `ltl_up_to_null(F-E) = False`;
- `ltl_up_to_null(F-A) = True` (already aperiodic);
- consistency: shadow bytes equal ⟹ essential bytes equal, sampled.

### 9.1 M3b — addendum required by the F-M3 theory reply (runs with the M4 pass)

The pair gate above asserted the consistency law one-way; Thm 4.4(2)
is a biconditional and must be gated as one. On the SAME 1000-pair
sample (same seeds as `m3_laws.md`), assert **byte-equal reduced
essentials ⟺ all-zero aligned xor-profile**, both directions — both
sides are already computed per pair, this is assertion-only. Expected
outcome: equality on the 159 null-disagreement pairs whose shadows
differ, inequality on every positive-distance pair (~680). A violation
in either direction convicts Thm 4.4(2): stop the line, file against
the paper. Append the tally as a row to the `m3_laws.md` report (or a
small `m3b` companion) with the usual header.

## 10. M4 (QNT3) — entropy

Paper Prop 5.1: `h(L) = log₂ ρ(A)` with `A` the letter-count matrix
on `Live × Live` (`A[c][c'] = |{a : c·λ(a) = c'}|`; `Live` from the
calculus liveness scan — grep `live` under `calculus/`/`surgery`).
The only float-bearing milestone; the float is quarantined to the
final `log₂`.

**Do NOT run one Collatz–Wielandt loop on the whole matrix.** `A` is
reducible whenever some live class is transient among live classes —
the common case — and on a reducible matrix the CW bracket never
tightens (on `diag(2, 1)` every positive `v` gives min-ratio 1,
max-ratio 2, forever): the flat loop spins to the budget kill. Use
the block decomposition the paper's proof cites [LM95 §4.4]:
`ρ(A) = max ρ(A_B)` over irreducible diagonal blocks `B`.

Algorithm (`quant/entropy.py`):

1. `Live = ∅` (iff `L = ∅`): return `h = 0` exactly (paper §5
   convention), enclosure width 0.
2. SCC-condense the Live subgraph (edges `c → c·λ(a)` inside `Live`;
   reuse the SCC routine already in `chain`/`kernel`). Per SCC `B`:
   - singleton, no self-loop: `ρ_B = 0`, skip;
   - singleton `c` with self-loops: `ρ_B = A[c][c]` exactly, width 0;
   - nontrivial: set `B' := I + A_B`. `B'` is primitive (irreducible
     + positive diagonal) and `ρ(A_B) = ρ(B') − 1` (nonnegative
     shift). Power-iterate over `Fraction`: `v = (1, …, 1)`; each step
     `w = B'·v`, bracket `lo = min_j w_j/v_j`, `hi = max_j w_j/v_j`
     (CW: `ρ(B') ∈ [lo, hi]` for EVERY positive `v` — soundness never
     depends on convergence; primitivity contracts the bracket
     geometrically); renormalize `v = w / max(w)`. To cap `Fraction`
     bit growth, keep `v` in fixed point over the COMMON denominator
     `10**40` (round each entry to that grid, kept strictly positive;
     per-entry `limit_denominator` is a trap — the entries' lcm blows
     up inside the exact `B'·v`) — rounding `v` only slows
     convergence, never unsounds the bracket (CW holds for every
     positive `v`, whatever its provenance). Stop
     when `hi − lo < Fraction(1, 10**9)` or at 10 000 iterations; a
     non-converged bracket is still a valid enclosure, reported as a
     datum (like a budget kill).
3. `ρ(A) ∈ [max_B lo_B, max_B hi_B]`, exact `Fraction`s.
4. `h_lo, h_hi := log₂` of the two bounds, widened one
   `math.nextafter` ulp outward each side — the ONLY float step.
   Return `(h_lo, h_hi)` + certificate: the `Live` set, the block
   list, each block's exact rational bracket (replayable, no floats).

Fixtures (`tests/quant/fixtures3`; assertions exact, no floats):

- **F-J**: `Σ^ω`, `|Σ| = 2` → assert `ρ_lo = ρ_hi = 2` exactly,
  `h = 1`.
- **F-K**: `L = a^ω` over `{a, b}` → every live class has exactly one
  live successor; assert `ρ = 1` exactly, `h = 0`.
- **F-L (golden mean — the irrational case, certified rationally)**:
  `L =` "no factor `bb`" over `{a, b}` (a safety language; hand-build
  the invariant as in `fixtures2`; every nontrivial live block is
  `[[1,1],[1,0]]`-shaped). `ρ = φ = (1+√5)/2`: assert IN FRACTIONS
  the sign test on `ρ² = ρ + 1` — `lo² ≤ lo + 1` and
  `hi² ≥ hi + 1` — plus `hi − lo < 1e-9`; the enclosure provably
  straddles `φ` with no float in the check.

Laws (gate `m4_gate`, ≤ 15 s per case, machine report
`m4_entropy.{md,csv}` under `reference/quant/`, usual header):

- `L = ∅ ⟹ h = 0`; `L ≠ ∅ ⟹ ρ_lo ≥ 1` (every live class has a live
  successor, so the live subgraph has a cycle; a violation convicts
  the liveness scan — stop the line);
- `ρ_hi ≤ |Σ|` exactly (hence `h ≤ log₂|Σ|`; with `v₀ = 1` the
  first `hi` is already a row-sum bound, so this must hold from
  iteration 0);
- monotonicity on sampled aligned pairs carrying a real inclusion
  (reuse M2's L3 inclusion detection): `L₁ ⊆ L₂` ⟹ the
  enclosure-safe reading `ρ_lo(L₁) ≤ ρ_hi(L₂)`;
- `h(cl(L)) = h(L)` structurally: `cl` via the calculus safety-hull
  surgery on the same table; assert `Live(cl(L)) = Live(L)` as sets
  and the letter-count submatrices identical — never on floats;
- M3b (§9.1) runs in the same pass.

DONE when: F-J/F-K/F-L green; corpus gate green (0 red; budget kills
and non-converged brackets are data rows); M3b green; machine report
filed; finding F-M4 in the report.

## 11. M5 (QNT4) — the Markov product

Paper Thm 3.5. Scope, one sentence: compute `Pr_M(L)` exactly for a
state-labelled chain `M`, the spec side held as the invariant, with a
`.mc` reader in the ratified P-M5 format (report, 2026-07-11).

### 11.1 The `.mc` format (P-M5, ratified — the reader rejects, never repairs)

A restricted PRISM-language subset, state-labelled (Moore), the same
file loadable unmodified by PRISM and Storm:

- one `dtmc` model, one module, one state variable
  `s : [0..N-1] init i;` — a single initial state;
- exactly one guarded command per state:
  `[] s=k -> 1/3:(s'=k1) + 2/3:(s'=k2);` — probabilities are rational
  literals (`1/3`, `1`); assert each command's branches sum to exactly
  1 as `Fraction`s;
- one `label "a" = s=…|…;` per letter: label names are the letters of
  the paired language's alphabet VERBATIM (never PRISM's reserved
  `"init"`/`"deadlock"`); the letter labels must PARTITION the state
  space — every state satisfies exactly one; `ℓ(q)` = that letter;
- alphabet equality with the paired `.sos` is checked, not assumed;
- keep the parser a strict ~100-line reader of this subset, not a
  PRISM front-end (no constants, no formulas, no multiple modules).

The reader API takes an optional initial-state override (the gates
below run the same chain from several starts; no file rewriting).

### 11.2 Word semantics (ratified decision — do not drop the first letter)

`word(s₀s₁s₂…) := ℓ(s₀)·ℓ(s₁)·ℓ(s₂)…` — the initial state's label IS
the word's first letter, matching PRISM/Storm path semantics
("same file, same number"). Paper §2.3/§3.5 now state the chain model
state-labelled natively, so §11.3 is Thm 3.5 read verbatim. The
theorem allows an initial distribution `ι`; `.mc` restricts to a
Dirac (PRISM single init) — the Bernoulli-embedding gate of §11.5
reconstructs a distribution by hand, which is exactly the theorem's
`ι`-linearity.

### 11.3 Algorithm (`quant/product.py`)

1. Product on the reachable part of `states(M) × 𝒞` from
   `(q₀, λ(ℓ(q₀)))`; step `(q, c) —P(q,q')→ (q', c·λ(ℓ(q')))`.
2. Bottom SCCs of the product (reuse the Tarjan already in
   `chain`/`kernel`). Per bottom SCC `B`: base state `q̂` = least
   `M`-state occurring in `B`; cycle semigroup `T` = folds of labels
   of `M`-cycles at `q̂`, by BFS over `(M-state, class)` pairs from
   `(q̂, [ε])` collecting the class at each return to `q̂`, iterated to
   a fixpoint (cycle labels read `ℓ(q')` per step — the label of `q̂`
   itself closes the cycle, opens the next); kernel of `T` by the
   two-sided sink routine of §3.2 parameterized by generator set; `k`
   any kernel idempotent; `θ_B := Val(c, k)` for the least
   `(q̂, c) ∈ B`.
3. Absorption probabilities by one linear system over `Fraction`
   (reuse M1's solver); `Pr_M(L) = Σ_B θ_B · Pr[absorption in B]`.
4. PARANOID (in-engine, flag on): `θ_B` unchanged under a second base
   state of `B` (when one exists) and a second kernel idempotent.

### 11.4 Fixtures (`tests/quant/fixtures4`; assertions exact)

- **F-M (pins §11.2 — the discriminating fixture).** `Σ = {a, b}`;
  states `q_a, q_b`, `ℓ` as named; every state moves `1/3 : q_a`,
  `2/3 : q_b`; initial `q_a`. `L = a·Σ^ω`: assert `Pr = 1` exactly
  (the word opens with `a` deterministically; the dropped-letter
  reading would give `1/3` — a red here convicts the convention, stop
  the line). `L = b·Σ^ω`: assert `Pr = 0`.
- **F-N (deterministic, periodic).** `q_a → q_b → q_a`, both
  probability 1, initial `q_a`. `L = (ab)^ω`: `Pr = 1`;
  `L = (ba)^ω`: `Pr = 0`.
- **F-O (real absorption split).** `q₀` (`ℓ = a`) with
  `1/3 : q₁, 2/3 : q₂`; `q₁` (`ℓ = a`) and `q₂` (`ℓ = b`) absorbing
  self-loops. `L =` "finitely many `b`": `Pr = 1/3`; `L =`
  "infinitely many `b`": `Pr = 2/3`. Two bottom SCCs, exercises the
  linear system.

### 11.5 Gates (`m5_gate`, ≤ 15 s per case, report `m5_product.{md,csv}` under `reference/quant/`, usual header)

- **Bernoulli-embedding law (all census languages, both `p`'s of M3
  — uniform and skewed).** Chain `{q_a}_{a∈Σ}`, `ℓ(q_a) = a`,
  `P(q_a → q_b) = p(b)`; run once per initial state:
  `Σ_a p(a)·Pr_{M_a}(L) = μ_p(L)` byte-exact against M1. (Each
  `Pr_{M_a}(L) = μ_p(aΣ^ω ∩ L)/p(a)`; the sum telescopes to `μ_p(L)`.
  Exercises §11.2 `|Σ|` times per language.)
- **Complement flip.** On each corpus complement pair, one seeded
  random chain (exact rational probabilities, small denominators):
  `Pr_M(L) + Pr_M(L̄) = 1` exactly (`Val` flips per verdict; the
  absorption system is shared).
- **Route A product-side oracle** on a seeded sample (≥ 200
  languages): paired det DELA × the same chain, per-BSCC acceptance
  bit by M2's Emerson–Lei evaluation on the BSCC's transition set,
  same absorption linear system — assert byte-equal `Pr`. Spot only
  for what M2 already uses; bounded-or-skipped, a skip is a datum.
- **Reader round-trip.** Every gate chain is written to `.mc` text,
  re-read, asserted identical (the parser is exercised in-gate, not
  only on fixtures). PRISM/Storm same-file runs are E4 territory, not
  M5.

DONE when: F-M/F-N/F-O green; all four gates green (0 red; budget
kills and skips are data rows); machine report filed; finding F-M5 in
the report.

## 12. M6 (QNT5) — the census campaign

Machine reports under `reference/quant/` (one `.md` + one `.csv` per
experiment, date / git-rev / seed / corpus header; `.cat`/CSV sidecar
columns, no JSON). E1 measure+θ-profile columns (distribution per
Wagner degree / safety band); E2 entropy column; E3 the *exact* metric
geometry per alphabet slice — NOT sampled: (a) all μ=0 languages are
one `d_p = 0` class and all μ=1 languages another (skip their pairs
entirely); (b) among the strictly-interior languages, the exact
`d_p = 0` classes are the byte-classes of the reduced essential forms
(paper Thm 4.4) — no pairwise work; re-check a sample of merged and
separated pairs with the aligned xor-profile; (b') the frontier
column: `ltl_up_to_null` per language — report how many non-LTL
census languages are null-equivalent to LTL ones; (c) exhaustive
all-pairs `d_p`
between class representatives (the M1 census counts make this a few
`10^5` alignments at worst) — report diameter, distance distribution,
clustering by Wagner degree, nearest-LTL-neighbor per non-LTL
language; E4 pipeline demo (one spec, a family of chains,
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
