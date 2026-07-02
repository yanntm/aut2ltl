# Literature review prompt — the syntactic ω-semigroup oracle

*Pose this to a search-enabled model, optionally attaching
`aut2ltl/bls/definability/oracle/algorithm.md` for the full construction.*

---

We have built and implemented an exact decision procedure for LTL-definability
of ω-regular languages. Given any ω-automaton, we determinize it to a
deterministic Emerson–Lei automaton `D` and read off its **acceptance-enriched
transformation monoid** `EM(D)`: the element of a finite word `w` maps each
state `q` to the pair `(δ(q,w), acceptance marks collected from q along w)`.
Because two words with the same enriched element induce identical run
skeletons in every ω-context, `EM(D)` recognizes the language and the
syntactic ω-semigroup `S(L)₊` (Arnold's congruence, 1985) is a computable
quotient of it. We then decide via the classical characterization: `L` is
LTL-definable iff `S(L)₊` is aperiodic (Perrin 1984, Perrin–Pin *Infinite
Words*, Diekert–Gastin 2008).

The computational core is a **collapse of Arnold's two-sided congruence** that
exploits the determinism and rootedness of `D`: acceptance of an
ultimately-periodic word sees its finite prefix only through one state, so the
congruence factors into (i) `~lin` — pointwise *residual-language equality* of
the state parts, a `Q × Q` relation computed once on `D` with no monoid
involved — intersected with (ii) `~ω` — a **right** congruence refining a
per-element "acceptance profile" (a `|Q|`-bit vector: from each state, is
iterating this element forever accepting). Both factors are right-invariant,
so one Moore-style refinement of one seed computes the syntactic quotient; no
left translation is ever used. Aperiodicity is read by power-iterating the
quotient's classes.

On the negative side the procedure emits a **machine-checkable certificate**:
a "counting family" — linear `u·vⁿ·x` or ω-power `u·(vⁿ·y)^ω` whose
membership toggles with `n mod p`, `p > 1` — obtained *constructively* from
any group class of the quotient (a distinguishing-word chase over the
right-translation tables; the two family shapes are exactly the observable
shadows of `~lin` vs `~ω`), and *replayed by membership queries against the
input automaton* before the verdict is asserted. Positive answers are theorems
(the quotient is the presentation-independent invariant); the only remaining
outcome is resource exhaustion (`|EM|` can reach `(|Q|·2^{|C|})^{|Q|}`). The
whole pipeline is implemented and validated (Spot for automata primitives,
pure Python for the algebra; no computer-algebra system on the decisive path).

**Your task: a rigorous prior-art and adjacent-work review.** We believe the
characterizations are classical but the *explicit, implemented construction*
— the enriched-monoid quotient computed on the fly, the `~lin`/`~ω`
factoring, and the certified non-definability witnesses — may be new. Confirm
or refute, direction by direction:

1. **Explicit constructions of the syntactic ω-semigroup.** Arnold 1985
   defines the congruence; Perrin–Pin (*Infinite Words*, 2004) and
   Carton–Perrin–Pin ("Automata and semigroups recognizing infinite words",
   2008) state effectiveness. Does *any* publication give an actual algorithm
   — data structures, refinement procedure, complexity — for computing
   `S(L)₊` from an automaton? Check also Pécuchet (1980s) and Wilke's algebra
   papers (1991/1993).
2. **The enriched monoid's root.** We attribute the idea to Büchi 1962: the
   complementation congruence via matrices over {no path, path, path through
   an accepting state}. Verify this lineage and locate who first stated that
   this "transition ω-semigroup of an automaton" recognizes the language and
   surjects (after quotient) onto the syntactic one. Is a
   deterministic/Emerson–Lei (mark-set) variant spelled out anywhere?
3. **Preugschat–Wilke** ("Effective characterizations of simple fragments of
   temporal logic using prophetic automata", FoSSaCS 2012 / LMCS): the
   closest known neighbor — effective decisions of TL fragments via
   Carton–Michel backward-deterministic automata. Exactly how do they obtain
   the syntactic invariants, did they ever implement, and does their route
   anticipate our collapse? Also Wilke, "Classifying discrete temporal
   properties" (STACS 1999).
4. **Right congruences and FDFAs — the adjacent thread most likely to hide
   prior art on our collapse.** Maler–Staiger ("On syntactic congruences for
   ω-languages"), Angluin–Fisman ("Families of DFAs as acceptors of ω-regular
   languages"), Angluin–Boker–Fisman, and the FDFA learning line (ROLL tool,
   Li–Turrini et al.). An FDFA is a leading right congruence (≈ our residual
   classes) plus per-class progress congruences (≈ our profiles?). Does
   anyone decide star-freeness/LTL-definability via FDFAs or canonical right
   congruences? Is there a published statement resembling "`~lin ∩ ~ω`, both
   right-invariant, one refinement"?
5. **Complexity.** Cho–Huynh 1991: deciding aperiodicity of a DFA's language
   is PSPACE-complete (finite words). Locate the ω-analog: the precise
   complexity of deciding LTL/FO-definability from a deterministic parity /
   Muller / Emerson–Lei automaton (and from a nondeterministic Büchi one).
   Check the related-work sections of Boker–Lehtinen–Sickert, "On the
   Translation of Automata to Linear Temporal Logic" (FoSSaCS 2022), and
   Diekert–Kufleitner's work on fragments over infinite words.
6. **Tool landscape.** AMoRE (Kiel, ~1995) computed syntactic monoids and
   star-freeness for *finite* words — did it, or any successor, ever handle ω?
   Do GOAL, Owl, Spot, ROLL, or any academic prototype decide
   LTL-definability of an ω-automaton in practice? We currently claim "among
   the first practical deciders" — stress-test that claim.
7. **Certificates of non-definability.** Any prior work emitting *checkable
   witnesses* that an ω-regular (or even regular, finite-word) language is
   not star-free — counting families, modular counters, or similar objects a
   third party verifies by membership queries alone? Frame against the
   certifying-algorithms literature (McConnell–Mehlhorn–Näher–Schweitzer).
8. **Symbolic algebra.** Any published symbolic (BDD/decision-diagram)
   computation of transition monoids, semigroup closures, or syntactic
   quotients? (We have a prospective design: elements as `|Q|`-slot vectors,
   letters as slot-local right-multiplications, closure and refinement as
   set-of-vectors fixpoints.)

For each direction: verdict (confirms / refutes / nuances our attribution),
the key references with venue and year, and one paragraph of what the source
actually does. Close with an overall assessment of the four novelty claims:
(a) the explicit implemented quotient construction, (b) the `~lin`/`~ω`
collapse, (c) the certified counting-family witnesses with replay, (d) first
practical decider. Flag anything that threatens them, and anything beautiful
we should absorb regardless.
