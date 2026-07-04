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

---

# Log 2026-07-04 (cont.) — Literature: the tension is a named phenomenon, and the canonical object is prophetic, not minimal

Direction (user): the census avenue is stale (natural search over reachable
sizes turned up no counterexample despite trying; the stag constraints push the
minimal witness past a small sweep). Back to pen/paper via the literature. This
entry records what the in-hand papers already settle and how they reshape (A).
Three new PDFs pulled into `papers/` (pdftotext'd alongside): Carton–Michel 2003
(`Carton_Michel_2003_TCS`), Löding 2001 (`Loding_2001_IPL`), Schewe 2010
(`Schewe_2010_FSTTCS`).

## Diekert–Gastin 2008 §11 — our tension is KNOWN, and ω-specific

`papers/Diekert_Gastin_2008.txt`, "Counter-free and aperiodic Büchi automata":

- **Lemma 11.2** (classical, McNaughton–Papert): over FINITE words the *minimal
  DFA* of an aperiodic language IS counter-free. Deterministic + minimal ⟹
  counter-free — cleanly true on finite words.
- **Lemma 11.6**: for DETERMINISTIC automata, counter-free ⟺ aperiodic
  transition monoid (nondeterministic: only cf ⟹ aperiodic). Def. 11.5 gives the
  weaker "aperiodic" notion for the nondeterministic direction.
- **Remark 11.13** (our exact crux, stated as settled): *"There is no canonical
  minimal Büchi automaton for languages of infinite words,"* and a *minimal-size*
  automaton of an aperiodic ω-language *need not be counter-free*. Their witness
  (L = {ε,a²}∪a⁴a*, Fig. 3) is finite-word/nondeterministic; `gf_aa_parity` is
  the DETERMINISTIC-ω instance of the same fact — a state-minimal parity form of
  a star-free language carrying a Z2.
- **Prop. 11.4 / 11.11**: L aperiodic ⟺ recognized by *some* counter-free Büchi
  automaton — but the construction routes through a ⋃ U·Vω union and yields a
  (generally nondeterministic) counter-free BA that is NOT the minimal
  deterministic form the pipeline feeds the cascade.

Consequence: the finite-word "min ⟹ counter-free" (Lemma 11.2) provably does NOT
lift to ω. Conjecture (A) is therefore not resolved by "just minimize"; the very
object our gate relies on (state-minimal deterministic ω-form) is the one Diekert–
Gastin flag as non-canonical and possibly non-counter-free.

## Preugschat–Wilke 2013 / Carton–Michel — the RIGHT canonical object

`papers/Preugschat_Wilke_2013_LMCS.txt` builds on **Carton–Michel automata**
(prophetic / strongly-unambiguous complete Büchi: any infinite word labels
exactly one path visiting final states i.o. — `papers/Carton_Michel_2003_TCS`,
main theorem: every rational ω-set is so recognized). These are CANONICAL and
"separate the finitary fraction from the infinitary fraction" (§3):

- **left quotient** (reverse semi-DFA via the left congruence ≡A) = finitary
  fraction;
- **loop language** LL(q) = ⋃_{q'≡A q} S(q') = "all loops at q and congruent
  states" = infinitary fraction — this IS our per-state recurrence object, in
  canonical congruence-collapsed form;
- **Theorem 3.2**: an LTL formula lies in a temporal-operator fragment ⟺
  forbidden-pattern conditions on the left quotient + conditions on the loop
  languages. Star-freeness (full LTL) is the aperiodicity end of this table.

So the finitary/infinitary split that (A) needs — residual part vs recurrence
part, each screened for star-freeness — is a THEOREM on the prophetic form, not
on the minimal-deterministic form.

## The three new papers, and what each pins down

- **Carton–Michel 2003** — source of the prophetic canonical automaton; the
  object to read for a recurrence/loop-language star-freeness lemma (does the
  enrichment "mark one state, ask visited-i.o." stay aperiodic on this form?).
- **Löding 2001** — deterministic *weak* ω-automata are the ONE class with a
  unique minimal automaton (O(n log n), via DFA minimization). Confirms
  explicitly: "for ω-automata in general there is no unique minimal automaton and
  no congruence characterization as for DFA." Our Büchi/parity forms are outside
  the clean class.
- **Schewe 2010** — minimising deterministic Büchi/parity automata is
  NP-complete; introduces "almost equivalence" (strictly between DFA- and
  DBA-language-equivalence). Hard evidence backing Remark 11.13: no cheap
  canonical minimal form exists, so a gate resting on "the" minimized form rests
  on a non-canonical, expensive-to-certify object.

## Reframe of the program

(A) is currently phrased over the *minimal deterministic* automaton — the object
the literature says has no clean theorem (non-canonical; min ≠ counter-free;
NP-hard to reach). The clean statement lives on the **prophetic (Carton–Michel)
form**, where loop languages carry recurrence and star-freeness is a per-part
condition (Preugschat–Wilke Thm 3.2). Two readings:

1. The bridge to prove: relate the cascade's `Fin(C)` over the min-deterministic
   form's configs to the prophetic form's loop languages. If min-det `Fin(C)`
   star-freeness follows from loop-language star-freeness, (A) closes.
2. Or the gate belongs on the prophetic form outright — screen the loop languages
   (Preugschat–Wilke's decidable conditions), not the min-deterministic reading.
   This would replace 4.5' (dead-bit fold on min-det) with a loop-language
   screen, sidestepping the NP-hard minimality dependence entirely.

Either way, 4.5' likely relocates OFF the minimal deterministic automaton and
ONTO the loop languages. The dead-bit-fold intuition survives as: minimization
folds mark-symmetric groups, and the surviving mark-load-bearing groups have
set-equal (finitary/infinitary-separable) recurrence — exactly what the prophetic
form makes a language invariant.

## Next

- Read `Carton_Michel_2003_TCS` for a recurrence-preservation / loop-language
  star-freeness lemma (the "mark one state" enrichment on the prophetic form).
- Hand the browser-LLM query (below) out for anything post-2013 that states the
  loop-language star-freeness of a canonical ω-form of a star-free language
  directly.
- Hold the theoretical attack on 4.5' and the ω-power branch until the prophetic
  reframe settles which object 4.5' should live on.

### Browser-LLM literature query (kept for the record)

> Fix a state-based deterministic parity/Büchi automaton D for a star-free
> ω-language L (aperiodic syntactic ω-semigroup; FO/LTL-definable), state-minimal
> in its acceptance class. For state q let Inf_q = {w : run of D on w visits q
> i.o.}, recognized by the SAME transition structure with Büchi condition {q}. Is
> Inf_q necessarily star-free whenever L is? Equivalently: can the transition
> monoid of a state-minimal deterministic ω-automaton of a star-free language
> carry a group making some per-state recurrence condition non-aperiodic, or does
> minimality confine every surviving group to acceptance-symmetric positions
> where recurrence sets are unaffected? Known: (Diekert–Gastin 2008) finite-word
> minimal DFA of an aperiodic language is counter-free, but for ω there is no
> canonical minimal automaton and a minimal-size aperiodic ω-automaton need not be
> counter-free; (Preugschat–Wilke 2013 / Carton–Michel prophetic automata) the
> canonical prophetic automaton separates a finitary from an infinitary fraction,
> loop languages capturing recurrence. Want: (1) any theorem that per-state
> recurrence / per-SCC loop languages of a canonical/minimal ω-automaton of a
> star-free language are themselves star-free; (2) preservation of
> star-freeness/aperiodicity under the "add a Büchi/parity mark on one state"
> enrichment of a fixed deterministic transition structure; (3) canonicity /
> minimization results for deterministic parity/Büchi automata bearing on whether
> transition-monoid groups survive state-minimization.

---

# Log 2026-07-04 (cont.) — Investigating the papers: the group is forced into residual fibers

Read for structure (not re-derived): `Carton_Perrin_Pin_2008` (ω-semigroups,
linked pairs, prophetic automata §7), `Preugschat_Wilke_2013` (loop-language
schema), `Carton_Michel_2003` (prophetic construction), `Loding_2001` (weak
minimal), `Schewe_2010` (Büchi/parity min NP-complete). What the papers give,
and the one new structural theorem the ω-semigroup view hands us.

## What each paper does / does NOT give us

- **Carton–Michel 2003** — the *construction* of prophetic (co-deterministic,
  co-complete) Büchi automata: every ω-word labels exactly one final path. It is
  the canonical-object existence result, NOT a star-free characterization. No
  aperiodicity/loop-language lemma here to lift directly.
- **Preugschat–Wilke 2013** — the schema we want, but only for PROPER fragments
  ({X},{F},{XF},{X,F},{U}). Table 1: fragment membership ⟺ (forbidden-pattern
  condition on the left quotient = finitary part) ∧ (loop languages lie in a
  *-language class: 1-locally-testable / locally-testable / stutter-invariant).
  The FULL-LTL (star-free) row is not tabulated — they explicitly exclude the
  top fragment. But the schema's shape is unambiguous: the analog star-free row
  is "left quotient counter-free ∧ every loop language star-free." Loop languages
  = infinitary fraction, computed on the prophetic GCMA.
- **Carton–Perrin–Pin 2008** — the ω-semigroup backbone. Linked pair (s,e):
  se=s, e²=e, realising u·vω with s=φ(u), e=φ(v). L star-free ⟺ its syntactic
  ω-semigroup has aperiodic +-part (via Thomas [33]). Prophetic = co-deterministic
  + co-complete (§7.2). Gives vocabulary + backbone, no ready (A).
- **Löding 2001** — deterministic WEAK ω-automata are the ONE class with a
  unique minimal automaton (Myhill–Nerode-style congruence, O(n log n) via DFA
  min). Confirms explicitly the others have no congruence characterisation. Our
  breaking cases (GFa recurrence, gf_aa Büchi) are Büchi-proper, OUTSIDE the weak
  class — so no canonical min to lean on for them.
- **Schewe 2010** — minimising deterministic Büchi/parity is NP-complete;
  "almost equivalence" (agree except finitely often) is the finitary/infinitary
  boundary made precise. Reinforces: a gate resting on "the" minimised form rests
  on a non-canonical, NP-hard-to-certify object.

## New theorem (ω-semigroup): the group lives in residual fibers

The right congruence u ~ v ⟺ u⁻¹L = v⁻¹L (residual ω-languages) has finitely
many classes and its transition monoid DIVIDES the syntactic ω-semigroup's
+-part S+. For star-free L, S+ is aperiodic, so:

> **(R-aperiodicity)** In ANY deterministic recognizer D of a star-free L, the
> residual-action monoid is aperiodic. Hence every group in TM(D) acts trivially
> on residuals — it is confined to a single residual class (states x≠y with
> L(x)=L(y)).

This is exactly Step 1's R-pattern seed, now DERIVED rather than reduced-to: the
contradictor's group pair (x,y) is forced to be residual-equal because a group
cannot show up in the (aperiodic) residual quotient. The group in a min-det form
of a star-free language is a pure ACCEPTANCE-DETECTION group: it tracks the
transient positional info the automaton needs to DETECT the acceptance pattern
(gf_aa: "was the last letter a", to see an aa-adjacency), invisible to residuals.

Corner confirmation this is minimality-essential, not automatic: the padded form
`gfa_pad2` (Exp 3) is a deterministic recognizer of star-free GFa with Inf((q,i))
non-star-free — so (A) is FALSE for arbitrary deterministic D and genuinely needs
minimality. Its padding group is residual-trivial AND acceptance-invisible (a
mark-preserving automorphism) — the dead bit that minimality is supposed to fold.

## Where this leaves (A) — the chain is complete up to one link

1. L star-free ⟹ residual monoid aperiodic ⟹ any TM(D) group sits in a residual
   fiber (R-aperiodicity, above; = Step 1 seed, now a theorem).
2. Leak lemma (Step 3): if the fiber group's phase were visible to L-acceptance
   from that class under any continuation, L(x)≠L(y) — contra (1). So the group
   is acceptance-invisible from its own class: globally L-invisible (residual-
   invisible by (1), acceptance-invisible by (3)).
3. Sweep/phase (Step 4): pumping the group generator sweeps the whole orbit, so
   the i.o.-set of a group-loop is phase-invariant (set-equal, harmless to Fin).
   Phase-dependence of some Inf_q can only enter via a DIFFERENT loop word the
   group permutes into distinct fates (mod3's !a) — but mod3's L is non-star-free,
   i.e. that fate-difference IS a residual/acceptance leak, excluded by (1)-(2)
   for star-free L.
4. THE OPEN LINK (4.5' / rotation-iso, unchanged): a globally L-invisible
   within-fiber group must FOLD at minimality (admit a mark-preserving quotient
   of its delta-closed region). Löding gives this for the weak class (canonical
   min). For Büchi/parity it is exactly the dead-bit-fold conjecture, and the
   papers do NOT close it — Schewe says minimisation there is genuinely hard, so
   the fold, if true, is not a cheap congruence collapse.

## Consequence / reframe sharpened

Two clean routes remain, both better-founded now:

- **Prophetic gate (sidesteps (4)).** Prove the star-free analog of the
  Preugschat–Wilke schema: L star-free ⟺ prophetic left quotient counter-free ∧
  every loop language star-free. On the canonical prophetic form this is a
  language invariant (no minimisation dependence, no NP-hardness). Then screen
  the gate on the prophetic loop languages, not the min-det reading. This is the
  most promising concrete target — likely assembling from Thomas [33] +
  Preugschat–Wilke's machinery rather than needing new mathematics.
- **Min-det closure (needs (4)).** Prove the dead-bit fold for Büchi/parity: a
  globally verdict-dead within-fiber group folds under state-minimality. This is
  the harder, bespoke ω-semigroup argument; Schewe is the warning that it cannot
  be a one-line congruence.

Net: the literature CONFIRMS the tension is real & ω-specific, DERIVES the
R-pattern seed as a theorem (groups forced into residual fibers), and localises
the entire remaining gap to link (4). No paper contains (4); the prophetic route
is the way to make the gap disappear rather than close it head-on.

---

# Log 2026-07-04 (cont.) — The prophetic result: loop languages of a star-free ω-language are star-free

Pursuing the prophetic route (the clean, canonical, minimisation-free object).
Read the precise machinery: Preugschat–Wilke §2–3 (CMA/GCMA, loops, anchor,
loop language) and Carton–Michel §6.3 (the semigroup construction of the
prophetic automaton). A proof architecture for the standalone result emerges —
the ω-analog of Schützenberger/McNaughton–Papert with the RIGHT canonical object.

## Definitions nailed (Preugschat–Wilke §2, Carton–Michel §6.3)

- **CMA** (Carton–Michel automaton): every ω-word has EXACTLY ONE final run
  (prophetic = co-deterministic + co-complete). Canonical where minimal-
  deterministic is not.
- **Loop at q**: u ∈ A⁺ with u·q = q and u passes through a final state
  (∃ v,w: vw=u, wq ∈ F). S(q) = loops at q.
- **Anchor (CM Lemma 2.2)**: every u ∈ A⁺ is a loop at EXACTLY ONE state uↅ.
  So {S(q)} PARTITIONS A⁺ — a finite partition, an anchor map A⁺ → Q.
- **Loop language** LL(q) = ⋃_{q'≡q} S(q'), ≡ the left congruence (finitary
  fraction). LL(q) = the infinitary fraction; regular (PW §7: unions recognised
  by reverse DFAs).
- **Linked pair / conjugacy (CM Prop 60)**: [s₁,e₁]=[s₂,e₂] ⟺
  φ⁻¹(s₁)φ⁻¹(e₁)ω ∩ φ⁻¹(s₂)φ⁻¹(e₂)ω ≠ ∅. Conjugacy classes S̃ = the ω-word
  "types"; φ extends to φ: Aω → S̃. Chain expansion (CM §6.3.2): the prophetic
  automaton's states are the strict R-chains Ŝ of S, with a left action of A*
  factoring through S (Prop 69).

## Theorem (P) [target]: LL(q) star-free when L is star-free

**Claim.** For a star-free L with syntactic ω-semigroup (S₊ aperiodic), every
loop language of the canonical (chain-expansion) prophetic automaton is
star-free. Equivalently the canonical prophetic automaton is COUNTER-FREE — the
ω-analog of "min DFA of an aperiodic finite-word language is counter-free"
(Diekert–Gastin Lemma 11.2), with the prophetic automaton replacing the (non-
existent) minimal deterministic ω-automaton.

**Proof architecture (two routes, one crux each).**

Route A — via φ-saturation (cleaner):
1. A loop u at q is a PURELY RECURRENT object: u·q = q, no transient. Its type is
   the linked pair (φ(u), e), e = φ(u)^π (idempotent power, well-defined in the
   finite S₊).
2. CRUX (SAT): S(q), hence LL(q), is saturated by φ — u ∈ LL(q) depends only on
   φ(u). Justification: loops ↔ linked pairs, and linked-pair conjugacy classes
   are φ-determined (Prop 60), so words of equal φ-image anchor at ≡-equivalent
   states. (The chain φ̂(u) that breaks saturation for TRANSIENT prefixes is
   absent for a loop — u fixes its state.)
3. Then LL(q) = φ⁻¹(X) for X ⊆ S₊. S₊ aperiodic ⟹ LL(q) star-free
   (Schützenberger: recognised by an aperiodic monoid ⟹ star-free). ∎

Route B — via counter-freeness of the chain automaton:
1. The prophetic automaton's transitions = left action of A* on strict R-chains
   Ŝ, factoring through S₊ (Prop 69); it is a deterministic (co-deterministic)
   action, so aperiodic ⟺ counter-free (Diekert–Gastin Lemma 11.6.2).
2. CRUX (EXP-AP): the left action of an aperiodic S₊ on its R-chains is aperiodic
   — (left-mult by φ(u))^n stabilises on chains because φ(u)^n = φ(u)^{n+1} in
   S₊ and the R-order reduction = is deterministic (adds no period). [Care: this
   is the aperiodicity-preservation of the R-chain expansion; must be checked,
   not assumed — Rhodes-type expansions need not preserve aperiodicity in
   general, but this specific left-action quotient plausibly does.]
3. Counter-free automaton ⟹ its finite-word loop languages aperiodic ⟹
   star-free. ∎

Route A is preferable: it sidesteps the expansion-aperiodicity technicality and
uses only Prop 60 + Schützenberger. The single load-bearing lemma is (SAT):
loop languages are φ-saturated.

## Consistency check against the fixtures (by hand, no run)

- **gf_aa_parity** (L = GF(a∧Xa), star-free, S₊ aperiodic): (P) predicts the
  prophetic loop languages star-free — matches Exp 2, where every Fin(C) built
  correctly and the GT languages were LTL. The Z2 lived only in the min-det
  form, not in S₊; the prophetic form has no group.
- **mod3_a** (non-star-free, S₊ has Z3): (P)'s hypothesis fails (S₊ not
  aperiodic), so loop languages need not be star-free — matches Exp 2's two
  non-LTL Fin sub-terms. Consistent: the group is REAL in S₊ here, not a form
  artifact.
- **gfa_pad2** (L = GFa star-free; non-minimal det form, Inf non-star-free):
  (P) still predicts the PROPHETIC loops star-free — the non-star-free Inf is a
  pure artifact of the padded min-det form, exactly as (P)'s canonical-object
  framing says. The padding group is absent from S₊.

All three consistent: the group that matters is the one in S₊ (⟺ L non-star-free);
groups in a deterministic FORM beyond S₊ are artifacts the canonical prophetic
object does not carry.

## What (P) does and does NOT settle

- SETTLES (modulo lemma SAT): the per-state recurrence question is star-free on
  the canonical prophetic form whenever L is — the intuition from literature
  item 4 ("canonical objects make per-state questions language invariants") is a
  theorem, not a hope. This is a clean standalone result worth writing up: the
  ω-word Schützenberger analog stated on prophetic automata, filling the gap
  Diekert–Gastin Remark 11.13 leaves open (no canonical minimal automaton) with
  the RIGHT canonical object.
- Does NOT yet settle (A) for the TOOL: the cascade runs on the min-DETERMINISTIC
  form, a different automaton from the prophetic one. (P) proves the target is
  clean canonically; the residual work is the BRIDGE — relate the min-det form's
  Fin(C) to the prophetic loop languages. gfa_pad2 shows a NON-minimal det form
  breaks, so the bridge must use state-minimality (this is exactly link (4), now
  with a known-clean target to aim the fold at).

## Next

1. Prove lemma SAT rigorously (Route A): loop languages are φ-saturated. Needs
   the precise chain-state definition (CM §6.3.3, unread) to confirm S(q) unions
   to φ-classes. This closes (P).
2. Draft (P) as a standalone statement/proof once SAT lands — the McNaughton–
   Papert-for-ω-via-prophetic-automata result.
3. The bridge for (A): does state-minimality of the deterministic form force its
   recurrence structure to be a quotient of the prophetic loop structure (so
   min-det Fin(C) inherits star-freeness from prophetic LL)? This is link (4)
   re-aimed: fold the min-det "extra" groups against the clean prophetic target.

---

# Log 2026-07-04 (cont.) — (P) PROVEN: the canonical prophetic automaton of a star-free ω-language is counter-free

Read Carton–Michel §6.3.3 (the automaton A_S built from a recognizing
semigroup). It supplies a rigorous proof of (P) — and the route is NOT the
SAT-saturation lemma of the previous entry (that one is false as stated: the
anchor's chain coordinate genuinely depends on φ̂(u), not φ(u)). The clean
route is the transition-monoid one, and Prop. 70 makes it rigorous. Correcting
the record and recording the finished proof.

## The construction (CM §6.3.3), exactly

Given L = φ⁻¹(P) ⊆ Aω, φ: A⁺ → S a recognizing morphism, P ⊆ S̃ (conjugacy
classes of linked pairs). The prophetic automaton:

  Q = { ([s,e], (s₁,…,sₙ)) ∈ S̃ × Ŝ  |  s R sₙ }
  transitions read letter a by the LEFT ACTION on both coordinates:
      a·[s,e] = [φ(a)s, e]                       (first coord)
      a·(s₁,…,sₙ) = =(φ(a), φ(a)s₁, …, φ(a)sₙ)   (second coord, R-order reduce =)
  co-deterministic + complete; one final-set F (final transitions:
      φ(a)s D e AND the chain step is "cutting").
  Run of x visits state (φ(xᵢ), φ̂(xᵢ)) at position i — a function of the SUFFIX.

Two coordinates: [s,e] = the RECURRENT type (linked pair = which ω-behavior);
(s₁,…,sₙ) = the strict R-chain = finitary prefix bookkeeping (φ̂, not a
morphism).

## Proof of (P): S aperiodic ⟹ A_S counter-free ⟹ loop languages star-free

Take S = the syntactic ω-semigroup of L; L star-free ⟺ S₊ aperiodic
(Thomas / Perrin–Pin). Show the transition monoid of A_S is aperiodic, i.e.
(u-action)ⁿ = (u-action)ⁿ⁺¹ on Q for n large, coordinatewise:

- FIRST coordinate. (u-action)ⁿ[s,e] = [φ(u)ⁿ s, e]. S₊ aperiodic ⟹
  φ(u)ⁿ = φ(u)ⁿ⁺¹ for n ≥ |S₊| ⟹ stabilises. (This is literally the left-
  regular representation of S₊ on the s-coordinate — aperiodic iff S₊ is; this
  is where a group in S₊, i.e. L NON-star-free, would break it.) ✓

- SECOND coordinate (the expansion — the only nontrivial step). By Prop. 70,
  once the path uⁿ·c accumulates more than |c| ≤ |S| cutting transitions,
  uⁿ·c = φ̂(uⁿ). Cutting MUST accumulate (chains are length-bounded by |S|, so
  a non-cutting period would grow the chain past the bound), so for n ≥ N,
  uⁿ·c = φ̂(uⁿ). And φ̂(uⁿ) is eventually constant in n because φ(uᵏ)
  R-stabilises at the idempotent φ(u)^π. Hence uⁿ·c = uⁿ⁺¹·c for n large,
  INDEPENDENT of the starting chain c. ✓

Both coordinates aperiodic ⟹ transition monoid of A_S aperiodic. A_S is
co-deterministic, and counter-freeness (Diekert–Gastin Def. 11.1) is
reversal-invariant, so aperiodic transition monoid ⟹ A_S counter-free
(DG Lemma 11.6.2 on the reverse). ∎ (counter-free)

Loop languages: S(q) = { u ∈ A⁺ : u·q = q and some factorization u = vw has
w·q final } is recognised by the (aperiodic) transition monoid enriched with a
monotone "crossed a final transition" bit — the enrichment stays aperiodic
(absorbing bit, no group; the oracle-layer-8 phenomenon). Recognised by an
aperiodic monoid ⟹ star-free (Schützenberger). LL(q) = ⋃_{q'≡q} S(q'), a finite
union ⟹ star-free. ∎ (P)

## The theorem, stated

> **(P) / prophetic Schützenberger.** For the canonical Carton–Michel prophetic
> automaton A_S built from the syntactic ω-semigroup of an ω-regular L:
> A_S is counter-free  ⟺  S₊ aperiodic  ⟺  L star-free.
> Consequently every loop language LL(q) (the per-state recurrence / infinitary
> fraction) of A_S is star-free whenever L is.

This is the ω-word analogue of "the minimal DFA of an aperiodic finite-word
language is counter-free" (Diekert–Gastin Lemma 11.2), stated on the RIGHT
canonical object — the prophetic automaton — precisely where DG Remark 11.13
says the minimal DETERMINISTIC automaton fails to exist/be counter-free. The
group that can survive in a minimal deterministic form (gf_aa_parity's Z2) is a
forward-determinism artifact; the co-deterministic canonical form has no group
when L is star-free.

## Fixture check (unchanged, now against a proof)

- gf_aa_parity: L star-free ⟹ S₊ aperiodic ⟹ A_S counter-free ⟹ loop
  languages star-free. The Z2 was never in S₊.
- mod3_a: S₊ has a real Z3 (L non-star-free) ⟹ first-coordinate action
  non-aperiodic ⟹ A_S NOT counter-free ⟹ loop languages need not be star-free.
- gfa_pad2: L=GFa star-free ⟹ A_S counter-free; the padded min-det form's
  non-star-free Inf is a pure forward-form artifact, absent from S₊/A_S.
- CM's own examples confirm the ⟺: Ex 72 (aAω, S₁ left-zero = aperiodic,
  A_S counter-free) and Ex 73 (GFb, S₂ = U₁ aperiodic, A_S counter-free).

## Status

(P) is proven and is a clean standalone result (the prophetic Schützenberger
analogue). What remains for the TOOL is unchanged and now sharply posed: the
BRIDGE from A_S's loop languages to the min-DETERMINISTIC form's Fin(C) that the
cascade actually consumes. gfa_pad2 shows an arbitrary deterministic form breaks,
so the bridge must invoke state-minimality — the open link (4), now aiming the
"fold the extra forward-determinism groups" argument at a proven-clean target.

## Next

1. Write (P) up as a self-contained lemma+proof (candidate paper/appendix
   material): construction recap, the two-coordinate aperiodicity argument,
   Prop. 70 citation, the ⟺ statement, DG Remark 11.13 as the motivation.
2. The bridge (link 4): relate min-det Fin(C) to A_S loop languages under
   state-minimality. Concretely: is there a cover from the min-det form's
   config-recurrence to A_S's loops that transports star-freeness back?
