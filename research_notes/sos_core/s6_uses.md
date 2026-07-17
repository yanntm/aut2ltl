## 5. What the invariant unlocks

The invariant was built to be used. This section first splits the cost of
building the table from the cost of using it, then reads decisions off the
finished table: the band of identity questions the semantics answers nearly
for free, and the definability frontier. Throughout, an invariant is handled
through its finite presentation `(𝒞, λ, ·, P)` under shortlex keys — the
serialized form the byte-equality remark of §3.3 announced.

### 5.1 Complexity

Two costs must be kept apart: building the invariant from an automaton, and
using it once built.

**Building.** The construction is dominated by the size of the enriched
semigroup: an enriched element is a vector of `|Q|` slots over the local
domain `Q × 2^F` (Definition 4.2), so

```
    |EM₊(D)| ≤ (|Q|·2^{|F|})^{|Q|},
```

and the `|Q|` in the exponent is the source of the explosion. That a wall
sits somewhere is a mathematical necessity, not an engineering apology:
deciding aperiodicity of a regular ω-language — the LTL read-off of §5.3 —
is PSPACE-complete, with hardness transferred from finite-word minimal-DFA
aperiodicity [CH91] and the ω upper bound from [DG08, Prop. 12.3]; the
surrounding classifications are no cheaper. Everything around the enriched
semigroup is benign by contrast: each generator acts slot-wise; the loop
verdicts cost one functional-graph walk per element; the residual partition
of the states and the congruence on the elements are two Moore refinements
over the closed table, polynomial in `|EM₊(D)|` and `|Q|`; and `P(D)` is one
lasso test per linked pair. The cost is entirely the size of
`EM₊(D)`, and that size is intrinsic to the problem, not to the construction.

**Using.** Once built, the sizes change meaning: `|𝒞|` is a function of `L`
alone (Theorem 4.11) — the intrinsic complexity of the language, the
ω-analogue of the syntactic monoid's size — where `|Q|` and `|EM₊(D)|` were
functions of a presentation. The serialized invariant is `O(|𝒞|²)` table
entries plus a pair set `P ⊆ 𝒞 × 𝒞`, and every operation below is a scan of
that table. The presentation debt — determinization [Saf88], then `EM₊(D)` —
is paid once, at entry; nothing downstream ever revisits the automaton.

**Symbolic prospects.** On a more optimistic note, every object and operation
here is BDD-friendly and the redundancy is high, so a symbolic approach is
likely to alleviate much of this inherent complexity. The ingredients are all
Boolean — the alphabet `2^AP`, the mark sets over `F`, the `Inf`/`Fin`
formula `Acc` — and every step is a set operation, not an arithmetic one: closing
`EM₊(D)` under composition, the two right relations of §4.3, and the
partition refinement of §4.4 are all images, fixpoints, and quotients over
sets, native to decision diagrams.

### 5.2 The exportable invariant and the identity band

What the field exchanges today is a presentation — an automaton in the
Hanoi Omega-Automata (HOA) exchange format, one machine among many for its
language. The invariant serializes to
a file that *is* the language. `𝓘(GF(aa))`, in full:

```
SOS v1
ap: a
classes: 6
0 eps
1 !a
2 a
3 !a;a
4 a;!a
5 a;a
letters: !a->1 a->2
mult:
0: 0 1 2 3 4 5
1: 1 1 3 3 1 5
2: 2 4 5 2 5 5
3: 3 1 5 3 5 5
4: 4 4 2 2 4 5
5: 5 5 5 5 5 5
accept:
5 5
residuals: 1
0 eps
res-step:
0: 0 0
```

The file is the tool's export, verbatim — the one place the paper keeps the
raw letters: the alphabet is the single atom and its negation, `ap: a` with
`!a` for the paper's `b`, and keys read `x;y` for `x·y`. Classes are listed
by shortlex key, monoid convention: class `0 eps` is the adjoined `[ε]`, so
`classes: 6` counts `|𝒞| = 5` plus the basepoint. The row `c: …` of `mult`
gives `c·d` for `d` in id order; `accept` lists `P` — here the single pair
`([a·a], [a·a])`, ids `5 5`. The trailing `residuals:` block is derived
data — the right congruence, recomputable from the core, so byte equality is
unaffected; its single class exhibits `GF(aa)`'s prefix-independence.

The file decides lassos by Definition 3.5 with no further apparatus. For
`(a·b)^ω`: the stamp sends the loop to `𝒮(ab) = 4 = [a·b]`, already idempotent
(`4·4 = 4`); the empty stem gives `s = e = 4`; and `4 4` is not listed under
`accept`: rejected — no `aa` recurs.

*Example (canonicity, in bytes).* The two non-isomorphic presentations of
`GF(aa)` in §4.4 — run-parity and reset — both construct exactly this file.
Language equality of the two inputs is not tested; it is exhibited: one
language, one file.

**Proposition 5.1 (the identity band).** Let `𝓘(L) = ⟨𝒮, P⟩` and `𝓘(L')` be
syntactic invariants over `Σ`, serialized under shortlex keys. Then:

(i) *(equality)* `L = L'` iff the two serializations are byte-identical;

(ii) *(membership)* `u·v^ω ∈ L` is decided by one evaluation of `𝒮` — the
letter map `λ`, then table products — and one lookup in `P`
(Definition 3.5);

(iii) *(emptiness, universality)* `L = ∅` iff `P = ∅`, and `L = Σ^ω` iff `P`
is the set of all linked pairs of `𝒮`;

(iv) *(witness)* every `(s, e) ∈ P` yields, from its keys, the canonical
lasso `u_s·(u_e)^ω ∈ L`.

*Proof.* (i) is Theorem 3.10(ii) with the byte-equality remark: the unique
isomorphism is the identity on shortlex names. (ii) is Definition 3.5, whose
verdict is presentation-independent by Theorem 3.10(i). (iii): every linked
pair names a lasso — pick `u ∈ s`, `v ∈ e` by surjectivity: `𝒮(v)^π = e` and
`𝒮(u)·e = s` — so `P = ∅` accepts no lasso and `P` full accepts them all;
two regular ω-languages agreeing on all lassos are equal
[PP04, Ch. I, Cor. 9.8], here to `∅` and to `Σ^ω` respectively. (iv): the
presentation `(u_s, u_e)` lands on `(s, e)` — the keys are nonempty,
`𝒮(u_e) = e` is idempotent so `e^π = e`, and `𝒮(u_s)·e = s·e = s` — and
`(s, e) ∈ P` accepts it. ∎

**Proposition 5.2 (complement).** `𝓘(L̄) = ⟨𝒮_L, LP(𝒮_L) ∖ P(L)⟩`, writing
`LP(𝒮)` for the set of all linked pairs of a stamp: the complement shares
the stamp — classes, keys, letter map, table — and flips the pair set within
the linked pairs.

*Proof.* Both context shapes of Definition 3.7 are membership equivalences,
symmetric in `L` and `L̄`, so `≈_L = ≈_{L̄}` and the syntactic stamps
coincide, keys included. Every linked pair names at least one lasso (proof
of 5.1(iii)), and all lassos sharing a name share one verdict
(Theorem 3.10(i)): the names split, `P(L)` holding those whose lassos lie in
`L`, and the remaining linked pairs are exactly the names of the lassos of
`L̄` — that is, `P(L̄)`. ∎

*Remark (what the flip is, and is not).* On our deterministic Emerson–Lei
input, complementation is already cheap — dualize `Acc` on the same `D` — so
the flip claims no speedup over the input format; the expensive contrast
(`2^{Θ(n log n)}` for nondeterministic Büchi [Saf88]) belongs to
nondeterminism. The gain is the target: the flipped invariant is *already
canonical* — it is `𝓘(L̄)` itself, no re-canonicalization — and it makes a
structural fact plain: `L` and `L̄` share their entire algebra, and `P`
alone tells them apart. Equality is where the band has no automaton-level
rival: a corpus of `N` presentations deduplicates by `O(N²)` pairwise
product constructions, a corpus of serialized invariants by hashing — equal
languages, identical bytes.

### 5.3 The LTL frontier

**Theorem 5.3 (the aperiodicity cut — classical).** A regular `L ⊆ Σ^ω` is
LTL-definable iff `𝒞_L` is **aperiodic**: no class has a power cycle of
period `≥ 2` — equivalently, `c^π·c = c^π` for every `c ∈ 𝒞_L`.

The chain is LTL `=` FO[<] `=` star-free `=` aperiodic syntactic algebra
[Kam68, Tho79, DG08], the ω-transport of Schützenberger's theorem [Sch65];
see [DG08] for the consolidated account. What this paper adds is not the
theorem but the table it is read off:

**Corollary 5.4 (the decision).** On the constructed invariant `𝓘(D)`,
LTL-definability of `L(D)` is decided by finitely many table products —
compute `c^π` for each class, test `c^π·c = c^π` — and the verdict is exact
in both directions, whatever `D` presented the language, because
`𝓘(D) = 𝓘(L)` (Theorem 4.11). ∎

Canonicity is what the exactness rests on. On a non-canonical recognizer
only one direction survives: aperiodicity of `EM₊(D)` — or of the transition
monoid — is inherited by the quotient and thus *sufficient* for LTL, but a
group there proves nothing, since it can be pure presentation
(Proposition 4.5's one-state witness; `GF(aa)`'s transposition, which §4.4
kills). On the four examples: `aUGb` — `[a·b]` falls to the idempotent
`[b·a]` in one step, every power cycle has period 1: LTL. `GF(aa)` — the
`Z₂` of its presentation died in the quotient, all five classes settle with
period 1: LTL. `Even` and `EvenBlocks` — `[a]·[a] = [a·a]` and
`[a·a]·[a] = [a]`, a power cycle of period 2: a genuine group, not LTL, and
the invariant's verdict certifies it.

**A practical instance.** The Property Specification Language PSL
(IEEE 1850), with its sequential extended regular expressions (SEREs),
properly extends LTL and is the specification idiom of hardware
verification; the mod-2 counting that
takes a written property out of LTL lives *syntactically* in an even
repetition `{·}[*2]`. "Is this PSL property actually LTL?" — simpler, far
better tool-supported — is asked with no tool to answer it; it is exactly
the table check above, and `Even` and `EvenBlocks` are its minimal
witnesses.
