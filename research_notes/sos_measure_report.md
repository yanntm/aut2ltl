# Measure, Distance, and Entropy on the Syntactic ω-Semigroup — results

The answer to `research_notes/sos_measure_spec.md` §8 (milestone QNT5):
the `sosl.sos.quant` package run against the E-series, measured on the
`flat_canon` census and on the QNT4 pipeline demo. Each finding `Fn` is a
checked prediction of the paper `research_notes/sos_measure.md`; the
paper states results in pure form and cites no artifact — this report is
where each claim is tied to a regenerable machine report.

Every campaign writes a machine-generated report under `reference/quant/`
(one `.md` + one `.csv`) carrying a date / git-rev / seed / corpus
header, so any row below is reproducible from that file alone. Commands
run from `sosl/`. Spot appears only inside the Route A oracle,
bounded-or-skipped; a blown per-case budget is a datum, never a wait.

*Status (2026-07-11): M1 (measure), M2 (oracle + laws), M3
(distance / shadow / essential), M4 (entropy) and the M3b addendum are
done, green corpus-wide, and theory-accepted (F-M1..F-M4). M5 (Markov
product; spec §11 is the work order, P-M5 ratified) is next, on the
user's go; M6 (the census campaign that fills the ⟨TBD⟩ slots below)
follows it.*

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

## Harness state

Engine: `sosl/sosl/quant/` (placement provisional) — `chain` / `kernel`
/ `theta` / `measure` (+ `value_vector`) / `routea` / `distance` /
`shadow` / `essential` / `entropy`; `PARANOID` on; `Fraction` end to
end, the one float quarantined to `entropy`'s final `log₂`; Spot
parse-only inside `routea`. Gates, run from `sosl/` as
`python3 -m tests.quant.<name>`, machine reports under
`reference/quant/`:

| gate | laws | machine report | state |
|---|---|---|---|
| `fixtures`, `fixtures2` | F-A..F-C, F-D..F-I hand ground truth | (in-test, exact) | green |
| `flip_gate` | μ(L)+μ(¬L)=1, profile negation | `m1_measure.{md,csv}` | green 4248/4248 |
| `oracle_gate` | L1 oracle agreement, both `p`'s | `m2_oracle.{md,csv}` | green 4248/4248, 0 skips |
| `law_gate` | L2–L5 modularity/monotonicity/trichotomy/obligation | `m2_laws.md` + csvs | green, 0 red |
| `m3_gate` | shadow/essential case laws, symmetry, consistency, triangle, Prop 4.5 | `m3_laws.md` + csvs | green 6222 cases / 993 pairs / 497 triples, 0 red |
| `fixtures3` | F-J..F-L entropy hand ground truth (golden mean by rational sign test) | (in-test, exact) | green |
| `m4_gate` | entropy case laws + monotonicity under inclusion | `m4_entropy.md` + csvs | green 6222 cases / 1000 pairs, 0 red, 0 non-converged |
| `m3b_gate` | Thm 4.4(2) biconditional: essentials ⟺ null xor-profile | `m3b_thm442.{md,csv}` | green 999/1000, 0 red |

Budget kills (15 s per case) are recorded as data in each aggregate;
the corpus is concurrently regenerated, so gate counts are dated
snapshots — rerun rather than trust totals.

## Findings

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
