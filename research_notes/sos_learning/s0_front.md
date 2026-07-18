# Learning the Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Shadow draft — rev. 2026-07-18. Remaining `⟨TBD: …⟩` placeholders await the
M4 campaign's completed sweep.*

## Abstract

The syntactic ω-semigroup of a regular ω-language `L` is its canonical algebra:
presentation-independent, complete, and the object from which membership,
equivalence, and every definability property of `L` — LTL-definability included —
are read. It has recently been materialized for the first time [SωS26]: the
abstract algebra represented by a computable, serializable invariant
`𝓘(L) = ⟨𝒮, P⟩` — a stamp classifying the finite words, a set of accepting
linked pairs over it — constructed there from a deterministic automaton. This
paper shows the algebra is *learnable*: we give an active-learning algorithm in
the MAT model whose queries are memberships of ultimately-periodic words only,
whose target is the invariant `𝓘(L)`, and whose hypotheses are its
automaton-like Cayley form.
To our knowledge it is
the first MAT learner for the full ω-regular class whose limit is the
language's own algebra — a canonical object of `L` itself, rather than an
acceptor chosen from a family.
Two results carry the
paper. First, a *harvest theorem*:
any lasso on which a hypothesis errs surrenders a separating table column, by a
two-phase replacement chain — stem first, then loop-head, where a left extension
of a loop is nothing but a rotation of it — with a binary search in each phase. Second,
a finding of independent interest: an observation table with two-sided columns is
*still not enough*, because membership's error signal is one-sided — the table can
stabilize on a correct acceptor coarser than the algebra, an FDFA in algebraic
clothing, and does so *permanently* on a language as plain as `a → Xa`; such a
certified stall is provably never a congruence — a correct acceptor and no
algebra at all. What restores two-sidedness is a *left-saturation* sweep over class
representatives whose checks cost no queries at all — the rotation lemma's slot
collapse transported to the learner's
side; with it, the fixpoint is exactly Arnold's quotient, after at most `|𝒞|`
class splits
and `O(|𝒞|²·|Σ|)` membership queries plus a logarithmic-cost analysis per
counterexample — output-polynomial in the canonical target. The established FDFA
approach learns one of three competing canonical families of DFAs — none of them
the language's own algebra, all of them acceptors, answering no definability
question by themselves; this learner converges to the one object such questions
are read from — and two learned invariants are compared by byte-equality, whereas
acceptors need a product construction. On a complement-closed census of 3938
ω-regular languages the learner reconstructs every canonical invariant
byte-for-byte, at class counts past a hundred; over a thousand of them stall
permanently without the sweep — the right congruence falling as many as
fifty-three classes short of an algebra that counterexample-guided refinement
provably never reaches — and the family includes prefix-independent
languages, whose recovering left contexts act entirely inside the loop, as
rotations.

---

## 1. Introduction

Active learning asks a machine to reconstruct an unknown language *exactly*,
from experiments alone. In Angluin's minimally adequate teacher (MAT) model
[Ang87] — the setting of this paper, recalled in §2.1 — the learner poses
membership queries ("is this word in the language?") and equivalence queries
("is this hypothesis the language?", answered by *yes* or by a
counterexample), and the L\* algorithm learns the minimal DFA of any regular
language with polynomially many queries. The paradigm's reach is practical —
assume–guarantee verification [FCC+08]; state-machine models learned from
black-box implementations of smart cards, network protocols, and legacy
software (see [Vaa17] for a survey) — and its
engine is always the same: convergence to a *canonical* target, an object
owned by the language rather than by any machine presenting it.

Active learning of ω-regular languages has a structural handicap that finite words
never had. For finite words, Angluin's L\* rests on the Myhill–Nerode theorem: the
right congruence of the language *is* the minimal acceptor, so an observation table
of prefixes against suffixes converges to a canonical object. For ω-words the right
congruence is not informative: it can be trivial while the language is complex, and
languages as plain as `FG(a ∨ Xa)` have a one-class right congruence [AF21]. The
earliest ω-learner drew the line honestly: Maler and Pnueli's L\* extension [MP95]
covers exactly the languages whose right congruence carries everything — `L` and
its complement both deterministic-Büchi, by the Staiger theorem they build on
[Sta83] — and stops there. The field's route past the line — families of DFAs (FDFAs) covering
the lasso structure [AF16, ABF18] — works, at a price: *three* canonical normal
forms per language (periodic, syntactic, recurrent) instead of one object, the
choice among them the learner's; and what is learned is an *acceptor*, not the
language's algebra — no definability question is answerable from it without
further construction.

The canonical object exists. Arnold's syntactic congruence [Arn85] quotients finite
words by interchangeability in every ultimately-periodic context, in two shapes —
in the stem, or inside the loop — and its quotient, the syntactic ω-semigroup
(SωS), is the exact ω-analogue of the syntactic monoid: presentation-independent,
finite, and complete for definability. It was recently materialized for the
first time [SωS26] — represented by the computable invariant `𝓘(L)`,
constructed from a deterministic automaton; the key computational step
there is a **rotation lemma** [SωS26, Lem 4.1] — a left factor prepended to a
loop merely *rotates* it, `x·(u·y)^ω = x·u·(y·u)^ω`, a right extension read at a
shifted starting slot — which renders the two-sided congruence as the coarsest
right-invariant refinement of a seed relation [SωS26, Thm II].

This paper's observation is that the rotation lemma is not about automata at all —
but transporting it to the query model splits it in two, and the split is the
story. Its *right-extension* half becomes a harvest procedure: any lasso on which
the hypothesis errs is interpolated, through representative replacements at the
stem and then at the head of the loop, into a chain of membership queries whose
bit must flip — and the flip *is* a new separating column (§4). Its *slot* half —
left factors act only by re-indexing finitely many slots [SωS26, Lem 4.3] —
becomes a saturation
rule: the columns' left prefixes need range only over class representatives, so
the two-sidedness that membership errors cannot signal (§4.2, the failure we did
not anticipate) is enforced by a query-free sweep (§4.3). On top of the two halves
we build an L\*-style learner whose hypotheses are not automata but the invariant
`𝓘(L)` itself, in its finite presentation `(𝒞, λ, ·, P)`: classes keyed by
shortlex representatives, letter map,
multiplication table, accepting linked pairs. The result is, to our
knowledge, the first active-learning algorithm for the *full* class of
ω-regular languages whose limit is a canonical object of the language — the
algebra its definability questions are read from — rather than an acceptor
chosen from a family; placing ω-learning back on the L\* footing that
Myhill–Nerode's failure at ω seemed to forbid is what this paper is for.

**Contributions.**
1. A two-sorted observation table for Arnold's congruence, with lasso membership
   queries only, and a hypothesis in *Cayley form* — a deterministic automaton on
   classes plus accepting pairs — requiring no monoid products mid-learning (§3).
2. The harvest theorem: every disagreeing lasso surrenders a separating column,
   found by a two-phase replacement chain with binary search — the loop phase
   enacting the rotation; this is the finiteness ingredient the generic algebraic
   approach lacks at ω [US20] (§4.1).
3. The finding: two-sided columns are not enough. Membership's error signal is
   one-sided, and the table can stabilize on a correct acceptor strictly coarser
   than the algebra — the right-congruence obstruction [AF21] reborn one level up.
   The stall is real and minimal: `a → Xa` stalls permanently, four classes
   against five, with zero counterexamples (Proposition 4.4). A query-free
   left-saturation sweep over class representatives — the rotation
   lemma's slot collapse [SωS26, Lem 4.3] — restores two-sidedness (§4.2–4.3).
4. The saturated-fixpoint theorem: termination after at most `|𝒞|` splits, and
   canonicity — the fixpoint *is* the syntactic stamp, exported as `𝓘(L)`;
   equivalence between
   hypotheses is invariant equality, replacing product constructions — with a
   converse: an exactly-certified fixpoint is either canonical or carries no
   algebra at all (§5, Theorem 5.3).
5. An implementation as a pure query learner, and an evaluation against the
   canonical target: byte-exact reconstruction across a complement-closed
   census of 3938 languages (`N` past 100, zero mismatches), the query bounds
   of Proposition 5.4 confirmed (harvest logarithmic in counterexample
   length), saturation shown indispensable on a family of over a thousand
   permanent stalls whose canonical algebras are provably beyond
   counterexample-guided refinement — prefix-independent languages among
   them, the ω-power left action of Corollary 4.7 realized — and a comparison
   to the FDFA baseline (ROLL) on which only the algebra answers
   LTL-definability, the FDFA answering it not at all (§6).

**Relation to the algebraic approach.** The closest work is Urbat and Schröder's
algebraic automata learning [US20], and the relationship is precise. Generically,
for languages recognized by a monad `T`, they prove that the syntactic `T`-algebra
is the minimal automaton of a *linearized* language over the alphabet of an
automata presentation of the free algebra — `Syn(L) ≅ Min(lin(L))` [US20,
Thm 5.14] — and learn that automaton by a generalized L\*. Instantiated to Wilke
algebras this covers ω-regular languages, in principle. In instance it is not
effective: the presentation validating the isomorphism carries the sorted alphabet
`Σ₊,ω = {ω} ∪ {·v^ω : v ∈ Σ⁺}`, whose letters are *operations* — `ω` sends `w` to
`w^ω`, and `·v^ω` sends `w` to `w·v^ω`: one letter per finite word `v`, Arnold's
ω-power contexts recast as an *infinite alphabet* — while the finite restriction to `{ω}`
alone is only a *weak* presentation, outside the theorem, of which [US20] itself
notes that the resulting learned object resembles a family of DFAs. The rotation
lemma is exactly the missing finiteness: no ω-power context need be an alphabet
letter known in advance, because a counterexample-driven harvest of at most `|𝒞|`
ω-columns reaches the same congruence (§4, Theorem 5.1). [US20] settles what the
target is; this paper makes the ω-instance an algorithm, and runs it.

Three running examples — `GF(aa)`, `Even`, `EvenBlocks` [SωS26] — recur
throughout (descriptions, automata and target invariants in §2.3,
Figures 1–2). Two of them are traced *live* through §3–5: `Even`
(`(aa)*·!a·Σ^ω`, co-safety: membership is decided by a finite prefix, i.e. on
the stem) and `EvenBlocks`
(prefix-independent, trivial right congruence — outside [MP95]'s class,
degenerate for any FDFA's leading automaton, and precisely the case the ω-sort
of our columns is built for). The trace has a punchline worth spoiling: the two
languages hand the learner first counterexamples that break the *same wrong
name* — in both, the pair `([a],[a])` and its representative lasso `a·a^ω` have
absorbed everything that ever read an `a` — and the algorithm routes the two
repairs through opposite Arnold shapes. `GF(aa)`, whose transition-monoid
group is a presentation artifact the algebra destroys, remains the evaluation's
third specimen (§6).
