# sos_core_322 — prospective §3.1 edit (trimming, stamp) and §3.2 under the standing hypothesis

## Part 1 — §3.1, the edit

Replaces Definition 3.1 and inserts two paragraphs after its example. The rest of
§3.1 — the shortlex convention, the `aUGb` example, the letter-map paragraph, the
idempotent power, Definition 3.2 (pair set; invariant) — is untouched except
*algebra* → *stamp* wherever the word occurs ("The stamp of `aUGb`…", "two stamps
may share their classes…", "a pair set over a stamp `𝒜`").

**Definition 3.1 (stamp `𝒜 = (𝒞, λ, M)`).** A **stamp** `𝒜` over `Σ` is a triple:

- `𝒞` is a finite set of **classes**, denoted `[c]`, where `c ∈ Σ*` is the
  **representative** of that class; the empty word is always in its own class `[ε]`;
- `λ : Σ ∪ {ε} → 𝒞` is the **letter map**, associating to each letter of the
  alphabet its class; by definition `λ(ε) = [ε]`;
- `M : 𝒞 × 𝒞 → 𝒞` is the **multiplication table**: **associative**, with `[ε]` a
  two-sided **identity** — for all `c ∈ 𝒞`, `M(c, [ε]) = M([ε], c) = c` — so
  `(𝒞, M)` is a finite monoid, and we write `s·t := M(s, t)`;

and it is **trimmed**:

- `[ε]` is **isolated**: no letter maps to it — `λ(x) ≠ [ε]` for `x ∈ Σ` — and no
  product recreates it — `s·t = [ε]` only for `s = t = [ε]`;
- every other class is **reachable**: `𝒞 ∖ {[ε]}` is exactly the set of products
  `λ(x₁)·λ(x₂)·⋯·λ(xₙ)`, `n ≥ 1`, of letter classes.

[Shortlex-representative convention — unchanged.]

[*Example* "The stamp of `aUGb`…" — unchanged text, term substituted.]

**Trimming costs nothing.** From here on every stamp is trimmed — the hypothesis
is part of Definition 3.1, we do not restate it, and where a proof leans on it we
name it. It is a cheap hypothesis on both counts. Reachability is decided — and
repaired — by one breadth-first walk: close `λ(Σ)` under right multiplication by
the letter classes, at most `|𝒞|` rounds of `|Σ|` products each, and discard what
the walk never met; the discarded classes are closed out of every product with the
kept ones (their products with reached classes are reached), so restricting `M`
is legal, and — as §3.2 makes precise — a discarded class is the value of no word:
no reading ever consults it, and the recognized language is unchanged. Isolation
is a shape, not a repair: it forbids confusing "nothing yet" with "acts like
nothing" — a nonempty word may act as the identity on every class (`Even`'s
`[a·a]`, §3.4) yet is never the class `[ε]` itself, which is adjoined, not
generated. Neither clause costs a language: the language of any such triple,
trimmed or not, is regular (the proof of Theorem 3.8 uses neither clause), and
§3.5 builds a trimmed invariant for every regular language.

**The name.** *Stamp* is Pin and Straubing's term [PS05, §2]: "a morphism from a
finitely generated free monoid onto a finite monoid", the objects of the
C-varieties introduced by Straubing [Str02] to generalize Eilenberg's variety
theorem. Definition 3.1 presents that morphism by its finite data — the letter
map and the table; the morphism itself is the fold of §3.2, onto precisely by
reachability. Isolation adds the one demand [PS05] does not make: the identity's
sole preimage is the empty word. The reason the object of study is a morphism
carrying its monoid, and not the monoid alone, is the letter map being data in
its own right — the `(a|c)*·b^ω` example above — and that is the founding point
of C-varieties [Str02]: classes of languages that the syntactic monoid cannot
see, the syntactic *stamp* can.

## Part 2 — §3.2, full text

### 3.2 Semantics: the language of a saturated invariant

An invariant decides lassos with the data it carries and nothing else: `λ`
assigns each letter its class, the table `M` extends that assignment to whole
words, and `P` lists the pairs that accept. The extension is the fold.

**Definition 3.3 (fold `⟦u⟧` of a finite word `u`).** Let `𝒜 = (𝒞, λ, M)` be a
stamp over `Σ`. The **fold** of `𝒜` is the map `⟦·⟧ : Σ* → 𝒞` extending the
letter map to all finite words through the table: for `u = x₁x₂⋯xₙ ∈ Σ*`,
`⟦u⟧ := λ(x₁)·λ(x₂)·⋯·λ(xₙ)`, the empty product being `⟦ε⟧ := λ(ε) = [ε]`; we
call `⟦u⟧` the fold of `u`.

The fold is well defined: `M` is a total function and associative
(Definition 3.1), so the product of the letter classes always exists and its
value does not depend on how it is parenthesized — one class per word. It is
moreover a monoid morphism — `⟦u·v⟧ = ⟦u⟧·⟦v⟧`, `⟦ε⟧ = [ε]` — the only one
agreeing with `λ` on the letters: on nonempty words it is §2's morphism `φ`,
realized on the table, and the adjoined `[ε]` extends it to the empty word.
Trimming is read on the fold: reachability makes it **onto** — every class is
the fold of some word — and isolation pins `[ε]`'s preimage to `{ε}` — the fold
of a nonempty word is a product of classes other than `[ε]`, which isolation
keeps away from `[ε]`. The fold *is* the stamp in the sense of [PS05], the
surjective morphism `Σ* → (𝒞, M)`; Definition 3.1 is its table form.

*Example.* §2 read two lassos on Figure 1: `aab·b^ω`, in `aUGb`, and
`ba·(ab)^ω`, outside it. Their pieces fold on Figure 1′, one edge per letter
from `[ε]`: `⟦aab⟧ = [a·b]` — the first `a` enters `[a]`, the second stays
there (`[a]·[a] = [a]`, the self-loop), the `b` moves on to `[a·b]`. And
`⟦ba⟧ = [b]·[a] = [b·a]` — the class of the *dead* words (§3.1): an `a` after
a `b`, which no continuation rescues, so the walk never leaves it again. The
loops fold the same way, `⟦b⟧ = [b]` and `⟦ab⟧ = [a·b]`. What the reading of a
whole lasso does with these four values is Definition 3.7 — the pieces are
ready.

**A lasso does not choose its cut.** §2 read a lasso through a morphism: the
loop settles on an idempotent `e`, the stem on an `s` absorbed by it, and the
linked pair `(s, e)` names the lasso. It also warned: one lasso, many names —
`a·(ba)^ω = ab·(ab)^ω`, one ω-word, presented with the cut between stem and
loop placed differently. Whatever acceptance `P` encodes must not depend on
the cut, and the moves that change a cut are generated by one schema — a
factor carried from the loop's front onto the stem,
`u·v₁·(v₂v₁)^ω = u·(v₁v₂)^ω`. Its image on classes is the classical conjugacy
of linked pairs; one identity prepares it.

**Lemma 3.4 (exchange: `c·(dc)^ω = (cd)^ω·c`).** In any stamp, for all
classes `c, d`: `c·(dc)^ω = (cd)^ω·c`.

*Proof.* Associativity gives `c·(dc)^m = (cd)^m·c` for every `m ≥ 1`. Pick
`k₁, k₂ ≥ 1` with `(cd)^{k₁} = (cd)^ω` and `(dc)^{k₂} = (dc)^ω`; at
`m := k₁·k₂` both powers are the idempotent powers simultaneously —
`(cd)^m = ((cd)^{k₁})^{k₂} = (cd)^ω`, likewise `(dc)^m = (dc)^ω` — so
`c·(dc)^ω = (cd)^ω·c`. ∎

**Definition 3.5 (conjugate pairs [PP04, Ch. II, Prop. 2.6]).** Over a stamp
`𝒜`, the **rotation step** at classes `s, c, d` with `s·(cd)^ω = s` relates
the pairs

```
    (s, (cd)^ω)   ∼   (s·c, (dc)^ω).
```

Both are linked pairs: `(cd)^ω` is idempotent and absorbed by hypothesis;
`(dc)^ω` is idempotent and `(s·c)·(dc)^ω = s·(cd)^ω·c = s·c` by exchange
(Lemma 3.4). Two linked pairs are **conjugate** when a chain of rotation
steps connects them. Stem extension is the degenerate step `c = d`: the loop's
value is unchanged and the stem absorbs one turn.

**Definition 3.6 (saturated invariant).** An invariant `𝓘 = ⟨𝒜, P⟩` is
**saturated** when `P` is closed under conjugacy: for every rotation step,

```
    (s, (cd)^ω) ∈ P   ⟺   (s·c, (dc)^ω) ∈ P.
```

Whether an invariant is saturated is decided by inspection of its components:
at most `|𝒞|³` triples generate rotation steps, each decided inside the
stamp — no word, no lasso, no language is consulted.

*Example.* On Figure 1 (`aUGb`), conjugacy moves nothing: in every rotation
step the stem absorbs the factor it receives (`s·c = s`) and the rotated loop
re-folds to the same idempotent (`(dc)^ω = (cd)^ω`), so every linked pair is
conjugate only to itself. The check: the loops of the six linked pairs that
avoid `[ε]` (no others ever matter, as Definition 3.7 will make exact) are the
idempotents `[a]`, `[b]`, `[b·a]`. A product `cd` with idempotent power `[a]`
must equal `[a]`, forcing `c ∈ {[ε], [a]}` — which the stems paired with `[a]`
(`[a]` and `[b·a]`) absorb, while `dc` stays in `{[a]}`; symmetrically for
`[b]`, whose stems `[b]`, `[a·b]`, `[b·a]` all absorb `[b]`; and the only stem
paired with the loop `[b·a]` is `[b·a]` itself, the zero, which absorbs
everything, while `dc` re-folds to `[b·a]`. Every pair set over this stamp
is therefore saturated, and each of the 2⁶ subsets of the six linked pairs
recognizes a language: the six pairs sort every lasso of `Σ^ω` into six
families, and a pair set collects a union of them. `([a],[a])` holds `a^ω`
alone; `([b],[b])` holds `b^ω`; `([a·b],[b])` the lassos `a⁺b^ω` — at least
one `a`, then `b`'s forever; `([b·a],[a])` and `([b·a],[b])` the words that
died — an `a` after a `b` — and still end in `a^ω`, respectively `b^ω`; and
`([b·a],[b·a])` the lassos where both letters recur forever (`GF a ∧ GF b`).
`aUGb` itself is the union of the second and third families — its pair set,
printed under Figure 1; its complement is the other four pairs, one flip of
`P`.

**Definition 3.7 (reading of a lasso).** Let `𝓘 = ⟨𝒜, P⟩` be an invariant and
`α ∈ Σ^ω` a lasso. A **presentation** of `α` is a pair `(u, v)`, `u ∈ Σ*`,
`v ∈ Σ⁺`, with `α = u·v^ω`. Its **reading** is the pair `(⟦u⟧·e, e)`, where
`e := ⟦v⟧^ω` — the loop folded to its idempotent power, the stem folded and
absorbing it — and the reading **accepts** iff that pair belongs to `P`. A
pair that is the reading of some presentation of `α` is a **name** of `α`.

Trimming pins the names down exactly. No name touches `[ε]`: a loop is
nonempty, so its fold — and that fold's powers — stay away from `[ε]`
(isolation), and a stem cannot reach `[ε]` alone, since `s·e = s` with
`s = [ε]` forces `e = [ε]` — nothing that happens forever has an empty trace.
Conversely, every linked pair avoiding `[ε]` is a name: by reachability
`e = ⟦v⟧` and `s = ⟦u⟧` for some nonempty `v` and `u`, the idempotent `e` is
its own idempotent power, and the presentation `(u, v)` of the lasso `u·v^ω`
reads to `(s·e, e) = (s, e)`. The pairs a reading can produce are therefore
exactly the linked pairs in which `[ε]` does not appear, and each of them is
produced. Rotation never leaves this ground either: a step whose loop is
`[ε]` is degenerate — `(cd)^ω = [ε]` forces `cd = [ε]` (isolation, down the
powers), hence `c = d = [ε]`. Pairs of `P` outside the named ground are
consulted by no reading and moved by no step; we assume without further
comment that `P` contains none.

*Example.* On Figure 1′ (`aUGb`), the four values of the fold example
assemble. For `aab·b^ω` presented `(aab, b)`: the loop's fold `[b]` is already
idempotent, so `e = [b]`; the stem's fold `[a·b]` absorbs it,
`[a·b]·[b] = [a·b]`; the reading is `([a·b], [b])`, listed in `P` — accepted.
For `ba·(ab)^ω` presented `(ba, ab)`: the loop's fold `[a·b]` is not
idempotent — its square `[b·a]` is, so `e = [b·a]` — and the stem's fold
`[b·a]` absorbs it; the reading is `([b·a], [b·a])`, not listed — rejected. On
the drawing, a reading is §3.1's walk made algebraic: a finite path that ends
circling a cycle, the name recording where the path settled and what the
cycle folds to.

**A lasso read twice.** A lasso has many presentations, and Definition 3.7
reads each on its own — nothing yet says two readings of one lasso agree, and
for an arbitrary pair set they do not. The witness is the second running
example (§1): **`Even`** — an even number of `a`'s before the first `b`, then
anything. Its invariant, studied in §3.4, has five classes; here only the
`·a` column matters:

```
 λ(a) = [a],  λ(b) = [b]
 ·a :  [ε]↦[a]    [a]↦[a·a]   [b]↦[b]     [a·b]↦[a·b]   [a·a]↦[a]
 ·b :  [ε]↦[b]    [a]↦[a·b]   [b]↦[b]     [a·b]↦[a·b]   [a·a]↦[b]
```

with `P = { ([b],[b]), ([b],[a·a]), ([b],[a·b]) }` — once `[b]` is reached,
the first `b` read after an even count of `a`'s, every loop accepts
(Figure 3, §3.4). The `·a` row swaps `[a] ⇄ [a·a]`: the powers of `[a]`
alternate, the only idempotent among them is `[a·a]`, so `[a]^ω = [a·a]`. Now
read `a^ω` twice. Presented `(ε, a)`: `e = [a·a]`, stem `[ε]·[a·a] = [a·a]` —
the name `([a·a], [a·a])`. Presented `(a, a)`: stem `[a]·[a·a] = [a]` — the
name `([a], [a·a])`. One ω-word, two names, one per parity of the stem: the
fold counts the parity of the *cut*, and the cut is the presentation's
choice, not the word's. `Even`'s pair set holds neither name — `a^ω` never
sees a `b`, both readings must reject, and both do. A pair set holding one
name and not the other — add the single pair `([a·a], [a·a])` to `P` and
stop — reads the single word `a^ω` both accepted and rejected: it recognizes
nothing. Saturation forbids exactly this: the rotation step at
`([a·a], [a], [a])` relates the two names, so a saturated `P` holds both or
neither.

For a saturated invariant the readings of one lasso agree, and the agreed
verdicts trace a regular language:

**Theorem 3.8 (the language `L(𝓘)` of a saturated invariant).** Let
`𝓘 = ⟨𝒜, P⟩` be a saturated invariant. Then all presentations of one lasso
read to one verdict, and the accepted lassos are exactly the lassos of the
regular language

```
    L(𝓘)  :=  ⋃ { fold⁻¹(s)·(fold⁻¹(e) ∩ Σ⁺)^ω  :  (s, e) ∈ P,  e·e = e,  s·e = s },
```

the unique regular language with those lassos: `𝓘` **recognizes** `L(𝓘)`.

The proof rests on one fact — any two names of one lasso are conjugate — and
is given in §3.3.
