# BLS and counters — what the cascade actually needs (2026-07-04)

Where the Boker–Lehtinen–Sickert construction really uses counter-freeness,
what the implemented cascade (`aut2ltl/bls/`) does on group-bearing inputs, and
what that means for the definability gate. Investigation over three small
inputs, fully reproducible (pointers below).

## Direction

The kr cascade is fronted by a gate (`aut2ltl/bls/gate/`) that admits an input
only behind a proved-aperiodic reading of one deterministic form's transition
monoid. Two established facts set up the tension:

- the ungated cascade translates `gf_aa_parity` — an *LTL* language,
  `GF(a & Xa)`, deliberately encoded with a Z2 in its transition monoid —
  **correctly**, on the very form the gate declines
  (`tests/probes/bls_ungated.py`);
- the ungated cascade emits a confident **wrong** formula on `mod3_a`, a
  genuinely non-LTL (mod-3 counting) language — the silent unsoundness the
  gate exists to stop.

Both deterministic forms of `gf_aa_parity` (generic-minimal and the
parity-sbacc the cascade builds from) carry the Z2
(`tests/probes/form_aperiodic.py`), so no form-level aperiodicity screen can
separate these two cases. The question: what *does* separate them — what is
the exact border of what the cascade can cover?

## What the paper actually assumes

Reading `aut2ltl/bls/paper/Automata2LTL.txt` (digest:
`aut2ltl/bls/paper/automata-to-ltl-construction.md`):

- Counter-freeness is load-bearing in **exactly one place**: Proposition 6
  (Krohn–Rhodes–Holonomy), the *existence* guarantee that a counter-free
  semiautomaton is homomorphic to a **reset** cascade.
- The entire technical core is unconditional given that object: Lemma 4 (the
  five reachability formulas match their intended semantics) and Lemma 7
  (`Fin(C)`) are stated for *arbitrary* reset cascades; Props. 7/8 need only
  the homomorphism (cover) π.

So the construction's real soundness premise is "a genuine reset cascade,
covered, with acceptance lifted" — counter-freeness is only the ticket that
buys it. On a non-counter-free input the paper is silent (precondition unmet),
not negative.

## Hypothesis

The construction is sound whenever it is *semantically* aperiodic — i.e. the
operators are well-formed in the presence of an aperiodic **syntactic
ω-semigroup** (= the language is LTL), regardless of groups in the
presentation. Counter-freeness of the form is a presentation-dependent proxy
the authors could prove inside, not the real barrier. (Consistent with
benchmark experience: with the gate skipped, on formula-derived inputs the
cascade never answered inaccurately where checkable.)

## Experiment 1 — which paper premise breaks (`tests/probes/casc_cover_check.py`)

The probe decomposes one HOA and checks the two premises separately on the
resulting cascade: (a) every level is a reset semiautomaton (per combined
letter: identity or constant), (b) the cover π commutes with the true lifted
dynamics.

| input | cover π | reset premise | cascade output |
|---|---|---|---|
| `gf_aa` (LTL, aperiodic form) | holds | holds | correct — on-theorem |
| `gf_aa_parity` (LTL, Z2 form) | holds | **violated**: one letter, top level ⟨a, lower=1⟩ = transposition {1↔2} | correct — off-theorem |
| `mod3_a` (non-LTL) | holds | **violated**: one letter, level 1 ⟨a, below=(2,)⟩ = 3-cycle (1 3 2) | wrong |

Findings: SgpDec's cover is genuine in all cases — the break is *only* the
reset property, at exactly one group letter each. The parser labels those
levels `kind=reset` unchecked (`LevelInfo.kind` is asserted, not verified), so
`Cascade.has_nontrivial_groups()` reads no groups: the "group misread as
reset" of the gate's docstring is real but is a *labeling* gap, not a
corrupted cover. Crucially, the violation is structurally identical in the
correct and the wrong case — **no local structural test on the cascade can
delineate coverage**.

## Experiment 2 — grounding every Fin(C) sub-term (`tests/probes/fin_ground.py`)

For each reachable config C, the probe builds the cascade's `Fin(C)`
sub-formula and compares it against its exact Lemma-7 semantics: the
configuration automaton with `Fin(0)` acceptance, marks on transitions leaving
C. (Config-level ground truth matters: on `mod3_a` the cover is not injective —
6 reachable configs over 5 states — so state-level ground truth is wrong for
the doubled state.) It also reports the aperiodicity screen's reading of each
ground-truth language.

| input | Fin(C) | build vs ground truth | GT language |
|---|---|---|---|
| `gf_aa_parity` | (1,1) | correct | LTL (certified by match) — *screen reads "group"* |
| `gf_aa_parity` | (1,2), (2,1) | correct | LTL, screen aperiodic |
| `mod3_a` | (1,1,2), (1,2,2), (1,3,2), (1,4,2) | correct | LTL, screen aperiodic |
| `mod3_a` | (1,1,1), (2,1,1) | **wrong** — pure under-approximations | non-LTL (see below) |

Findings:

- `gf_aa_parity` is correct **at every sub-term**. The earlier
  "limit-cancellation" theory (individually wrong Fins whose errors cancel in
  the acceptance combination) is refuted — the operators compute correct
  reachability over the group-carrying cascade.
- `mod3_a` breaks in exactly two sub-terms, and both target languages are
  genuinely non-LTL: in mod3's config graph the Z3 cycle
  {(1,1,2),(1,3,2),(1,2,2)} exits to (1,1,1) only from position (1,1,2) on
  `!a`, so "visits (1,1,1) finitely often" is decided by the count of `a`'s
  **mod 3** — properly non-star-free. The formulas' missed witnesses are
  `a; cycle{!a}` and `a;a;a; cycle{!a}`: an LTL formula for a non-LTL target
  must err somewhere, and it errs *exactly on the words whose truth is the
  modular count*.
- The screen over-reads at sub-term granularity too: parity's Fin((1,1))
  screens "group" yet is built correctly (its language is star-free — the
  benign-group phenomenon recurring one level down).

## The law, and an unexpected consequence

**Empirical law (9/9 sub-terms):** the cascade builds a sub-term correctly iff
that sub-term's target language is LTL. Groups in the presentation are
harmless per se; what breaks the operators is a genuinely *modular question*,
never a group in the carrier. This confirms the hypothesis — and sharpens it
from per-input to per-sub-term.

The sharpening cuts back, though: correctness is governed by LTL-ness of the
**form's sub-problems**, not of the input language. The two can diverge in
principle: pad an LTL language's automaton with a redundant mod-3 counter
(product with a counter the acceptance ignores) and some "visits C finitely
often" becomes modular — a non-LTL sub-term inside an LTL input, so the
cascade should *lie on an LTL language*. If such forms are reachable, the
language-level oracle alone is NOT a sufficient gate. What plausibly protects
the practice: `decompose_aut` normalizes to a *minimized* sbacc parity form,
which strips redundant counters before the operators see them. Hence the crux:

> **For a minimal deterministic form of an LTL language, is every Fin(C)
> (and every reach sub-problem) itself LTL-definable?**

Yes ⟹ minimized input + language-LTL ⟹ cascade correct: the semantic
(oracle) gate is exactly right and the form screen is provably replaceable.
No ⟹ the gate genuinely needs form-level information, and the benchmark
record is luck of a characterizable kind.

## Reproduction

All probes are single-input, seconds each (GAP + SgpDec required, see
`install_gap.sh`):

```
python3 tests/probes/casc_cover_check.py samples/fixtures/hoa/definability/gf_aa_parity.hoa
python3 tests/probes/casc_cover_check.py samples/fixtures/hoa/definability/gf_aa.hoa
python3 tests/probes/casc_cover_check.py samples/fixtures/hoa/various/mod3_a.hoa
python3 tests/probes/fin_ground.py      samples/fixtures/hoa/definability/gf_aa_parity.hoa
python3 tests/probes/fin_ground.py      samples/fixtures/hoa/various/mod3_a.hoa
python3 tests/probes/bls_ungated.py     samples/fixtures/hoa/definability/gf_aa_parity.hoa
```

## Where to take it

1. **The crux question, adversarially:** hunt a *minimal* deterministic form
   of an LTL language with a group whose phases are limit-distinguishable
   per-state (making some Fin(C) non-LTL). The padded-counter trick produces
   non-minimal ones only; the question is whether minimality forbids the
   pattern. Finding one refutes the pure-semantic gate; failing to find one
   points at a theorem.
2. **The crux question, theoretically:** "run visits q infinitely often" is a
   linked-pair condition in the ω-semigroup; look for a short argument that
   for a minimal recognizer of a star-free ω-language these per-state
   recurrence languages stay star-free (Carton–Perrin–Pin and
   Preugschat–Wilke, in `papers/`, are the places to look — Preugschat–Wilke
   in particular decomposes definability testing per-SCC/per-state).
3. **Honest labeling regardless:** the parse should stop asserting
   `kind=reset` — record the actual per-letter action class so
   `has_nontrivial_groups()` tells the truth; the reset premise is checkable
   in milliseconds (Experiment 1's check).
4. **Gate consequence to draft once 1/2 settles:** if the theorem holds, the
   gate's decline on group readings can be replaced by the language-level
   oracle for *minimized* forms; if the counterexample exists, the gate needs
   a per-sub-term screen (Experiment 2's ground-truth automata are exactly the
   objects to screen).

---

# Log 2026-07-04 (cont.) — the theoretical program

Direction set: no counterexample hunt (random-formula experiments and the
genaut exhaustive census have revealed no error — absence of evidence, but a
lot of it); solve (A) theoretically, starting from the semantic fact (L is
LTL, i.e. S(L) aperiodic) and eliminating the contradictors. The SOSG oracle
(`aut2ltl/bls/definability/oracle/algorithm.md`) supplies the vocabulary: the
acceptance-enriched monoid EM(D), the loop-profile function A(q,c), and the
collapse of the syntactic congruence into residual equality (~lin) +
loop-profile equality (~omega). Note its layer 14 already records the
conservative policy this investigation may discharge: "a proven-LTL language
can still present an encoding group the holonomy parser misreads."

The program:

- Contradictor of (A), formalized: a state q0 of the minimized form D whose
  recurrence language Inf(q0) = "run visits q0 infinitely often" is
  non-star-free while L(D) is star-free. Inf(q0) is recognized by the SAME
  semiautomaton with different marks (transitions leaving q0), so L and
  Inf(q0) share the transition monoid and differ only in enrichment.
- Sweep observation: while pumping v^n, the run sweeps the whole v-orbit
  every period, so the swept part of any loop's visited set is
  phase-invariant. Phase-dependence of "visits q0" can only enter through
  the continuation path (the finite context read from a phase-dependent
  state).
- Fallback (B) if (A) falls: the assembly consumes Fin(C) only through the
  lifted acceptance combination; orbit-level recurrence is always
  phase-invariant, hence star-free; if the construction's per-Fin errors are
  confined to phase-discrimination (mod3's errors were pure
  under-approximations on exactly the modular words), the assembled
  combination over a phase-saturated acceptance set could still be correct.
  "Wrong sub-terms, right total, whenever L is star-free."

# Attempt at (A) — reduction and partial eliminations

Setting: D deterministic, complete, trim, MIN-SIZE in its acceptance class
(parity sbacc; see "cracks" below for how honest that assumption is w.r.t.
the pipeline), L = L(D) star-free. All state languages L(q) are residuals of
L; recall L(x) = L(y) implies L(delta(x,u)) = L(delta(y,u)) for every finite
u (residuals of equal languages are equal) — context-wise residual equality
comes for free.

## Step 0 — on-theorem zone (cited)

If TM(D) is aperiodic, EVERY enrichment of D is star-free (oracle layer 8:
aperiodicity is inherited upward through any mark enrichment — the state
part stabilizes, then the mark part grows monotonically in a finite lattice
and stabilizes one step later). So all Fin(q) are star-free and (A) holds.
The whole question lives where TM(D) has a group that dies in L's quotient.

## Step 1 — the contradictor reduces to a two-state pattern

Suppose Inf(q0) is not star-free. By the certificate completeness (oracle
layer 2, Arnold), Inf(q0) admits a counting family, linear or omega-power.

Linear shape: n |-> [ q0 visited i.o. on u v^n x ] toggles with n mod p,
p > 1, x a fixed lasso. Let x_n = delta(iota, u v^n). Since S(L) is
aperiodic, [u v^n]_{S(L)} is eventually constant in n, so the residuals
L(x_n) are eventually CONSTANT. Pick N past both indices: x = x_N and
y = x_{N+1} satisfy

  (R-pattern)  x != y reachable,  L(x) = L(y),  and a single lasso rho
               visits q0 i.o. from x and finitely often from y.

(x != y because the recurrence differs; determinism.) The omega-power shape
reduces analogously via conjugation — u (v^n y)^omega toggling gives two
phase-shifted loops from residual-equal states whose closed cycles disagree
on visiting q0; same pattern with rho the rotated loop word. [Stated, not
fully written out; the linear case is the load-bearing one below.]

So the contradictor of (A) is exactly: a min-size D of a star-free L
containing a reachable residual-equal pair (x, y) and a state q0 with a
lasso rho on which the two runs disagree FOREVER about q0-recurrence.
Note what is automatic: rho itself, and every ultimately-periodic variant,
gets the SAME acceptance from x and from y (that is what L(x) = L(y) says)
— the q0-discrepancy swings no acceptance decision from this pair. The
contradictor requires recurrence that is acceptance-orthogonal along the
pair.

## Step 2 — elimination: the automorphism lemma (kills decorations)

Lemma. A min-size deterministic automaton has no nontrivial mark-preserving
automorphism h (a permutation of Q commuting with delta and preserving
marks... with h(iota) = iota... more precisely: any h whose orbit
equivalence is delta-compatible and mark-compatible). Proof: the quotient
D/h is deterministic (delta-compatibility), the projection of the D-run is
the D/h-run with identical marks, so L(D/h) = L(D) with fewer states —
contradicting min-size. QED.

Consequence: every "decorated" contradictor dies — in particular the padded
mod-3 counter (redundant product component the acceptance ignores): its
phase shift IS a mark-preserving automorphism, so it cannot survive
minimization. This is the formal version of "minimization strips redundant
counters."

## Step 3 — elimination: the leak lemma (kills mark-correlated recurrence)

Worked non-example (instructive failure). Try to build the R-pattern
directly: Q = {x, y, x'}, letter a swaps x,y (the Z2; x' -a-> y), letter b:
x -> x' -> x (2-cycle), y -> y. Put the only Buchi mark on x -b-> x'. Then
rho = b^omega from x visits x' i.o., from y never — the wanted eternal
discrepancy with q0 = x'. But check the premise: rho = b^omega is ACCEPTED
from x (mark i.o.) and REJECTED from y (no marks): L(x) != L(y), and the
pair (x,y) is a-phase-connected, so u a^n b^omega toggles membership in L
with n mod 2 — a counting family for L itself: L is not star-free. The
construction violated the hypothesis, not the conclusion.

Lemma (leak). If visits to q0 correlate with acceptance along the pair — if
some ultimately-periodic continuation distinguishes x from y in ACCEPTANCE
— then L(x) != L(y), the phase family transports it to a counting family
for L, and L was not star-free. Contrapositive: under the hypothesis of
(A), the discrepant recurrence must be invisible to acceptance from (x, y)
under EVERY continuation. The contradictor cannot put its marks anywhere
the pair can see them differently.

## Step 4 — the residual gap, stated precisely

What survives Steps 2–3 is narrow but not yet empty:

  a min-size parity-sbacc D, a reachable pair x != y with L(x) = L(y),
  a lasso rho whose two runs disagree forever on visiting q0, where
  (i) the pair structure is NOT a mark-preserving automorphism (q0 and its
      partner-path states carry genuinely different marks or wiring — they
      are needed globally, for L from iota via OTHER prefixes), yet
  (ii) from x and y all continuations agree on acceptance (Step 3).

"Globally load-bearing, locally orthogonal." gf_aa_parity shows pieces of
this can coexist (residual-equal distinct states, a mark-load-bearing Z2 —
but there every discrepancy is transient: the phase runs merge on !a and
sweep on a, so no ETERNAL q0-discrepancy exists and all Inf(q) are
star-free). The open question is whether min-size can afford an eternal
discrepancy that pays no acceptance rent from its own pair while paying
rent from elsewhere.

## Step 5 — the pattern is decidable: a census predicate

The reduction buys a concrete search primitive, much sharper than "run bls
and verify the formula": the R-pattern is a STRUCTURAL, decidable predicate
on a deterministic automaton —

  exists x != y with L(x) = L(y)          (spot language_map, exact)
  and exists q0 with nonempty
      Inf(q0)-from-x  intersect  Fin(q0)-from-y   (pair-product emptiness)

Run it over the genaut census / the validation corpus on the pipeline's
minimized forms of star-free languages: empty outcome = strong evidence for
(A) plus an induction target; a hit = feed that automaton to fin_ground.py
and see whether the cascade actually breaks (it might not — fallback (B)).
Either outcome is decisive information, and the probe costs one product per
state pair.

## Cracks to keep honest

- The pipeline's "minimized" is best-effort (SAT-min only under a size
  threshold). A proved (A) covers practice only where min-size actually
  holds; above the threshold the theorem's hypothesis is unverified.
- Minimality is class-relative (min among parity-sbacc). Step 2's quotient
  stays in class (automorphism quotients preserve the acceptance shape), so
  the lemma is sound; but any future merge argument stronger than
  automorphisms must not accidentally compare against recognizers outside
  the class.
- Step 1's omega-power branch is sketched, not written out; the conjugation
  bookkeeping (rotating the loop to align phase partners) needs a careful
  paragraph before (A) can be called reduced in full.

## Next

1. Attack Step 4: either prove that an eternal acceptance-orthogonal
   discrepancy forces a size reduction (a merge subtler than an
   automorphism — the pair-closure of (x,y) along rho is the object to
   quotient), or extract from the attempt the shape of the counterexample.
2. Implement the Step-5 census predicate as a probe; run it over genaut
   minimized star-free forms.
3. Write out the omega-power branch of Step 1.
4. Literature check against the gap: Preugschat–Wilke (per-SCC definability
   tests) and Carton–Michel prophetic automata (canonical objects make
   per-state questions language invariants) — the gap may already be a
   known lemma in canonical-form clothing (papers/ has both).

---

# Log 2026-07-04 (cont.) — Experiment 3: the padded form, run for real

Question asked (user): off-minimal, is it actually TRUE that the cascade can
build bad stuff despite the language being LTL — or was that only a
sub-term-level thought experiment? Answer: now demonstrated. And fallback
(B) is refuted by the same run.

## The fixture

`samples/fixtures/hoa/definability/gfa_pad2.hoa` — GFa (last-letter 2-state
recognizer) product an acceptance-inert position-parity bit: 4 states
(q,i), every letter flips i, accepting = both phases of q1. All states
reachable, deterministic, complete, sbacc. Language = GFa exactly
(checked against the reference formula in the run). The padding is the
smallest mark-preserving-automorphism specimen: Z2 in the transition monoid
(both letters flip the bit), acceptance saturated across phases, and every
per-state recurrence question "visit (q,i) i.o." = "q at fixed position
parity i.o." is non-star-free.

## The bypass

The pipeline can never see this form: `decompose_aut` re-postprocesses its
input and the reduction merges the bisimilar phases (the probe prints it:
4 states in, postprocess would leave 2). A Language-level mock is not
enough — `decompose_lang` routes through `decompose_aut`, whose docstring
calls the re-normalization "harmless" (true for the language, form-
destroying for this experiment). So the probe `tests/probes/bls_padded.py`
replicates `decompose_aut` BELOW its postprocess line — determinism check,
`extract_generators`, `decompose_gens`, context fields — feeding the padded
automaton verbatim as the working D, then grounds every Fin(C) and runs the
ungated hierarchy dispatch.

## Result

```
python3 tests/probes/bls_padded.py samples/fixtures/hoa/definability/gfa_pad2.hoa 'GFa'
```

- all four Fin(C) sub-terms WRONG (each mixes the phases; witnesses are
  parity-shifted lassos);
- the assembled buchi formula is WRONG: `ok=True`, technique buchi, but
  NOT equivalent to the input. Containment: formula STRICTLY UNDER the
  language (extra: none) — it misses `a; a; cycle{a; !a}`, a word with
  infinitely many a's, plainly in GFa;
- input == GFa confirmed; output != GFa.

## Consequences

1. **Established, not conjectured: the cascade lies on an LTL language when
   fed a non-minimal form.** The wrongness is real at the answer level, on
   the simplest liveness language there is.
2. **Fallback (B) is refuted.** The acceptance here is phase-saturated by
   construction — the exact situation (B) said could cancel — and the
   errors did not cancel: the total is strictly under-approximating, same
   error shape as mod3's sub-terms.
3. **The "deeper semantics" idea is qualified at answer granularity.** The
   construction is not sound "because it is semantic": on an arbitrary form
   of a star-free language it can be wrong. What it is, per Experiment 2,
   is *per-question semantic*: right exactly where the questions the form
   makes it ask are star-free.
4. **Minimization is load-bearing, not a convenience.** The pipeline's
   aggressive normalization (postprocess reduction) is a soundness
   component: it is what keeps padded forms out. The benchmark record
   (random formulas, genaut census, no failures) is now explained ONLY if
   conjecture (A) holds for the forms the normalization actually produces.
   (A) is the whole ballgame; there is no (B) safety net.
5. **Gate consequence.** The semantic oracle alone (language-level LTL-ness)
   is NOT a sufficient admission criterion in general — it is sufficient
   only in conjunction with the minimizing normalization, conditional on
   (A). The oracle doc's layer-14 caution ("delegation policy stays with
   the form reading") was right to be conservative; the precise discharge
   is: oracle-LTL + minimized form + (A) proved.

---

# Log 2026-07-04 (cont.) — Step 4 worked: the pair-closure argument

Direction (user): no exhaustive search; either state-minimality yields the
guarantee, or the failure is constructively explainable and the example
designable — or shown impossible. Also in play: the idea that OUR
minimization quietly replaced the paper's counter-freeness in a semantic
way. Status after this session: (A) not closed, but reduced to one
candidate closing theorem; two lemmas strengthened; every naive
counterexample design provably dies. D is min-size state-based (sbacc), L
star-free, throughout.

## 4.1 The pattern refines: the pair is a genuine group orbit

In the R-pattern (Step 1), x and y are not arbitrary: x = delta(iota, u
v^N), y = delta(x, v). Choosing N so that f = st_{v^N} is idempotent, both
x and y are f-fixed, and t = st_v restricted to Fix(f) is a permutation
with y = t(x): the pair sits on a genuine cyclic orbit realized by the
word v (reading v^p from x returns to x). The toggling lasso is u v^n rho.

## 4.2 Step 2' — the automorphism lemma strengthens to closed regions

Lemma 2'. Min-size forbids a mark-preserving automorphism phi of ANY
delta-closed region R (not just global ones). Proof: quotient only R by
phi-orbits; delta-consistency inside R is phi-equivariance; in-edges from
outside R redirect to the class of their target; determinism is preserved;
a run entering R projects onto the quotient run, and with state-based
acceptance and phi mark-preserving, the inf-mark behavior is unchanged, so
the language is unchanged and the automaton got smaller. QED.

This upgrades the padding argument: any LOCAL mark-preserving phase
symmetry in the reachable closure of the pair is fatal to minimality.

## 4.3 The dichotomy: set-equal vs set-different pair cycles

Consider the pair closure P from (x, y) (product dynamics; diagonal
absorbing). On the discrepancy lasso rho the pair sequence eventually
enters a recurrent pair-cycle with component cycles C1 (x-side) and C2
(y-side), both reading the same loop word. Two cases:

- C1 = C2 AS SETS (same cycle entered at shifted phase). No recurrence
  discrepancy exists — both runs visit the same states i.o. This is
  exactly gf_aa_parity: its pair closure from (0,2) has the single
  non-diagonal cycle ((0,2),(2,0)), set-equal, and !a hits the diagonal.
  Transient discrepancies are harmless for Fin.
- C1 != C2 as sets, q0 in C1 \ C2. This IS the contradictor.

So (A) restates cleanly: **in a min-size state-based form of a star-free
language, every residual-equal-seeded recurrent pair-cycle is set-equal.**

## 4.4 The constraint cascade on a would-be counterexample

Chasing the design through the lemmas (each attempted concrete automaton
below died to the named constraint):

1. Verdict-blindness is automatic and is NOT extra information: "all
   ultimately-periodic continuations get equal verdicts from x and y" is
   literally L(x) = L(y). The leak lemma is its transport to L's
   star-freeness via the v-pump.
2. The separate-loops letter (b: x->..->x and y->..->y, cycles disjoint —
   the eternal-discrepancy carrier) leaks INSTANTLY unless the two b-cycles
   are verdict-equal: unequal cycle verdicts separate residuals, the v-pump
   turns that into a counting family for L. Adding such a letter to
   gf_aa_parity (b as identity) makes b^omega accept from 0 and reject
   from 2 — L stops being star-free on the spot. The padded fixture dodged
   this only by mark-SYMMETRIC cycles, which is Step 2' food.
3. So the twin cycles must be verdict-equal with DIFFERENT mark sets
   (e.g. 2-cycles marked at shifted positions — verdict-equal for Buchi,
   set-different, mark-different). Every explicit 4-state attempt at this
   (two coupled Z2's, swap letter a, loop letter b, marks at shifted
   positions) turned out phi-equivariant for the shifted-mark isomorphism
   psi (x1<->y2, x2<->y1) — psi extends over the swap letter automatically
   in every symmetric wiring — and dies to Step 2'.
4. What the survivor must therefore be: twin recurrent cycles, verdict-
   equal in every context, mark-set-different, admitting NO mark-
   isomorphism of the delta-closed region containing them, plus min-size
   of the whole automaton. Note gf_aa_parity already realizes
   "residual-equal, unmergeable, mark-asymmetric, no mark-preserving
   automorphism, min-size" — everything EXCEPT set-different recurrent
   twin cycles. The entire question now lives in that one ingredient.

## 4.5 The candidate closing theorem

Conjecture (rotation-iso). For state-based acceptance: if two disjoint
recurrent cycles reading the same loop word are verdict-equal under EVERY
context (entry offsets and exit words), then some rotation-style alignment
of them is a mark-isomorphism of the omega-recurrent closure.

If true, (A) follows: the contradictor's twin cycles admit a mark-iso of a
closed region (transients cannot carry the discrepancy), Step 2' contradicts
min-size, done. The natural tool is the oracle's rotation lemma
(`definability/oracle/algorithm.md` layer 5): conjugacy already moves loop
profiles around cycles with right-extensions only; the missing step is
lifting profile equality to a state-level isomorphism on the recurrent
part. This is where the argument currently stops.

## 4.6 On "minimization replaced counter-freeness semantically"

The emerging shape supports the intuition, with a precise reading:
counter-freeness says NO groups in the form; minimization (via Step 2')
says no SYMMETRIC groups — every group whose phases are mark-equivalent is
folded. What survives minimization is exactly the mark-load-bearing groups
(parity's Z2), and those are precisely the ones our experiments show the
cascade tolerating — their discrepancies are transient/set-equal, i.e.
invisible to Fin questions. Minimization is a semantic filter: it keeps a
group only when the group carries mark-placement content, and (if the
rotation-iso conjecture holds) mark-placement content forces set-equal
recurrence, which Fin cannot see. That is the subtle sense in which
"minimized" stands in for "counter-free": not by removing groups, but by
removing exactly the groups whose recurrence would be Fin-visible.

## Next

- Prove or refute the rotation-iso conjecture (4.5). Attack: two disjoint
  same-word verdict-equal-in-all-contexts cycles; use the enriched element
  of the loop word and its rotations; show mark profiles must align under
  some power of the rotation, then extend the alignment over the recurrent
  closure by determinism. Refutation would hand us the counterexample
  blueprint directly (the wiring my symmetric attempts could not reach).
- If proved: assemble (A) end-to-end (Steps 1, 2', 4.3, 4.5) and state the
  gate discharge: oracle-LTL + min-size sbacc form => cascade sound.
- The omega-power branch of Step 1 still needs its conjugation paragraph.

---

# Log 2026-07-04 (cont.) — 4.5 attacked from the refutation side: three stags, one death mechanism

Attempted to build the counterexample ("the stag": twin same-word antler
cycles, verdict-equal, mark-set-different, no mark-iso). Three designs,
each killed — and the deaths align into a single structural reason that
now looks like the missing proof step.

## Stag 1 — shifted marks, 4 states (samples/fixtures/hoa/definability/stag1.hoa)

Antlers b: x<->x1, y<->y1; swap a: x<->y; symmetry broken at y1-a->x
(equivariant would be y1-a->x1); marks alpha = {x1, y} (shifted so the
aligned pairing is not mark-preserving). Hand-checked verdict-equality on
five lasso families. The SOSG oracle (tests/probes/oracle_dump.py) is the
right judge and answered instantly: det_generic_minimal has ONE state — L
is UNIVERSAL. Reject-cycles would have to avoid alpha, i.e. live inside
{x, y1}, which has no cycle. Dead: maximally non-minimal.

## Stag 2 — marks on the tips, 4 states (paper only)

Same skeleton, alpha = {x1, y1}. Now a^omega rejects (cycle {x,y} unmarked)
and L is non-trivial. Worked the language out by hand: reject iff the tail
is a-only, i.e. L = GF(!a). Star-free, yes — but recognizable with 2
states, so the 4-state stag is fat: not min-size. (Notably NOT
bisimulation-reducible — x and y have marks-differing successors — the
shrink needs SAT-min. The stag survives cheap reduction and dies to
minimality proper.)

## Stag 3 — two non-isomorphic bb-detectors, 6 states (paper only)

The most principled attempt: L = GF(b & Xb); antler sides = the two
non-isomorphic 3-state recognizers of it (the gf_aa-style aperiodic form
and the gf_aa_parity-style shifted form), linked by a side-swapping reset
letter a. Sides never merge (every letter preserves-or-swaps the side), all
states residual-equal, and the sides are structurally non-isomorphic — no
automorphism exists at all, dodging Step 2' completely. Dead anyway: L is
GF(b & Xb), recognizable in 3 states; the side bit is fat; not min-size.

## The common death: verdict-dead bits fold

Why every stag's language collapses to something smaller than its body,
articulated once:

1. For state-based acceptance (Buchi/parity/EL over Inf/Fin of states),
   the verdict of a run depends ONLY on its i.o.-set; transient states and
   transient marks are verdict-dead. A recurrent cycle's verdict is
   intrinsic (entry-point-independent): Buchi reads C-cap-alpha != empty,
   parity reads min color on C — no memory of how the cycle was entered.
2. The stag's side-bit (which antler am I in) is verdict-dead by
   construction on the recurrent part (verdict-equal twins) and cannot
   earn relevance from transients (1). So the side distinction never
   influences any verdict from any start: it is globally verdict-dead.
3. In every construction, a recognizer without the side bit therefore
   existed, and min-size rejected the stag.

## Upgraded conjecture (the dead-bit fold) — the remaining formal gap

Conjecture 4.5'. In a min-size deterministic state-based automaton, there
is no globally verdict-dead distinction: any equivalence on states that is
delta-closed-as-a-pairing (the pair closure of a residual-equal pair) and
never influences a verdict admits a strictly smaller recognizer of L.

If 4.5' holds, (A) follows for the pipeline's forms: the contradictor's
set-different twin cycles are exactly a globally verdict-dead distinction;
4.5' hands the smaller recognizer; min-size contradiction; every Fin(q0)
of a min-size state-based form of a star-free language is star-free.

What is genuinely missing: the general FOLD construction. The naive
quotient by the pairing is mark-inconsistent precisely in the interesting
(mark-shifted) cases — the smaller recognizer in the examples was found by
re-recognizing L, not by quotienting D. Two candidate routes:
- via omega-semigroup recognition: L star-free + verdict-dead side-bit =>
  the syntactic morphism factors through the side-collapsed monoid; bound
  the min-size recognizer by the factored object (this would use
  star-freeness a second time, which feels right — 4.5' may be false for
  general omega-regular L and true under aperiodicity);
- via a marked-product construction: run the folded semiautomaton and
  re-derive marks from a bounded window (the gf_aa vs gf_aa_parity lesson:
  shifted marks recognize the same threshold language — maybe provably
  always re-markable on the folded carrier).

Note the loop that worked here: design stag -> oracle judges (exact,
instant, with certificates) -> death mechanism extracted -> conjecture
sharpened. stag1.hoa kept as the fixture record of the method.

## Next

- Prove 4.5' (either route), or find the stag that gives the side bit a
  verdict-live duty somewhere while keeping it verdict-dead from the pair
  — the two routes above say precisely what such a beast must defeat.
- The omega-power branch of Step 1 still owes its conjugation paragraph.
