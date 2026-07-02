# Definability — the novelty investigation

*A research note around the syntactic ω-semigroup oracle
(`aut2ltl/bls/definability/oracle/algorithm.md`): is the construction new,
where does it sit in the literature, and what should we absorb from the
neighbors? Deliberately decorrelated from the source — abstract and
free-ranging.*

**Method.** The standalone prompt `oracle_litt.md` (repo root) is posed to
search-enabled online models; their digests come back as feedback and are
integrated here, round by round — each finding tagged with who asserts it
(*R1* = round 1 reviewer, *us* = our own reading), because reviewer claims
are leads, not evidence, until we confirm them against the papers first-hand
(reading queue, §5). Earlier in-house material: `non_ltl_certificates.md`
(the certificate's design rationale), `witness_log.md`.

---

## 1. The four novelty claims

Status values: `open` → `supported` / `nuanced` / `threatened` / `refuted`,
with the deciding source named.

| # | claim | status | notes |
|---|---|---|---|
| (a) | **Explicit implemented quotient construction** of `S(L)₊` | **supported, twice-narrowed** | invariant + effectiveness classical; R3 sharpens R1: Carton–Perrin–Pin *do* give a concrete high-level algorithm (max-plus matrix ω-semigroup from an NBA, then syntactic quotient by **saturation over all contexts**) — so claim "first *refinement-based*, deterministic-EL, implemented", not "first algorithm". Second narrowing: monoid-**closure** is implemented in the Ramsey-based inclusion line (us, D2). Unpreempted: refinement route + decision + implementation |
| (b) | **The `~lin`/`~ω` collapse** | **nuanced — reframe** | the finitary×infinitary *split* is not ours: Arnold's two-part congruence, Preugschat–Wilke's realization, the FORC/FDFA leading/progress structure (R1+R3, D3–D4; R3: "strongly anticipated but not preempted … a new, clean formulation"). Ours is the **right-only forward realization**: one Moore refinement of one seed, no left translation, licensed by the rotation lemma (§4.1). Claim the mechanism, credit the split |
| (c) | **Certified counting-family witnesses with replay** | **supported — strongest, 3/3** | all rounds concur; R3: "confirmed novel … no published precedent in this exact form", with the useful contrast that classical algebraic proofs exhibit a finite-order element in a group H-class but never package it replayable (D7). Frame as certifying algorithm (McConnell et al. 2011), lead with this |
| (d) | **First practical decider** | **supported, 3/3, hedged** | searched negative three times over (R1, R3: "very likely *the* first"; R2's contrary Spot claim was confabulation). Keep the "we are aware of no tool that…" phrasing until our own D6 sweep, but the claim is not under threat |

The characterizations themselves (LTL = FO[<] = star-free = aperiodic
syntactic ω-semigroup; Arnold's congruence; the counter-free deterministic
screen) are classical and claimed as such — Thomas 1979, Perrin 1984, Arnold
1985, Perrin–Pin *Infinite Words* 2004, Diekert–Gastin 2008. The claims are
about the *construction*.

## 2. The eight directions

### D1 — Explicit constructions of the syntactic ω-semigroup

*Does any publication give an actual algorithm for computing `S(L)₊` from an
automaton?*

**R1 verdict: nuances — mathematics classical, no implemented algorithm
found.** Arnold (1985) defines the coarsest recognizing congruence.
Carton–Perrin–Pin ("Automata and semigroups recognizing infinite words",
*Logic and Automata*, 2008) write the syntactic congruence explicitly — on
the `S₊` part the two conditions `xuyz^ω ∈ P ⇔ xvyz^ω ∈ P` and
`x(uy)^ω ∈ P ⇔ x(vy)^ω ∈ P` (exactly our layer-4 shapes), plus the one-sided
`S_ω` condition — and remark the ω-power matrix coefficients are effectively
computable. Perrin–Pin (*Infinite Words*, 2004) is the reference
presentation. None give a refinement procedure, element representation, or
complexity. Pécuchet (mid-1980s) and Wilke's algebras (right binoids, IJAC
1993) are in the same theoretical register.

**Our reading.** Consistent with what we know. Also worth a pass: Colcombet's
Green's-relations survey ("Green's relations and their use in automata
theory") for any effectiveness statement with more algorithmic content.
Consequence for (a): state invariant + computability as classical, claim the
implementation and the on-the-fly enriched route — and pre-narrow against the
closure precedent in D2.

*R2 pointer (weak, low priority):* syntactic semigroups are "sometimes
computed via wreath/block products rather than partition refinement" — no
reference given. Worth one search pass: any effective Krohn–Rhodes-route
computation of a syntactic (ω-)semigroup would be adjacent to both this
direction and the BLS cascade we already implement.

**R3 sharpening — the CPP algorithm is more concrete than R1 admitted.**
Per R3, Carton–Perrin–Pin (and the Perrin–Pin survey line) give an actual
algorithm: from a *nondeterministic* Büchi automaton, build the finite
ω-semigroup of matrices over the max-plus-style semiring `{−∞, 0, 1}`
(entries tracking path existence and `F`-visits), recognize `L` by the
morphism, then quotient by **saturation** — for all contexts `x, y, z`,
check the membership conditions directly. So the honest contrast for claim
(a) is *saturation over contexts* vs. *our single right refinement*: they
quantify contexts brute-force on the built algebra; we never enumerate a
left context at all. This is precisely what to verify first-hand in the
survey (reading queue #2): how explicit their quotient step really is, and
whether any complexity/data-structure remark accompanies it.

### D2 — The enriched monoid's lineage

*Who first stated that the acceptance-enriched transition monoid recognizes
`L` and surjects onto `S(L)₊`? Is a deterministic/EL variant written down?*

**R1 verdict: confirms the Büchi 1962 lineage; the deterministic mark-set
variant not found in print.** Carton–Perrin–Pin is the modern statement: to
each finite word a `Q × Q` matrix over a path semiring (no path / path /
path through accepting), an ω-operation via successful paths, a finite
ω-semigroup recognizing `L` and surjecting (after quotient) onto the
syntactic one. Our `q ↦ (δ(q,w), marks(q,w))` is the
deterministic-collapse-with-mark-sets instance — "close to folklore",
present it as the deterministic EL instance of the Büchi/CPP transition
ω-semigroup, a packaging contribution.

**Our reading — one addition R1 missed, and it moves claim (a).** The
Ramsey-based Büchi inclusion/universality line *implements* the closure of
exactly these enriched matrices: Fogarty–Vardi ("Büchi complementation and
size-change termination", TACAS 2009; "Efficient Büchi universality
checking", TACAS 2010), Abdulla et al. ("Advanced Ramsey-based Büchi automata
inclusion testing", CONCUR 2011) compute with "supergraphs"/"boxes" — state
pairs decorated with an accepting-visit bit — closed under composition, with
subsumption pruning. Size-change termination (Lee–Jones–Ben-Amram) is the
same monoid-closure shape. So "computing the transition ω-semigroup of an
automaton in a tool" **has precedent**; what that line never does is quotient
to the syntactic algebra, read aperiodicity, or decide definability. Honest
statement of (a): the closure is engineering with precedent, the **quotient
and decision** are the unpreempted part. Cite this line preemptively.

*R2 concurrence (weak but independent):* the mark-set element is "more
granular than the usual Muller transition profile" (set of states visited
vs. exact marks collected per start state), and the skeleton lemma for
Emerson–Lei "does not appear to be a direct rephrasing of standard
Muller/Rabin treatments" — reads as "likely novel as a construction tuned
for the EL acceptance native to Spot". Take as encouragement for the
packaging framing, not as evidence.

### D3 — Preugschat–Wilke and TL-fragment characterizations

*The closest neighbor: does their route anticipate the collapse?*

**R1 verdict: nuances, partially threatens (b); does not touch (a), (c),
(d).** Preugschat–Wilke ("Effective Characterizations of Simple Fragments of
Temporal Logic Using Carton–Michel Automata", FoSSaCS 2012; LMCS 9(2), 2013)
convert the input to a Carton–Michel automaton (reverse-deterministic,
prophetic: every ω-word has exactly one final run), then split: a **left
congruence** `≡_A` on states (equal sets of finite words driving into the
final-run structure) as the finitary factor, and **loop languages** `LL(q)`
(finite words closing an accepting loop at `q`) as the infinitary factor;
each fragment is a forbidden-pattern condition on the quotient plus a
language condition on the loops. That *is* the finitary×infinitary split.
Differences that matter: (i) their canonicalization is a left congruence on
a co-deterministic form — right-invariance comes free from co-determinism;
ours is two right congruences on a forward-deterministic form folded into
one refinement — right-only must be *earned* (the rotation lemma, §4.1).
(ii) They characterize the simple fragments ({X}, {F}, {XF}, {X,F}, {U}),
not full LTL; per R1, the {U}-fragment even takes TL-definability as a
*precondition*, citing Diekert–Gastin for that decision. (iii) No
implementation, no experiments, no certificates (EF games and forbidden
patterns, not replayable witnesses). Also cite Wilke, "Classifying discrete
temporal properties" (STACS 1999) as the classification predecessor.

**Our reading.** Agree this is the paper a knowing referee reaches for;
pre-empt it in related work exactly as R1 frames: the split is theirs (and
intrinsic to the ω-semigroup pair `(S₊, S_ω)` before them), the forward
right-only mechanism is ours. Verify first-hand: how effective their
construction actually is end-to-end (Carton–Michel conversion cost), and the
exact status of the {U} precondition — that detail carries weight for "full
LTL border is *our* output, their *input*". Their loop-language DFAs are an
independent cross-check of our `~ω` on shared fixtures (§4.4).

*R3 cross-check:* independently concurs on the essentials — fragments of
future LTL only, prophetic conversion with doubly-exponential worst case,
no implementation, no certificates, "does not threaten the novelty of the
full-LTL pipeline". R3 does *not* repeat R1's {U}-precondition claim, so
that detail remains single-sourced — still flagged for first-hand reading.

### D4 — Right congruences and FDFAs

*Does anyone decide star-freeness/LTL via right congruences or FDFAs?*

**R1 verdict: structural parallel, no definability decision found.** FDFAs
(Angluin–Boker–Fisman, MFCS 2016 / LMCS 2018): a leading right congruence +
per-class progress right congruences, built for Myhill–Nerode-style
correspondence — structurally our residuals + profiles. The thread:
Maler–Staiger (STACS 1993 / TCS 1997, corr. 2008) relating the simple right
congruence to Arnold's iteration congruence; Le Saëc's saturating right
congruences (1990); Angluin–Fisman's informative right congruences (IC
2021); the ROLL learning tool (Li et al.). All recognition, canonical forms,
learning — no star-freeness/aperiodicity decision, no "`~lin ∩ ~ω`, both
right-invariant, one refinement" statement found.

**Our reading.** Matches our knowledge; this stays the direction most likely
to hide a near-miss, so the Maler–Staiger and Angluin–Fisman papers are
high in the reading queue — specifically whether any of their canonical
right congruences *is* our `~lin` seed under another name (likely) and
whether anything plays the profile role (we believe not: that is where the
acceptance bit is "lifted just right"). Newer FDFA work (limit FDFAs, Li et
al. ~2023) worth a skim for the same reason.

*R3 precision (the strongest statement of the parallel so far):*
Maler–Staiger's **FORC** (families of right congruences) is the direct
ancestor of the leading-congruence idea; the **syntactic FDFA** takes the
syntactic right congruence as leading automaton, with progress DFAs
accepting exactly the `v` with `u·v^ω ∈ L` per class — "an FDFA is
*precisely* a leading right congruence plus per-class acceptance profiles".
Yet R3 confirms the whole line stops at representation/learning: no
star-freeness decision, no two-sorted syntactic extraction, no certificates.
The gap statement survives its sharpest formulation — good. Absorb item:
emit a **syntactic FDFA as an intermediate artifact** (§4.8).

### D5 — Complexity of the ω-decision

*Precise complexity of deciding LTL/FO-definability from deterministic
parity/Muller/EL, and from nondeterministic Büchi.*

**R1 verdict: anchors confirmed.** Cho–Huynh (TCS 88, 1991): finite-word
aperiodicity from a DFA is PSPACE-complete. Diekert–Gastin (2008) reduces
FO/star-freeness of an ω-language to aperiodicity. Selivanov–Wagner
(Fund. Inform. 2008): topological properties of regular ω-languages
NL-complete for deterministic forms, PSPACE-complete nondeterministic; per
R1 "aperiodicity specifically PSPACE-complete". Boker–Lehtinen–Sickert
(FoSSaCS 2022) is the converse map (counter-free deterministic → LTL,
double-exp nesting / triple-exp length, first elementary bound); they assume
aperiodicity, decide nothing, implement nothing — the gap they leave is
exactly our decision + implementation.

*R3 corroborates the suspicion:* R3 does **not** repeat R1's
Selivanov–Wagner aperiodicity attribution and states flatly that "precise
bounds … are not pinned down in one place; no single reference gives the
precise tight bound" — the ω-analog of Cho–Huynh is "at least PSPACE-hard
and in EXPSPACE (or better with on-the-fly methods)". Two rounds, and only
the unsourced one claims the result exists. §4.2 firms up as a theorem
candidate — and our on-the-fly analysis there is already sharper than R3's
"PSPACE in the monoid size" (elements are poly-sized; the guess-and-power
walk should give PSPACE in the *input*).

**Our reading — R1's Selivanov–Wagner sentence is suspect and the gap is an
opportunity.** "NL-complete for deterministic" cannot cover aperiodicity:
Cho–Huynh hardness is already *from a DFA* (deterministic input), and
finite-word star-freeness embeds into ω (`L ↦ L·#^ω` over `Σ ⊎ {#}`,
deterministic recognizer built directly), so aperiodicity from a
deterministic ω-automaton is PSPACE-hard. The NL results almost certainly
concern the topological/Wagner-hierarchy properties (where deterministic
Muller is indeed cheap — Wilke–Yoo). **Verify first-hand.** If no crisp ω
statement exists, our collapse plausibly *proves* the theorem
(PSPACE-completeness from deterministic EL) — see §4.2, promoted to a
result-candidate, not related work.

### D6 — Tool landscape

*Does any tool decide LTL-definability of an ω-automaton?*

**R1 verdict: supports (d), as a searched negative.** AMoRE (Kiel ~1995):
syntactic monoids + aperiodicity + star-freeness, finite words only, no ω
successor found. Spot: Manna–Pnueli hierarchy + stutter-invariance, not
star-freeness (and stutter-invariance ≈ LTL\X is neither necessary nor
sufficient for LTL). Owl: translation/synthesis. GOAL: ω-automata
manipulation/games. ROLL: FDFA learning. Phrase as "we are aware of no
tool…; AMoRE did the finite-word analog three decades ago".

**Our reading.** Add to the sweep before we assert: Pin's own **Semigroupe**
software (syntactic monoids + variety tests, finite words) and whatever
Paperman's successor tooling is; GAP's Semigroups package (Mitchell) as the
enumerative computational-algebra baseline. All finite-word or
general-algebra; none ω, none definability — but they belong in the
tool-landscape paragraph.

### D7 — Certificates of non-definability

*Any prior checkable witnesses of non-star-freeness, verifiable by
membership queries alone?*

**R1 verdict: least preempted — push hard.** Frame: McConnell–Mehlhorn–
Näher–Schweitzer, "Certifying algorithms" (CS Review 5(2), 2011). The
finite-word germ is folklore (failure of `x^n = x^{n+1}` exposes a counting
word — the usual proof of Schützenberger), but nothing found that (i)
packages non-star-freeness as a certifying algorithm, (ii) handles ω with
the two family shapes as the `~lin`/`~ω` shadows, (iii) replays against the
input before asserting. Certifying model checking (Namjoshi CAV 2001 line)
certifies model ⊨ property — a different object.

*R3 (3/3 on this claim):* "confirmed novel … no published precedent in this
exact form", with a contrast worth quoting in the paper: standard algebraic
proofs witness non-aperiodicity by *exhibiting a finite-order element in a
group H-class* — an object internal to the algebra, meaningless without
trusting the construction — never by packaging it as a replayable family.

**Our reading — one sharpening.** The finite-word world *does* have
automaton-level witnesses: forbidden-pattern characterizations yield a
subgraph in the DFA as evidence. But those are **representation-dependent**
— checkable only against that automaton. The counting family is
**language-level**: checkable by membership queries against *any*
presentation, which is what makes replay-against-the-input meaningful and
what "certifying" should mean for a language-class problem. That contrast
belongs in the paper. In McConnell et al.'s taxonomy, check whether we meet
their "strongly certifying" definition (we believe yes: the checker needs no
trust in determinization, GAP, or the algebra).

### D8 — Symbolic algebra

*Any published symbolic (DD-based) computation of transition monoids,
closures, or syntactic quotients?*

**R1 verdict: open, plausibly novel — unprovable negative.** Symbolic
*automata* are standard (MONA's MTBDD DFAs, symbolic-automata toolkits,
Pous's symbolic language-equivalence). Transformation-semigroup computation
exists but enumerative (GAP Semigroups). No BDD-symbolic monoid
closure/quotient found. Claim as "symbolic monoid closure", positioned
against both lines.

**Our reading — technique precedent to absorb.** Symbolic *partition
refinement* exists: signature-based bisimulation minimization on BDDs
(sigref — Wimmer et al.). That is "refinement as a set-of-vectors fixpoint"
in spirit, on states rather than monoid elements — the natural citation base
for the symbolic tier's refinement half, alongside the closure half's
frontier-BFS-on-DDs. Keeps R1's framing: not symbolic automata, symbolic
*algebra*.

## 3. Round log

- **Round 1 — 2026-07-02, search-enabled online model** (digest integrated
  above, tagged R1). Movements: (a) open → supported-pre-narrowed; (b) open
  → nuanced-reframe (Preugschat–Wilke is the paper to pre-empt); (c) open →
  supported-strongest; (d) open → supported-hedged. R1's two absorb-regardless
  suggestions logged as §4.3–§4.4. Two R1 statements we distrust pending
  first-hand reading: the Selivanov–Wagner "aperiodicity NL/PSPACE" attribution
  (see D5 — we believe it conflates topological with algebraic properties)
  and the exact form of P–W's {U}-fragment precondition (load-bearing for
  the "their input, our output" contrast). Two R1 gaps filled by us: the
  Ramsey-based implemented-closure precedent (D2), the
  forbidden-pattern-vs-language-level contrast (D7).

- **Round 2 — 2026-07-02, second online model** (weaker, unsourced; mined
  for convergence with R1, not trusted alone). **Converges with R1 on:** the
  collapse and the single right-congruence-seed refinement as the most
  original theoretical pieces ("novel or at least non-obvious"); the
  EL-enriched monoid as an unwritten packaging of classical material;
  certificate + replay unpreempted; the contribution engineering-heavy.
  **Diverges:** grades theory "low-to-medium" — but its hedge rested on an
  alleged Spot automaton-level `is_ltl` decider that does not exist (we
  build on Spot daily; its semantic classifiers are the Manna–Pnueli
  hierarchy and stutter-invariance), so the grade is discounted. Pickups
  placed inline: the wreath/block-product search pointer (D1), the
  Muller-profile-granularity concurrence (D2).

- **Round 3 — 2026-07-02, third online model** (the best-sourced round; no
  hallucinated tool claims, declines to overclaim on complexity).
  Movements: (a) → twice-narrowed (the CPP max-plus-matrix + saturation
  algorithm is more concrete than R1 admitted; our differentiator is the
  refinement route, D1); (b) confidence up ("strongly anticipated but not
  preempted … new, clean formulation"), with the sharpest statement yet of
  the FORC/FDFA parallel (D4); (c) → 3/3 confirmed, plus the H-class
  packaging contrast (D7); (d) → 3/3, upgraded to "very likely *the*
  first" (D6). D5: R3 independently corroborates our Selivanov–Wagner
  suspicion by *not* repeating it and calling the ω bound un-pinned —
  §4.2 firms up. New absorb item: syntactic FDFA as intermediate artifact
  (§4.8).

- **Paper round P1 — 2026-07-02, first-hand reading** (P–W, S–W, CPP, D–G;
  details + line pointers in §6). Both review disagreements resolved: P–W
  {U}-precondition **confirmed** (R1 right), S–W aperiodicity attribution
  **refuted** (R1 wrong). One finding all three rounds missed, against us:
  **DG Prop 12.3** settles D5 (PSPACE-complete from NBA) and kills §4.2 as
  a theorem candidate. (a)'s contrast pinned exactly: CPP quotient by
  context saturation vs our single right refinement. (c)/(d) unscathed —
  DG's decider is a paper-only guessing procedure, no certificate.

**Convergence after three rounds** (the narrowing-down target): all rounds
agree that (i) the collapse *mechanism* — one right refinement, no left
translation — is the original theoretical piece while the split itself is
anticipated; (ii) the certificate + replay is unpreempted in exactly this
form; (iii) no tool decides ω-LTL-definability; (iv) the characterizations
are classical and must be claimed as engineering + route. Sole material
disagreements: R1's Selivanov–Wagner attribution (2-vs-1 against, resolve
via paper) and R1's P–W {U}-precondition detail (single-sourced, resolve
via paper). Both resolutions live in the reading queue.

## 4. Exploration directions

Threads worth pulling regardless of the review's outcome — some are
result-candidates, not related-work hygiene.

### 4.1 The rotation lemma — name it, state it, prove it

The step that licenses right-only: in Arnold's ω-power context `x·(u·y)^ω`
the tested word sits *inside* the cycle, yet the collapse checks only
`Aprof(e·b)` under right extension. The license is conjugacy: any occurrence
of `e` in a cycle rotates to the front without changing the ω-word, so
right-seeded profile equality covers all placements. In `algorithm.md` this
is chased silently through layer 5's "both quantifications"; in a paper it
is **the** lemma of claim (b) — P–W get right-invariance free from
co-determinism, we buy it with rotation. Write the two-line proof, give it
the name.

### 4.2 The complexity theorem candidate — **KILLED by first-hand reading**

**Diekert–Gastin 2008 already prove it** (see §6, DG entry): Cho–Huynh
hardness transfers to NBA, and their **Proposition 12.3** gives the PSPACE
upper bound for aperiodicity of `L(A)` from a nondeterministic Büchi
automaton. So the decision is PSPACE-complete from NBA — in the very survey
we cite, missed by all three review rounds (R1 named the wrong paper, R3
said "no single reference"). What survives of 4.2: (i) cite DG Prop 12.3
properly; (ii) a remark-level corollary for deterministic-EL input if we
want it; (iii) the observation that DG's witness-guessing walk through
Büchi's matrix monoid is the *complexity-theoretic shadow* of our
construction — on-the-fly elements, poly-sized, only the count explodes —
which frames our oracle as the practical counterpart of their
nondeterministic argument. Notably DG say explicitly their approach is
*not* based on Arnold's congruence (they test "maximal aperiodic quotient
still recognizes"), and their procedure guesses `m = 3^{n²}`-th powers —
paper-only, not implementable; claims (c)/(d) untouched.

### 4.3 Symmetric certification (R1's suggestion, aligned with our §11 note)

The negative answer is trust-free (replayed family); the positive rests on
the computation. BLS gives the positive side a certificate *shape*: the
defining formula, checked formula-vs-automaton by standard equivalence. That
is the surrounding project — but the framing "a decision procedure
certifying in both directions" is stronger than "positive answers are
theorems" and worth adopting. Open sub-question (already in our §11): is
there a positive certificate *cheaper* than a formula — an aperiodicity
proof object (e.g. per-class idempotence bounds `s^N = s^{N+1}` with
checkable class representatives) a third party verifies without redoing the
refinement?

### 4.4 Carton–Michel as cross-check (R1's suggestion)

P–W's loop-language DFAs are an independent effective handle on the
infinitary factor. Even keeping profiles, running both on the shared
fixtures (mod3, gf_aa pair, evenblocks) would cross-validate `~ω` against a
construction with completely different trust assumptions — and give the
comparison sentence the related-work section needs anyway.

### 4.5 The collapse as a general recipe

`~lin ∩ ~ω` as an instance of: syntactic congruence = observable equivalence
under a basis of contexts, computable by one right-refinement whenever every
context factor is right-invariant (finite-word syntactic monoid = the
one-factor case). Is there a clean general statement? If yes it subsumes
4.1; if no, 4.1 *is* the general statement's ω-instance and the paper can
say so.

### 4.6 Fragment lattice for free

Once `S(L)₊` is materialized, the decidable-fragment characterizations
(P–W's lattice, Diekert–Kufleitner's fragment work, Wilke 1999) are readings
of the same algebra. Inventory: which fragments are decidable by a
subroutine over our quotient with *no new machinery*? A "the oracle decides
the whole lattice" section would widen the contribution cheaply.

### 4.7 The symbolic `EM` (D8)

Elements as `|Q|`-slot vectors, letters as slot-local right-multiplications,
closure and refinement as set-of-vectors fixpoints; cite sigref for the
refinement half. If D8's negative holds, this is a second paper, not a
section.

### 4.8 A syntactic FDFA as intermediate artifact (R3's suggestion)

The quotient's data — residual classes as the leading congruence, per-class
acceptance behavior as progress information — is a syntactic FDFA in all but
serialization. Emitting one would (i) hand the learning/FDFA community a
canonical object our oracle computes exactly rather than learns, (ii) make
the `~lin`/`~ω` ↔ leading/progress correspondence concrete instead of
rhetorical, and (iii) give the paper a second exportable artifact beside the
witness. Cheap if true; check what ROLL's FDFA format accepts.

## 6. First-hand reading log (verified facts + grep-back pointers)

All pointers are into `papers/*.txt` (line numbers of the pdf2text). Facts
below are **read at the source**, not reviewer claims.

- **Preugschat–Wilke** (`Preugschat_Wilke_2013_LMCS.txt`) — READ, resolved.
  - {U}-fragment: Thm 8.1 at **L858–866** lists "(B)(a) L(A) is
    TL_A-definable" as an explicit conjunct → full LTL-definability is an
    *input* to their characterization. Uses Peled–Wilke stutter theorem
    (Thm 8.2, L875).
  - Cor 9.4 + proof at **L987–991**: for automaton input they cite [7] =
    Diekert–Gastin for "the decidability of the LTL-definability" —
    outsourced, confirmed verbatim.
  - Input is a *formula* (GCMA `A_ϕ` built from subformulas, §2.8
    L316–385); arbitrary Büchi input costs CMA conversion `(12n)^n`
    (Thm 2.1, L173–175), GCMA→CMA `2^{mn}` (Thm 2.3, L195–196).
  - The split: left congruence `≡_A` (`L_q = {u : uq ∈ I}` equality) +
    loop languages `LL(q)`, §3.1 **L391–421**. Fragments {X},{F},{XF},
    {X,F},{U} only (Table 1, L456–483).
  - Complexity §9 **L902–991**: PSPACE-hard all fragments (Prop 9.2),
    in PSPACE except {X,F} in E (Thm 9.3). EF-game + forbidden-pattern
    proofs; **no implementation, no certificates** anywhere.
- **Selivanov–Wagner** (`Selivanov_Wagner_2008_FundInform.txt`) — READ,
  R1's attribution **refuted**. Paper is exclusively *topological* (Wadge-
  closed) properties: abstract L15–21, result tables **L85–105** (NL/P det,
  PSPACE nondet — all Wagner-hierarchy classes `C_α`). Aperiodicity appears
  only as finite-word background color in the intro (**L35**). No
  ω-aperiodicity result. Aperiodicity is not Wadge-closed, so it *cannot*
  be in scope.
- **Carton–Perrin–Pin** (`Carton_Perrin_Pin_2008.txt`) — READ (the parts
  that matter for (a)/D1/D2).
  - §4 **L493–511**: Arnold congruence, exactly our two context shapes
    (their eq. 4.1) + the ω-sort condition (4.2).
  - §5.2 **L646–707**: Büchi→ω-semigroup via `Q×Q` matrices over
    `K = {−∞,0,1}` (no path / path / path through final); ω-power
    "effectively computed" by circuit detection (**L700–702**). This is
    the enriched monoid's published ancestor, nondeterministic form.
  - The syntactic quotient is **Example 5.3, L782–799**: "one should
    compute the syntactic congruence ∼P of P in S" by quantifying **all**
    `x,y,z ∈ S₊` — brute-force two-sided saturation on the finite algebra.
    No refinement, no data structures, no complexity, no implementation.
    (The phrase "our algorithm" at L853 is a *different* construction:
    weak recognition → Muller, Le Saëc–Pin–Weil.)
  - Claim (a)'s contrast, now exact: *saturation over context triples*
    (them) vs *one right refinement, no left translation* (us).
- **Diekert–Gastin** (`Diekert_Gastin_2008.txt`) — READ §1 + §12; **the
  round-3 surprise, against us on D5**.
  - Intro **L167–173**: Cho–Huynh PSPACE-hardness "transfers to
    (non-deterministic) Büchi automata"; upper bound "might belong to
    folklore … but we did not find any reference. So we prove this result
    here, see Proposition 12.3."
  - §12 **L1499–1668**: Prop 12.1 — `L` aperiodic iff the maximal
    aperiodic quotient `M/(x^m = x^{m+1})` of any recognizing monoid still
    recognizes `L`. Prop 12.2 — recognition by a quotient ⟺ linked-pair
    saturation. **Prop 12.3** — PSPACE: guess six elements of Büchi's
    matrix monoid `BT(A)` *on the fly, letter by letter* (poly-sized
    matrices, `m = 3^{n²}`), compare `uv^{m+ε}w` pairs, test
    `h⁻¹(s)h⁻¹(e)^ω ⊆ L` by matrix reachability. Explicitly **not** via
    Arnold's congruence (**L1518–1520**).
  - Consequences: D5 answered (PSPACE-complete from NBA); §4.2 reframed
    (see there); (d) untouched — a nondeterministic guessing procedure
    with `3^{n²}` exponents is not a practical decider and emits no
    certificate. Their §11 (L1151+) defines counter-free *nondeterministic*
    Büchi automata ("seems to be an original part", L157); deterministic
    models explicitly out of scope (L92–93).

- **Maler–Staiger** (`Maler_Staiger_1997_TCS.txt`) — READ (Defs, §1–3).
  - **Definition 1, L159–176** is the load-bearing block: (1) syntactic
    right-congruence `x ∼_E y ⟺ ∀β ∈ Σ^ω (xβ ∈ E ⟺ yβ ∈ E)` — this **is**
    our `~lin` at word level (residual equality); known and must be cited.
    (2) simple syntactic congruence `≃_E` = its two-sided closure
    (`∀u: ux ∼ uy` — left contexts, which our determinism+rootedness
    collapse to states). (3) infinitary `≈_E` via `u(xv)^ω` contexts.
    (4) **Arnold's iteration congruence displayed as the conjunction
    `≃_E ∧ ≈_E`** — so the *two-part factoring* of Arnold's congruence is
    explicitly in M–S 1997, not just implicit in Arnold. Honesty for (b):
    the split has a 1997 display; ours is the *computable right-only
    realization* (state residuals + profiles + one refinement), full stop.
  - Their `≈_E` quantifies a two-sided context (`u · _ · v` inside the
    ω-power); no state collapse, no profiles, no refinement procedure, no
    aperiodicity/definability application in §1–3. §6 = FORC (families of
    right congruences), the recognition/canonicity thread (L48–51,
    L109–118). Minimal-state automaton caveat (L208–212): `∼_E`-quotient
    need not accept `E` — their motivating pathology, orthogonal to us.
  - Fact 1 (L220): finite-state `E` with infinite iteration monoid exists
    (non-regular corner) — trivia, not our regime.

**Still unread** (grep targets for cheap entry): Maler–Staiger — grep
`right congruence|syntactic` for whether `~lin` is theirs; ABF/AF — grep
`syntactic FDFA|progress` for the exact leading/progress definitions;
Cho–Huynh — the theorem statement only (input model); McConnell — grep
`strongly certifying` for the definition; Fogarty–Vardi/Abdulla — grep
`supergraph|arc|composition` to scope what they close; Wilke 1999, BLS
related work, Tsai — low priority.

## 7. Reading queue (remaining; done items moved to §6)

~~1. Preugschat–Wilke~~ ~~2. Carton–Perrin–Pin~~ ~~3. Selivanov–Wagner~~
~~Diekert–Gastin~~ — all resolved, see §6.

4. **Maler–Staiger**, TCS 1997 — is `~lin` theirs under another name?
5. **Angluin–Boker–Fisman** LMCS 2018 + **Angluin–Fisman** IC 2021 — the
   FDFA parallel, precisely (syntactic FDFA definition).
6. **Cho–Huynh**, TCS 1991 — exact theorem statement (input model) only.
7. **McConnell et al.** 2011 — the "strongly certifying" definition.
8. **Fogarty–Vardi** 2010/2012, **Abdulla et al.** 2011 — scope exactly
   what monoid-like object they close (supergraphs/arcs).
9. **Boker–Lehtinen–Sickert** 2022 — related-work re-read.
10. **Wilke** STACS 1999, **Tsai et al.** — low priority backdrop.
