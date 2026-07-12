# SoS quantitative — frozen experiments record

**Frozen. Reference only, never worked from.** This file holds the work
orders that are closed and the theory↔engineering exchanges that closed
them. It is the detail behind milestones M1–M5 of the measure / distance /
entropy thread: what was ordered, what came back, what was ratified, and the
reasoning that settled each dispute. It is written at time of writing and is
not maintained.

Live direction lives elsewhere: the **paper** `sos_measure.md` (normative
math), the **spec** `sos_measure_spec.md` (§0 ground rules + the open
milestone), the **report** `sos_measure_report.md` (open findings and the
predictions still to be checked). The **machine artifacts** every number
below is read from are under `reference/quant/`, each carrying its own
date / git-rev / seed / corpus header and its regeneration command — they,
not this file, are the reproducibility record.

Part 1 is the closed work orders as the spec stated them. Part 2 is the
findings they produced, with the theory replies that accepted them.

---

# Part 1 — the closed work orders (M1–M5)

*As written in `sos_measure_spec.md` when each milestone was live. The §0
ground rules they all assume stay in the spec.*

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

---

# Part 2 — the closed findings, and the exchanges that settled them

*Each finding is a checked prediction of the paper; each reply is theory's
ratification of it. Numbers are dated snapshots of a corpus that is
concurrently regenerated — rerun a gate rather than trust a total here.*

**F-M1 (2026-07-11, git b5cc0062e) — θ-profile + exact measure land; the
flip law holds corpus-wide.** Engine in `sosl/sosl/quant/` (placement
provisional, to move later); Theorem 3.4 implemented as specified
(bottom SCCs → kernel idempotent → one `Val` lookup per component →
transient system over `Fraction`). The three hand fixtures F-A/F-B/F-C
pass with exact equality under uniform and `p(a)=1/3`, including the
Lemma 3.3 idempotent-independence check on F-C and the byte-equal
complement route on F-B; `PARANOID` re-derivations stayed silent
throughout. Flip gate `μ(L) + μ(¬L) == 1` (exact) with pointwise-negated
profiles: **4248/4248 green**, 0 crashes, 0 missing, no reduce anywhere.
Distribution over the census: 1737 languages with `μ = 0`, 1737 with
`μ = 1`, 774 strictly interior — the exact 0/1 tie is the corpus's
complement-closure showing through the measure, an unplanned
cross-check. Median table 15 classes (max 121); median 1 bottom SCC
(max 7); worst case 173 ms. Machine report:
`reference/quant/m1_measure.{md,csv}`; regeneration (from `sosl/`):
`python3 -m tests.quant.flip_gate --list | while read f; do timeout 15
python3 -m tests.quant.flip_gate "$f" >/dev/null; done; python3 -m
tests.quant.flip_gate --aggregate` (fixtures:
`python3 -m tests.quant.fixtures`). No disagreement between spec and
paper surfaced.

**Theory reply to F-M1 (2026-07-11) — ACCEPTED, with one scope caveat
and one spec bug.**

*Ratification.* The implementation is §4.1 as stated: the two-sided
sink is the `J`-minimum, hence the kernel [PP04]; `k = idem(t)` for the
least-keyed `t ∈ K` uses the closure of `K` under powers; reading
`θ_C = Val(c, k)` at the least-keyed `c ∈ C` exercises exactly the two
freedoms Lemma 3.3 grants (choice of representative, choice of kernel
idempotent), and the `PARANOID` re-derivations are numerical replays of
Lemma 3.3(1)/(2) — silent on all 4248 languages and on the F-C fixture
where `K = S` makes the idempotent choice maximal. The absorption
certificate summing to exactly 1 on every case discharges the
"classical finite-chain facts" step of Theorem 3.4's proof at the level
of the solver.

*Scope caveat — the flip gate is θ-blind.* `μ(L) + μ(¬L) = 1` with
pointwise-negated profiles holds for ANY lookup rule that reads a fixed
linked cell per bottom SCC, right or wrong: the `P`-flip negates every
cell's membership, and the absorption vector depends only on the
semiautomaton. F-M1 therefore certifies the transient solver, the
profile/complement plumbing, and engine totality on the census — but
the *ground truth of θ* rests, so far, on the three hand fixtures
alone. This is precisely M2's burden; until the independent oracle and
the obligation cross-check are green, Theorem 3.4 is corroborated, not
corpus-tested. (Corollary of the same observation: the 1737/1737 tie
of `μ=0`/`μ=1` counts is the corpus's complement-closure seen through
the flip law — a pairing check, not θ evidence.)

*Spec bug (reported per §0's own rule).* §8 grounded Route A on an
"existing calculus exit" `𝓘 → NBA`. No such exit exists — NBA exits are
a standing calculus non-goal. Route A is re-based on the corpus's
paired `det/*.hoa` (deterministic, complete, Emerson–Lei, same
basename ⟺ same language): under any full-support Bernoulli `p` the
run of a deterministic complete automaton is a finite Markov chain,
a.s. absorbed in a BSCC whose every edge then recurs infinitely often,
so acceptance of a BSCC is the EL condition evaluated on its edge-mark
set, and `μ` is the same transient system M1 already solves — exact,
Spot for parsing only. §8 has been rewritten into the M2 work order
accordingly.

*Verdict.* M1 accepted; M2 unblocked and specified.

**F-M2 (2026-07-11, git 142b0bbfd) — the oracle and the laws are green;
θ is now corpus-tested.** Route A (`quant/routea.py`: BSCC × EL
analysis of the paired `det/*.hoa`, Spot parse-only, M1's solver)
agrees with `measure` **exactly on 4248/4248** census entries under
BOTH `p`'s (uniform and `p(a) ∝ 1+a`), zero skips — law L1. Laws L2/L3
(modularity + monotonicity on materialized aligned products): **994/1000**
sampled pairs green, 0 red, 6 budget-blown at the 15s cap (big aligned
products, the V1a ratio tail; a datum), 130 pairs carrying a real
inclusion, and on every pair the `included` decision coincided with
pair-set order on the shared table. Law L4 (trichotomy `p`-freeness, 3
seeded random rational `p` per file) and L5 (θ = the constant stem
verdict on every bottom SCC of every obligation-band row, 3182 rows):
**6220/6220 green** — the corpus grew 4248 → 6220 mid-campaign
(concurrent regeneration); the case laws cover the grown census, L1's
4248 is its dated snapshot. Machine reports:
`reference/quant/m2_oracle.{md,csv}`,
`reference/quant/m2_laws.md` (+ `m2_laws_pairs.csv`,
`m2_laws_cases.csv`), regeneration commands in their headers.

**Theory reply to F-M2 (2026-07-11) — ACCEPTED; the F-M1 caveat is
discharged twice over.** The θ-blindness caveat on the flip gate is
closed by two *independent* convictions: L1 tests every θ bit against
an automaton-side computation that shares only the linear solver with
the invariant side (different object, different absorption structure —
invariant classes vs automaton states — agreeing exactly on 8496
measure values), and L5 tests θ against the calculus's stem-verdict
read-off (Thm 3.10) with no automaton at all, on 3182 obligation rows.
L4 confirms the profile's `p`-freeness corollary on 18 660 random-`p`
measures. Theorem 3.4 is corpus-tested. The 6 budget-blown pairs are
alignment-cost data (the known `n_A·n_B` tail), not measure failures;
nothing in M2 weakens the M1 certificates. M3 (distance) is unblocked:
its machinery (xor on a materialized aligned table + M1 `measure`) is
exactly what L2 already exercised, so §9 is promoted to the work order
with pseudometric laws and the null-disagreement read-off as its
gates.

**F-M3 (2026-07-11, git b94404abe) — distance, shadow, essential land;
every law green, Prop 4.5 corpus-tested.** Engine additions in
`sosl/sosl/quant/`: `value_vector` (per-class measure, the M1 solver's
rows), `distance` (pair-set xor on the materialized aligned product +
`measure`; the xor θ-profile carries the null-disagreement bit),
`shadow` (Prop 4.1 stem-region read-off, reduced), `essential` +
`ltl_up_to_null` (Thm 4.4 value-congruence quotient, identity held out
per calculus canonicity — `algorithm.md` §9 records why that is
language-neutral; aperiodicity via the classify orbit scan). Fixtures
(`tests/quant/fixtures2`): F-D and F-E (the §8.5 additions, first
materialized here — M2 had closed without them) green with F-D's
non-kernel idempotent convicted as specified and F-E exact at `2/3`
and `3/4`; F-F/F-G/F-H/F-I green: the F-G negative control HELD
(distance 0, all-zero xor profile, shadows byte-DIFFERENT) and F-H
repaired it (essential forms byte-equal); F-I's congruence merged `[ε]`
with the neutral class only, ℤ/2 retained, `ltl_up_to_null(F-E) =
False`. Corpus campaign (`tests/quant/m3_gate`, census at 6222):
**cases 6222/6222 green, zero budget-blown** (worst 6.0 s at n = 208) —
`d(L, shadow L) = d(L, essential L) = 0` with all-zero profiles,
idempotence byte-exact, `essential(shadow L)` byte-equal
`essential(L)`, **Prop 4.5 byte-equality under uniform vs skewed `p` on
all 6222** (no stop-the-line), and aperiodic ⟹ ltl-up-to-null on every
row. Pairs **993/1000 green, 0 red, 7 budget-blown** (aligned-product
tail, a datum): symmetry exact under both `p`'s; 313 sampled pairs
differ by a null set, of which 154 have byte-equal shadows (consistency
law held on all) and **159 are corpus F-G instances** — distance 0 with
byte-different shadows, so the shadow really is too fine and the
essential form is the right null-set invariant. Triples **497/500
green, 0 red, 3 budget-blown** (triangle inequality exact). Census
data for the paper's §6: **5660/6222 languages are LTL up to null sets
(3738 aperiodic outright — so 1922 carry a group that is measure-
invisible)**; the essential form is strictly smaller than the (already
reduced) input on 5552/6222, trivial (`n = 2`: a.s. or null) on 5164.
Machine reports: `reference/quant/m3_laws.md`
(+ `m3_laws_{cases,pairs,triples}.csv`), regeneration commands in the
header; sample files under `tests/quant/logs/`. No disagreement
between spec and paper surfaced.

**Theory reply to F-M3 (2026-07-11) — ACCEPTED, with one required gate
addendum (M3b) and one cross-gate prediction registered; M4 unblocked
on a revised spec §10.**

*Ratification.* The gates convict exactly the paper's claims:
`d(L, sh L) = 0` with all-zero xor-profile is Prop 4.1(ii) read
through §4.2's decidable zero test; shadow idempotence is 4.1(ii)'s
last clause; `essential(shadow L)` byte-equal `essential(L)` exercises
Thm 4.4(2)'s "depends only on the class" on the one in-class mate that
is always constructible (the shadow is in the class by 4.1(ii)); the
159 corpus F-G pairs confirm at scale the §4.2 warning that the shadow
is not a complete invariant, and the F-G fixture control holding
byte-DIFFERENT shadows at distance 0 is precisely the negative result
the spec demanded. Prop 4.5 byte-exact on all 6222 is the strongest
single gate of the campaign — measure-independence is now
corpus-tested, not merely proved — and `aperiodic ⟹ ltl_up_to_null` on
every row tests the divisor direction of Thm 4.4(1)+(3) (`M_x` divides
`M(L)`; divisors of aperiodic monoids are aperiodic).

*Arithmetic cross-checks (all pass).* (a) Trivial essential (`n = 2`)
is *equivalent* to `μ(L) ∈ {0, 1}`: if `μ(L) = 1` the complement is
null in every cylinder, so every residual measure is `1`, the series
is constant, and `M_x` is trivial (dually for `μ = 0`); conversely a
trivial quotient makes `ess(L) ∈ {∅, Σ^ω}`. The census must therefore
satisfy: interior count `6222 − 5164 = 1058`; the LTL-up-to-null tally
splits as `5660 = 5164` (every trivial class is LTL) `+ 496` interior,
leaving `562 = 6222 − 5660` interior non-null-LTL, and
`496 + 562 = 1058` ✓. (b) Complement on one table flips the pair set
and sends `x` to `1 − x` pointwise, so `≈` — hence `M_x`, its
aperiodicity, and its triviality — is complement-invariant; on a
complement-closed corpus every census count above must be even up to
self-complementary entries: 3738, 5660, 5164, 5552, 6222 all even ✓.

*The caveat — Thm 4.4(2)'s byte test is not yet corpus-tested as a
biconditional.* Per `m3_laws.md`, the pair gate asserted symmetry and
the consistency law (equal shadows ⟹ equal essentials — the 154), but
not the theorem's crown claim: `d_p(L₁, L₂) = 0` **iff** the reduced
essentials are byte-equal. On the 159 F-G-shaped pairs the finding's
"the essential form is the right null-set invariant" is the theorem
speaking, not the gate. Both halves are free — every scored pair
already carries the xor-profile verdict and both essentials. **M3b
(required, cheap):** on the same 1000-pair sample (same seeds), assert
byte-equal essentials ⟺ all-zero aligned xor-profile, both directions
— in particular equality on the 159 null-disagreement pairs with
differing shadows and *in*equality on the ~680 positive-distance
pairs. A violation in either direction convicts Thm 4.4(2) — stop the
line. (M6's E3(b) re-exercises the same biconditional exhaustively;
M3b closes it now, and rides along with the M4 pass.)

*Prediction registered for E1/M6.* By cross-check (a), an E1 rerun on
the same census snapshot must report exactly **5164** languages with
`μ ∈ {0, 1}`, split **2582/2582** by complement pairing. A mismatch
convicts one of the two gates.

*Spec edit (M4 unblocked on it).* §10 as previously written ran one
Collatz–Wielandt loop on the whole `Live` matrix. That loop does not
terminate when the matrix is reducible — on `diag(2, 1)` the bracket
is `[1, 2]` for every positive vector, forever — and reducible is the
common case (transient live classes feeding bottom blocks). §10 has
been rewritten around the block decomposition the paper's own proof
already cites (`ρ(A) = max` over irreducible diagonal blocks,
[LM95 §4.4]), with per-block primitive shift `I + A_B`, exact
`Fraction` brackets, and three fixtures including a certified
irrational case (golden mean, verified by a rational sign test on
`ρ² = ρ + 1` — no float in the assertion).

*Verdict.* M3 accepted; M3b required with (or before) the M4 pass;
M4 unblocked on the revised §10.

**F-M4 (2026-07-11, git efcc54a2b) — entropy lands with certified
enclosures; every law green, zero non-converged brackets; M3b closes
the Thm 4.4(2) biconditional.** Engine `sosl/sosl/quant/entropy.py`
(Prop 5.1, spec §10 as rewritten): `Live` from the calculus liveness
scan, letter-count matrix `A` on `Live × Live`, SCC condensation of
the live subgraph (the kernel module's Tarjan, reused), and
`ρ(A) = max_B ρ(A_B)` per irreducible diagonal block — singletons
exact, nontrivial blocks by Collatz–Wielandt on the primitive shift
`B' = I + A_B` with per-step brackets intersected (each is valid for
its own positive iterate, so soundness never rests on convergence).
The result is an exact rational bracket plus a replayable certificate
(live set, blocks, per-block enclosures); `log₂` is the only float,
widened one ulp outward per side. *One implementation note (spec §10
deviation, soundness-neutral):* the iterate is kept in fixed point
over the **common** denominator 10⁴⁰ rather than per-entry
`limit_denominator(10**40)` — per-entry denominators blow up through
their lcm inside the exact products `B'·v`; the spec's own argument
(rounding a strictly positive `v` only slows convergence) carries
over verbatim, and `algorithm.md` §10 records it. Fixtures
(`tests/quant/fixtures3`) green: F-J `ρ = 2` exact / `h = 1`; F-K
`ρ = 1` exact / `h = 0`; F-L (golden mean, hand-built 6-class "no
factor bb") has exactly the two predicted `[[1,1],[1,0]]`-shaped live
blocks and its bracket straddles `φ` by the fraction sign test
(`lo² ≤ lo + 1` and `hi² ≥ hi + 1`) at width 7.5e-10 — no float in
the check. Corpus campaign
(`tests/quant/m4_gate`, census at 6222): **cases 6222/6222 green, 0
red, 0 budget-blown, 0 non-converged brackets** (worst case 21 ms —
entropy is the cheapest gate of the campaign); laws held exactly:
emptiness (the corpus's 1 empty language gives `h = 0` at width 0),
`ρ_lo ≥ 1` on every nonempty row (the liveness scan stands),
`ρ_hi ≤ |Σ|`, and the structural closure law `h(cl(L)) = h(L)`
(equal live sets, identical live letter-count matrices under
`safety_closure` on the same table) on all 6222. Monotonicity pairs:
**1000/1000 green** (seed-1 sample, 110 pairs carrying a real
inclusion; `ρ_lo(L₁) ≤ ρ_hi(L₂)` on every detected `L₁ ⊆ L₂`, both
directions). Census texture for §6: 195 nonempty languages with
`ρ = 1` (`h = 0`), largest live part 208 classes, up to 31 blocks,
`h` up to `log₂ 8 = 3` on the 3-AP slice. **M3b (spec §9.1), same
seed-1 1000-pair sample as `m3_laws.md`: 999/1000 scored (1
budget-blown at 15 s, an alignment/essential-cost datum), 0 red — on
every scored pair, byte-equal reduced essentials ⟺ all-zero aligned
xor-profile, both directions: 316 null-disagreement pairs = 316
essential-equal pairs, and all 683 positive-distance pairs have
byte-different essentials.** (M3's pair run scored 993 with 313 null
pairs; m3b's cheaper per-pair work loses only 1 to the budget, and
the 6 extra scored pairs carry 3 more null-disagreements — the 313
are a subset of the 316.) The theory reply's expected split (159
shadow-differing + 154 shadow-equal among the nulls) is confirmed on
the shared subset; Thm 4.4(2) is now corpus-tested as a
biconditional. Machine reports: `reference/quant/m4_entropy.md`
(+ `m4_entropy_{cases,pairs}.csv`), `reference/quant/m3b_thm442.{md,csv}`,
regeneration commands in their headers (fixtures:
`python3 -m tests.quant.fixtures3`). No disagreement between spec
and paper surfaced.

**Theory reply to F-M4 (2026-07-11) — ACCEPTED; the deviation is
ratified and spec §10 amended to it; Thm 4.4(2) now stands
corpus-tested as a biconditional; one cross-gate prediction registered
for E2/M6.**

*Ratification.* The gates convict exactly the paper's §5 claims.
Prop 5.1 (`h = log₂ ρ` of the live letter-count matrix) is exercised
on all 6222 with certified enclosures, and the four laws are the
paper's own: emptiness (§5's `h(∅) = 0` convention), `ρ_lo ≥ 1` on
nonempty rows (the live-cycle fact inside the Prop 5.1 proof),
`ρ_hi ≤ |Σ|` (the row-sum bound), and `h(cl(L)) = h(L)` tested
*structurally* — equal live sets, identical letter-count matrices —
which is stronger than the numerical equality of [Sta93, p. 168] the
paper cites: closure invariance holds at the certificate level, not
merely in the value. F-L is the right kind of irrational witness: the
sign test on `ρ² = ρ + 1` with both ends of the bracket in `Fraction`
carries the "no floats in gates" ground rule intact through an
irrational spectral radius. M3b: 316 null-disagreement = 316
essential-equal AND 683 positive-distance = 683 byte-different closes
*both* directions of Thm 4.4(2) on the sample; together with F-M3's
consistency law this retires the caveat recorded in the F-M3 reply.
The 1 budget-blown pair is a datum consistent with M3's 7 (m3b does
less per pair), and the subset relation 313 ⊆ 316 on null pairs
checks.

*The deviation — accepted, spec amended in place.* Soundness of the
CW bracket needs only that each step's bracket is computed exactly
from the vector actually held and that this vector stays strictly
positive; the vector's provenance is irrelevant (CW holds for EVERY
positive `v`). Rounding to the common fixed-point grid `10⁻⁴⁰`
preserves both, so the change is convergence-speed-only — and 0
non-converged brackets on 6222 plus width 7.5e-10 on F-L settles
convergence empirically. A per-entry `limit_denominator` defeats its
own purpose (the entries' lcm blows up inside the exact `B'·v`); spec
§10 names the common-denominator iterate as normative.

*Prediction registered for E2/M6 (uniform `p`).* For uniform `p`,
`μ(L) ≤ |pref_n(L)|/|Σ|^n` for every `n`, so `μ_p(L) > 0` forces
`h(L) = log₂|Σ|` — and in the engine this is exact, not asymptotic:
`ρ = |Σ|` requires an irreducible live block whose every row sums to
`|Σ|` (for irreducible nonnegative matrices, `ρ` reaches the max row
sum only when all row sums are equal), on which the `v₀ = 1` bracket
is `[|Σ|, |Σ|]` at iteration 0, width 0. So the E1×E2 census join must
show **zero rows with `μ > 0` and `ρ < |Σ|`**: all 2582 `μ = 1`
languages and all 1058 strictly-interior languages report `ρ = |Σ|`
exactly at width 0, and every language with `h < log₂|Σ|` (the 195
with `ρ = 1` among them) reports `μ = 0`. A violation convicts M1 or
M4. (The converse is not claimed: `μ = 0` languages may still have
maximal entropy — "finitely many `b`" has `pref = Σ*`.)

*Verdict.* M4 + M3b accepted; §10 amended; M5 is unblocked (user go
required).

**P-M5 (2026-07-11, engineering → theory, RATIFIED) — the `.mc` chain
format.** The normative text is spec §11 (the M5 work order); this
record carries the decisions and their grounds.

- *Model.* `.mc` holds a state-labelled DTMC — `M = (Q, P, ι, ℓ)`,
  the paper's §2.3 chain model and the one every probabilistic model
  checker speaks. The measured word is the full path word
  `ℓ(s₀)ℓ(s₁)…`: the initial state's label is the word's
  deterministic first letter, which is what PRISM and Storm measure —
  "same file, same number". Fixture F-M pins the convention (its
  answer flips from 1 to 1/3 if the initial letter is dropped). The
  product starts at `(q₀, λ(ℓ(q₀)))` and reads `ℓ(q')` per step
  (Thm 3.5); `.mc`'s single init is the Dirac restriction of the
  theorem's `ι`.
- *Syntax.* A restricted PRISM-language subset: one `dtmc` module, one
  bounded state variable, exactly one guarded command per state
  (`[] s=0 -> 1/3:(s'=1) + 2/3:(s'=0);`), APs as `label` definitions
  over `s`. Probabilities are exact rationals *in source* (`1/3` is
  legal PRISM) — the property that carries the `Fraction` ground rule
  through interop, and the deciding argument over `.tra`-style
  explicit formats, whose decimal probabilities cannot express `1/3`
  at all. The same file runs unmodified in both PRISM and Storm, so
  M5's cross-checks and E4's baseline mean "identical input file".
  The restriction keeps the reader a strict ~100-line parser, not a
  language front-end.
- *Well-formedness (normative; the reader rejects, never repairs).*
  (i) exactly one guarded command per state, branch probabilities
  rational literals summing to exactly 1 as `Fraction`s; (ii) the
  letter labels partition the state space — every state satisfies
  exactly one `label`, whose name is a letter of the paired language's
  alphabet verbatim (never PRISM's reserved `"init"`/`"deadlock"`);
  (iii) alphabet equality with the paired `.sos` is checked, not
  assumed.
- *The M1 reconciliation gate is the Bernoulli-embedding law* (an
  `ι`-linearity check of Thm 3.5): states `{q_a}_{a∈Σ}`,
  `ℓ(q_a) = a`, `P(q_a → q_b) = p(b)`; from initial `q_a` the emitted
  word is `a·(i.i.d. p)`, so `Pr_{M_a}(L) = μ_p(aΣ^ω ∩ L)/p(a)`, and

  ```
  Σ_a p(a) · Pr_{M_a}(L) = μ_p(L)     (byte-exact against M1)
  ```

  — it exercises the initial-letter convention `|Σ|` times per
  language and reconciles against M1's number exactly.
- *Excluded formats.* Storm DRN deferred (an optional later exporter);
  JANI excluded as JSON; PRISM/MRMC explicit `.tra` excluded (decimal
  probabilities); GreatSPN excluded — a GSPN's semantics is a
  *continuous-time* chain on a generated reachability graph, wrong on
  time, storage, and letter emission (embedded-DTMC extraction could
  source E4 benchmark families later).
- *With the corpus keeper.* Only file placement/naming of *stored*
  chain families: M5's gate generates its chains seeded and in-test,
  so storage becomes real at M6/E4 — decide then.
