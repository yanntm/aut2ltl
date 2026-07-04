# What the SOSG is for — a use-case catalog

*Untracked scratch. Prospective and liberal on purpose: the moment the ideas
crystallize, written down before they evaporate. The through-line: once you can
**build** the syntactic ω-semigroup of a language (and its finite-word
specialization, the syntactic monoid), you hold the canonical, complete algebra
of that language — and an astonishing amount of what people do to ω-/regular
languages by hand, by heuristic, or by expensive automata surgery becomes a
lookup, a set-flip, or a table check on that one object. Deciding "is it LTL"
and synthesizing the formula are two small tenants of a large building.*

---

## The headline: a definability / classification hub

The strongest thing here is not "we decide LTL." It is that the SOSG is a **hub
from which a whole zoo of definability questions are read off cheaply**. Once the
syntactic algebra is materialized, membership of `L` in a temporal or logical
class is, in most cases, checking a finite set of algebraic identities or
forbidden patterns — near-free relative to the cost of building the object. From
one construction you can answer, for the same language and with no new machinery:
star-free / FO(<) / full-LTL (aperiodic), **FO² / two-variable / the variety DA**
(unambiguous, `XF`-style fragments), **piecewise-testable** (J-trivial),
**locally and threshold-locally testable**, **definite / reverse- / generalized-
definite**, levels of the **Straubing–Thérien** and dot-depth hierarchies, and —
for ω — the **Manna–Pnueli hierarchy** (safety, guarantee, obligation, recurrence,
persistence, reactivity) and the Preugschat–Wilke temporal-operator fragments
(`{X}`, `{F}`, `{U}`, …). This is the pitch: not a single-question decider but a
**"definability profiler"** for a temporal specification — feed it a property,
get its coordinates in every classical hierarchy at once. "Is it LTL?" is one row
of that table.

## The classifier's cousin: which machine suffices

Sitting beside the logical classes are the *automaton-shape* questions, and they
are structural properties of the same ω-semigroup: is `L` **deterministic-Büchi-
recognizable** (topologically Gδ), deterministic-co-Büchi, **weak**, and what are
its **Rabin/parity index** bounds. A tool that, given any presentation, tells you
the cheapest acceptance type that can recognize the language — and *why* — is
directly useful to anyone building or optimizing ω-automata, and it comes out of
the algebra rather than out of trying constructions and failing.

---

## The algebra of languages, done on the object

**Complement is free — and that is the quotable one.** The SOSG of `L` and of its
complement are the *same algebra*; only the accepting set of linked pairs flips.
Complement is a set-complement over the linked pairs — `O(#pairs)`. Against a world
where complementing a Büchi automaton is the notorious `2^{O(n log n)}` operation,
"complement is flipping one bit-vector" is the kind of line that sells the object.

**Membership, emptiness, universality are one lookup each.** Membership of a lasso
`u·v^ω`: fold `u,v` through the letter map and multiplication table, power `v` to
its idempotent `e`, test `(u·e, e)` against the accepting set. Emptiness is "the
accepting set is empty"; universality is "the accepting set is everything." These
are the trivialities that a canonical algebra is *supposed* to make trivial, and
it does.

**Union and intersection are the honest ones — a product, then re-canonicalize.**
`L₁ ∪ L₂` and `L₁ ∩ L₂` are recognized by the product ω-semigroup `S₁ × S₂` with
the combined accepting set; the *canonical* SOSG of the result is that product
re-syntactified with the same `~lin ∧ ~ω` collapse. Cost is the automata-product
size `|S₁|·|S₂|` plus a polynomial quotient — not free, but no exponential blow-up,
and the boolean algebra of languages closes on the object without ever
determinizing or complementing an automaton.

**Equality is a hash.** Two languages are equal iff their canonical cores are
byte-identical. Where pairwise ω-equivalence is a PSPACE tournament, bucketing a
corpus by *true language* is a hash-join. The sweet spot is **many-to-many**:
deduplicating a benchmark suite (the ω-automata competition set, a genaut census)
by actual language, cross-checking that two tools produced the same property,
differential testing, and memoization/caching keyed on language identity inside a
larger pipeline.

---

## A canonical interchange format for ω-languages

HOA serializes automata, and there are many HOA per language — it is a *dump*, not
an *invariant*. The serialized SOSG (the "semantic HOA") is **the** file for a
language: canonical, complete, comparable by bytes. That makes it a natural
interchange and archival format — a language-keyed database, a provenance record,
a deduplicating key — precisely in the places where "same language, different
automaton" currently defeats tooling. It is the object HOA would be if HOA were
canonical.

---

## Learning a SOSG — and classifying as you learn

The SOSG is learnable in the MAT model, and the interesting part is *why*: the
**rotation lemma**, which makes the two-sided congruence right-computable, is
exactly what makes it right-**learnable**. Two-sided (syntactic) objects resist
query learning because you can only append on the right; the rotation lemma shows
everything is recoverable from the right-only seed `(~lin, Aprof)`, which maps onto
the two components of an FDFA (leading right-congruence + progress/loop data), both
of which existing algorithms (Angluin–Fisman, ROLL) already learn. Learn the seed,
assemble the two-sided algebra. The payoff over plain FDFA-learning: a **canonical
target** (equivalence queries answered by the hash, termination bounded by
`|S(L)|`), and a learner that **classifies and explains as it goes** — the moment
the learned algebra shows a group it can declare "not LTL" and hand out the
counting certificate, and otherwise it can emit the formula and the fragment
coordinates. A learner that returns not just the language but its logical
complexity is, I suspect, a paper of its own.

---

## Finite words and LTLf — the same object, a live audience

Drop the ω-part and the construction *is* the classical **syntactic monoid**
computation, with the whole hub above specialized to regular finite-word languages:
star-free = FO = **LTLf**, piecewise-testable, DA, the finite-word hierarchies. This
matters now because LTLf is everywhere it wasn't a decade ago — planning, **reward
machines** in reinforcement learning, declarative **process mining**. "Given this
reward machine / this mined DECLARE model, is its language star-free / in which
fragment, and here is the LTLf formula (or here is why it is not)" is a concrete,
current ask, and it is the AMoRE functionality reborn with certificates, synthesis,
and a canonical form — for an audience AMoRE never had.

---

## Turning the algebra back into a machine

The right-Cayley automaton of the aperiodic quotient is a **canonical, forward,
deterministic, counter-free** automaton for any LTL language — the object no
minimal deterministic ω-automaton provides. Its role is to feed every downstream
construction that *assumes* counter-freeness and quietly relies on it as a rug for
its own soundness — the Boker–Lehtinen–Sickert cascade first among them, but the
pattern is general. When such a construction declines a group-bearing presentation,
the SOSG can hand it a counter-free one built from the algebra. (Its open acceptance
lemma is the one thing standing between "canonical transition structure" and
"drop-in replacement.") This closes the loop back to where this whole investigation
started.

---

## The two tenants everyone will name first (and shouldn't)

**Deciding LTL-definability** and **synthesizing the LTL formula** are real, and
they are how the object will be introduced — but in this catalog they are use
cases, not the thesis. The decision is one hub query; the synthesis is one of two
*reifications* (as a formula; the Cayley automaton is the other, as a machine). The
**non-LTL certificate** — a representation-independent, replayable counting family
that refutes definability by membership queries against any presentation of `L` —
is genuinely novel and worth foregrounding *as a certification story*, but it too
is a by-product of holding the algebra, not the reason to hold it.

---

## Prospective, and slightly wild

- **A definability profiler as a service.** Point it at a corpus of LTL/PSL specs
  from real verification projects and produce the distribution: how many are
  *really* safety, how many *really* star-free, how many secretly count. An
  empirical map of "what specifications people actually write" in algebraic
  coordinates — a measurement paper waiting to be run, and the SOSG is the
  instrument.
- **Explaining spec complexity.** A group in the algebra *is* the reason a monitor
  or a determinization blew up — it is the modular count the language cannot avoid.
  The SOSG can tell an engineer *why* their property is expensive and point at the
  offending loop, not just that it is.
- **Differential oracle for temporal tooling.** Two translators, two determinizers,
  two simplifiers — run each, hash the SOSG, compare. A canonical language identity
  turns a fleet of heuristic tools into things you can regression-test against each
  other on true semantics.
- **A canonical normal form for LTL/LTLf.** The synthesized formula is a *function
  of the algebra*, hence a normal form: same language, same formula. A canonical
  representative per language is useful for caching, for teaching, for "are these
  two specs the same" at the syntax level.
- **Pedagogy.** An "algebra explorer" that shows a student the syntactic monoid /
  ω-semigroup of a language they type, colors the groups, and says what fragment it
  lives in. The abstract objects of a semester of automata theory, made clickable.
- **Bridge to algebraic language theory tooling.** Semigroupe, GAP's Semigroups —
  the finite-monoid computation ecosystem — has never had an ω front-end that hands
  it *the syntactic ω-semigroup of an automaton*. This is that front-end, and the
  varieties/identities community could consume it directly.

---

*What it was all for: we set out to understand why a cascade tolerated groups it
had no right to, and we came out holding the canonical algebra of the language and
a list of things it unlocks that have nothing to do with cascades. The
counter-freeness question was the doorway; the room turned out to be much larger
than the door. And it really was interesting at the time.*
