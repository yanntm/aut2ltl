## 6. What the invariant unlocks

The invariant was built to be used. This section reads decisions off the
finished table: first the band of identity questions the semantics answers
nearly for free, then the definability frontier. Throughout, an invariant is
handled through its finite presentation `(𝒞, λ, ·, P)` under shortlex keys —
the serialized form the byte-equality remark of §3.3 announced.

### 6.1 The exportable invariant and the identity band

What the field exchanges today is a presentation — an automaton in the
Hanoi Omega-Automata (HOA) exchange format, one machine among many for its
language. The invariant serializes to
a file that *is* the language. `𝓘(GF(aa))`, in full:

```
SOS
alphabet: a b
classes: 5
0 a
1 b
2 a·a
3 a·b
4 b·a
letters: a→0  b→1
table:
0: 2 3 2 2 0
1: 4 1 2 1 4
2: 2 2 2 2 2
3: 0 3 2 3 0
4: 2 1 2 2 4
accept:
2 2
```

Classes are listed by shortlex key; the row `c: …` of `table` gives `c·d`
for `d` in key order; `accept` lists `P` — here the single pair
`([a·a], [a·a])`. *(Block to re-verify by engineering against the tool
export, under the `EM₊`/`b` conventions.)*

The file decides lassos by Definition 3.5 with no further apparatus. For
`(a·b)^ω`: the stamp sends the loop to `𝒮(ab) = 3 = [a·b]`, already idempotent
(`3·3 = 3`); the empty stem gives `s = e = 3`; and `3 3` is not listed under
`accept`: rejected — no `aa` recurs.

*Example (canonicity, in bytes).* The two non-isomorphic presentations of
`GF(aa)` in §4.4 — run-parity and reset — both construct exactly this file.
Language equality of the two inputs is not tested; it is exhibited: one
language, one file.

**Proposition 6.1 (the identity band).** Let `𝓘(L) = ⟨𝒮, P⟩` and `𝓘(L')` be
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

**Proposition 6.2 (complement).** `𝓘(L̄) = ⟨𝒮_L, LP(𝒮_L) ∖ P(L)⟩`, writing
`LP(𝒮)` for the set of all linked pairs of a stamp: the complement shares
the stamp — classes, keys, letter map, table — and flips the pair set within
the linked pairs.

*Proof.* Both context shapes of Definition 3.7 are membership equivalences,
symmetric in `L` and `L̄`, so `≈_L = ≈_{L̄}` and the syntactic stamps
coincide, keys included. Every linked pair names at least one lasso (proof
of 6.1(iii)), and all lassos sharing a name share one verdict
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

### 6.2 The LTL frontier

**Theorem 6.3 (the aperiodicity cut — classical).** A regular `L ⊆ Σ^ω` is
LTL-definable iff `𝒞_L` is **aperiodic**: no class has a power cycle of
period `≥ 2` — equivalently, `c^π·c = c^π` for every `c ∈ 𝒞_L`.

The chain is LTL `=` FO[<] `=` star-free `=` aperiodic syntactic algebra
[Kam68, Tho79, DG08], the ω-transport of Schützenberger's theorem [Sch65];
see [DG08] for the consolidated account. What this paper adds is not the
theorem but the table it is read off:

**Corollary 6.4 (the decision).** On the constructed invariant `𝓘(D)`,
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
