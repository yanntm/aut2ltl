# Learning the Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Shadow draft — rev. 2026-07-19. Every §6 figure traces to the committed
census record via the report companion.*

## Abstract

The syntactic ω-semigroup of a regular ω-language `L` is its canonical
algebra: presentation-independent, complete, and the object from which
membership, equivalence, and every definability property of `L` —
LTL-definability included — are read. It was recently materialized as a
computable, serializable invariant `𝓘(L)`, constructed from a deterministic
automaton [SωS26]. This paper shows the invariant is *learnable*: an
active-learning algorithm in Angluin's MAT model whose only queries are
memberships of ultimately-periodic words, and whose limit is `𝓘(L)` itself —
to our knowledge the first learner for the full ω-regular class whose target
is a canonical object of the language, rather than an acceptor chosen from a
family. Counterexamples do half the work: any lasso on which a hypothesis
errs surrenders a separating table column. The other half they provably
cannot do: membership's error signal is one-sided, and the learner can
stabilize on a correct acceptor strictly coarser than the algebra,
*permanently*, already on a language as plain as `a → Xa` — and such a
certified stall never carries an algebra at all. What restores two-sidedness
is a saturation sweep whose checks cost no queries, and with it the fixpoint
is exactly the syntactic invariant, at output-polynomial query cost. On a
complement-closed census of 6222 languages the learner reconstructs every
syntactic invariant byte-for-byte; half of them stall permanently without
the sweep; and LTL-definability is read off each learned invariant — a
question no family of acceptors answers.

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
ABF18]. All of these targets are acceptors. None is an object of the
language alone, and none answers a definability question without further
construction.

Yet the canonical object exists. Arnold's syntactic congruence [Arn85]
quotients finite words by interchangeability in every lasso context — in
the stem, or inside the loop — and its quotient, the syntactic ω-semigroup,
is the exact ω-analogue of the syntactic monoid. It was recently
materialized as the invariant `𝓘(L)`: a finite classifier of finite words
plus a set of accepting stem–loop pairs, serialized to a byte-canonical
file, constructed from a deterministic automaton [SωS26]. The key step there
is a *rotation lemma*: carrying a factor from a loop's front onto the stem
leaves the infinite word unchanged — a left extension of a loop is nothing
but a rotation of it.

This paper shows the same object is learnable, and by the same lemma — which
is not about automata at all. Transported to the query model it splits in
two. One half turns any lasso the hypothesis gets wrong into a new column of
the table: counterexamples pay their way, as they do in L\*. The other half
turns left contexts — the two-sided congruence's whole difficulty — into a
sweep of table checks that cost no queries at all.

That sweep is not an optimization, and its necessity is the paper's central
finding — one we did not anticipate. Membership queries can only catch a
hypothesis that mispredicts some lasso, and that error signal is one-sided:
the learner can stabilize on a correct *acceptor* strictly coarser than the
algebra, every prediction right, the equivalence oracle assenting —
permanently. The stall is not exotic. We searched for the smallest
realization and found a two-letter implication: on `a → Xa` the sweep-free
learner converges, with zero counterexamples, one class short of the
algebra — and we prove no counterexample can ever arrive. Nor is the result
merely one class short: a certified stall's classes carry no algebra at
all. The refinement loop that drives L\* — and every ω-learner since — has
nothing left to react to; what breaks the stall must be a query the learner
poses on its own initiative. The sweep is that query, and it closes the gap
exactly.

**Contributions.**

1. A learning algorithm for the syntactic invariant `𝓘(L)` of any ω-regular
   language — to our knowledge the first: plain lasso membership and
   equivalence queries, no algebra mid-learning, and a limit byte-equal to
   what the construction of [SωS26] produces (§3–§4).
2. A structural finding: counterexample-guided refinement is provably not
   enough at ω. The learner stalls permanently on languages as simple as
   `a → Xa`, certified correct as an acceptor yet carrying no algebra; a
   query-free saturation sweep repairs it, the repaired fixpoint is exactly
   the syntactic invariant, and the query cost is output-polynomial (§4–§5).
3. Experimental evidence from a complete tool implementation: on a
   complement-closed census of 6222 languages every syntactic invariant is
   reconstructed byte-for-byte, half the census stalls without the sweep,
   and a comparison to the state-of-the-art FDFA learner ROLL shows
   comparable sizes and queries — with LTL-definability read off our result,
   and not off theirs (§6).

The closest prior work, Urbat and Schröder's algebraic automata learning
[US20], identified the syntactic algebra as the right learnable target for
ω-regular languages — but obtained no effective algorithm: their instance
needs infinitely many alphabet letters, one per possible loop, known in
advance. The rotation lemma supplies the missing finiteness; §7 details the
comparison.

Five examples accompany the paper, each with its automaton and target
algebra drawn in §2.3. Three run through the text — `GF(aa)`, whose
presentation carries a spurious group the algebra destroys; `Even`, the
canonical mod-2 language; and `EvenBlocks`, its prefix-independent twin,
invisible to every right-congruence-seeded approach. Two of them are traced
live through §3–§5, and their traces share a punchline: both languages hand
the learner the same wrong merge, and the repairs route through the two
opposite shapes of Arnold's congruence. The last two, `a → Xa` and
`a ∧ XG¬a`, are the stall specimens, found by exhaustive search over the
smallest instances: the reef where every learner without the sweep runs
aground.
