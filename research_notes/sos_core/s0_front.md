# Materializing the Syntactic ω-Semigroup: a Canonical Representation of Regular ω-Languages

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-18*

## Abstract

The syntactic ω-semigroup of a regular ω-language is its canonical algebra:
presentation-independent and complete — it determines membership, equality,
and every definability property of the language. Defined by Arnold in 1985,
this abstract algebra has, to our knowledge, never been materialized as a
concrete computable finite object. We define it through the invariant
`𝓘(L) = ⟨𝒮, P⟩`: a stamp `𝒮 : Σ⁺ → 𝒞` classifying the finite words by a
finite table, together with an acceptance layer `P` of linked pairs over it,
equipped with a standalone lasso-membership semantics. This is a canonical normal form for regular ω-languages, which
the domain has never had: under shortlex naming, two languages are equal iff
their serialized invariants are byte-identical. The mathematical core is a
rotation lemma, to our knowledge new: it makes Arnold's two-sided syntactic
congruence right-invariant — computable by right multiplications alone, and
so by ordinary partition refinement — and it characterizes the *well-formed*
invariants, those whose semantics gives every lasso one verdict. Every
well-formed invariant, however obtained, canonicalizes onto the syntactic
one; a deterministic Emerson–Lei automaton supplies one, and
`𝓘(D) = 𝓘(L(D))` follows: one language, one table, whatever
the presentation. LTL-definability, the safety–progress rung, and the
weakest deterministic acceptance become read-offs of the invariant.

## 1. Introduction

On finite words, regular language theory has a normal form. The minimal
deterministic finite automaton (DFA) is *the* automaton of a language —
computed, hashed, compared for sixty years — and behind it stands the
syntactic monoid, the canonical algebra through which the deepest structural
facts are read, most famously Schützenberger's theorem: star-free equals
aperiodic [Sch65, PP04]. On infinite words — the setting of model checking
and reactive synthesis — there is no analogue: a regular ω-language has no
canonical minimal deterministic ω-automaton, and every pipeline in the field
manipulates *presentations*, never languages [PP04]. Two automata for one
language share nothing observable; each language-level question must first
be argued independent of the presentation it is asked on, and equality
itself is decided by products and complementation, never by comparison.

The canonical algebra exists — on paper. Arnold [Arn85] defined the
syntactic congruence of a regular ω-language: the coarsest congruence
saturating it (membership depends only on the classes), of finite index,
whose quotient — the **syntactic ω-semigroup** — is a function of the
language alone and recognizes it. In principle this is the exact ω-analogue
of the syntactic monoid, and it closes the classical chain: linear temporal
logic (LTL) `=` first-order logic `FO[<]` `=` star-free `=` aperiodic
syntactic ω-semigroup [Kam68, Tho79, DG08] — every earlier item of the chain
is a syntax, the last is the semantics, and it is the one this paper builds.
In practice the syntactic ω-semigroup is a phantom: to our knowledge no
tool materializes it from an automaton, and the algorithmic accounts of the
flagship application — deciding LTL-definability — are complexity arguments
that emit no algebra and no evidence [DG08].

The obstruction is structural, not just size, and its two halves were each
solved in isolation without ever being combined. First, a recognizer for
infinite behaviour must remember *acceptance along runs*: the transition
monoid forgets the acceptance events along a run, which are exactly what
ω-acceptance consumes — Carton, Perrin and Pin have a recognizer that keeps
them [CPP08],
but reach the syntactic quotient only by saturation over context triples, an
example rather than a procedure. Second, Arnold's congruence is inherently
*two-sided*, while the one operation a finite table offers for free is
multiplication on the right — Maler and Staiger display the congruence as a
finitary–infinitary split [MS97], but compute no quotient, and their loop
test still hides a two-sided context. This paper supplies the missing
mathematics and assembles the construction. Our contributions:

1. **The invariant** (§3). The syntactic ω-semigroup made concrete: a
   finite classifier of finite words together with a set of accepting
   stem–loop pairs, carrying its own membership semantics on ultimately
   periodic words. It is canonical — one language, one object: under
   shortlex naming, language equality is byte equality of serialized files.

2. **Rotation and canonicalization** (§4). A loop may be rotated — a factor
   carried from the loop's front onto the stem leaves the ω-word
   unchanged — and this single move is how two presentations of one ω-word
   come to disagree. The lemma that tames it serves twice: it characterizes
   the *well-formed* invariants — those whose semantics gives every lasso
   one verdict — and it turns Arnold's two-sided congruence right-invariant,
   computable by right multiplications alone, hence by ordinary partition
   refinement. To our knowledge this reduction is new, and it delivers more
   than a construction: every well-formed invariant, however obtained,
   canonicalizes onto the syntactic invariant of its language.

3. **The construction** (§5). From any deterministic Emerson–Lei automaton,
   a well-formed invariant: words classified by their runs — transition map
   and mark map — with acceptance read off the states stems reach and the
   loops that close there; canonicalization does the rest, and two automata
   for one language construct the identical file.

§6 puts the invariant to work: costs, the identity questions, the LTL
frontier. §7 reviews related work; §8 opens the directions the invariant
makes available; §9 concludes.

The construction is implemented, in the tool `aut2ltl`
(github.com/yanntm/aut2ltl); this paper is its theoretical ground, and
neither the implementation nor its empirical evaluation is presented here.

Four running examples accompany the paper, met first as tables and only
later as automata: `aUGb`, the pedagogical thread of §2–§3, and `GFaa`,
`Even`, `EvenBlocks`, chosen to exercise both context shapes of the
congruence and both sides of the LTL frontier. Each has its own page
(Ex. 1–4) at the end of the paper — language, formula, classification,
automaton, invariant.
