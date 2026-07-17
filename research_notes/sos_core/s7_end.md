## 6. Related work

**Arnold [Arn85].** The syntactic congruence is his: the coarsest congruence
saturating a rational ω-language, of finite index, with a recognizing
quotient — three pages from 1985, and the canonicity §3.3 inherits. What the
note does not contain is a construction: no acceptor input, no algorithm —
and forty years without either.

**Perrin–Pin [PP04]; Wilke.** The algebraic frame — ω-semigroups, linked
pairs, the lasso-density fact this paper leans on throughout — is theirs.
Wilke's axiomatization carries the identity `s·(ts)^ω = (st)^ω`; our
rotation identity `c·(dc)^π = (cd)^π·c` is its finite shadow (§3.3),
redeployed as a computation scheme rather than an axiom.

**Maler–Staiger [MS97].** They display the syntactic congruence as a
finitary × infinitary conjunction; at the single slot `q₀` the finitary half
is the classical right congruence. No quotient is computed, and the
infinitary half still quantifies a two-sided context inside the loop.
§4.3's two relations are that split made right-only, and the rotation lemma
is the step the display lacks.

**Carton–Perrin–Pin [CPP08].** A recognizer that sees acceptance — Boolean
transition matrices recording path existence and accepting visits — with the
syntactic quotient reached by saturation over context triples: an example,
not a procedure. The automaton stamp plays their matrices' role on
deterministic Emerson–Lei input; the rotation lemma replaces the saturation.

**Pin–Straubing [PS05].** Stamps: comparing surjective morphisms rather than
abstract semigroups, the reason the letter map is data (§3.1). We transpose
the notion from `Σ*` to `Σ⁺`, where the ω-theory lives.

**Diekert–Gastin [DG08].** The consolidated star-free/aperiodic account, and
the PSPACE aperiodicity argument [DG08, Prop. 12.3] — a nondeterministic
on-the-fly bound that emits no algebra and no evidence. The construction
here is its evidence-producing counterpart, at the same worst-case price
(§5.1); their formula-extraction induction is the path §7 names for rendering.

**Learning [AF16, ABF18, AF21].** The recorded obstruction: the right
congruence alone does not characterize an ω-regular language — LTL languages
with a trivial right congruence exist [AF21] — so the field learns families
of DFAs [AF16, ABF18], presentation-dependent acceptors. The rotation lemma
reads the two-sided congruence from right extensions at prefix-indexed
slots — observation-table shaped (§7).

## 7. Perspectives

The point of an archetype is what it makes routine. Each direction below
opens on the invariant — the language itself in hand — where the
automaton-level literature left it closed or presentation-bound; each is one
claim, not a development.

**Classification beyond the LTL cut.** The acceptance index — Büchi,
co-Büchi, parity `[i, j]`, Rabin — and, subsuming it, the exact Wagner
degree are chain and superchain structure of the syntactic algebra
[CP97, CP99]: data the table carries, computable on it. The finer
first-order fragments (FO², Σ₂, until rank) likewise pair a variety
condition on `𝒞` with a topological side condition [DK09, Wilke99].

**Rendering the algebra as a formula.** On the aperiodic side, a defining
LTL formula is reachable in principle from the algebra by the
Diekert–Gastin induction [DG08]. Starting from automata, the state of the
art translates counter-free automata only [BLS22], with no route from an
arbitrary presentation — nor, without the algebra, a practical way to decide
eligibility in the first place (§5.3).

**Operating on invariants.** Equality and complement (§5.2) are the
degenerate cases of a calculus: align two stamps over one common table — the
one product-priced move — and Boolean combinations of languages become
pointwise operations on pair sets, re-canonicalized by the quotient of §4.3.
The costs concentrate where they must: the ω-rational constructors
(prefixing by a word set, ω-power) and alphabet surgery such as projection
embed powersets — determinization's price resurfacing exactly there, and
only there.

**A census of small languages.** Byte-canonicity makes the small ω-regular
*languages* enumerable: catalogued by `|𝒞|`, one item each, two items
distinct iff their files differ — where existing censuses enumerate
machines and meet each language once per presentation. A reference atlas of
the small languages, deduplicated by the invariant, becomes a well-defined
object of study.

**Learning the algebra.** The rotation lemma is an observation-table
discipline: every two-sided demand of the congruence is met by right
extensions read at prefix-indexed slots (rotation on runs, Lemma 4.8) —
rows and columns, the
shape a minimally-adequate-teacher (MAT) learner consumes. Learning the
syntactic ω-semigroup itself from
membership queries on lassos therefore looks feasible — where [AF21] records
the obstruction for right congruences and the field learns
presentation-dependent families of acceptors instead [AF16, ABF18].

**One level down: finite words.** Run on a complete DFA — final states in
place of marks — the construction degenerates to the classical syntactic
monoid: the mark maps add nothing, the ω-power shape disappears with the
ω-words it quantified over, and the seed is already the congruence — no
rotation, no refinement. The degenerate case landing on the known answer
audits the machinery; and the same aperiodicity check of §5.3 then decides
LTLf-definability [DV13], one level down, where the same tooling gap stands.

## 8. Conclusion

For finite words, the syntactic monoid has carried the algebraic theory of
regular languages for sixty years: one finite algebra per language,
canonical, and everything readable from it. For infinite words the analogous
algebra — the syntactic ω-semigroup of Arnold — has existed since 1985 on
paper only.

The obstruction was never size alone; it was structure. A recognizer for
infinite behaviour must remember acceptance along runs, not endpoints — that
is the mark map. And the syntactic congruence is two-sided, while
everything a finite table offers for free is right-handed — that is the
rotation lemma: a left context carries no information of its own, it only
moves the point where a right test is read. The lemma is the mathematical
core of the paper, and it stands on its own.

What a canonical form changes is the unit of discourse. Automata are
presentations: every pipeline that manipulates them manipulates a choice,
and anything read off them must first be argued independent of that choice.
The invariant is the language: equality is identity of two files, complement
flips a set of pairs, membership is a table walk, LTL-definability is the
absence of a group — and the classical taxonomy of ω-regular languages turns
into structural facts about one finite invariant. Beyond verdicts, the
invariant in hand invites operation — computing with languages, cataloguing
them,
learning them — directions that were closed at the level of presentations.
The construction of this paper reifies Arnold's phantom: the syntactic
ω-semigroup is no longer only defined — it is built.
