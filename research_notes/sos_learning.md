# Learning the Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Shadow draft — 2026-07-05 — placeholders marked `⟨TBD: …⟩`*

## Abstract

The syntactic ω-semigroup of a regular ω-language `L` is its canonical algebra:
presentation-independent, complete, and the object from which membership,
equivalence, and every definability property of `L` — LTL-definability included —
are read. It has recently been constructed from a deterministic automaton for
the first time [SωS26]. This paper shows it is *learnable*: we give an active-learning
algorithm in the MAT model whose queries are memberships of ultimately-periodic
words only, whose target is the exportable invariant `𝓘(L) = (𝒞, λ, M, P)`, and
whose hypotheses are its automaton-like Cayley form. Two results carry the
paper. First, a *harvest theorem*:
any lasso on which a hypothesis errs surrenders a separating table column, by a
two-phase replacement chain — stem first, then loop-head, where a left extension
of a loop is nothing but a rotation of it — with a binary search in each phase. Second,
a finding of independent interest: an observation table with two-sided columns is
*still not enough*, because membership's error signal is one-sided — the table can
stabilize on a correct acceptor coarser than the algebra, an FDFA in algebraic
clothing. What restores two-sidedness is a *left-saturation* sweep over class
representatives whose checks cost no queries at all — the rotation lemma's slot
collapse reborn on the learner's
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
finite, and complete for definability. It was recently constructed from a
deterministic automaton for the first time [SωS26]; the key computational step
there is a **rotation lemma**:
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
throughout (descriptions and automata in §2, Figure 1). Two of them are traced *live* through §3–5: `Even`
(`(aa)*·!a·Σ^ω`, co-safety: membership is decided by a finite prefix, i.e. on
the stem) and `EvenBlocks`
(prefix-independent, trivial right congruence — outside [MP95]'s class,
degenerate for any FDFA's leading automaton, and precisely the case the ω-sort
of our columns is built for). The trace has a punchline worth spoiling: both
languages hand the learner the *same* first counterexample, and the algorithm
routes it through opposite Arnold shapes. `GF(aa)`, whose transition-monoid
group is a presentation artifact the algebra destroys, remains the evaluation's
third specimen (§6).

## 2. The objects, minimally

Everything in this section is prior work — the definitions are Arnold's
[Arn85], the two construction facts are from [SωS26] — but we state it
self-contained and only as far as the learner uses it. The reader we have in mind knows
observation tables and MAT learning; no algebra beyond what follows is assumed.

**Lassos.** `Σ` is a finite alphabet (for temporal-logic applications,
`Σ = 2^AP`). A **lasso** is an ultimately-periodic word `u·v^ω`: a finite stem
`u`, a finite non-empty loop `v` repeated forever. Two ω-regular languages are
equal iff they agree on all lassos, so lassos are the only infinite words that
ever need to be mentioned: every query below is one, and "the language" means
its lasso membership function.

**The congruence.** Fix an ω-regular `L ⊆ Σ^ω`. Two finite words are
**syntactically congruent**, `u ≈_L v`, when swapping one for the other never
changes membership — and in a lasso the swap can sit in only two places, the
stem or the loop. These are Arnold's two context shapes [Arn85]:

```
    (linear)    ∀ x, y ∈ Σ*, t ∈ Σ⁺ :   x·u·y·t^ω ∈ L  ⟺  x·v·y·t^ω ∈ L
    (ω-power)   ∀ x, y ∈ Σ*         :   x·(u·y)^ω  ∈ L  ⟺  x·(v·y)^ω  ∈ L
```

For ω-regular `L` the congruence has **finitely many classes** [Arn85]; write
`𝒞` for the classes, `[u]` for the class of `u`, and adjoin `[ε]` as an
identity. Being a congruence means exactly that the class of a concatenation is
a function of the classes: `[u]·[v] := [u·v]` is well defined — the classes
form a finite monoid, and this multiplication is the table `M` below. This
quotient is written `S(L)₊`; with the identity counted, `S(L)₊¹`. One
convention is fixed here once and for all: `[ε]` is a **fresh** identity,
adjoined unconditionally and never identified with the class of a non-empty
word — even when `S(L)₊` owns a neutral element of its own, which happens:
in `Even` below, `[aa]` multiplies as the identity on every word class. This
deliberately departs from the semigroup-theory convention that `S¹` adjoins
a unit only when none exists; the fresh unit costs one redundant class and
buys a guarantee the learner leans on throughout — every class other than
`[ε]` consists of non-empty words, so it carries a non-empty shortlex key,
and every representative lasso built from keys (§3) has a non-empty loop.
Canonicity is unaffected: the fresh adjunction is a function of `L` alone.
Completed with the acceptance datum `P` below, this is the **syntactic
ω-semigroup** of `L`.

**Linked pairs name lassos.** Iterate a class: the powers `[v], [v]², [v]³, …`
move in a finite monoid, so they eventually cycle, and some power is an
**idempotent** — there is `k` with `[v]^k·[v]^k = [v]^k`. A **linked pair** is
a pair of classes `(s, e)` with `e·e = e` and `s·e = s`, both classes of
non-empty words (`e = [ε]` would name an empty loop, and `s·e = s` with
`e ≠ [ε]` then keeps `s` out of `[ε]` as well); folding a lasso
`u·v^ω` as `(u·v^k)·(v^k)^ω` lands on one — `s = [u·v^k]`, `e = [v^k]` — and
membership of the lasso depends *only* on that pair [PP04]. So the acceptance datum of the algebra is a set `P` of accepting
pairs, not a set of accepting classes: loops are named separately from stems.

**The invariant.** Packaging the above: `𝓘(L) = (𝒞, λ, M, P)` with each class
keyed by its shortlex-least word (shortlex throughout this paper uses the
letter order of the serialization — valuation bitvectors ascending, so
`!a < a` in the examples), `λ : Σ → 𝒞` the letter map, `M` the
multiplication table, `P` the accepting linked pairs. Membership of any lasso
is decided from `𝓘(L)` alone — fold the stem and loop through `λ` and `M`,
iterate the loop's class to its idempotent, look up the pair in `P` — and
`𝓘(L)` is a **complete, canonical invariant**: two ω-regular languages over the
same alphabet are equal iff their invariants are byte-equal after keying
[SωS26, Thm 5.1]. This is the learner's target, and it answers definability
directly: `L` is LTL-expressible
iff no power sequence `c, c², c³, …` in `M` cycles with period `> 1` — the
aperiodicity read-off [SωS26].

**The rotation lemma.** The construction of [SωS26] computes `≈_L` from a
deterministic automaton via a rotation lemma [SωS26, Lem. 4.4]: the two-sided congruence
is the coarsest *right*-invariant refinement of a finite seed — because a left
factor prepended to a loop merely rotates it, `x·(a·u·y)^ω = x·a·(u·y·a)^ω`, a
left extension is a right extension read from a shifted start, and left
contexts as a whole act only by re-indexing finitely many slots. Nothing else
from that construction is used here: §4 transports the lemma's two halves into
the query model, and the algorithm never sees an automaton.

**The three specimens, concretely.** For the reader who wants to check every
bit below by hand, here are the running examples — descriptions and automata
reproduced from [SωS26]:

- **`GF(aa) := GF(a ∧ Xa)`** — "infinitely many `aa`-factors." It *is* LTL, but a
  natural presentation encodes the letter `a` as a transposition, so its transition
  monoid carries a spurious group. The SωS *destroys* that group.
- **`Even := (aa)*·!a·Σ^ω`** — over the single atom `a`, an even number of `a`'s then a
  `!a` then anything; in PSL, the words with a prefix matching the SERE
  `{a[*2]}[*] ; !a`. The canonical mod-2 language; *not* LTL, its group genuine, and —
  because a prefix fixes the parity — refuted by Arnold's *linear* (first) shape.
- **`EvenBlocks`** — "infinitely many `!a`'s, and eventually every completed `a`-block
  has even length"; the same `{a[*2]}` even-block SERE, now recurring. Also *not* LTL
  with a genuine mod-2 group, but *prefix-independent*: no finite prefix changes
  membership, so its group is invisible to the linear shape and only Arnold's
  *ω-power* (second) shape can witness it. This is the example that keeps both shapes
  honest.

<table>
<tr>
<td align="center"><img src="sos_figs/img/gf_aa.png" alt="GF(aa) run-parity automaton" width="280"></td>
<td align="center"><img src="sos_figs/img/even.png" alt="Even automaton" width="280"></td>
<td align="center"><img src="sos_figs/img/evenblocks.png" alt="EvenBlocks automaton" width="280"></td>
</tr>
<tr>
<td align="center"><b>(a) <code>GF(aa)</code></b><br>2 states, <code>Inf(0)</code> (Büchi).<br>The <code>a</code>-letter transposes the<br>two states — a <code>Z₂</code> in the<br>transition monoid.</td>
<td align="center"><b>(b) <code>Even</code></b><br>4 states, <code>Inf(0)</code> (Büchi).<br>Parity pair <code>2/1</code>, an accepting<br>sink <code>0</code>, a rejecting sink <code>3</code>.</td>
<td align="center"><b>(c) <code>EvenBlocks</code></b><br>2 states, <code>Fin(0) ∧ Inf(1)</code>.<br>Prefix-independent; the parity<br>of a completed block lives on<br>the <code>!a</code>-transitions' marks.<br>PSL: <code>GF!a ∧ FG(!a → X{a[*2][*];!a}!)</code></td>
</tr>
</table>

**Figure 1.** The deterministic, complete, transition-based Emerson–Lei
automata of the three running examples, reproduced from [SωS26] (acceptance
reads the transition marks seen infinitely often: `Inf(c)` — mark `c` recurs,
`Fin(c)` — it does not). In this paper the automata belong to the *teacher*:
the learner only ever sees their answers.

**The query model.** A teacher for `L` answers **membership queries** on lassos
(`u·v^ω ∈ L`?) and **equivalence queries** on hypotheses `𝓗` (an invariant-shaped
tuple, §3), returning a lasso counterexample on failure. This is the standard MAT
model [Ang87] restricted to ultimately-periodic words, which is no restriction at
all: lassos determine `L`, and every query the algorithm ever poses is one.

In our experiments the teacher is built on the construction of [SωS26]:
membership is one deterministic run, and an equivalence query builds `𝓘` of the hypothesis's
language and compares invariants byte-for-byte — canonicity making the teacher
cheap is itself a small advertisement for the object. Our teacher returns
*minimal* counterexamples (shortest stem, then shortest loop, then shortlex),
which makes runs deterministic and the worked examples reproducible; §6 measures
what non-minimal policies cost. Nothing in the learner's correctness depends on
this realization.

## 3. The observation table

**Definition 3.1 (table).** A table is `T = (R, E_lin, E_ω)` where `R ⊆ Σ*` is a
finite set of **rows** containing `ε` and `Σ`, observed together with its
frontier `R·Σ`, and the columns are of two sorts:

- `E_lin ⊆ Σ* × Σ* × Σ⁺` — **linear columns**; the entry of row `u` at
  `(x, y, t)` is the bit `[ x·u·y·t^ω ∈ L ]`;
- `E_ω ⊆ Σ* × Σ*` — **ω-columns**; the entry of row `u` at `(x, y)` is the bit
  `[ x·(u·y)^ω ∈ L ]`.

Rows `u, v` are **table-equivalent**, `u ≡_T v`, when all entries agree.

Every entry is one membership query. By construction `≈_L` refines `≡_T` for any
column set — columns are particular Arnold contexts — so learning is the business
of growing `E_lin ∪ E_ω` until `≡_T` *is* `≈_L` on the rows, and growing `R` until
the rows exhaust `𝒞`.

The two sorts divide the labor exactly as Arnold's two shapes do. On `Even`,
linear columns already separate everything —
the stem decides membership. On `EvenBlocks`, *every* linear column is a constant
row-function (prefix-independence: a stem mutation is swallowed), and the entire
language lives in the ω-sort: the column `(ε, !a)` separates rows `a` and `aa`,
since `(a·!a)^ω ∉ L` and `(aa·!a)^ω ∈ L`. A learner without the ω-sort cannot even
represent what distinguishes them — this is [AF21]'s obstruction, met head-on.
(§4.1 shows the learner *finding* `(a, !a)`, that column's prefixed cousin,
unaided.)

*Example (day one, on `Even`).* `Even = (aa)*·!a·Σ^ω` over `Σ = {a, !a}` — an
even block of `a`, then `!a`, then anything; membership of any word is fixed by
the parity of the `a`-count before its first `!a`. Initialize `R = {ε, a, !a}`,
`E_ω = {(ε, ε)}`, `E_lin = ∅`; Table 1 is the whole state of knowledge.
`a` and `!a` split at once, and every frontier word folds into one of them by
its single bit. Two of these merges are quietly wrong — `aa ≉_L a` (alive with
opposite parity) and `a·!a ≉_L a` (`a·!a` is doomed: its first `!a` closed an
odd block) — and the single column cannot see either. The run below catches
both, by two different mechanisms (§4.1, §4.3).

| word | `(ε,ε)_ω` | class |
|---|:--:|---|
| `ε` | — | `[ε]` |
| `a` | `0` | `[a]` |
| `!a` | `1` | `[!a]` |
| *frontier:* | | |
| `a·a` | `0` | → `[a]` ✗ |
| `a·!a` | `0` | → `[a]` ✗ |
| `!a·a` | `1` | → `[!a]` |
| `!a·!a` | `1` | → `[!a]` |

**Table 1.** Day one on `Even`: rows above the frontier line, one ω-column
(the entry of word `p` is `[p^ω ∈ L]`), `→` the class each frontier word folds
into. The two merges marked `✗` are wrong (`≉_L`) but invisible: no observed
context separates the words yet.

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
promoted frontier words `rep(c)·a`, where `rep(c)` — written `w_c` for short —
is the shortlex-least row of class `c`. On a closed and consistent table, the
transition `step(c, a) := class of w_c·a` is well defined and agrees on every
member of `c`; the letterwise **fold** `ψ(u) := step(…step([ε], u₁)…, u_n)`
therefore satisfies `ψ(u) = [u]_{≡_T}` for every table word `u`, and `≡_T` is a
right congruence on rows.

*Proof.* Consistency is precisely the agreement of `step` across members;
coherence follows by induction along access words, closedness supplying the row
at each step. ∎

More generally, write `fold(d, u)` for the letterwise `step`-walk on `u`
started at an arbitrary class `d`, so that `ψ(u) = fold([ε], u)`. Folds compose
over *literal* concatenation — `ψ(x·y) = fold(ψ(x), y)`, immediately from the
definition — a small identity used repeatedly below; note that it concatenates
*words*, not classes: nothing yet says `fold(d, u)` and `fold(d, w_{ψ(u)})`
agree, and §4.2 turns exactly on that gap.

**The hypothesis, in Cayley form.** A closed, consistent table presents the
hypothesis `𝓗 = (𝒞_T, λ, step, P)`: the table's class set (written `𝒞_T`, to
keep it apart from the target's `𝒞`), `λ(a) = ψ(a)`, the transition
function `step` — a deterministic automaton *on classes* — and an accepting-pair
cache `P`. No monoid product is computed mid-learning; the multiplication table
is exported only at the end (§5). `P` is a **cache of teacher truths**: on demand,
`P(s, e) := teacher[ w_s·(w_e)^ω ]`, one membership query per pair, memoized —
so `P` is never "wrong," only indexed by classes that may later split.

**Prediction.** For a lasso `w·z^ω`: compute the fold orbit `c_j = ψ(z^j)` (each
step folds the literal `z` once); the orbit is deterministic over `𝒞_T`, so its
index and period are each at most `|𝒞_T|` and there is
`k ≤ 2·|𝒞_T|` with `c_{2k} = c_k` — take the least — and predict with
the pair `s = ψ(w·z^k)`, `e = c_k`:  `𝓗` answers `P(s, e)`. By construction the
prediction *is* the teacher's verdict on the representative lasso
`w_s·(w_e)^ω` — a genuine lasso: no word ever joins the permanent singleton
`[ε]`, so `e ≠ [ε]` and the loop `w_e` is non-empty, §2's fresh-identity
convention earning its keep. That definition is load-bearing: a counterexample is therefore
always a pair of concrete lassos — the queried one and its representative
collapse — on which the *teacher's own bits differ*.

*Example (a prediction, and its miss).* We now run the prediction procedure in
slow motion, on `EvenBlocks`: infinitely many `!a`, and eventually every
completed `a`-block has even length — a *block* being a maximal run of `a`,
*completed* when the next `!a` closes it. Day one (Table 2) has the same shape
as `Even`'s: the single ω-column splits `a` from `!a`, and every frontier word
merges by its one bit. One entry deserves a pause: `!a·a` lands with `a` here,
not with `!a` as it did in `Even` — `(!a·a)^ω` completes an odd block forever,
bit `0`. So the hypothesis's worldview is: there are three kinds of finite
words — the empty one, the pure `!a`-blocks, and *everything that has ever
seen an `a`*. Its `step` function says exactly that: from `[!a]`, reading `a`
moves to `[a]`; from `[a]`, no letter ever leaves.

| word | `(ε,ε)_ω` | class |
|---|:--:|---|
| `ε` | — | `[ε]` |
| `a` | `0` | `[a]` |
| `!a` | `1` | `[!a]` |
| *frontier:* | | |
| `a·a` | `0` | → `[a]` |
| `a·!a` | `0` | → `[a]` |
| `!a·a` | `0` | → `[a]`  (≠ `Even`!) |
| `!a·!a` | `1` | → `[!a]` |

**Table 2.** Day one on `EvenBlocks`: same shape as Table 1, one telling
difference — `!a·a` folds to `[a]`, so `[a]` is absorbing and the fold sees
only "have I read an `a` yet".

Now predict the lasso `(ε, aa!a)`, following the definition step by step.
*Fold the loop:* `ψ(aa!a)` walks `[ε] →_a [a] →_a [a] →_{!a} [a]`, so
`c_1 = [a]`. *Find the idempotent power:* `c_2 = ψ((aa!a)²)` continues the
walk from `[a]` — absorbed, so `c_2 = [a]` — and the least `k` with
`c_{2k} = c_k` is `k = 1`: the hypothesis believes `[a]` is already
idempotent. *Form the pair:* `s = ψ(ε·aa!a) = [a]`, `e = [a]`. This step is
the whole point of a prediction: the hypothesis has just **named** the queried
lasso by the pair `([a], [a])` — the same name it gives `a·a^ω`, `(a·!a)^ω`,
`(!a·a)^ω`, and every other lasso whose folds collapse into `[a]` — and one
name gets one verdict. *Look up the name:* the cache has no entry for
`([a],[a])`, so it costs one membership query on the shortlex keys,
`w_{[a]}·(w_{[a]})^ω = a·a^ω` — rejected, no `!a` at all. Cached; prediction
`0`.

The miss: `(aa!a)^ω ∈ L` — infinitely many `!a`, and every recurring completed
block is `aa`, length two. The hypothesis gave one name to two lassos that the
language distinguishes, and that is all a counterexample ever is in this
design: the queried lasso and its representative collapse, two concrete
lassos, teacher bits `1` and `0`.

The minimization policy of §2 explains why this exact lasso is the one
returned. Enumerating stems shortest-first and loops shortest-then-shortlex:
`(ε, a)`, `(ε, !a)`, `(ε, aa)`, `(ε, a!a)`, `(ε, !a·a)`, `(ε, !a!a)` and
`(ε, aaa)` are all predicted correctly — each folds to a name whose
representative lasso the language happens to treat the same way — and
`(ε, aa!a)` is the first place the name `([a],[a])` cracks. A misprediction is
an equality the table wrongly believes; the harvest of §4.1 turns this one
into the column that refutes it.

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

**Theorem 4.3 (harvest).** Each counterexample adds the flip column and splits
one class — the frontier word `u` leaves the class of `v` — so `|𝒞_T|` grows by
one per equivalence query, at a cost of `O(log(|w| + |𝒞_T|·|z|))` membership
queries.

*Example (one counterexample, two shapes).* Both running specimens return the
*same* minimal counterexample from their first equivalence query: `(ε, aa!a)`,
predicted `0` through the pair `([a],[a])`, truly in both languages. The
junction query `[a·(aa!a)^ω ∈ L]` routes them oppositely. On `Even` it answers
`0` — the prepended `a` flips the parity — against `γ_0 = [(aa!a)^ω] = 1`: the
flip is in the **stem chain**. Walking it: `γ_1 = [a·a!a·(aa!a)^ω] = 1` (first
`!a` after two `a`), `γ_2 = [a·!a·(aa!a)^ω] = 0` (after one). The flip at
`1→2` hands over `u = rep(ψ(a))·a = aa`, `v = rep(ψ(aa)) = a`, and the linear
column `(ε, !a, aa!a)`: entries `1` for `aa`, `0` for `a` — the parity merge of
day one, split. On `EvenBlocks` the junction answers `1` — a prefix cannot harm
a prefix-independent language — equal to `γ_0`, so the whole stem chain is
flat and the flip is in the **loop chain**: `δ_1 = [a·(aa!a)^ω] = 1`,
`δ_2 = [a·(rep(ψ(aa))·!a)^ω] = [a·(a!a)^ω] = 0` (recurring odd blocks). Same
flip position, same pair `u = aa`, `v = a`, but the minted column is the
ω-column `(a, !a)` — the prefixed cousin of the `(ε, !a)` we exhibited in §3,
found by the machinery rather than by inspection. Table 3 shows both tables
after the split. One word, two languages, Arnold's two shapes: the
counterexample analysis is the two-shape split of the congruence, run
backwards.

*(a) `Even`, after the stem harvest:*

| word | `(ε,ε)_ω` | **`(ε, !a, aa!a)_lin`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `[a]` |
| `!a` | `1` | **`1`** | `[!a]` |
| **`aa`** | `0` | **`1`** | **`[aa]`** |
| *frontier:* | | | |
| `a·!a` | `0` | **`0`** | → `[a]` ✗ still |
| `aa·!a` | `1` | **`1`** | → `[!a]` |

*(b) `EvenBlocks`, after the loop harvest:*

| word | `(ε,ε)_ω` | **`(a, !a)_ω`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `[a]` |
| `!a` | `1` | **`1`** | `[!a]` |
| **`aa`** | `0` | **`1`** | **`[aa]`** |

**Table 3.** The same counterexample `(ε, aa!a)` processed in the two
languages (minted column and promoted row in bold; `ε`-row and unchanged
frontier omitted). In (a) the flip landed in the stem chain and minted a
*linear* column; in (b) the stem chain was flat and the loop chain minted an
*ω-column*. Both pull `aa` out of `[a]` — and in (a) the doomed `a·!a` still
hides there, which is §4.3's catch.

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
column format. Neither running specimen realizes the stall *permanently* — in
both, the wrong merge eventually poisons some prediction, so an equivalence
query would catch it later (a transient stall). But nothing in the correctness
argument excludes a permanent one, canonicity is unprovable without the repair
below, and §5 flags the hunt for a concrete permanent stall as an open exhibit.

### 4.3 The repair: left-saturation over class representatives

The missing ingredient is the other half of the rotation lemma (§2): a left
factor acts only by re-indexing a slot, and slots are finitely many; on the
learner's side, left contexts need range only over **class representatives**. Augment the loop with a **left-saturation sweep**: for every
table word `u` with class representative `v = rep(ψ(u))`, `u ≠ v`, and every
class `d` with representative `r = rep(d)`,

```
    check   fold(d, u) = fold(d, v)          (a pure table computation — zero queries)
```

**Lemma 4.4 (saturation progress).** If `fold(d, u) =: c_a ≠ c_b := fold(d, v)`,
then two membership queries and at most one frozen-prefix binary search yield a
new separating column and a class split.

*Proof.* Since `c_a ≠ c_b`, some existing column `κ` separates their
representatives — distinct classes differ on some column, by definition of
`≡_T`; say `κ = (x°, y°, t°)` (the ω-sort is symmetric), so the table
already holds `[x°·w_{c_a}·y°·t°^ω] ≠ [x°·w_{c_b}·y°·t°^ω]`. Query the two words
under the same context: `A = [x°·r·u·y°·t°^ω]`, `B = [x°·r·v·y°·t°^ω]`.
- If `A ≠ B`: mint the column `(x°·r, y°, t°)`. It separates `u` from `v`
  directly — a genuine Arnold context — splitting their shared class.
- If `A = B`: the bits `A, B` cannot both agree with the two differing
  representative bits; say `A ≠ [x°·w_{c_a}·y°·t°^ω]`, where
  `c_a = fold(d, u) = fold(ψ(r), u) = ψ(r·u)` — folds composing over the
  literal concatenation `r·u`. So the word `r·u` and its own class
  representative behave differently under `x°·_·y°·t°^ω`. Run the stem
  chain of §4.1 on the segment `r·u` with the prefix `x°` **frozen** in place:
  `γ''_j = [ x° · rep(ψ((r·u)[1..j])) · (r·u)[j+1..] · y°·t°^ω ]`, from
  `γ''_0 = A` to `γ''_{|ru|} = [x°·w_{c_a}·y°·t°^ω] ≠ A`. The flip exists,
  binary search finds it, and Lemma 4.1's argument applies verbatim with `x°`
  frozen: the flip at position `j` separates the frontier word
  `rep(ψ((r·u)[1..j]))·(r·u)[j+1]` from the row `rep(ψ((r·u)[1..j+1]))` by the
  column `(x°, (r·u)[j+2..]·y°, t°)` — the prefix is `x°` alone, the unconsumed
  segment migrating into the middle component. Either way one class splits. ∎

*Example (a saturation sweep on `Even`, in full).* Resume `Even` after §4.1's
split: four classes `[ε], [a], [!a], [aa]`, with `a·!a` still merged into
`[a]` — the doomed word still passing for an alive one. The sweep's subjects
are the five table words that are not class representatives; against the four
classes `d`, that is twenty checks, each a pure fold computation. Table 4 is
the *entire* sweep — zero membership queries on this page. (The scan order is
pinned, for reproducible traces: subjects in shortlex order, classes in key
order; a different order changes which cell fires first — never the
fixpoint.)

| `u` (vs `v = rep`) | `d = [ε]` | `d = [!a]` | `d = [a]` | `d = [aa]` |
|---|:--:|:--:|:--:|:--:|
| `!a·!a` (vs `!a`) | `[!a]` | `[!a]` | `[a]` | `[!a]` |
| `!a·a` (vs `!a`) | `[!a]` | `[!a]` | **`[aa]` ≠ `[a]`** | `[!a]` |
| `a·!a` (vs `a`) | `[a]` | `[!a]` | **`[!a]` ≠ `[aa]`** | `[a]` |
| `aa·!a` (vs `!a`) | `[!a]` | `[!a]` | `[a]` | `[!a]` |
| `aa·a` (vs `a`) | `[a]` | `[!a]` | `[aa]` | `[a]` |

**Table 4.** The left-saturation sweep on `Even`'s four-class table: cell
`(u, d)` compares `fold(d, u)` against `fold(d, rep(ψ(u)))`; a single value
means they agree. Twenty checks, zero queries, two hits — both at `d = [a]`,
both symptoms of the one wrong merge. In scan order the first to fire is
`(!a·a, [a])`.

Escalate the fired cell (Lemma 4.4): `u = !a·a`, `v = !a`, `d = [a]`,
`r = a`, diverging folds `c_a = fold([a], !a·a) = [aa]` and
`c_b = fold([a], !a) = [a]`. Pause on what fired: `!a·a` is *correctly*
merged with `!a` — the divergence arises because its fold from `[a]` walks
through the wrong merge, not because the subject is misplaced. The escalation
convicts the guilty word anyway. The column separating `rep([aa]) = aa` from
`rep([a]) = a` is the harvested `κ = (ε, !a, aa!a)`, and the two probe
queries — the escalation's only queries — are

```
    A = [ a·!a·a ·!a·(aa!a)^ω ] = 0        (r·u under κ's context)
    B = [ a·!a   ·!a·(aa!a)^ω ] = 0        (r·v under κ's context)
```

`A = B`: the first branch yields nothing, so we are in the second. Which side
disagrees with its own fold class? `ψ(r·u) = c_a = [aa]`, whose
representative `aa` holds κ-bit `1 ≠ A` — the `u`-side. Run the frozen-prefix
chain on the segment `r·u = a·!a·a` inside κ's context (here `x° = ε`, so the
freeze is invisible; a genuinely frozen prefix arises when κ carries one):

| `j` | prefix of `a·!a·a` | its rep | queried lasso | bit |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `a!aa·!a·(aa!a)^ω` | `0` |
| 1 | `a` | `a` | `a·!aa·!a·(aa!a)^ω` | `0` |
| 2 | `a·!a` | `a` | `a·a·!a·(aa!a)^ω` | **`1`** |
| 3 | `a·!a·a` | `aa` | `aa·!a·(aa!a)^ω` | `1` |

**Table 5.** The escalation's chain: replace a growing prefix of `a·!a·a` by
its class representative, query under κ's context. The flip at `j = 1 → 2`
hands over the frontier word `a·!a` (that is, `rep(ψ(a))·!a`) and the row `a`
(that is, `rep(ψ(a·!a))`), separated by the minted **linear column
`(ε, a!a, aa!a)`** — entries `0` for `a·!a`, `1` for `a`. The doomed word
leaves `[a]`.

Two membership bits and a two-probe chain did the work of an equivalence
round: this merge was transient (the very next equivalence query would have
returned `(ε, a!a)`), but the sweep neither knew nor needed to know that —
and §4.2's permanent stall, should it exist, is caught by nothing else. One
remark completes the picture: the *other* hit, `(a·!a, [a])`, escalates
through the **first** branch — there `c_a = [!a]`, `c_b = [aa]`, the
separating column is the original ω-column `κ = (ε, ε)`, and the probes
`A = [(a·a!a)^ω] = 1 ≠ 0 = [(a·a)^ω] = B` differ, minting the ω-column
`(a, ε)` directly, the left factor absorbed into the column prefix. Same
split, other arm: one four-class table exercises both branches of Lemma 4.4,
and the fixpoint is the same five classes either way — only the *trace*
needs the pinned order. Table 6 shows the resulting table, which is final.

| word | `(ε,ε)_ω` | `(ε,!a,aa!a)_lin` | **`(ε,a!a,aa!a)_lin`** | class |
|---|:--:|:--:|:--:|---|
| `a` | `0` | `0` | **`1`** | `[a]` |
| `!a` | `1` | `1` | **`1`** | `[!a]` |
| `aa` | `0` | `1` | **`0`** | `[aa]` |
| **`a·!a`** | `0` | `0` | **`0`** | **`[a!a]`** |

**Table 6.** `Even` at the fixpoint (saturated column and promoted row in
bold; `ε`-row omitted). The four bit-signatures are pairwise distinct — with
`[ε]`, the five classes of `S(Even)₊¹` — and every frontier word now folds
cleanly: `a·!a·a` carries the all-zero signature of the absorbing reject and
joins `[a!a]`; `aa·!a` carries the all-one signature of the committed accept
and joins `[!a]`.

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

is exactly `𝓘(L)` — in particular byte-equal to the output of any construction
of it [SωS26, Thm 5.1].

*Proof.* *Termination.* Every mechanism that keeps a round going adds a class:
a promotion introduces a frontier word differing from every row on some column,
a consistency minting separates the violating pair on the minted column, a
saturation escalation and a counterexample harvest each split a class
(Theorem 4.3, Lemma 4.4). Every such witness is an Arnold context separating
two concrete words, so distinct classes are `≈_L`-distinct at all times, and
`|𝒞_T| ≤ |S(L)₊¹|` bounds the total.

*The kernel is a two-sided congruence.* Right-invariance is Lemma 3.3. For
left-invariance, first extend the sweep's guarantee from table words to all
words: **claim** — `fold(d, u) = fold(d, w_{ψ(u)})` for every `d ∈ 𝒞_T` and
every `u ∈ Σ⁺`. Induction on `|u|`; for `u = u₁·a`:

```
    fold(d, u₁·a) = step(fold(d, u₁), a)             (definition)
                  = step(fold(d, w_{ψ(u₁)}), a)      (induction hypothesis)
                  = fold(d, w_{ψ(u₁)}·a)             (definition)
                  = fold(d, w_{ψ(u)})                (sweep: w_{ψ(u₁)}·a is a
                                                      frontier word, and
                                                      ψ(w_{ψ(u₁)}·a) = ψ(u))
```

The claim gives left-invariance: if `ψ(u) = ψ(v)` then for any `x`,
`ψ(x·u) = fold(ψ(x), u) = fold(ψ(x), w_{ψ(u)}) = fold(ψ(x), w_{ψ(v)})
= fold(ψ(x), v) = ψ(x·v)`.

*The kernel saturates `L`.* Predictions are everywhere correct (equivalence
granted) and depend on a lasso only through `ψ`-values of its literal words.
Let `ψ(u) = ψ(v)` and take any Arnold context; replacing `u` by `v` in it,
occurrence by occurrence, changes no `ψ`-value along the fold — the kernel is a
two-sided congruence — hence no prediction, hence no membership: `u ≈_L v`.

*The bijection.* Three facts assemble it. (i) `ψ`-equal implies `≈_L`-equal —
just proved — so the map `c ↦ [w_c]_{≈_L}` is well defined on classes, and
every word `u` satisfies `u ≈_L w_{ψ(u)}` (coherence gives `ψ(u) = ψ(w_{ψ(u)})`).
(ii) Distinct classes are `≈_L`-distinct — every split was witnessed by an
Arnold context — so the map is injective. (iii) Every `≈_L`-class is hit: any
word `u` lands, by (i), in the same `≈_L`-class as the representative of
`ψ(u)`. So `𝒞_T ≅ S(L)₊¹`; the map is multiplicative by definition of the
exported `M` (`M(c, c') = fold(c, w_{c'}) = ψ(w_c·w_{c'})`, folds composing
over literal concatenation), and
matches `λ` and `P` on representatives. Shortlex keys are recovered exactly
because the fold is a deterministic automaton: the shortlex-least word reaching
class `c` under BFS is the shortlex-least word of its `≈_L`-class. ∎

The theorem earns the paper's title: nothing about the *language* forced the
fixpoint to be canonical — §4.2 exhibits the non-canonical stall — it is the
saturation rule, i.e. the rotation lemma's slot collapse, that pins the fixpoint
to the syntactic object.

*Example (the run, completed, on `Even`).* After §4.3's split the table is
Table 6, and the next sweep and equivalence query are clean. The whole run,
Tables 1 → 3(a) → 6: five classes from **two splits — one per mechanism** (the
stem chain split `aa` from `a`, the saturation escalation split `a·!a` from
`a`) — on **three columns** (`(ε,ε)_ω` initial, `(ε, !a, aa!a)_lin` harvested,
`(ε, a!a, aa!a)_lin` saturated). The BFS re-keying returns
`ε, !a, a, a!a, aa`, and the exported multiplication table
`M(c, c') = fold(c, w_{c'})` is

```
  ·      [ε]  [!a]  [a]  [a!a]  [aa]
  [ε]     0    1     2     3     4
  [!a]    1    1     1     1     1
  [a]     2    3     4     1     2
  [a!a]   3    3     3     3     3
  [aa]    4    1     2     3     4
```

— cell for cell the syntactic table of [SωS26], computed there from a
deterministic automaton and here from lasso queries alone: Theorem 5.1,
performed. Two read-offs complete the export (Table 7): the accepting pairs,
and the aperiodicity check.

*(a) linked pairs `(s, e)`, `e` ranging over the idempotents; cell = the
accept bit of `w_s·(w_e)^ω`, `–` = not linked (`s·e ≠ s`):*

| `s` \ `e` | `[!a]` | `[a!a]` | `[aa]` |
|---|:--:|:--:|:--:|
| `[!a]` | **1** | **1** | **1** |
| `[a]` | – | – | `0` |
| `[a!a]` | `0` | `0` | `0` |
| `[aa]` | – | – | `0` |

*(b) power orbits `c, c², c³, …`:*

| `c` | `c²` | `c³` | eventual period |
|---|:--:|:--:|:--:|
| `[!a]` | `[!a]` | `[!a]` | 1 |
| `[a]` | `[aa]` | `[a]` | **2** |
| `[a!a]` | `[a!a]` | `[a!a]` | 1 |
| `[aa]` | `[aa]` | `[aa]` | 1 |

**Table 7.** The learned `𝓘(Even)`'s two read-offs. (a) Eight linked pairs,
three accepting — the whole `[!a]` stem row: once the good prefix has
happened, every loop accepts; this is `P`. (b) Power iteration of every
class: a single orbit of period two, `[a] → [aa] → [a]` — the genuine `Z₂` —
so `Even` is **not** LTL-definable, read off the learned object in four
lines (§2's aperiodicity read-off). Five classes is exactly `|S(Even)₊¹|`,
and the `.sos` export is byte-equal to the construction from the
automaton — the equivalence oracle's last check, passed by construction.

`EvenBlocks` completes the same way: four further splits beyond the one
traced in §4.1, all in the ω-sort, to its eight classes — keys
`ε, !a, a, !a·a, a·!a, a·a, !a·a·!a, a·!a·a`, the count and keys fixed by the
reference algebra. Table 8 sets up the run as a ledger, one row per split;
the theory fills the first row and *predicts* the shape of the rest, the
implementation's transcript (§6) supplies them — the discipline being that
the paper's traces are predictions the tool must reproduce, not
transcriptions of what it did.

| # | trigger | chain | minted column | split | `\|𝒞_T\|` after |
|:--:|---|---|---|---|:--:|
| 1 | EQ: `(ε, aa!a)` | loop | `(a, !a)_ω` | `aa` out of `[a]` | 4 |
| 2 | ⟨TBD-M3 transcript⟩ | | | | 5 |
| 3 | ⟨TBD-M3 transcript⟩ | | | | 6 |
| 4 | ⟨TBD-M3 transcript⟩ | | | | 7 |
| 5 | ⟨TBD-M3 transcript⟩ | | | | 8 |

**Table 8.** The `EvenBlocks` run as a split ledger: trigger (equivalence
counterexample or sweep escalation), the chain that processed it, the minted
column, the word separated. Row 1 is §4.1's split. ⟨TBD-M3: rows 2–5 and the
final signature table (the Table 6 analogue, seven word rows against the
discovered ω-columns) from the machine transcript, which the pinned scan and
minimal-counterexample policies make deterministic; also the two runs' query
ledgers by phase — fill / harvest / saturation / `P` — grounding Proposition
5.2's bound in the two small instances.⟩

**Proposition 5.2 (query complexity).** Writing `N = |S(L)₊¹|` and `ℓ` for the
longest counterexample returned: the learner poses at most `N` equivalence
queries and `O(N²·|Σ| + N·log(N·ℓ))` membership queries — table entries
`O(N·|Σ|)` words × `O(N)` columns; per split a junction query, a binary
search `O(log(N·ℓ))` and two saturation probes; and one membership query per
linked pair of the final table for `P` (at most `N²`, absorbed by the entry
term). All queried
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
be written into: teacher = the reference construction engine (membership = one run;
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
once vetted.⟩

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
transports — is [SωS26]. In sum: [MP95] learned the class
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
