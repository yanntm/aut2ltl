## 7. Related work

**Active learning of ω-regular languages.** The line begins with Maler and
Pnueli [MP95], who lift L\* [Ang87] to the subclass of languages `L` with both
`L` and its complement deterministic-Büchi-recognizable — exactly the class
where, by the Staiger theorem they build on [Sta83], the syntactic right
congruence carries the whole language, so a prefix observation table converges.
Farzan et al. [FCC+08] reach the full class by learning the `$`-language
`{u$v : u·v^ω ∈ L}` — introduced, and proved regular and complete for `L`, by
Calbrix, Nivat and Podelski [CNP93] — with plain L\* and extracting a
nondeterministic Büchi automaton. Angluin and Fisman [AF16] systematize this direction as families of
DFAs — a leading right-congruence automaton with per-state progress DFAs — in
three canonical flavors (periodic, syntactic, recurrent), the periodic one being
the FDFA rendering of the `$`-language [LCZL21]; Angluin, Boker and Fisman
[ABF18] study FDFAs as acceptors in their own right, and the trivial-right-
congruence obstruction is [AF21]. Li, Chen, Zhang and Liu [LCZL21] give the
classification-tree FDFA learner implemented in ROLL [LSTCX19], our experimental
baseline. On the passive side, Bohn and Löding extend RPNI to deterministic
ω-automata [BL21] and learn deterministic Büchi automata from samples by
combinations of DFAs [BL22]. All of these target acceptors. Nearest to our
ω-columns in spirit are Michaliszyn and Otop's *loop-index queries* [MO22]:
alongside membership and equivalence, their teacher reveals, for each lasso,
after how many letters *the target automaton* enters its final cycle — an
oracle that, by design, "depend[s] on a particular automaton" [MO22]. It buys
polynomial-time learning of deterministic Büchi automata and, through
LimSup-weighted automata, of deterministic parity automata — the full
ω-regular class — at the price that both the auxiliary query and the learned
object are tied to the teacher's presentation. Our ω-columns probe the same
loop structure through plain lasso memberships, and the limit is
presentation-independent; indeed [MO22]'s own motivation notes that at ω
"there is no notion of the canonical (syntactic) automaton" — true of
automata, and precisely the gap the algebra fills.

**Algebraic learning.** Van Heerdt, Sammartino and Silva's CALF [vHSS17] frames
automata learning categorically but instantiates no ω-algorithm. The decisive
step is Urbat and Schröder [US20], discussed in §1: the syntactic algebra is,
abstractly, the right and learnable target (`Syn(L) ≅ Min(lin(L))`), and the
Wilke-algebra instance stalls on an infinite alphabet of ω-power letters — the
finiteness supplied here by the rotation lemma. Counterexample processing in §4
adapts the binary-search analysis of Rivest and Schapire [RS93].

**The algebra itself.** The two-sorted finite-word/ω-word algebra is Wilke's
[Wil93], in the ω-semigroup form of Perrin and Pin [PP04]; the congruence is
Arnold's [Arn85], its finitary/infinitary display Maler and Staiger's [MS97],
and its materialization as the invariant `𝓘(L)` — with the rotation lemma
this paper transports — is [SωS26]. In sum: [MP95] learned the class
where the right congruence suffices; the FDFA line patched the right congruence
with families of acceptors; [US20] identified the canonical algebraic target
without an effective ω-instance; this paper learns that target, effectively.

## 8. Conclusion

The syntactic ω-semigroup was constructible [SωS26]; it is also learnable, and by
the same mechanism: the rotation lemma, which there collapsed a two-sided
congruence into right computations on a table, here splits into a harvest
procedure and a saturation rule — rows, columns, and representative slots of
lasso queries. On the way we met a finding worth the trip: two-sided columns are
*not enough*, because membership's error signal is one-sided, and without the
saturation sweep the table stalls on a correct acceptor strictly coarser than
the algebra — permanently, already on `a → Xa` (Proposition 4.4), where the
stalled export is not even associative — indeed a certified stall never
carries an algebra at all (Theorem 5.3) — a stall beyond counterexample-guided
refinement, dissolved by the same slot collapse. The learner's limit is not an acceptor
chosen from a family but the canonical invariant of the language — the object
definability questions are read from — so learning and classification cease to
be separate activities. A complement-closed census of 3938 languages bears
this out: the learner reconstructs every canonical invariant byte-for-byte,
and on over a thousand of them — right congruences falling as many as
fifty-three classes short, prefix-independent languages among them — the
algebra is reached only by the saturation sweep, the two-example finding of
§4.2 made generic.
