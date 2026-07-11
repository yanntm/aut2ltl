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

**Proposal P-M5 (2026-07-11, engineering → theory + corpus keeper) —
the `.mc` chain format: adopt the state-labelled convention and an
existing format.** Spec §11 left the sidecar format open ("CSV-shaped,
no JSON — fix with the corpus keeper"); after surveying what exists
(PRISM language / PRISM explicit `.tra`+`.lab` / Storm DRN / MRMC
`.tra` / JANI / GreatSPN nets), engineering proposes to align on the
ecosystem rather than invent a dialect:

1. *Semantics — Moore convention.* Every probabilistic model checker
   speaks the **state-labelled DTMC**: APs on states, the run's word =
   the sequence of state labels. Adopt it for `.mc` (the spec's
   transition-emitting source is its Mealy presentation; no loss of
   generality, the corpus generates Moore-form directly). The §11
   product changes by one line: `letter(q → q') := ℓ(q')`.
2. *Syntax — a restricted PRISM-language subset* as the corpus `.mc`
   format: one `dtmc` module, one bounded state variable, exactly one
   guarded command per state (`[] s=0 -> 1/3:(s'=1) + 2/3:(s'=0);`),
   APs as `label` definitions over `s`. Probabilities are exact
   rationals *in source* (`1/3` is legal PRISM), so the `Fraction`
   ground rule survives interop — unlike PRISM/MRMC explicit `.tra`,
   whose decimal probabilities cannot express `1/3` at all. The same
   file runs unmodified in both PRISM and Storm (Storm has a PRISM
   front-end), which upgrades M5's cross-checks and E4's baseline to
   "identical input file". The restriction keeps the reader a strict
   ~100-line parser, not a language front-end. (Storm's DRN kept as an
   optional later exporter; JANI excluded as JSON; GreatSPN excluded —
   a GSPN file is a net whose semantics is a *continuous-time* chain
   on a generated reachability graph, wrong on time, storage, and
   letter emission, though embedded-DTMC extraction could source E4
   benchmark families later.)
3. *One theory-visible decision to ratify.* PRISM/Storm measure the
   full path word `ℓ(s₀)ℓ(s₁)…` — the initial state's label is the
   word's deterministic first letter; the Mealy reading drops it. For
   "same file, same number" against PRISM/Storm, Thm 3.5's setup must
   include the initial label in the emitted word. Needs a spec §11
   (and possibly paper §2) remark either way.

M5 implementation waits on this being accepted or amended.
