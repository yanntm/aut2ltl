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

*Status (2026-07-11): M1 (measure), M2 (oracle + laws) and M3
(distance / shadow / essential) are done, green corpus-wide, and
theory-accepted (F-M1, F-M2, F-M3). The F-M3 reply requires one cheap
gate addendum, M3b (the Thm 4.4(2) biconditional on the existing pair
sample), to run with the M4 pass. M4 (entropy) is unblocked on the
rewritten spec §10; M5 (Markov product) and M6 (the census campaign
that fills the ⟨TBD⟩ slots below) are not started.*

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
`shadow` / `essential`; `PARANOID` on; `Fraction` end to end, floats
nowhere; Spot parse-only inside `routea`. Gates, run from `sosl/` as
`python3 -m tests.quant.<name>`, machine reports under
`reference/quant/`:

| gate | laws | machine report | state |
|---|---|---|---|
| `fixtures`, `fixtures2` | F-A..F-C, F-D..F-I hand ground truth | (in-test, exact) | green |
| `flip_gate` | μ(L)+μ(¬L)=1, profile negation | `m1_measure.{md,csv}` | green 4248/4248 |
| `oracle_gate` | L1 oracle agreement, both `p`'s | `m2_oracle.{md,csv}` | green 4248/4248, 0 skips |
| `law_gate` | L2–L5 modularity/monotonicity/trichotomy/obligation | `m2_laws.md` + csvs | green, 0 red |
| `m3_gate` | shadow/essential case laws, symmetry, consistency, triangle, Prop 4.5 | `m3_laws.md` + csvs | green 6222 cases / 993 pairs / 497 triples, 0 red |

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
