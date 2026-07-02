# Related work — where the oracle stands

Companion to `algorithm.md`. That document constructs; this one positions:
the papers the construction stands on or beside, what each establishes, and
our exact relationship to it — why we even cite it. Claims here follow
first-hand reading; the investigation notebook, with per-paper line pointers
into the sources, is `research_notes/definability.md` at the repo root.

## 1. The foundations the oracle computes on

**Thomas 1979; Perrin 1984; Perrin–Pin, *Infinite Words* (2004); Arnold
1985; Diekert–Gastin 2008.** The characterization chain LTL = FO[<] =
star-free = aperiodic syntactic ω-semigroup is entirely classical: Perrin
proved star-free ⟺ aperiodic on ω-words, Thomas the counter-free
deterministic screen, Diekert–Gastin survey the chain, and Arnold defined
the syntactic congruence of an ω-regular language — the coarsest congruence
saturating it — whose two context shapes, linear and ω-power, are exactly
the two certificate shapes of layer 2. *Why cited:* these are the theorems
the oracle transports and never re-proves; every soundness argument in
`algorithm.md` bottoms out on one of them. We claim the construction, not
one inch of the characterization.

## 2. The recognizer's ancestry — and the quotient contrast

**Carton–Perrin–Pin, "Automata and semigroups recognizing infinite words"
(2008).** The modern account of the transition ω-semigroup Büchi's
complementation argument attaches to an automaton: from a nondeterministic
Büchi automaton, `Q × Q` matrices over `{−∞, 0, 1}` (no path / path / path
through an accepting state), ω-power effectively computable, the resulting
finite ω-semigroup recognizing `L` (§5.2 there). The syntactic quotient
appears as their Example 5.3: quantify **all** context triples `x, y, z`
over the built algebra — brute-force two-sided saturation, with no
refinement procedure, no data structures, no complexity statement, no
implementation. *Why cited:* layer 3's `EM(D)` is the deterministic
Emerson–Lei instance of their matrices — rows collapse to a function, the
accepting *bit* upgraded to the exact mark *set* EL acceptance needs — and
the quotient step is our sharpest contrast: saturation over context triples
(them) versus a state relation plus one right refinement, no left
translation ever (us — layer 5's collapse).

## 3. The two-part congruence — who split it, who computed it

**Maler–Staiger, "On syntactic congruences for ω-languages" (TCS 1997).**
Their Definition 1 is load-bearing for us twice. It defines the syntactic
right congruence `x ∼ y ⟺ ∀β ∈ Σ^ω (xβ ∈ L ⟺ yβ ∈ L)` — which is layer 5's
`~lin` read at the initial state; the object is theirs and cited as such in
the layer. And it displays Arnold's congruence as the conjunction of a
finitary and an infinitary part — the *split* itself has a 1997 display.
What M–S do not have: any state collapse (their infinitary part quantifies
a two-sided context inside the ω-power), profiles, a refinement procedure,
or an aperiodicity application; their agenda — continued as FORC, families
of right congruences — is recognition and canonical forms. *Why cited:*
credit for the split and for `~lin`'s word-level ancestor. Our contribution
against this backdrop is the computable right-only realization: state
residuals, profiles, one Moore refinement, licensed by the rotation lemma.

**Preugschat–Wilke, "Effective characterizations of simple fragments of
temporal logic using Carton–Michel automata" (LMCS 2013).** The closest
published neighbor. They convert to a prophetic (reverse-deterministic)
automaton and split: a left congruence on states as the finitary factor,
per-state loop languages as the infinitary one — the same
finitary×infinitary architecture, realized co-deterministically, where
right-invariance comes for free. The scope differences that matter: they
characterize the simple fragments ({X}, {F}, {XF}, {X,F}, {U}) — not full
LTL; the {U} characterization takes TL-definability of the input as an
explicit precondition (their Thm 8.1(B)(a)), citing Diekert–Gastin for that
decision (their Cor 9.4); arbitrary Büchi input pays a `(12n)^n` conversion
to the prophetic form; and there is no implementation and no certificate
anywhere — EF games and forbidden patterns. *Why cited:* the knowing
referee's first question. The full-LTL border is their *input* and our
*output*; our forward-deterministic route must earn right-invariance (the
rotation lemma) where co-determinism hands it to them; and their
loop-language DFAs are the natural independent cross-check of `~ω` on
shared fixtures.

## 4. Right congruences as representations — the FDFA line

**Klarlund 1994; Angluin–Fisman (TCS 2016); Angluin–Boker–Fisman (LMCS
2018); Angluin–Fisman (Inf. Comput. 2021); the ROLL tool (Li et al.).**
FDFAs — a leading
automaton plus per-state progress DFAs — are the machine model of
Maler–Staiger's families of right congruences, and are structurally our
residuals + profiles. Angluin–Boker–Fisman state the axis themselves: FDFA
theory works with right congruences where the algebraic theory of
recognition works with two-sided congruences — our construction is
precisely a bridge, computing the two-sided syntactic invariant with
right-only machinery. Angluin–Fisman 2021 documents from this side why the
plain syntactic right congruence cannot see LTL-ness: LTL languages exist
whose right congruence is *trivial* (`FG(a ∨ Xa)`) — layer 9's blindness in
their vocabulary; the profile half is the repair. The entire line stops at
representation, canonicity, and learning: no definability decision
anywhere. *Why cited:* the structural kinship must be acknowledged and the
gap named. The closest canonical object is the **syntactic FDFA** of
Angluin–Fisman's learning paper (TCS 2016), after Maler–Staiger's syntactic
FORC: leading automaton = the syntactic right congruence, one progress DFA
per class. Read at the source, the kinship stops at the architecture: their
progress components are *guarded* right congruences — the ω-test runs only
over periods returning to the leading class, the left context stays
anchored per class, and the infinitary data is an accepting-state marking,
not a per-state acceptance profile. Nothing in the line plays the profile
role, and the canonical FDFAs are learning *targets*, never computed from
an automaton. The quotient's data — residual classes as leading congruence,
per-class acceptance behavior as progress — is nonetheless a syntactic FDFA
in all but serialization, so emitting one is a cheap exportable artifact;
one practical detail, from their own subtlety, is that the syntactic FDFA
is unsaturated under exact acceptance, so an emitted artifact must carry
their *normalized* acceptance.

## 5. Complexity — the decision is PSPACE-complete, and by whom

**Cho–Huynh (TCS 1991).** Finite-word aperiodicity is PSPACE-complete from
a **minimum-state DFA** — hardness holds with minimal deterministic input,
no determinization slack. Their characterization is the cycle pattern
`δ(p,u) ≠ p`, `δ(p,u^r) = p` *on the minimal automaton* — the
representation-dependent witness that section 7 contrasts with ours.

**Diekert–Gastin (2008), Prop. 12.3.** The ω upper bound, in the very
survey that carries the characterization chain: aperiodicity of `L(A)` from
a nondeterministic Büchi automaton is in PSPACE, by guessing elements of
Büchi's matrix monoid on the fly, letter by letter, and comparing
`u·v^{m+ε}·w`-style pairs with `m = 3^{n²}`. Together with Cho–Huynh's
transferring hardness: PSPACE-complete from NBA. Their procedure is a
complexity argument, not an algorithm — a nondeterministic walk with
astronomical exponents, emitting no certificate, and explicitly not via
Arnold's congruence. *Why cited:* the honest anchor for layer 12 (the
explosion is intrinsic; caps are a necessity), and the frame that positions
the oracle as the practical, deterministic, certificate-producing
counterpart of their nondeterministic argument — their on-the-fly
poly-sized elements are the complexity shadow of our BFS closure.

**Boker–Lehtinen–Sickert (FoSSaCS 2022).** The converse direction:
counter-free deterministic automaton → LTL formula, with the first
elementary bounds on the construction. They assume aperiodicity and decide
nothing; the gap they leave — decide first, then construct — is exactly the
seam between this oracle and the surrounding project.

## 6. Implemented monoid closures — the precedent, and where it stops

**Lee–Jones–Ben-Amram (size-change termination, 2001); Fogarty–Vardi
(TACAS 2010, LMCS 2012); Abdulla et al. (CONCUR 2011).** Computing the
closure of acceptance-enriched transition matrices inside a tool has
precedent: the Ramsey-based inclusion/universality line closes exactly
Büchi's arc matrices ("supergraphs") under composition. But its central
optimization is subsumption — keep only ⊑-minimal elements — and the pruned
set is explicitly *not closed under composition*: the monoid is
deliberately destroyed, because inclusion testing consumes only
downward-closed information. *Why cited:* honesty about claim boundaries.
"We compute the transition ω-semigroup in a tool" alone would be preempted;
what has no precedent is holding the exact algebra, quotienting it to the
syntactic invariant, and reading a decision off it — an operation the
Ramsey line's data structures could not support even in principle.

## 7. Certification — what kind of certifying algorithm this is

**McConnell–Mehlhorn–Näher–Schweitzer, "Certifying algorithms" (2011).**
The discipline the certificate follows: a witness checkable without
trusting its producer, with a simple soundness proof. Two precisions from
the source. First, their strong/ordinary/weak distinction concerns
preconditions and collapses on a trivial one (ours: any automaton is a
legal input) — so the accurate term for the oracle is **negative-side
certifying**: every NOT_LTL carries a replayable witness; the LTL answer is
a theorem without one (a defining formula that verifies, the surrounding
project's business, would complete the symmetry). Second, the counting
family is *language-level* — checkable by membership queries against any
presentation of `L` — where the classical evidence for non-aperiodicity is
representation-bound: a forbidden pattern in the minimal DFA (Cho–Huynh's
cycle) or a finite-order element in a group H-class, both meaningless
without trusting the very construction under audit. No published packaging
of non-star-freeness as a replayable, representation-independent
certificate is known to us, on finite or infinite words.

## 8. Tools

No tool known to us decides LTL-definability of an ω-automaton. AMoRE
(Kiel, mid-1990s) did the finite-word analog — syntactic monoids,
aperiodicity, star-freeness — three decades ago, with no ω successor. Spot
classifies by the Manna–Pnueli hierarchy and stutter-invariance (neither
necessary nor sufficient for LTL); Owl translates and synthesizes; GOAL
manipulates ω-automata and games; ROLL learns FDFAs; Semigroupe and GAP's
Semigroups package compute finite-word and general algebra. *Why cited:*
the tool landscape behind the "first practical decider" claim, which stays
in the "we are aware of no tool that…" form.
