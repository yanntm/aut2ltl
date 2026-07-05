# Learning the Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Shadow draft — 2026-07-05 — placeholders marked `⟨TBD: …⟩`*

## Abstract

The syntactic ω-semigroup of a regular ω-language `L` is its canonical algebra:
presentation-independent, complete, and the object from which membership,
equivalence, and every definability property of `L` — LTL-definability included —
are read. A companion paper [SωS26] shows it constructible from any deterministic
automaton for `L`. This paper shows it is *learnable*: we give an active-learning
algorithm in the MAT model whose queries are memberships of ultimately-periodic
words only, and whose hypotheses and target are the exportable invariant
`𝓘(L) = (𝒞, λ, M, P)`. Two results carry the paper. First, a *harvest theorem*:
any lasso on which a hypothesis errs surrenders a separating table column, by a
two-phase replacement chain — stem first, then loop-head, the loop phase enacting
the companion paper's rotation lemma — with a binary search in each phase. Second,
a finding we did not anticipate: an observation table with two-sided columns is
*still not enough*, because membership's error signal is one-sided — the table can
stabilize on a correct acceptor coarser than the algebra, an FDFA in algebraic
clothing. What restores two-sidedness is a query-free *left-saturation* sweep over
class representatives, the rotation lemma's slot collapse reborn on the learner's
side; with it, the fixpoint is exactly `S(L)₊`, after at most `|𝒞|` class splits
and `O(|𝒞|²·|Σ|)` membership queries plus a logarithmic-cost analysis per
counterexample — output-polynomial in the canonical target. The established FDFA
approach learns one of three competing canonical families of DFAs — none of them
the language's own algebra, all of them acceptors, answering no definability
question by themselves; this learner converges to the one object such questions
are read from, with equivalence between hypotheses decided by byte-equality of
invariants. ⟨TBD: one-sentence experimental headline on the census benchmark⟩

---

## 1. Introduction

Active learning of ω-regular languages has a structural handicap that finite words
never had. For finite words, Angluin's L\* rests on the Myhill–Nerode theorem: the
right congruence of the language *is* the minimal acceptor, so an observation table
of prefixes against suffixes converges to a canonical object. For ω-words the right
congruence is not informative: it can be trivial while the language is complex, and
languages as plain as `FG(a ∨ Xa)` have a one-class right congruence [AF21]. The
earliest ω-learner drew the line honestly: Maler and Pnueli's L\* extension [MP95]
covers exactly the languages whose right congruence carries everything — `L` and
its complement both deterministic-Büchi, by the Staiger theorem they build on — and
stops there. The field's route past the line — families of DFAs (FDFAs) covering
the lasso structure [AF16, ABF18] — works, at a price: *three* canonical normal
forms per language (periodic, syntactic, recurrent) instead of one object, the
choice among them the learner's; and what is learned is an *acceptor*, not the
language's algebra — no definability question is answerable from it without
further construction.

The canonical object exists. Arnold's syntactic congruence [Arn85] quotients finite
words by interchangeability in every ultimately-periodic context, in two shapes —
in the stem, or inside the loop — and its quotient, the syntactic ω-semigroup
(SωS), is the exact ω-analogue of the syntactic monoid: presentation-independent,
finite, and complete for definability. The companion paper [SωS26] constructs it
from a deterministic automaton; its key computational step is a **rotation lemma**:
the two-sided congruence is the coarsest right-invariant refinement of a seed
relation, because a left factor prepended to a loop merely *rotates* it — a right
extension read at a shifted starting slot.

This paper's observation is that the rotation lemma is not about automata at all —
but transporting it to the query model splits it in two, and the split is the
story. Its *right-extension* half becomes a harvest procedure: any lasso on which
the hypothesis errs is interpolated, through representative replacements at the
stem and then at the head of the loop, into a chain of membership queries whose
bit must flip — and the flip *is* a new separating column (§4). Its *slot* half —
left factors act only by re-indexing finitely many slots — becomes a saturation
rule: the columns' left prefixes need range only over class representatives, so
the two-sidedness that membership errors cannot signal (§4.2, the failure we did
not anticipate) is enforced by a query-free sweep (§4.3). On top of the two halves
we build an L\*-style learner whose hypotheses are not automata but the invariant
`𝓘(L)` itself: classes keyed by shortlex representatives, letter map,
multiplication table, accepting linked pairs.

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
   A query-free left-saturation sweep over class representatives — the rotation
   lemma's slot collapse — restores two-sidedness (§4.2–4.3).
4. The saturated-fixpoint theorem: termination after at most `|𝒞|` splits, and
   canonicity — the fixpoint *is* `S(L)₊`, exported as `𝓘(L)`; equivalence between
   hypotheses is invariant equality, replacing product constructions (§5).
5. ⟨TBD: implementation + evaluation contribution line, after §6 exists⟩

**Relation to the algebraic approach.** The closest work is Urbat and Schröder's
algebraic automata learning [US20], and the relationship is precise. Generically,
for languages recognized by a monad `T`, they prove that the syntactic `T`-algebra
is the minimal automaton of a *linearized* language over the alphabet of an
automata presentation of the free algebra — `Syn(L) ≅ Min(lin(L))` [US20,
Thm 5.14] — and learn that automaton by a generalized L\*. Instantiated to Wilke
algebras this covers ω-regular languages, in principle. In instance it is not
effective: the presentation validating the isomorphism carries the sorted alphabet
`Σ₊,ω = {ω} ∪ {·v^ω : v ∈ Σ⁺}` — one letter per finite word `v`, Arnold's ω-power
contexts recast as an *infinite alphabet* — while the finite restriction to `{ω}`
alone is only a *weak* presentation, outside the theorem, of which [US20] itself
notes that the resulting learned object resembles a family of DFAs. The rotation
lemma is exactly the missing finiteness: no ω-power context need be an alphabet
letter known in advance, because a counterexample-driven harvest of at most `|𝒞|`
ω-columns reaches the same congruence (§4, Theorem 5.1). [US20] settles what the
target is; this paper makes the ω-instance an algorithm, and runs it.

Three running examples — `GF(aa)`, `Even`, `EvenBlocks`, the triptych of [SωS26] —
recur at every definition. The third is the important one here: prefix-independent
with a trivial right congruence, it lies outside [MP95]'s class, degenerates the
leading automaton of any FDFA for it, and is precisely the case the ω-sort of our
columns is built for.

## 2. Background and query model

We import the companion paper's objects wholesale and recall only what the learner
touches; see [SωS26, §2] for the unhurried version. `Σ` is a finite alphabet. A
**lasso** is `u·v^ω`; ω-regular languages are determined by their lassos. Two
finite words are **syntactically congruent**, `u ≈_L v`, when interchangeable in
Arnold's two context shapes [Arn85]:

```
    (linear)    ∀ x, y ∈ Σ*, t ∈ Σ⁺ :   x·u·y·t^ω ∈ L  ⟺  x·v·y·t^ω ∈ L
    (ω-power)   ∀ x, y ∈ Σ*         :   x·(u·y)^ω  ∈ L  ⟺  x·(v·y)^ω  ∈ L
```

The quotient `S(L)₊ = Σ⁺/≈_L`, completed with its accepting linked pairs, is the
syntactic ω-semigroup, reified as the invariant `𝓘(L) = (𝒞, λ, M, P)` — classes
keyed by shortlex-least representatives, letter map, multiplication table,
accepting linked-pair set — a complete, canonical, exportable representation of
`L` [SωS26, Thm 5.1].

**The query model.** A teacher for `L` answers **membership queries** on lassos
(`u·v^ω ∈ L`?) and **equivalence queries** on hypotheses `𝓗` (an invariant-shaped
tuple), returning a lasso counterexample on failure. This is the standard MAT
model restricted to ultimately-periodic words, which is no restriction at all:
lassos determine `L`, and every query the algorithm ever poses is one.

In our experiments the teacher is the companion construction itself: membership is
one deterministic run, and an equivalence query builds `𝓘` of the hypothesis's
language and compares invariants byte-for-byte — canonicity making the teacher
cheap is itself a small advertisement for the object. Nothing in the learner
depends on this realization.

## 3. The observation table

**Definition 3.1 (table).** A table is `T = (R, E_lin, E_ω)` where `R ⊆ Σ*` is a
finite, shortlex-reduced set of **rows** containing `ε` and `Σ`, observed
together with its frontier `R·Σ`, and the columns are of two sorts:

- `E_lin ⊆ Σ* × Σ* × Σ⁺` — **linear columns**; the entry of row `u` at
  `(x, y, t)` is the bit `[ x·u·y·t^ω ∈ L ]`;
- `E_ω ⊆ Σ* × Σ*` — **ω-columns**; the entry of row `u` at `(x, y)` is the bit
  `[ x·(u·y)^ω ∈ L ]`.

Rows `u, v` are **table-equivalent**, `u ≡_T v`, when all entries agree.

Every entry is one membership query. By construction `≈_L` refines `≡_T` for any
column set — columns are particular Arnold contexts — so learning is the business
of growing `E_lin ∪ E_ω` until `≡_T` *is* `≈_L` on the rows, and growing `R` until
the rows exhaust `𝒞`.

The two sorts divide the labor exactly as the two relations `~lin` and `~ω` of the
companion construction do. On `Even`, linear columns already separate everything —
the stem decides membership. On `EvenBlocks`, *every* linear column is a constant
row-function (prefix-independence: a stem mutation is swallowed), and the entire
language lives in the ω-sort: the column `(ε, !a)` separates rows `a` and `aa`,
since `(a·!a)^ω ∉ L` and `(aa·!a)^ω ∈ L`. A learner without the ω-sort cannot even
represent what distinguishes them — this is [AF21]'s obstruction, met head-on.

**Definition 3.2 (closed, consistent; minting).** The table is observed on its
**words** `W(T) = R ∪ R·Σ` (rows and frontier). `T` is **closed** when every
frontier word is `≡_T` to some row (else the offending frontier word is promoted
to `R`), and **consistent** when `u ≡_T v` implies `u·a ≡_T v·a` for all rows
`u, v` and letters `a`. A consistency violation at column `c` **mints** a new
column by migrating the letter into the column: for `c = (x, y, t)` linear, the
column `(x, a·y, t)`; for `c = (x, y)` ω, the column `(x, a·y)`. Minting is sound
bookkeeping — the entry of `u` at the minted column *is* the entry of `u·a` at
`c`, by the identities `x·u·(a·y)·t^ω = x·(u·a)·y·t^ω` and
`x·(u·(a·y))^ω = x·((u·a)·y)^ω` — so the minted column separates `u` from `v`
exactly because `c` separated their `a`-successors. The empty word is kept as a
permanent row for the adjoined identity `[ε]` (it seeds folds and is never
compared), matching the keying of `𝓘`.

**Lemma 3.3 (coherence).** Maintain rows as *access words*: `ε`, the letters, and
promoted frontier words `rep(c)·a`, where `rep(c)` is the shortlex-least row of
class `c`. On a closed and consistent table, the transition
`step(c, a) := class of rep(c)·a` is well defined and agrees on every member of
`c`; the letterwise **fold** `ψ(u) := step(…step([ε], u₁)…, u_n)` therefore
satisfies `ψ(u) = [u]_{≡_T}` for every table word `u`, and `≡_T` is a right
congruence on rows.

*Proof.* Consistency is precisely the agreement of `step` across members;
coherence follows by induction along access words, closedness supplying the row
at each step. ∎

**The hypothesis, in Cayley form.** A closed, consistent table presents the
hypothesis `𝓗 = (𝒞_T, λ, step, P)`: the classes, `λ(a) = ψ(a)`, the transition
function `step` — a deterministic automaton *on classes* — and an accepting-pair
cache `P`. No monoid product is computed mid-learning; the multiplication table
is exported only at the end (§5). `P` is a **cache of teacher truths**: on demand,
`P(s, e) := teacher[ w_s·(w_e)^ω ]`, one membership query per pair, memoized —
so `P` is never "wrong," only indexed by classes that may later split.

**Prediction.** For a lasso `w·z^ω`: compute the fold orbit `c_j = ψ(z^j)` (each
step folds the literal `z` once); since the orbit is deterministic over `𝒞_T`,
there is `k ≤ 2·|𝒞_T|` with `c_{2k} = c_k` — take the least — and predict with
the pair `s = ψ(w·z^k)`, `e = c_k`:  `𝓗` answers `P(s, e)`. By construction the
prediction *is* the teacher's verdict on the representative lasso
`w_s·(w_e)^ω`. That definition is load-bearing: a counterexample is therefore
always a pair of concrete lassos — the queried one and its representative
collapse — on which the *teacher's own bits differ*.

## 4. The learner

### 4.1 The harvest: every disagreeing lasso surrenders a column

Let `w·z^ω` be a lasso on which prediction and teacher disagree. **Normalize**
`(w', z') = (w·z^k, z^k)` with `k` as in the prediction — the same ω-word, now
with `s = ψ(w')`, `e = ψ(z')` the predicting pair. Write `n = |w'|`, `m = |z'|`.
Interpolate between the counterexample and its representative collapse by two
chains of teacher bits, each replacing a growing prefix by its class
representative:

```
    stem chain:   γ_i = [ rep(ψ(w'[1..i])) · w'[i+1..n] · z'^ω ∈ L ]      i = 0..n
    loop chain:   δ_i = [ w_s · ( rep(ψ(z'[1..i])) · z'[i+1..m] )^ω ∈ L ]  i = 0..m
```

Then `γ_0 = [w'·z'^ω ∈ L]` is the teacher's bit on the counterexample,
`γ_n = δ_0 = [w_s·z'^ω ∈ L]` is the junction, and `δ_m = [w_s·(w_e)^ω ∈ L]` is
the prediction. The concatenated bit sequence has differing endpoints, so it
flips at an adjacent pair; **one junction query** decides the half, and a
Rivest–Schapire binary search [RS93] — each probe one membership query — finds a
flip in `O(log n)` resp. `O(log m)` queries.

**Lemma 4.1 (stem harvest).** A flip `γ_i ≠ γ_{i+1}` yields the frontier word
`u = rep(ψ(w'[1..i]))·w'[i+1]` and the row `v = rep(ψ(w'[1..i+1]))`, currently
assigned the same class, separated by the **linear column**
`(ε, w'[i+2..n], z')`.

**Lemma 4.2 (loop harvest).** A flip `δ_i ≠ δ_{i+1}` yields the frontier word
`u = rep(ψ(z'[1..i]))·z'[i+1]` and the row `v = rep(ψ(z'[1..i+1]))`, currently
assigned the same class, separated by the **ω-column** `(w_s, z'[i+2..m])`.

*Proof of both.* The two flipped bits are exactly the entries of `u` and `v` at
the stated column — substitute and compare — and the columns are Arnold contexts,
so the separation is genuine: `u ≉_L v`. That `u` and `v` currently share a class
is the definition of `step`. Replacing the prefix *at the head of the loop* and
letting the ω-column's `(x, y)` format carry the rest is the rotation lemma
enacted: no search over rotations is ever needed. ∎

**Corollary 4.3 (progress).** Each counterexample adds the flip column and splits
one class — the frontier word `u` leaves the class of `v` — so `|𝒞_T|` grows by
one per equivalence query, at a cost of `O(log(|w| + |𝒞_T|·|z|))` membership
queries.

### 4.2 The gap: acceptance-correct is not algebra-correct

The harvest reacts to *membership* disagreements — and membership's error signal
is structurally one-sided. Predictions fold the **literal** words of the queried
lasso; they never consult the class of a row *embedded under a left context*. So
if two rows with `u ≉_L v` are merged, and no harvested column happens to carry
the separating prefix `x`, nothing observable ever goes wrong: every prediction
is computed from literal prefixes, every lasso verdict can be correct, the
equivalence oracle assents — and the learner stops with a table **coarser than
the syntactic congruence**. The fixpoint object is then a right-congruence-
flavored acceptor: an FDFA in algebraic clothing. This is the obstruction of
[AF21] reborn one level up — the table's *columns* are two-sided, but its *error
signal* is not — and it is, we believe, the honest reason no observation-table
route to the syntactic algebra existed: the missing ingredient is not a cleverer
column format.

### 4.3 The repair: left-saturation over class representatives

The missing ingredient is the other half of the rotation lemma. In the companion
construction, a left factor acts only by re-indexing a slot, and slots are
finitely many; on the learner's side, left contexts need range only over **class
representatives**. Augment the loop with a **left-saturation sweep**: for every
table word `u` with class representative `v = rep(ψ(u))`, `u ≠ v`, and every
class `d` with representative `r = rep(d)`,

```
    check   fold(d, u) = fold(d, v)          (a pure table computation — zero queries)
```

**Lemma 4.4 (saturation progress).** If `fold(d, u) =: c_a ≠ c_b := fold(d, v)`,
then two membership queries and at most one frozen-prefix binary search yield a
new separating column and a class split.

*Proof.* Since `c_a ≠ c_b`, some existing column `κ` separates their
representatives; say `κ = (x°, y°, t°)` (the ω-sort is symmetric), so the table
already holds `[x°·w_{c_a}·y°·t°^ω] ≠ [x°·w_{c_b}·y°·t°^ω]`. Query the two words
under the same context: `A = [x°·r·u·y°·t°^ω]`, `B = [x°·r·v·y°·t°^ω]`.
- If `A ≠ B`: mint the column `(x°·r, y°, t°)`. It separates `u` from `v`
  directly — a genuine Arnold context — splitting their shared class.
- If `A = B`: the bits `A, B` cannot both agree with the two differing
  representative bits; say `A ≠ [x°·w_{c_a}·y°·t°^ω]`, where `c_a = ψ(r·u)`
  (folds compose over *literal* concatenation). So the word `r·u` and its own
  class representative behave differently under `x°·_·y°·t°^ω`. Run the stem
  chain of §4.1 on the segment `r·u` with the prefix `x°` **frozen** in place:
  `γ''_j = [ x° · rep(ψ((r·u)[1..j])) · (r·u)[j+1..] · y°·t°^ω ]`, from
  `γ''_0 = A` to `γ''_{|ru|} = [x°·w_{c_a}·y°·t°^ω] ≠ A`. The flip exists,
  binary search finds it, and Lemma 4.1's argument — with `x°` riding along in
  the column's prefix slot — yields a frontier/row pair split by a column
  `(x°·rep(·), ·, t°)`. Either way one class splits. ∎

Saturation checks are free; escalations are bounded by the total number of
splits. The sweep runs after closedness and consistency, before each equivalence
query; a clean sweep certifies that `ψ`'s kernel is a **left** congruence on
table words — and it was a right congruence by Lemma 3.3.

**The loop, assembled.**

```
    R ← {ε} ∪ Σ;   E_ω ← {(ε, ε)};   E_lin ← ∅;   P ← ∅
    repeat:
        fill entries (membership queries)
        repair closedness (promote) and consistency (mint) to fixpoint
        left-saturation sweep; on escalation (Lemma 4.4): split, restart loop
        pose EQ(𝓗 = (𝒞_T, λ, step, P))
        if yes: export 𝓘 (§5) and stop
        else: normalize the counterexample; junction query; binary-search the
              flip; mint the harvested column (Lemma 4.1 or 4.2); split
```

## 5. Correctness and complexity

**Theorem 5.1 (saturated fixpoint = the syntactic ω-semigroup).** The loop
terminates after at most `|S(L)₊¹|` class splits. At its fixpoint — closed,
consistent, left-saturated, equivalence granted — the kernel of `ψ` is exactly
`≈_L`, the map `c ↦ [rep(c)]_{≈_L}` is an isomorphism `𝒞_T ≅ S(L)₊¹`, and the
export

```
    M(c, c') := fold(c, rep(c')),    λ, P as maintained,
    keys: shortlex-least word reaching each class — a BFS on the fold automaton
```

is `𝓘(L)`, byte-equal to the teacher-side construction.

*Proof.* *Termination.* Every split is witnessed by an Arnold context separating
two concrete words, so distinct classes are `≈_L`-distinct at all times:
`|𝒞_T| ≤ |S(L)₊¹|`, and every round that does not terminate splits (Corollary
4.3, Lemma 4.4).

*The kernel is a two-sided congruence.* Right: Lemma 3.3. Left: a clean
saturation sweep gives `fold(d, u) = fold(d, rep(ψ(u)))` for every table word and
class; by induction on word length this extends to all of `Σ*` — each step passes
through a frontier word, which the sweep covers — so
`ψ(u) = ψ(v) ⟹ ψ(x·u) = fold(ψ(x), u) = fold(ψ(x), v) = ψ(x·v)`.

*The kernel saturates `L`.* Predictions are everywhere correct (equivalence
granted) and depend on a lasso only through `ψ`-values of its literal words;
since the kernel is a congruence, replacing `u` by `v` with `ψ(u) = ψ(v)` in any
Arnold context changes no `ψ`-value along the fold, hence no prediction, hence no
membership: `u ≈_L v`. So the kernel refines `≈_L`; splits being sound, it also
coarsens it on representatives — and every word is `≈_L`-equivalent to its class
representative (`ψ(u) = ψ(w_{ψ(u)})` plus the refinement), so the class map is a
bijection, multiplicative by definition of the exported `M`, matching `λ` and `P`
on representatives. Shortlex keys are recovered exactly because the fold is a
deterministic automaton: the shortlex-least word reaching class `c` is computed
by BFS and equals the shortlex-least word of the `≈_L`-class. ∎

The theorem earns the paper's title: nothing about the *language* forced the
fixpoint to be canonical — §4.2 exhibits the non-canonical stall — it is the
saturation rule, i.e. the rotation lemma's slot collapse, that pins the fixpoint
to the syntactic object.

**Proposition 5.2 (query complexity).** Writing `N = |S(L)₊¹|` and `ℓ` for the
longest counterexample returned: the learner poses at most `N` equivalence
queries and `O(N²·|Σ| + N·log(N·ℓ))` membership queries — table entries
`O(N·|Σ|)` words × `O(N)` columns, plus per split a junction query, a binary
search `O(log(N·ℓ))`, two saturation probes, and one `P`-cache miss. All queried
words have length polynomial in `N`, `ℓ`, and the column lengths, themselves
harvested substrings of counterexamples. Output-polynomial in the canonical
target `N` is the honest yardstick — `N` can be exponentially larger than a
smallest acceptor, and §6 measures exactly that.

The converse of the yardstick is the sale: on languages with trivial or
near-trivial right congruence — `EvenBlocks`, `FG(a ∨ Xa)` [AF21], and
generically tail properties — the right-congruence-seeded part of any FDFA
degenerates while nothing here does, because nothing here is seeded by the right
congruence: the ω-columns query the loop structure directly. The historical arc
makes the point structural: [MP95] is exactly the fragment where the right
congruence is the whole story, and every extension since has been a workaround
for its failure — this one replaces the seed rather than patching it. ⟨TBD: can
we exhibit a family where some FDFA flavor is exponentially larger than `𝓘`? If
yes, the comparison cuts both ways and the section gets a theorem; if not, keep
it empirical.⟩ ⟨TBD: exhibit a concrete `L` where the *unsaturated* stall of §4.2
is strictly coarser than `S(L)₊` — we believe one exists, by analogy with
finite-word languages whose syntactic monoid is exponentially larger than their
residual structure; compute it with the tool once the learner runs.⟩

## 6. Evaluation

⟨TBD: entire section — after implementation. Fixed decisions, so the section can
be written into: teacher = the companion engine (membership = one run;
equivalence = invariant comparison); benchmark = the census of small automata
(2 states, 1 AP, 1 acceptance set, …), for which ground truth — `𝓘`, LTL status —
is already computed; metrics = membership/equivalence query counts, table
dimensions, wall time, against `|𝒞|`; baseline = an FDFA learner (ROLL family) on
identical teachers, with the equalized metric being cost-to-answer a definability
question (an FDFA cannot answer it without further construction — that asymmetry
is reported as a result, not a footnote); worked in-text examples = the triptych.⟩

## 7. Related work

**Active learning of ω-regular languages.** The line begins with Maler and
Pnueli [MP95], who lift L\* [Ang87] to the subclass of languages `L` with both
`L` and its complement deterministic-Büchi-recognizable — exactly the class
where, by the Staiger theorem they build on, the syntactic right congruence
carries the whole language, so a prefix observation table converges. Farzan et
al. [FCC+08] reach the full class by learning the `$`-language
`{u$v : u·v^ω ∈ L}` with plain L\* and extracting a nondeterministic Büchi
automaton. Angluin and Fisman [AF16] systematize this direction as families of
DFAs — a leading right-congruence automaton with per-state progress DFAs — in
three canonical flavors (periodic, syntactic, recurrent), the periodic one being
the FDFA rendering of the `$`-language [LCZL21]; Angluin, Boker and Fisman
[ABF18] study FDFAs as acceptors in their own right, and the trivial-right-
congruence obstruction is [AF21]. Li, Chen, Zhang and Liu [LCZL21] give the
classification-tree FDFA learner implemented in ROLL [LSTCX19], our experimental
baseline. On the passive side, Bohn and Löding extend RPNI to deterministic
ω-automata [BL21] and learn deterministic Büchi automata from samples by
combinations of DFAs [BL22]. All of these target acceptors. ⟨TBD: one sentence
on Michaliszyn–Otop's loop-index queries — nearest cousin of the ω-columns —
once the paper is in `papers/`.⟩

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
and its construction from an automaton — with the rotation lemma this paper
transports — the companion paper's [SωS26]. In sum: [MP95] learned the class
where the right congruence suffices; the FDFA line patched the right congruence
with families of acceptors; [US20] identified the canonical algebraic target
without an effective ω-instance; this paper learns that target, effectively.

## 8. Conclusion

The syntactic ω-semigroup was constructible [SωS26]; it is also learnable, and by
the same mechanism: the rotation lemma, which there collapsed a two-sided
congruence into right computations on a monoid, here splits into a harvest
procedure and a saturation rule — rows, columns, and representative slots of
lasso queries. On the way we met a finding worth the trip: two-sided columns are
*not enough*, because membership's error signal is one-sided, and without the
saturation sweep the table stalls on a correct acceptor that is an FDFA in
algebraic clothing — the right-congruence obstruction reborn one level up, and
dissolved by the same slot collapse. The learner's limit is not an acceptor
chosen from a family but the canonical invariant of the language — the object
definability questions are read from — so learning and classification cease to
be separate activities. ⟨TBD: closing sentence tied to the experimental
headline.⟩

---

## References

- **[ABF18]** D. Angluin, U. Boker, D. Fisman. *Families of DFAs as acceptors of
  ω-regular languages.* LMCS 14(1) 2018.
- **[AF16]** D. Angluin, D. Fisman. *Learning regular omega languages.* TCS 650
  (2016) 57–72.
- **[AF21]** D. Angluin, D. Fisman. *Regular ω-languages with an informative right
  congruence.* Inf. Comput. 278 (2021).
- **[Ang87]** D. Angluin. *Learning regular sets from queries and
  counterexamples.* Inf. Comput. 75 (1987) 87–106.
- **[Arn85]** A. Arnold. *A syntactic congruence for rational ω-languages.* TCS 39
  (1985) 333–335.
- **[BL21]** L. Bohn, C. Löding. *Constructing deterministic ω-automata from
  examples by an extension of the RPNI algorithm.* MFCS 2021.
- **[BL22]** L. Bohn, C. Löding. *Passive learning of deterministic Büchi automata
  by combinations of DFAs.* ICALP 2022.
- **[FCC+08]** A. Farzan, Y.-F. Chen, E. M. Clarke, Y.-K. Tsay, B.-Y. Wang.
  *Extending automated compositional verification to the full class of
  omega-regular languages.* TACAS 2008.
- **[LCZL21]** Y. Li, Y.-F. Chen, L. Zhang, D. Liu. *A novel learning algorithm
  for Büchi automata based on family of DFAs and classification trees.* Inf.
  Comput. 281 (2021) 104678.
- **[LSTCX19]** Y. Li, X. Sun, A. Turrini, Y.-F. Chen, J. Xu. *ROLL 1.0:
  ω-regular language learning library.* TACAS 2019.
- **[MP95]** O. Maler, A. Pnueli. *On the learnability of infinitary regular
  sets.* Inf. Comput. 118 (1995).
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for ω-languages.* TCS
  183 (1997) 93–112 (rev. 2008).
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups, Logic
  and Games.* Elsevier, 2004.
- **[RS93]** R. L. Rivest, R. E. Schapire. *Inference of finite automata using
  homing sequences.* Inf. Comput. 103 (1993).
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *The syntactic
  ω-semigroup, constructed.* Working draft, 2026.
- **[US20]** H. Urbat, L. Schröder. *Automata learning: an algebraic approach.*
  LICS 2020.
- **[vHSS17]** G. van Heerdt, M. Sammartino, A. Silva. *CALF: categorical
  automata learning framework.* CSL 2017.
- **[Wil93]** T. Wilke. *An algebraic theory for regular languages of finite and
  infinite words.* Int. J. Algebra Comput. 3(4) (1993) 447–489.
