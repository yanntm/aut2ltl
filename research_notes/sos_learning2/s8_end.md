## 8. Related work

**Active learning of ω-regular languages.** The line begins with Maler and
Pnueli [MP95], who lift L\* [Ang87] to the subclass of languages `L` with
both `L` and its complement deterministic-Büchi-recognizable — exactly the
class where, by the Staiger theorem they build on [Sta83], the syntactic
right congruence carries the whole language, so a prefix observation table
converges. Farzan et al. [FCC+08] reach the full class by learning the
`$`-language `{u$v : u·v^ω ∈ L}` — introduced, and proved regular and
complete for `L`, by Calbrix, Nivat and Podelski [CNP93] — with plain L\*
and extracting a nondeterministic Büchi automaton. Angluin and Fisman
[AF16] systematize this direction as families of DFAs — a leading
right-congruence automaton with per-state progress DFAs — in three
canonical flavors (periodic, syntactic, recurrent), the periodic one being
the FDFA rendering of the `$`-language [LCZL21]; Angluin, Boker and Fisman
[ABF18] study FDFAs as acceptors in their own right, and the observation
that the right congruence under-determines the language is [AF21]. Li,
Chen, Zhang and Liu [LCZL21] give the classification-tree FDFA learner
implemented in ROLL [LSTCX19], our experimental baseline. On the passive
side, Bohn and Löding extend RPNI to deterministic ω-automata [BL21] and
learn deterministic Büchi automata from samples by combinations of DFAs
[BL22]. Every one of these targets is an acceptor, and each learner is
complete for its target; §6's boundary theorem is our account of why
acceptors are what counterexample-guided refinement reaches — the FDFA
line and this paper are the two sides of [AF21]'s observation. Nearest to our
ω-columns in spirit are Michaliszyn and Otop's *loop-index queries* [MO22]:
alongside membership and equivalence, their teacher reveals, for each
lasso, after how many letters *the target automaton* enters its final
cycle — an oracle that, by design, "depend[s] on a particular automaton"
[MO22]. It buys polynomial-time learning of deterministic Büchi automata
and, through LimSup-weighted automata, of deterministic parity automata —
the full ω-regular class — at the price that both the auxiliary query and
the learned object are tied to the teacher's presentation. Our ω-columns
probe the same loop structure through plain lasso memberships, and the
limit is presentation-independent; indeed [MO22]'s own motivation notes
that at ω "there is no notion of the canonical (syntactic) automaton" —
true of automata, and precisely the gap the algebra fills.

**Algebraic learning.** Van Heerdt, Sammartino and Silva's CALF [vHSS17]
frames automata learning categorically but instantiates no ω-algorithm.
The decisive step is Urbat and Schröder [US20], and the relationship is
precise. Generically, for languages recognized by a monad `T`, they prove
that the syntactic `T`-algebra is the minimal automaton of a *linearized*
language over the alphabet of an automata presentation of the free
algebra — `Syn(L) ≅ Min(lin(L))` [US20, Thm 5.14] — and learn that
automaton by a generalized L\*. Instantiated to Wilke algebras this covers
ω-regular languages, in principle. In instance it is not effective: the
presentation validating the isomorphism carries the sorted alphabet
`Σ₊,ω = {ω} ∪ {·v^ω : v ∈ Σ⁺}`, whose letters are *operations* — `ω` sends
`w` to `w^ω`, and `·v^ω` sends `w` to `w·v^ω`: one letter per finite word
`v`, Arnold's ω-power contexts recast as an *infinite alphabet* — while
the finite restriction to `{ω}` alone is only a *weak* presentation,
outside the theorem, of which [US20] itself notes that the resulting
learned object resembles a family of DFAs. The rotation lemma is exactly
the missing finiteness: no ω-power context need be an alphabet letter
known in advance, because a counterexample- and legality-driven harvest of
at most `|𝒞|` ω-columns reaches the same congruence (§4, Theorem 5.2).
[US20] settles what the target is; this paper makes the ω-instance an
algorithm, and runs it. Counterexample processing in §4 adapts the
binary-search analysis of Rivest and Schapire [RS93].

**The algebra itself.** The two-sorted finite-word/ω-word algebra is
Wilke's [Wil93], in the ω-semigroup form of Perrin and Pin [PP04]; the
congruence is Arnold's [Arn85], its finitary/infinitary display Maler and
Staiger's [MS97], and its materialization as the invariant `𝓘(L)` — with
the rotation lemma and canonicalization theorem this paper transports —
is [SωS26]. In sum: [MP95] learned the class where the right congruence
suffices; the FDFA line patched the right congruence with families of
acceptors; [US20] identified the canonical algebraic target without an
effective ω-instance; this paper learns that target, effectively.

## 9. Conclusion

The syntactic ω-semigroup was constructible [SωS26]; it is now learnable —
by a student who refuses to believe anything that is not a language. The
learner's belief is at every step a well-formed invariant, the canonical
form of an ω-regular language; the rotation lemma, which on the
construction side made the two-sided congruence computable from an
automaton, splits on the learner's side into a harvest, where every
teacher counterexample pays for a witnessed split, and a legality
discipline, whose checks cost no queries and whose violations the learner
referees itself. Because a well-formed invariant denotes exactly one
language, an exact oracle can never falsely assent — and the boundary is a
theorem: what counterexample-guided refinement alone certifies is either
the canonical algebra or no algebra at all, the stall on a two-letter
implication made general. With the discipline, the limit is not an
acceptor chosen from a family but the language's syntactic invariant, the
object definability questions are read from: learning and classification
cease to be separate activities. A complement-closed census of 6222
languages bears this out — every invariant reconstructed byte-for-byte,
half of the census reachable only through the discipline.
