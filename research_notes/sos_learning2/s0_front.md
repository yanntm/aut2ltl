# Learning the Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Shadow draft — rev. 2026-07-19. §7's data traces to the committed census
record; regeneration status in the folder README.*

## Abstract

The syntactic ω-semigroup of a regular ω-language `L` is its canonical
algebra: presentation-independent, complete, and the object from which
membership, equivalence, and every definability property of `L` —
LTL-definability included — are read. It was recently materialized as a
computable, serializable invariant `𝓘(L)`, constructed from a deterministic
automaton [SωS26]. This paper shows the invariant is *learnable*, in
Angluin's MAT model, from lasso membership and equivalence queries alone.
The design rests on one typing discipline: **the learner never poses a
hypothesis that is not a language**. Its belief is at all times an
ω-regular language held in canonical form — every hypothesis it presents is
a well-formed invariant, the syntactic invariant of its own belief
language. The discipline pays structurally: a well-formed invariant denotes
exactly one language, so an exact equivalence oracle can never falsely
assent, and the permanent stalls that afflict acceptor-typed learners are
impossible by construction. Keeping the belief legal is cheap: two
query-free checks — the candidate stamp a genuine morphism, the pair set
saturated under conjugacy — and every violation is a free progress signal,
a disagreement the learner catches on its own and converts, by the same
chain mechanism that processes the teacher's counterexamples, into a
witnessed class split. The fixpoint is `𝓘(L)` itself, byte-equal to the
constructed reference, at output-polynomial query cost. Where the boundary
lies is itself a theorem: a fixpoint that counterexample-guided refinement
alone certifies is either the canonical algebra already or carries no
algebra at all — realized on the two-letter implication `a → Xa`, which
stalls permanently one class short. On a
complement-closed census of 6222 languages the learner reconstructs every
syntactic invariant byte-for-byte; without the legality discipline half of
them stall permanently; and LTL-definability is read off each learned
invariant: the aperiodicity check of [SωS26] applied verbatim to the
learner's output — a decision no current tool derives from an acceptor.

---

## 1. Introduction

Active learning asks a machine to reconstruct an unknown language *exactly*,
from experiments alone. In Angluin's minimally adequate teacher (MAT) model
[Ang87] the learner poses membership queries — is this word in the
language? — and equivalence queries — is this hypothesis the language?,
answered by *yes* or by a counterexample — and the L\* algorithm learns the
minimal DFA of any regular language with polynomially many queries. The
paradigm's reach is practical — assume–guarantee verification [FCC+08],
state machines learned from black-box implementations of smart cards and
network protocols [Vaa17] — but its engine is a theorem: by Myhill–Nerode,
the right congruence of the language *is* its minimal acceptor. Everything
one wants from L\* flows from the canonicity of that target: progress is
irreversible, cost is measured against the language's own invariant, and
questions about the language are answered on the learned object itself.

On infinite words the query interface survives — ultimately-periodic words,
*lassos*, are finite objects that determine an ω-regular language
completely — but the engine fails: the right congruence of an ω-regular
language can be trivial while the language is complex [AF21]. There is no
minimal deterministic ω-automaton to converge to, and the history of
ω-learning is a history of substitute targets: the subclass where the right
congruence still carries everything [MP95], encodings back into finite words
[FCC+08], and the standard modern route, *families of DFAs* (FDFAs) in three
competing canonical forms, the choice among them the learner's [AF16,
ABF18]. All of these targets are acceptors. The canonical FDFA forms are
even functions of the language alone — but each is a *family* of
one-slot acceptors: none carries the language's algebra, and none answers
a definability question without further construction.

Yet the canonical object exists. Arnold's syntactic congruence [Arn85]
quotients finite words by interchangeability in every lasso context — in
the stem, or inside the loop — and its quotient, the syntactic ω-semigroup,
is the exact ω-analogue of the syntactic monoid. It was recently
materialized as the invariant `𝓘(L)`: a finite classifier of finite words
plus a set of accepting stem–loop pairs, serialized to a byte-canonical
file [SωS26]. Two results of that construction matter here beyond the
object itself. A *rotation lemma* — carrying a factor from a loop's front
onto the stem leaves the infinite word unchanged — turns every left demand
of the two-sided congruence into a right computation. And a
*canonicalization theorem* carries every well-formed invariant, however
obtained, onto the syntactic invariant of its own language, by partition
refinement on its own table. [SωS26]'s larger case is that the invariant,
rather than any automaton, can serve as the unit of discourse for
ω-regular languages — identity, complement, classification as facts of one
file; this paper is that program's learning instance.

This paper shows the same object is learnable, and its design can be said
in one sentence: **the learner never poses a hypothesis that is not a
language.** Internally it keeps an observation table — rows, two sorts of
columns matching Arnold's two context shapes, membership bits: the private
ledger where separations are recorded and open slots tracked. But the table
is bookkeeping, not belief. Whenever the learner draws a conclusion or
faces the teacher, it first certifies that its table presents a legal
algebraic object — two query-free checks: the candidate classifier is a
genuine semigroup morphism, and the acceptance pairs are saturated under
conjugacy — and then holds that object in canonical form. What the teacher
sees, every time, is a *well-formed invariant*: the syntactic invariant of
the learner's current belief language.

The discipline is not hygiene for its own sake; it is where the learning
happens. A well-formed invariant denotes exactly one language, so if the
belief is not yet `L`, some lasso disagrees and an exact equivalence oracle
must surrender it: false assent is impossible. Each legality violation,
conversely, is a disagreement the learner catches without the teacher —
two concrete lassos that its own classes name identically, on which the
teacher's answers differ — and one chain of membership queries converts it
into a class split witnessed by a genuine Arnold context. Counterexamples
and legality violations are processed by the *same* mechanism; the teacher
is just one of three sources of disagreement, and the cheapest two are
self-served. Where the self-served queries become indispensable is itself
a theorem: counterexample-guided refinement alone — the engine of every
ω-learner to date — reaches acceptors and nothing finer; a fixpoint it
certifies is either the canonical algebra already or carries no algebra at
all, stalling permanently already on `a → Xa` (§6). The FDFA line and this
paper thus draw different consequences from one shared observation [AF21]:
the field enriches the acceptor family on the near side of that boundary;
the legality discipline is what crosses it, and the rotation lemma —
embedded already in the invariant's definitions — is what makes the
crossing computable.

**Contributions.**

1. A learning algorithm for the syntactic invariant `𝓘(L)` of any
   ω-regular language — to our knowledge the first: plain lasso membership
   and equivalence queries, every hypothesis a well-formed invariant, and a
   limit byte-equal to what the construction of [SωS26] produces (§3–§4),
   at output-polynomial query cost (§5).
2. A typing theorem and a boundary theorem. Legal beliefs make the error
   signal two-sided: no exact oracle ever falsely assents, and the
   certified fixpoint is the canonical algebra (§5). The boundary, refining
   [AF21]'s observation: a fixpoint that counterexample-guided refinement
   alone certifies is either canonical or carries no algebra at all — its
   partition is never a congruence — realized already on the two-letter
   `a → Xa`, before the first counterexample (§6).
3. Experimental evidence from a complete tool implementation: on a
   complement-closed census of 6222 languages every syntactic invariant is
   reconstructed byte-for-byte; the acceptor-typed relaxation stalls
   permanently on half of them; a comparison to the state-of-the-art FDFA
   learner ROLL shows comparable sizes and queries — with LTL-definability
   read off our result by [SωS26]'s aperiodicity check, a decision
   currently tooled on no acceptor representation (§7).

The closest prior work, Urbat and Schröder's algebraic automata learning
[US20], identified the syntactic algebra as the right learnable target for
ω-regular languages — but obtained no effective algorithm: their instance
needs infinitely many alphabet letters, one per possible loop, known in
advance. The rotation lemma supplies the missing finiteness; §8 details the
comparison.
