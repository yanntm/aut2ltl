# Materializing the Syntactic ω-Semigroup: a Canonical Representation of Regular ω-Languages

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-16*

## Abstract

The syntactic ω-semigroup of a regular ω-language is its canonical algebra:
presentation-independent and complete — it determines membership, equality,
and every definability property of the language. Defined by Arnold in 1985,
it has, to our knowledge, never been built from an automaton. We build it,
and we reify it: the invariant `𝓘(L) = ⟨𝒮, P⟩` — a stamp `𝒮 : Σ⁺ → 𝒞`
classifying the finite words by a finite table, and an acceptance layer `P`
of linked pairs over it — equipped with a standalone lasso-membership
semantics. This is a canonical normal form for regular ω-languages, which
the domain has never had: under shortlex naming, two languages are equal iff
their serialized invariants are byte-identical. The mathematical core is a
rotation lemma: Arnold's two-sided syntactic congruence is computable by
right multiplications alone — the structural fact missing from forty years
of literature between the definition and a construction. On it we build
`𝓘(D)` from any deterministic Emerson–Lei automaton `D` — an
acceptance-enriched stamp, then a right-computable quotient — and prove
`𝓘(D) = 𝓘(L(D))` against the semantics: one language, one table, whatever
the presentation. LTL-definability, the safety–progress rung, and the
weakest deterministic acceptance become read-offs of the one object.

## 1. Introduction

On finite words, regular language theory has a normal form. The minimal DFA
is *the* automaton of a language — computed, hashed, compared for sixty
years — and behind it stands the syntactic monoid, the canonical algebra
through which the deepest structural facts are read, most famously
Schützenberger's theorem [Sch65]. On infinite words — the setting of model
checking and reactive synthesis — there is no analogue: a regular ω-language
has no minimal deterministic ω-automaton, and every pipeline in the field
manipulates *presentations*, never languages. Two automata for one language
share nothing observable; each language-level question must first be argued
independent of the presentation it is asked on, and equality itself is a
PSPACE problem, not a comparison.

The canonical object exists — on paper. Arnold [Arn85] defined the syntactic
congruence of a regular ω-language: the coarsest congruence saturating it,
of finite index, whose quotient — the **syntactic ω-semigroup** — is a
function of the language alone and recognizes it. In principle this is the
exact ω-analogue of the syntactic monoid; in practice it is a phantom,
defined everywhere and built nowhere: no tool materializes it from an
automaton, and the algorithmic accounts of its flagship application —
deciding LTL-definability — are complexity arguments that emit no algebra
and no evidence [DG08].

The obstruction is structural, not just size, and its two halves were each
solved in isolation without ever being combined. First, a recognizer for
infinite behaviour must remember *acceptance along runs*: the transition
monoid forgets the marks a run collects, which is exactly what ω-acceptance
consumes — Carton, Perrin and Pin have a recognizer that keeps them [CPP08],
but reach the syntactic quotient only by saturation over context triples, an
example rather than a procedure. Second, Arnold's congruence is inherently
*two-sided*, while the one operation a finite table offers for free is
multiplication on the right — Maler and Staiger display the congruence as a
finitary–infinitary split [MS97], but compute no quotient, and their loop
test still hides a two-sided context. This paper supplies the missing
mathematics and assembles the construction. Our contributions:

1. **The object, reified** (§3). The invariant `𝓘(L) = ⟨𝒮, P⟩`: a stamp
   `𝒮 : Σ⁺ → 𝒞` presented by its classes, letter map and multiplication
   table, and a pair set `P` of linked pairs, with a self-contained
   lasso-membership semantics (Definition 3.5). Canonicity
   (Theorem 3.10) makes it a complete invariant — and, under shortlex
   naming, a normal form: language equality is byte equality of the
   serialized tables.

2. **The rotation lemma** (§3.3). A loop may be rotated — a factor carried
   from the loop's front onto the stem leaves the ω-word unchanged — and
   this single move generates every renaming of a lasso. Read on contexts,
   it collapses Arnold's two-sided congruence to a computation by right
   multiplications alone: the structural fact the literature lacked, and
   the engine of the construction.

3. **The construction** (§4). From any deterministic Emerson–Lei automaton
   `D`: an acceptance-enriched stamp — sound but too fine — then the
   quotient by two right-only relations, computed by partition refinement.
   Theorem 4.11 closes the loop against the semantics: `𝓘(D) = 𝓘(L(D))`,
   byte for byte, whatever presentation `D` was.

§5 splits the two costs — the construction pays an exponential that
PSPACE-hardness makes unavoidable, while everything on the finished table is
polynomial in `|𝒞|`, a size intrinsic to the language. §6 puts the object to
work: the identity band (equality, complement, membership, witnesses) nearly
for free, then the LTL frontier as a one-look read-off, exact in both
directions because the invariant is canonical. §7 positions the neighbours;
§8 opens the directions the reified object makes available — classification,
rendering to formulas, a calculus, a census, learning; §9 concludes.

Four running examples accompany the paper, met first as tables and only
later as automata: `aUGb`, the pedagogical thread of §2–§3, and `GF(aa)`,
`Even`, `EvenBlocks`, chosen to exercise both context shapes of the
congruence and both sides of the LTL frontier. Each has a one-page card
(Ex. 1–4) at the end of the paper — language, formula, classification,
automaton, invariant — transverse to the text and meant to be consulted at
leisure.
