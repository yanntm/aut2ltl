# sos_core_32 — proposed §3.2 (full text) and the re-cut of §3.3+

Standalone for review, not yet fused; companion to `sos_core_33.md`. The
reorganization: admissibility becomes the entry condition of the semantics —
§3.2 defines the query on *presentations*, exhibits the well-definedness
failure, and earns `L(𝓘)` through saturation; §3.3 keeps only canonization
(Arnold → `𝓘(L)` → `reduce`). Numbering is aligned: items 3.5–3.8 migrate from
`sos_core_33.md` into §3.2 with their numbers unchanged, so that file's
§3.9–3.15 apply verbatim as the new §3.3. Part 1 below is full replacement
text for §3.2; Part 2 lists the re-cut and its ripples.

---

## Part 1 — §3.2, full text

### 3.2 Semantics: the language of an invariant

An invariant decides lassos with the data it carries and nothing else: `λ`
assigns each letter its class, the table `M` extends that assignment to every
finite word — stem and loop alike — and `P` lists the pairs that accept. This
section builds the decision in that order — words to classes, presentations to
pairs — and ends on the exact law `P` must obey for the verdicts to define a
language at all.

**Definition 3.3 (fold).** Let `𝒜 = (𝒞, λ, M)` be an algebra over `Σ`. The
**fold** of `𝒜` is the map `⟦·⟧ : Σ* → 𝒞` extending the letter map to all finite
words through the table: for `u = x₁x₂⋯xₙ ∈ Σ*`,
`⟦u⟧ := λ(x₁)·λ(x₂)·⋯·λ(xₙ)`, the empty product being `⟦ε⟧ := λ(ε) = [ε]`; we call
`⟦u⟧` the fold of `u`.

The fold is well defined: `M` is a total function and associative
(Definition 3.1), so the product of the letter classes always exists and its
value does not depend on how it is parenthesized — one class per word. It is
moreover a monoid morphism — `⟦u·v⟧ = ⟦u⟧·⟦v⟧`, `⟦ε⟧ = [ε]` — the only one
agreeing with `λ` on the letters: on nonempty words it is §2's morphism `φ`,
realized on the table, and the adjoined `[ε]` extends it to the empty word.

*Example.* On Figure 1 (`aUGb`), the fold of a word is where its reading ends —
one letter, one edge, from the root: `⟦aab⟧ = [a]·[a]·[b] = [a·b]`, and
`⟦ba⟧ = [b]·[a] = [b·a]`, the dead class.

**Generated algebras.** Call `𝒜` **generated** when every class is the fold of
some word. From here on, algebras are generated; nothing is lost: the folds form
a submonoid, the query below consults no other class, and one breadth-first walk
of the letter actions restricts an arbitrary algebra to its generated part. We
write `𝒲 := ⟦Σ⁺⟧` for the **word classes**, the folds of nonempty words; `𝒲` is
closed under `M`, and in the canonical invariants of §3.3 `𝒲 = 𝒞 ∖ {[ε]}`,
though an arbitrary algebra may fold nonempty words onto its identity.

**Definition 3.4 (presentation; query).** Let `𝓘 = ⟨𝒜, P⟩` be an invariant over
`Σ`. A **presentation** of a lasso `w ∈ Σ^ω` is a pair `(u, v)` with `u ∈ Σ*`,
`v ∈ Σ⁺` and `w = u·v^ω`. The presentation **folds to** the pair of classes
`(⟦u⟧·e, e)`, where `e := ⟦v⟧^ω` is the idempotent power of the fold of the
loop; and the **query** of `(u, v)` on `𝓘` **accepts** iff that pair is listed:

```
    (u, v)  accepted   iff   (⟦u⟧·e, e) ∈ P,      e := ⟦v⟧^ω.
```

Deliberately, no language is defined yet: the query judges a *presentation*,
not an ω-word, and the section's remaining work is to earn the passage from one
to the other.

Say a pair **names** the lasso `w` when some presentation of `w` folds to it. A
name is a linked pair — `e² = e` by construction, and `(⟦u⟧·e)·e = ⟦u⟧·e` — and
both coordinates are folds of nonempty words: pick `k ≥ 1` with `⟦v⟧^k = e`;
then `e = ⟦v^k⟧` and `⟦u⟧·e = ⟦u·v^k⟧`. So every name lies in `𝒲 × 𝒲`. Pairs of
`P` outside the names — non-linked pairs, pairs touching a class with no
nonempty preimage — are inert: no presentation ever folds to them.

*Example.* On Figure 1 (`aUGb`), the two presentations we have been reading
since §2. For `(aab, b)`: the loop folds to `⟦b⟧ = [b]`, already idempotent, so
`e = [b]`; the stem folds to `⟦aab⟧ = [a·b]` and `[a·b]·[b] = [a·b]`. The pair
`([a·b], [b])` is in `P`: the query accepts. For `(ba, ab)`: the loop folds to
`⟦ab⟧ = [a·b]`, not idempotent — its square `[b·a]` is — so `e = [b·a]`; the
stem folds to `[b·a]` and `[b·a]·[b·a] = [b·a]`. The pair `([b·a], [b·a])` is
not in `P`: rejected, as §2 announced.

**The query is not yet a semantics.** The query reads one presentation, and a
lasso has many — `u·v^ω = (uv)·v^ω = u·(v²)^ω = (u·v₁)·(v₂·v₁)^ω` — and nothing
yet says they agree. For an arbitrary pair set they do not. Let `𝒵` be the
**mod-2 counter** over `Σ = {a, b}`: three classes `𝒞 = {[ε], [a], [a·a]}`,
both letters sharing a class — `λ(a) = λ(b) = [a]` — and products
`[a]·[a] = [a·a]`, `[a·a]·[a] = [a]`, `[a·a]·[a·a] = [a·a]`: the fold of a word
is the parity of its length. The only idempotent word class is
`[a·a] = [a]^ω`, and the linked pairs of word classes are `([a], [a·a])` and
`([a·a], [a·a])`. Now present `a^ω` twice: `(ε, a)` folds to
`([ε]·[a·a], [a·a]) = ([a·a], [a·a])`, while `(a, a)` folds to
`([a]·[a·a], [a·a]) = ([a], [a·a])` — one ω-word, two names, one per parity of
the stem. A pair set holding one name and not the other — say
`P = {([a·a], [a·a])}` — answers the single word `a^ω` both yes and no: it
defines no language. The flaw is visible in what the fold counts: the parity of
the *cut* between stem and loop — and the cut is the presentation's choice, not
the word's.

**One lasso, many names.** A loop may be **rotated**: a factor carried from the
loop's front onto the stem leaves the ω-word unchanged,
`u·g·(h·g)^ω = u·(g·h)^ω` — and rotation is the one move that changes a lasso's
name.

**Lemma 3.5 (rotation).** Let `𝒜` be a generated algebra and `s, g, h ∈ 𝒞` with
`g·h ∈ 𝒲` and `s·(gh)^ω = s`. Then `(s·g, (hg)^ω)` is a linked pair, and some
lasso is named by both `(s, (gh)^ω)` and `(s·g, (hg)^ω)`.

*Proof.* First the algebra identities. Associativity gives `g·(hg)^m = (gh)^m·g`
for every `m ≥ 1`. Pick `k₁, k₂ ≥ 1` with `(gh)^{k₁} = (gh)^ω` and
`(hg)^{k₂} = (hg)^ω`, and set `m := k₁·k₂`: then `(gh)^m = ((gh)^{k₁})^{k₂} =
(gh)^ω` and likewise `(hg)^m = (hg)^ω`, so `g·(hg)^ω = (gh)^ω·g`. Hence `(hg)^ω`
is idempotent and `(s·g)·(hg)^ω = s·(gh)^ω·g = s·g`: the rotated pair is linked.
Now pick words `p, q` with `⟦p⟧ = g`, `⟦q⟧ = h` and `p·q` nonempty — possible
because `𝒜` is generated: a class other than `[ε]` has only nonempty preimages,
and if `g = h = [ε]` then `g·h = [ε] ∈ 𝒲` supplies a nonempty preimage to use as
`p`. Pick also `w` with `⟦w⟧ = s`, and consider the single ω-word
`α := w·(pq)^ω`. The presentation `(w, (pq)^m)` folds to
`(s·(gh)^ω, (gh)^ω) = (s, (gh)^ω)`; the presentation `(w·p, (qp)^m)` — the same
ω-word, `w·(pq)^ω = w·p·(qp)^ω` — folds to
`(s·g·(hg)^ω, (hg)^ω) = (s·g, (hg)^ω)`. So `α` is named by both. ∎

Call two linked pairs **conjugate** when rotations connect them — the
equivalence generated by `(s, (gh)^ω) ∼ (s·g, (hg)^ω)`; the notion is classical
[PP04, Ch. II, Prop. 2.6]. Stem extension is the degenerate rotation
`g = h = ⟦v⟧`: the loop's value is unchanged and the stem absorbs one turn — why
`(u, v)` and `(uv, v)` may name one lasso by two pairs, as they did on `𝒵`.

**Definition 3.6 (saturation).** A pair set `P` over a generated algebra is
**saturated** when it is closed under conjugacy: for all `s, g, h ∈ 𝒞` with
`g·h ∈ 𝒲` and `s·(gh)^ω = s`,

```
    (s, (gh)^ω) ∈ P   ⟺   (s·g, (hg)^ω) ∈ P.
```

*Example.* On Figure 1 (`aUGb`), every conjugacy class is a singleton — whatever
factor a rotation moves, the dead class absorbs it, and the two accepting stems
absorb their loops — so *every* pair set over this algebra is saturated,
Figure 1's included: each of the 2⁶ subsets of its six linked pairs is a legal
acceptance layer. `𝒵` is the opposite pole: conjugacy pairs its two names, and
only two of the four subsets survive. A conjugacy forced inside a useful
invariant, and the saturation check it requires, is worked on `Even` in §3.4.

Saturation is table-checkable — finitely many triples `(s, g, h)`, each one
product and two lookups — and it is the exact law the query was owed. The
missing half is that *all* names of one lasso are conjugate, and it is a chase
of three moves:

**Lemma 3.7 (the names of a lasso).** In a generated algebra, any two names of
one lasso are conjugate.

*Proof.* Three preliminary observations. *(Powering.)* For `k ≥ 1`, the
presentations `(u, v)` and `(u, v^k)` fold to one pair: the powers of
`⟦v^k⟧ = ⟦v⟧^k` are powers of `⟦v⟧`, each set holds exactly one idempotent, so
`⟦v^k⟧^ω = ⟦v⟧^ω =: e`; and the stems agree, `⟦u⟧·e` both. *(Absorption.)*
`e·⟦v⟧ = ⟦v⟧·e` — powers of one element commute. *(One turn.)* For any `s` with
`s·e = s`, the rotation at `(s, ⟦v⟧, ⟦v⟧)` — legal, since `⟦v⟧² ∈ 𝒲` and
`(⟦v⟧²)^ω = e` — connects `(s, e)` to `(s·⟦v⟧, e)`.

Now let `(u, v)` and `(u', v')` present one lasso `w`, say `|u| ≤ |u'|`
(conjugacy is symmetric). Both stems are prefixes of `w` and the tail after `u`
is `v^ω`, so `u' = u·z` with `z` a prefix of `v^ω`: write `z = v^q·v₁` with
`0 ≤ |v₁| < |v|`, and split `v = v₁·v₂` (`v₂` nonempty). The tail of `w` after
`u'` is then `(v₂·v₁)^ω`, so `(u', v₂v₁)` is a third presentation of `w`.

*The names of `(u, v)` and `(u', v₂v₁)` are conjugate.* Choose `m ≥ 1` with
`⟦v⟧^m = e` and `(⟦v₂⟧⟦v₁⟧)^m = (⟦v₂⟧⟦v₁⟧)^ω =: f` simultaneously (the product
trick of Lemma 3.5). Applying *(one turn)* `q` times connects `(⟦u⟧·e, e)`, the
name `(u, v)` folds to, with `(⟦u⟧·⟦v⟧^q·e, e)`, the name `(u·v^q, v)` folds to.
If `v₁ = ε` that presentation is `(u', v)` and `v₂v₁ = v`: done. Otherwise one
rotation at the triple `(⟦u⟧⟦v⟧^q·e, ⟦v₁⟧, ⟦v₂⟧)` — legal, since
`⟦v₁⟧·⟦v₂⟧ = ⟦v⟧ ∈ 𝒲` and the stem absorbs `⟦v⟧^ω = e` — connects it further to
`(⟦u⟧⟦v⟧^q·e·⟦v₁⟧, f)`, and that pair is the name `(u', v₂v₁)` folds to: by
*(absorption)* and `g·(hg)^m = (gh)^m·g`,

```
    ⟦u⟧⟦v⟧^q·e·⟦v₁⟧  =  ⟦u⟧⟦v⟧^{q+m}·⟦v₁⟧  =  ⟦u⟧⟦v⟧^q·⟦v₁⟧·(⟦v₂⟧⟦v₁⟧)^m  =  ⟦u'⟧·f.
```

*The names of `(u', v₂v₁)` and `(u', v')` are equal.* Both loops repeat to the
same tail, `(v₂v₁)^ω = v'^ω`; the prefix of that tail of length `|v'|·|v₂v₁|` is
a common power, `v'^{|v₂v₁|} = (v₂v₁)^{|v'|}` as finite words, and *(powering)*
twice gives one name for all four presentations `(u', v')`, `(u', v'^{|v₂v₁|})`,
`(u', (v₂v₁)^{|v'|})` and `(u', v₂v₁)`. Chaining: the names of `(u, v)` and
`(u', v')` are conjugate. ∎

**Theorem 3.8 (admissibility).** Call an invariant `𝓘 = ⟨𝒜, P⟩` **admissible**
when `𝒜` is generated and `P` is saturated. For generated `𝒜`, the query of
Definition 3.4 gives every presentation of every lasso one verdict iff `P` is
saturated — iff `𝓘` is admissible. The accepted lassos of an admissible `𝓘` are
then exactly the lassos of the regular language

```
    L(𝓘)  :=  ⋃ { fold⁻¹(s)·(fold⁻¹(e) ∩ Σ⁺)^ω  :  (s, e) ∈ P,  e·e = e,  s·e = s },
```

the unique regular language with those lassos: the **language of `𝓘`**, defined
for admissible invariants and for them alone.

*Proof.* *(Saturated ⟹ one verdict.)* Two presentations of one lasso fold to
conjugate names (Lemma 3.7); a saturated `P` is closed under the steps that
generate conjugacy, so conjugate pairs are both in or both out of `P` — one
verdict.

*(One verdict ⟹ saturated.)* Let `(s, g, h)` satisfy `g·h ∈ 𝒲` and
`s·(gh)^ω = s`. Lemma 3.5 exhibits one lasso and two of its presentations
folding to `(s, (gh)^ω)` and `(s·g, (hg)^ω)`; one verdict on that lasso puts the
two pairs on one side of `P`.

*(The accepted lassos are the lassos of `L(𝓘)`.)* Let `w` be accepted: every
presentation `(u, v)` folds to one pair `(s, e) ∈ P`, `e := ⟦v⟧^ω`. Pick `k`
with `⟦v⟧^k = e`: the stem block `u·v^k` folds to `⟦u⟧·⟦v⟧^k = ⟦u⟧·e = s`, the
loop blocks `v^k` fold to `e`, so `w = (u·v^k)·(v^k)^ω` lies in the member of
the union indexed by `(s, e)`. Conversely let `w` be a lasso of `L(𝓘)`:
`w = w₀·w₁·w₂⋯` with `⟦w₀⟧ = s`, `⟦w_j⟧ = e` for `j ≥ 1`, `(s, e) ∈ P`,
`e² = e`, `s·e = s`; and let `(u, v)` present `w`. The block boundaries
`b_j := |w₀⋯w_j|` are infinitely many, so two of them, `m := b_j < m' := b_{j'}`,
lie beyond `|u|` and agree modulo `|v|`. The prefix `w[0, m) = w₀⋯w_j` folds to
`s·e^j = s`. Position `m` sits in the `v`-periodic tail at phase
`r := (m − |u|) mod |v|`: split `v = v₁·v₂` with `|v₁| = r`; the tail of `w`
after `m` is `(v₂v₁)^ω`, and `m' − m` is a multiple of `|v|`, so the segment
`w[m, m') = (v₂v₁)^{(m'−m)/|v|}` — nonempty, and folding to `e^{j'−j} = e`.
Thus `(w[0, m), w[m, m'))` is a presentation of `w` whose loop folds to the
idempotent `e` directly: it folds to `(s·e, e) = (s, e) ∈ P`. One of `w`'s
presentations accepts, hence — one verdict — all do.

*(Regularity and uniqueness.)* Each `fold⁻¹(c)` is recognized by the finite
monoid `(𝒞, M)` through the fold morphism (§2), hence regular; `L(𝓘)` is a
finite union of sets `X·Y^ω` with `X, Y` regular — ω-rational, hence regular
[PP04, Ch. II, Thm 7.5]. Two regular ω-languages with the same lassos are equal
[PP04, Ch. I, Cor. 9.8]. ∎

Theorem 3.8 pays Definition 3.4's debt and delivers the section's title: for an
admissible `𝓘` — and for it alone — `L(𝓘)` is a language, the union its
denotation, the query its decision procedure: fold the stem, fold the loop to
its idempotent power, one lookup in `P`.

*Example.* On `𝒵`, saturation leaves no choice: the rotation at
`(s, g, h) = ([a·a], [a], [a])` — legal, `g·h = [a·a] ∈ 𝒲` and
`[a·a]·[a·a] = [a·a]` — forces `([a·a], [a·a]) ∈ P ⟺ ([a], [a·a]) ∈ P`. The
admissible pair sets over `𝒵` are exactly `∅` and the full two-pair set —
denoting `∅` and `Σ^ω`, the two languages blind to the cut. That `Σ^ω` here
rides on three classes where two suffice (§3.3) is the other excess an
invariant can carry — presentation, not language — and canonization quotients
it away.

An invariant is a **representation**, then, exactly when it is admissible —
generated, so that its classes speak of words, and saturated, so that its
verdicts speak of ω-words. What is still missing is one representation per
language; that is §3.3's business.

---

## Part 2 — the re-cut of §3.3+ (pointers, not text)

**§3.3 "Canonization: the syntactic invariant, computed"** = `sos_core_33.md`
from Definition 3.9 (Arnold) through Corollary 3.15 and the reduce example,
verbatim, with the following joints:

1. **Drop the migrated preamble** of sos_core_33: its opening paragraph
   ("Definition 3.4 leaves two debts…"), the "Throughout this section the
   algebra is generated" paragraph, the "One lasso, many names" block,
   Lemma 3.5, Definition 3.6, Lemma 3.7, Theorem 3.8 — all now live in §3.2
   above, same numbers.

2. **New opener** for §3.3, replacing the dropped one (draft):

   > An invariant is a representation exactly when it is admissible
   > (Theorem 3.8); nothing yet singles one out per language — on `𝒵`, three
   > classes carried `Σ^ω` where two suffice, and nothing prefers the smaller.
   > This section closes that gap in two steps: the *target*, one invariant per
   > language, built on Arnold's congruence [Arn85] (Definition 3.10,
   > Theorem 3.12); and the *move* that reaches it — `reduce`, a canonization
   > of any admissible invariant, computed by right multiplications alone, in
   > polynomial time (Theorem 3.14). A finite word sits in a lasso either in
   > the stem or inside the loop, and interchangeability must hold in both
   > positions:

   …then straight into Definition 3.9.

3. **The 3.12→3.13 bridge** ("Canonicity hands every language one invariant;
   canonization is the road back…") stays; at fusion, trim its re-explanation
   of rotation-as-data if it reads redundant after §3.2.

4. **The closer** ("Rotation has now served twice, and the division of labor is
   the summary of the section") — adjust scope: the two services now span the
   two sections, the *law* in §3.2 (Theorem 3.8), the *computation scheme* in
   §3.3 (Theorem 3.14). Otherwise keep, including the parenthetical on the
   two-sided-splitting implementation form and the Wilke/PP04 positioning.

5. **Final example choice**: sos_core_33's all-six-pairs-on-`aUGb` reduce
   example stands; `𝒵` (full pair set → the two-class `Σ^ω` invariant) is a
   cheaper alternative already introduced in §3.2 — pick one at fusion, or keep
   aUGb and let `𝒵` be foreshadowing only.

**Ripples elsewhere (booked, not in this file):**

- **Old §3.2 text**: Definition 3.4 "(language of an invariant)" is replaced by
  "(presentation; query)" — the *name* "language of an invariant" is now carried
  by Theorem 3.8. The old closing paragraph ("That the verdict does not depend
  on the presentation… subject of the next section") is deleted, superseded.
- **§3.4**: content unchanged; the "Saturation, checked" example now cites
  Definition 3.6 (§3.2), and "membership by one fold" is licensed by
  admissibility of `𝓘(Even)` (Theorem 3.12). The `Even` two-name conjugacy
  fulfills the pointer left in §3.2's saturation example.
- **§2**: the "One lasso, many names… rotation lemma (§3)" trailer stays valid;
  optionally sharpen "(§3)" to "(§3.2)" at fusion.
- **§4**: two citation fixes — "§3.3's rotation lemma" (intro of §4.3, proof of
  Lemma 4.8) becomes "§3.2's". The larger §4 reframe (build *some admissible*
  invariant from `D`, then `reduce` it; slot space collapsing from `𝒞` to the
  machine's states) is the separate task announced by sos_core_33's closing
  paragraph — untouched here.
- **§3.1 untouched**: raw pair sets remain pure syntax; admissibility is the
  semantic entry condition, which is the point of the reorganization.
