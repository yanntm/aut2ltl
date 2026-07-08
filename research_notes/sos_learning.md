# Learning the Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Shadow draft — 2026-07-05, rev. 2026-07-07 (M3 results integrated from
`sosl_report.md`; remaining `⟨TBD: …⟩` placeholders await the M4 campaign)*

## Abstract

The syntactic ω-semigroup of a regular ω-language `L` is its canonical algebra:
presentation-independent, complete, and the object from which membership,
equivalence, and every definability property of `L` — LTL-definability included —
are read. It has recently been constructed from a deterministic automaton for
the first time [SωS26]. This paper shows it is *learnable*: we give an active-learning
algorithm in the MAT model whose queries are memberships of ultimately-periodic
words only, whose target is the exportable invariant `𝓘(L) = (𝒞, λ, M, P)`, and
whose hypotheses are its automaton-like Cayley form. To our knowledge it is
the first MAT learner for the full ω-regular class whose limit is a canonical
object of the language itself, rather than an acceptor chosen from a family.
Two results carry the
paper. First, a *harvest theorem*:
any lasso on which a hypothesis errs surrenders a separating table column, by a
two-phase replacement chain — stem first, then loop-head, where a left extension
of a loop is nothing but a rotation of it — with a binary search in each phase. Second,
a finding of independent interest: an observation table with two-sided columns is
*still not enough*, because membership's error signal is one-sided — the table can
stabilize on a correct acceptor coarser than the algebra, an FDFA in algebraic
clothing, and does so *permanently* on a language as plain as `a → Xa`. What restores two-sidedness is a *left-saturation* sweep over class
representatives whose checks cost no queries at all — the rotation lemma's slot
collapse reborn on the learner's
side; with it, the fixpoint is exactly `S(L)₊`, after at most `|𝒞|` class splits
and `O(|𝒞|²·|Σ|)` membership queries plus a logarithmic-cost analysis per
counterexample — output-polynomial in the canonical target. The established FDFA
approach learns one of three competing canonical families of DFAs — none of them
the language's own algebra, all of them acceptors, answering no definability
question by themselves; this learner converges to the one object such questions
are read from, with equivalence between hypotheses decided by byte-equality of
invariants. On an exhaustive census of the smallest shape admitting a non-LTL
language — 258 languages — the learner reconstructs every canonical invariant
byte-for-byte, and the saturation sweep is shown load-bearing on an
exhaustively enumerated family of 44 of them, whose right congruence falls up
to five classes short of the algebra and which no query learner without the
sweep reaches at all.

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
   lemma's slot collapse — restores two-sidedness (§4.2–4.3).
4. The saturated-fixpoint theorem: termination after at most `|𝒞|` splits, and
   canonicity — the fixpoint *is* `S(L)₊`, exported as `𝓘(L)`; equivalence between
   hypotheses is invariant equality, replacing product constructions (§5).
5. An implementation as a pure query learner, and an evaluation against the
   canonical target: byte-exact reconstruction on an exhaustive frontier-shape
   census (258 languages, zero mismatches), the query bounds of Proposition 5.2
   confirmed (harvest logarithmic in counterexample length), and saturation
   shown load-bearing on an enumerated family of 44 permanent stalls whose
   canonical algebra is provably unreachable from queries without it, and a
   comparison to the FDFA baseline (ROLL) on which only the algebra answers
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
throughout (descriptions and automata in §2.3, Figure 1). Two of them are traced *live* through §3–5: `Even`
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

## 2. Background

This section fixes notation and recalls the two bodies of prior work the
paper stands on: active learning in the MAT model (§2.1), and the syntactic
theory of ω-regular languages (§2.2); §2.3 introduces the running examples
and the teacher used in the experiments. Nothing in it is new, except one
bookkeeping convention flagged where it is fixed.

### 2.1 Active learning in the MAT model

**Exact learning from queries.** Active learning reconstructs a finite
description of an unknown language `L` that is available only through an
interface — a black-box implementation, a simulator, a system too opaque to
open. In Angluin's *minimally adequate teacher* (MAT) model [Ang87] the
interface is two queries: a **membership query** — is the word `w` in
`L`? — answered by a bit, and an **equivalence query** — is the hypothesis
`𝓗` exactly `L`? — answered by *yes* or by a **counterexample**, a word on
which `𝓗` and `L` disagree. The learner chooses its queries adaptively and
must terminate with an exact description of `L`.

**L\* in one paragraph.** For regular languages of finite words the model is
solved by Angluin's L\* [Ang87]. The learner maintains an **observation
table**: rows are access words (prefixes), columns are distinguishing
experiments (suffixes), and the entry at `(u, e)` is the membership bit of
`u·e`. A table that is **closed** (every one-letter extension of a row
matches some row's bit-vector) and **consistent** (rows with equal
bit-vectors have equal one-letter successors) induces a deterministic
automaton on the row classes — the hypothesis. Each counterexample is
processed into a new distinguishing experiment that splits at least one row
class; the binary search of Rivest and Schapire [RS93] does it with
logarithmically many membership queries. §3 will reuse every one of these
notions, changed only where ω-words force a change.

**Why it converges: a canonical target.** The bookkeeping above is not what
makes L\* work; the Myhill–Nerode theorem is. The right congruence
`u ~_L v ⟺ (∀y: u·y ∈ L ⟺ v·y ∈ L)` of a regular language has finitely many
classes, and its quotient *is* the minimal DFA — a **canonical object**, a
function of `L` and not of any machine presenting it. Canonicity is
load-bearing three times over. It is the progress measure: every split is
witnessed by a genuine `~_L`-separation, so the class count is bounded by
the target's size and each counterexample makes irreversible progress. It
makes complexity meaningful: queries are counted against the size of the
language's own invariant — *output-polynomial* — not against whichever
automaton the teacher happens to hold. And it makes the result usable:
questions about `L` are answered on the learned object itself. On this
view, active learning *is* the reconstruction of a canonical invariant
through queries, and the table is its bookkeeping.

**What survives at ω, and what breaks.** For ω-regular languages the query
interface survives intact. Infinite words cannot be typed into a teacher,
but the **lassos** — ultimately-periodic words `u·v^ω`, finite objects —
determine an ω-regular language completely (§2.2), so membership queries
are posed on lassos and counterexamples are returned as lassos; this has
been the standard move since [MP95, FCC+08, AF16]. What breaks is the
target. Myhill–Nerode fails at ω: the right congruence of an ω-regular `L`
can be trivial while `L` is complex [AF21], so there is no minimal
deterministic acceptor to converge to — and the history of ω-learning (§7)
is a history of substitute targets: a subclass where the right congruence
happens to suffice [MP95], encodings into finite words [FCC+08], families
of DFAs in three competing normal forms [AF16, ABF18]. All are acceptors;
none is a canonical object of `L` alone. This paper keeps the L\* view and
changes the target: the canonical invariant an ω-regular language actually
owns is the quotient of Arnold's syntactic congruence — recalled next — and
§§3–5 supply what was missing, a query-level route to a *two-sided*
congruence.

**Conventions.** One lasso membership query counts as one query; equivalence
queries are counted separately; all bounds are stated against the size of
the canonical target.

### 2.2 The syntactic ω-semigroup

Everything in this subsection is prior work — the congruence is Arnold's
[Arn85], its algebraic packaging Wilke's and Perrin–Pin's [Wil93, PP04], and
the two construction facts are from [SωS26] — restated in the exact form the
learner consumes.

**Lassos.** `Σ` is a finite alphabet (for temporal-logic applications,
`Σ = 2^AP`). A **lasso** is an ultimately-periodic word `u·v^ω`: a finite stem
`u`, a finite non-empty loop `v` repeated forever. Two ω-regular languages are
equal iff they agree on all lassos [PP04], so lassos are the only infinite
words that
ever need to be mentioned: every query below is one, and "the language" means
its lasso membership function.

**The congruence.** Fix an ω-regular `L ⊆ Σ^ω`. Two finite words are
**syntactically congruent**, `u ≈_L v`, when swapping one for the other never
changes membership; Arnold matches the swap positions to the anatomy of a
lasso — the swapped factor sits in the stem, or recurs inside the loop —
giving two context shapes [Arn85]:

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

### 2.3 The running examples, and the teacher

For the reader who wants to check every
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

**The query model, instantiated.** The MAT teacher of §2.1, for this paper:
membership queries are lassos (`u·v^ω ∈ L`?); equivalence queries take a
hypothesis `𝓗` (an invariant-shaped tuple, §3) and return a lasso
counterexample on failure. The restriction to ultimately-periodic words costs
nothing — lassos determine `L` (§2.2) — and every query the algorithm ever
poses is one.

In our experiments the teacher is built on the construction of [SωS26]:
membership is one deterministic run, and an equivalence query is decided
*exactly*, by the product of the teacher automaton's reachable configurations
with the transformation closure of the hypothesis — each loop word acts on the
hypothesis's classes as a function, so one representative lasso per
(configuration, loop-action) cell fixes both verdicts, and the shortlex-least
disagreeing cell is the counterexample. Our teacher returns
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
(§4.1 shows the learner *finding* a rotated cousin, `(a, a)`, unaided — and the
final sweep mints `(ε, !a)` itself, Table 8.)

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

**Definition 3.2 (closed, consistent; access words; minting).** The table is
observed on its
**words** `W(T) = R ∪ R·Σ` (rows and frontier). `T` is **closed** when every
frontier word is `≡_T` to some row (else the offending frontier word is promoted
to `R`), and **consistent** when `u ≡_T v` implies `u·a ≡_T v·a` for all rows
`u, v` and letters `a` — §2.1's notions, with two sorts of experiments in
place of suffixes. Rows are maintained as **access words**: `R` starts as
`{ε} ∪ Σ`, and every later row is a promoted frontier word `w_c·a`, where
the **representative** `rep(c)` of a class, written `w_c`, is its
shortlex-least row. Two structural facts follow and are used below: every
letter-prefix of a row is itself a row (rows are only ever created by
extending a row with one letter), and each promotion adds one letter to an
existing row while creating a new class, so rows — hence representatives —
have length `O(|𝒞_T|)`. A consistency violation at column `c` **mints** a new
column by migrating the letter into the column: for `c = (x, y, t)` linear, the
column `(x, a·y, t)`; for `c = (x, y)` ω, the column `(x, a·y)`. Minting is sound
bookkeeping — the entry of `u` at the minted column *is* the entry of `u·a` at
`c`, by the identities `x·u·(a·y)·t^ω = x·(u·a)·y·t^ω` and
`x·(u·(a·y))^ω = x·((u·a)·y)^ω` — so the minted column separates `u` from `v`
exactly because `c` separated their `a`-successors. The empty word is kept as a
permanent row for the adjoined identity `[ε]` (it seeds folds and is never
compared), matching the keying of `𝓘`.

**Lemma 3.3 (coherence).** On a closed and consistent table, the transition
`step(c, a) := class of w_c·a` is well defined and agrees on every member of
`c` — for any row `u` of class `c`, the table word `u·a` has class
`step(c, a)`. Consequently the letterwise **fold**
`ψ(u) := step(…step([ε], u₁)…, u_n)` satisfies `ψ(u) = [u]_{≡_T}` for every
table word `u`, and `≡_T` is a right congruence on rows.

*Proof.* *Well-definedness:* `w_c·a` is a table word (a row, or a frontier
word), and closedness assigns every table word the class of some row.
*Agreement:* for a row `u` of class `c` we have `u ≡_T w_c`, both rows, so
consistency gives `u·a ≡_T w_c·a`, i.e. `class(u·a) = step(c, a)`.
*Coherence*, by induction on `|u|` over table words. Base: `ψ(ε) = [ε]` by
definition. Step: every non-empty table word is `u = p·a` with `p` a row —
a frontier word extends a row by definition, and a non-empty row was created
as a one-letter extension of a row (Definition 3.2's access discipline) — and
`p`, a shorter table word, is covered by the hypothesis:
`ψ(u) = step(ψ(p), a) = step([p], a) = class(p·a) = [u]`, the third equality
by agreement. *Right congruence:* for rows `u ≡_T v` and a letter `a`,
agreement twice gives `[u·a] = step([u], a) = step([v], a) = [v·a]`. ∎

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

Now predict the lasso `(ε, !a·aa)`, following the definition step by step.
*Fold the loop:* `ψ(!a·aa)` walks `[ε] →_{!a} [!a] →_a [a] →_a [a]` — the
middle step crossing the telling entry above — so `c_1 = [a]`. *Find the
idempotent power:* `c_2 = ψ((!a·aa)²)` continues the walk from `[a]` —
absorbed, so `c_2 = [a]` — and the least `k` with `c_{2k} = c_k` is `k = 1`:
the hypothesis believes `[a]` is already idempotent. *Form the pair:*
`s = ψ(ε·!a·aa) = [a]`, `e = [a]`. This step is the whole point of a
prediction: the hypothesis has just **named** the queried lasso by the pair
`([a], [a])` — the same name it gives `a·a^ω`, `(a·!a)^ω`, `(!a·a)^ω`, and
every other lasso whose folds collapse into `[a]` — and one name gets one
verdict. *Look up the name:* the cache has no entry for `([a],[a])`, so it
costs one membership query on the shortlex keys,
`w_{[a]}·(w_{[a]})^ω = a·a^ω` — rejected, no `!a` at all. Cached; prediction
`0`.

The miss: `(!a·aa)^ω ∈ L` — infinitely many `!a`, and every completed block it
ever closes is `aa`, length two. The hypothesis gave one name to two lassos
that the language distinguishes, and that is all a counterexample ever is in
this design: the queried lasso and its representative collapse, two concrete
lassos, teacher bits `1` and `0`.

The minimization policy of §2.3 explains why this exact lasso is the one
returned. Enumerating stems shortest-first and loops shortest-then-shortlex
(`!a < a`): `(ε, !a)`, `(ε, a)`, the four two-letter loops, and then
`(ε, !a!a!a)`, `(ε, !a!a·a)`, `(ε, !a·a!a)` are all predicted correctly — each
folds to a name whose representative lasso the language happens to treat the
same way — and `(ε, !a·aa)` is the first place the name `([a],[a])` cracks. A
misprediction is an equality the table wrongly believes; the harvest of §4.1
turns this one into the column that refutes it.

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
queries: the normalized lengths are `n ≤ |w| + 2|𝒞_T|·|z|` and
`m ≤ 2|𝒞_T|·|z|`, since the stabilization power satisfies `k ≤ 2|𝒞_T|`.

*Example (two counterexamples, one wrong name, two shapes).* The two running
specimens' first equivalence queries return different lassos — `Even`'s
teacher hands back `(ε, aa!a)`, `EvenBlocks`'s the shortlex-earlier
`(ε, !a·aa)` — but the same failure: each is predicted `0` through the pair
`([a],[a])`, i.e. through the representative lasso `a·a^ω`, and each is truly
in its language. Normalization is trivial in both (`k = 1`, so `w' = z'` is
the loop itself), the stem representative is `w_s = a` in both, and the
junction query routes them oppositely. On `Even`, `[a·(aa!a)^ω] = 0` — the
prepended `a` flips the parity — against `γ_0 = [(aa!a)^ω] = 1`: the flip is
in the **stem chain**, Table 3(a). On `EvenBlocks`, `[a·(!a·aa)^ω] = 1` — a
prefix cannot harm a prefix-independent language — equal to `γ_0`, so the
stem chain is flat and the flip is in the **loop chain**, Table 3(c). Both
flips sit at position `1 → 2` of their chains, but they convict different
words: from (a), the frontier word `u = rep(ψ(a))·a = aa` against the row
`v = rep(ψ(aa)) = a`, minting the linear column `(ε, !a, aa!a)`, entries `1`
for `aa` and `0` for `a` — the parity merge of day one, split; from (c), the
frontier word `u = rep(ψ(!a))·a = !a·a` against the row
`v = rep(ψ(!a·a)) = a`, minting the ω-column `(a, a)` — a rotated cousin of
the `(ε, !a)` we exhibited in §3, found by the machinery rather than by
inspection. Tables 3(b) and 3(d) show the tables after the split. Two lassos,
one wrong name, Arnold's two shapes: the counterexample analysis is the
two-shape split of the congruence, run backwards.

*(a) `Even`, the stem chain `γ` — replace a growing stem prefix by its rep:*

| `i` | prefix | its rep | queried lasso | `γ_i` |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `aa!a·(aa!a)^ω` | `1` |
| 1 | `a` | `a` | `a·a!a·(aa!a)^ω` | `1` |
| 2 | `aa` | `a` | `a·!a·(aa!a)^ω` | **`0`** |
| 3 | `aa!a` | `a` | `a·(aa!a)^ω` | `0` |

*(b) `Even`, after the stem harvest:*

| word | `(ε,ε)_ω` | **`(ε, !a, aa!a)_lin`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `[a]` |
| `!a` | `1` | **`1`** | `[!a]` |
| **`aa`** | `0` | **`1`** | **`[aa]`** |
| *frontier:* | | | |
| `a·!a` | `0` | **`0`** | → `[a]` ✗ still |
| `aa·!a` | `1` | **`1`** | → `[!a]` |

*(c) `EvenBlocks`, the loop chain `δ` — stem pinned to `w_s = a`, replace a
growing loop prefix by its rep:*

| `i` | prefix | its rep | queried lasso | `δ_i` |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `a·(!a·aa)^ω` | `1` |
| 1 | `!a` | `!a` | `a·(!a·aa)^ω` | `1` |
| 2 | `!a·a` | `a` | `a·(a·a)^ω` | **`0`** |
| 3 | `!a·aa` | `a` | `a·(a)^ω` | `0` |

*(d) `EvenBlocks`, after the loop harvest:*

| word | `(ε,ε)_ω` | **`(a, a)_ω`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `[a]` |
| `!a` | `1` | **`0`** | `[!a]` |
| **`!a·a`** | `0` | **`1`** | **`[!a·a]`** |

**Table 3.** The two first counterexamples, processed (minted column and
promoted row in bold; `ε`-row and unchanged frontier omitted). In both
chains, row `i = 1` replaces a one-letter prefix by its own representative —
a no-op, bit unchanged — and the flips sit at `1 → 2`. In (a), row 3 is the
junction `γ_3 = δ_0`, already `0`: the stem chain flipped, minting a *linear*
column. In (c) the junction is `1` and the loop chain flips instead, minting
an *ω-column*; note row 3's lasso is `a·a^ω` — the representative lasso of
the predicting pair, i.e. the prediction itself, closing the chain. (a) pulls
`aa` out of `[a]`; (c) pulls `!a·a` out — and in (b) the doomed `a·!a` still
hides in `[a]`, which is §4.3's catch.

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
both, the wrong merge eventually poisons some prediction, and a later
equivalence query catches it (a transient stall). But the permanent stall is
not a hypothetical, and it does not take an exotic language: an exhaustive
census of the smallest automata (one atomic proposition; at one state every
fixpoint is canonical, so these are the smallest possible) finds it already at
`a → Xa`.

**Proposition 4.4 (the stall, realized).** Let `L = L(a → Xa)` — if the first
letter is `a`, so is the second — over `Σ = {a, !a}`. The saturation-free
learner reaches, before its first equivalence query, a closed and consistent
four-class table — `[ε]`, the singleton `[a]`, a committed-in class
`C₁ = !a·Σ* ∪ aa·Σ*`, a committed-out class `C₀ = a!a·Σ*` — whose hypothesis
language is exactly `L`. Every equivalence oracle therefore assents, bounded
or exact; the fixpoint is strictly coarser than `S(L)₊¹` — four classes
against five: the two accepting idempotents `[!a]` and `[aa]`,
right-indistinguishable but separated by the left context `x = a`, stay merged
inside `C₁` — and the exported multiplication table is acceptance-wrong: it
rejects `a^ω`.

*Proof.* Membership of an ω-word depends only on its first two letters, so on
lassos it is a function of the *commitment* of the literal prefix: every word
of `C₁` begins a member, every word of `C₀` begins a non-member, and the only
uncommitted non-empty word is the single letter `a` — the class `[a]` is a
singleton. The four-class partition is closed and consistent (`C₁` and `C₀`
absorb both letters; `a` steps into one or the other), so the learner reaches
it and stays. Now take any lasso `w·z^ω` with predicting pair
`s = ψ(w·z^k)`, `e = ψ(z^k)`. The stem `w·z^k` can never be the word `a`:
either it is longer than one letter, or `w = ε` and `z = a` — and there
`k = 1` fails the stabilization test (`ψ(a) = [a]` but `ψ(aa) = C₁`), so
normalization takes `k = 2` and the stem is `aa`. Hence `s ∈ {C₁, C₀}`
always, and the prediction — the teacher's bit on `w_s·(w_e)^ω`, with
`w_{C₁} = !a` and `w_{C₀} = a!a` — equals the commitment of `s`, which equals
the truth of the queried lasso. No counterexample exists. ∎

The census's second specimen, `a ∧ XG¬a` — the language of the single ω-word
`a·(!a)^ω` — stalls the same way one step deeper: the canonical `[!a·a]` stays
merged into `[!a]`, again separated only by `x = a`. There the alive class
`{a·!a^m}` squares to the dead class, so the loop idempotent `e` is always
dead, and the stem class `s` stays alive only when the literal `w·z^k` is of
the form `a·!a^m` — which forces a pure-`!a` loop, on which the representative
lasso `a·(!a)^ω` answers correctly; any stray `a` in the loop drags `s` to
dead through the literal fold before the faulty merge can matter. Two
exhibits, one mechanism, and both minimal:

| specimen | `\|S(L)₊¹\|` | stalled fixpoint | merged pair | separated by | export error |
|---|:--:|---|---|:--:|---|
| `a → Xa` | 5 | **4 — zero counterexamples** | `[!a] = [aa]`, both accepting idempotents | `x = a` only | rejects `a^ω` |
| `a ∧ XG¬a` | 4 | 3 — one counterexample | `[!a] = [!a·a]` | `x = a` only | accepts `a^ω` |

Both languages are LTL-definable and utterly plain: the flagship stall is a
two-letter implication, on which the saturation-free learner converges, is
certified by a *complete* equivalence oracle, and exports an algebra that
mispredicts `a^ω`. (Mechanically confirmed: the exact oracle of §2.3
certifies both stalled fixpoints — the proposition turns those two runs into
fixtures for the oracle itself, a counterexample there being an oracle bug —
and with saturation on, both reach their canonical algebras, byte-equal to
the reference.) Canonicity therefore cannot be recovered from membership
and equivalence queries alone — the repair below is not an optimization but
the difference between the algebra and an acceptor.

### 4.3 The repair: left-saturation over class representatives

The missing ingredient is the other half of the rotation lemma (§2.2): a left
factor acts only by re-indexing a slot, and slots are finitely many; on the
learner's side, left contexts need range only over **class representatives**. Augment the loop with a **left-saturation sweep**: for every
table word `u` with class representative `v = rep(ψ(u))`, `u ≠ v`, and every
class `d` with representative `r = rep(d)`,

```
    check   fold(d, u) = fold(d, v)          (a pure table computation — zero queries)
```

**Lemma 4.5 (saturation progress).** If `fold(d, u) =: c_a ≠ c_b := fold(d, v)`,
then two membership queries and at most one frozen-prefix binary search yield a
new separating column and a class split.

*Proof.* Since `c_a ≠ c_b`, some existing column `κ` separates their
representatives — distinct classes differ on some column, by definition of
`≡_T`; say `κ = (x°, y°, t°)` linear, so the table already holds
`[x°·w_{c_a}·y°·t°^ω] ≠ [x°·w_{c_b}·y°·t°^ω]` (for the ω-sort `κ = (x°, y°)`,
read `[x°·(w_{c}·y°)^ω]` throughout). Query the two words under the same
context: `A = [x°·r·u·y°·t°^ω]`, `B = [x°·r·v·y°·t°^ω]` (ω-sort:
`A = [x°·(r·u·y°)^ω]`, `B = [x°·(r·v·y°)^ω]`).
- If `A ≠ B`: mint the column that reproduces "`r·w` under `κ`" as a bit on
  the bare candidate `w` — and the two sorts here differ. For a *linear* `κ`
  the candidate sits in the finite prefix, so `r` prepends there:
  `(x°·r, y°, t°)`. For an *ω* `κ` the candidate rides in the period, and
  peeling one `r` off the repeating block gives
  `x°·(r·w·y°)^ω = x°·r·(w·y°·r)^ω`: `r` must seed *both* the prefix and the
  period's tail — `(x°·r, y°·r)`. (The bare-prefix form `(x°·r, y°)` keeps
  the period `w·y°` and need not separate at all: a prefix-independent
  language swallows the prefix — on `GF(aa)` it maps both `a` and `aa` to
  accepting, and the sweep never converges.) Either way the minted column
  separates `u` from `v` directly — a genuine Arnold context — splitting
  their shared class.
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

Escalate the fired cell (Lemma 4.5): `u = !a·a`, `v = !a`, `d = [a]`,
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
`(a, a)` directly — the left factor absorbed into the prefix *and* reseeded
at the period's tail, branch 1's ω-form in action. Same
split, other arm: one four-class table exercises both branches of Lemma 4.5,
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
        left-saturation sweep; on escalation (Lemma 4.5): split, restart loop
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
(Theorem 4.3, Lemma 4.5). Every such witness is an Arnold context separating
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
Let `ψ(u) = ψ(v)` and take any Arnold context. The two lassos it builds fold
to the same predicting pair: the kernel being a two-sided congruence, the
orbit values agree — `ψ(x·u·y·t^j) = ψ(x·v·y·t^j)` in the linear shape,
`ψ(x·(u·y)^j) = ψ(x·(v·y)^j)` in the ω-power shape, for every `j` — so index,
period, and the pair `(s, e)` coincide, and the two lassos receive the same
prediction. Predictions being everywhere correct, membership agrees:
`u ≈_L v`.

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
Tables 1 → 3(b) → 6: five classes from **two splits — one per mechanism** (the
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

`EvenBlocks` completes the same way, and entirely in the ω-sort: beyond the
counterexample traced in §4.1, two saturation escalations carry the table
from four to its eight classes — keys
`ε, !a, a, !a·a, a·!a, a·a, !a·a·!a, a·!a·a`, the count and keys fixed by the
reference algebra. Table 8 is the run as a split ledger, one row per event,
from the implementation's transcript — deterministic under the pinned scan
and minimal-counterexample policies, and reproducing §4.1's row exactly. One
reading note: a single sweep mint can split more than one class once the
table re-stabilizes — rows 2 and 3 each split two.

| # | trigger | chain | minted column | splits | `\|𝒞_T\|` after |
|:--:|---|---|---|---|:--:|
| 1 | EQ: `(ε, !a·aa)` | loop | `(a, a)_ω` | `!a·a` out of `[a]` | 4 |
| 2 | sweep escalation | frozen | `(a, !a·a)_ω` | `aa` out of `[a]`; `a·!a` out of `[!a·a]` | 6 |
| 3 | sweep escalation | frozen | `(ε, !a)_ω` | `a·!a·a` out of `[!a]`; `!a·a·!a` out of `[aa]` | 8 |

**Table 8.** The `EvenBlocks` run as a split ledger: trigger (equivalence
counterexample or sweep escalation), the chain that processed it, the minted
column, the words separated. The day-one sweep is clean — every fold check
on Table 2's three-class table agrees, the computation Table 4 spells out
for `Even` — so row 1, §4.1's split, is the run's first event; rows 2–3 are the sweep
enforcing two-sidedness — no second counterexample is ever needed, and the
run's second equivalence query certifies. Every one of the four columns is
of the ω-sort: prefix-independence in action (`~lin` is blind, so every
separation lives in the loop). The final sweep mints `(ε, !a)` — the very
column §3 exhibited by inspection. The resulting bit-signatures are the
fixpoint (the Table 6 analogue), pairwise distinct — with `[ε]`, the eight
classes of `S(EvenBlocks)₊¹`:

| word | `(ε,ε)_ω` | `(a,a)_ω` | `(a,!a·a)_ω` | `(ε,!a)_ω` |
|---|:--:|:--:|:--:|:--:|
| `!a` | `1` | `0` | `0` | `1` |
| `a` | `0` | `0` | `1` | `0` |
| `!a·a` | `0` | `1` | `0` | `0` |
| `a·!a` | `0` | `1` | `1` | `0` |
| `a·a` | `0` | `0` | `0` | `1` |
| `!a·a·!a` | `0` | `0` | `0` | `0` |
| `a·!a·a` | `1` | `0` | `0` | `0` |

The per-phase membership ledgers of the two runs ground Proposition 5.2's
itemization in the two small instances (`fill` — table entries; `harvest` —
junction and chain probes; `saturation` — escalation probes and frozen
chains; `P` — the pair cache):

| run | fill | harvest | saturation | `P`-cache | total | EQ | sweep escalations | columns lin/ω |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `Even` | 32 | 4 | 7 | 8 | **51** | 2 | 1 | 2 / 1 |
| `EvenBlocks` | 67 | 4 | 14 | 14 | **99** | 2 | 2 | 0 / 4 |

Both runs finish on a *single* counterexample — every other split is the
sweep's, two-probe escalations in place of whole equivalence rounds — and
both exported invariants are byte-equal to the reference construction.

**Proposition 5.2 (query complexity).** Write `N = |S(L)₊¹|` and `ℓ` for the
longest counterexample returned. The learner poses at most `N` equivalence
queries and `O(N²·|Σ| + N·log(N·ℓ))` membership queries, itemized by
mechanism:

- *table entries* — `O(N·|Σ|)` table words (at most `N` rows, each with its
  `|Σ|`-letter frontier) against `O(N)` columns (one initial; every other
  column is minted by an event that also splits a class, so at most one per
  split);
- *per harvest split* (at most one per equivalence query) — one junction
  query and one binary search over a chain of length
  `|w'| + |z'| = O(N·ℓ)` (the normalization power is at most `2N`), so
  `O(log(N·ℓ))` queries;
- *per saturation split* — two probe queries and at most one frozen-prefix
  binary search over the segment `r·u`, of length `O(N)` since
  representatives and table words are access words of length `O(N)`
  (Definition 3.2), so `O(log N)` queries;
- *the `P`-cache* — one membership query per linked pair of the final
  table, at most `N²`, absorbed by the entry term.

All queried words have length polynomial in `N`, `ℓ`, and the column
lengths — themselves harvested substrings of counterexamples, or `O(N)`-long
segments contributed by saturation. Output-polynomial in the canonical
target `N` is the honest yardstick — `N` can be exponentially larger than a
smallest acceptor (Proposition 5.3 makes both directions of the size
comparison exact), and §6 measures exactly that.

The converse of the yardstick is the sale: on languages with trivial or
near-trivial right congruence — `EvenBlocks`, `FG(a ∨ Xa)` [AF21], and
generically tail properties — the right-congruence-seeded part of any FDFA
degenerates while nothing here does, because nothing here is seeded by the right
congruence: the ω-columns query the loop structure directly. The historical arc
makes the point structural: [MP95] is exactly the fragment where the right
congruence is the whole story, and every extension since has been a workaround
for its failure — this one replaces the seed rather than patching it.

The size relationship between the two kinds of target can be settled exactly
rather than empirically, and it cuts one way:

**Proposition 5.3 (sizes cut one way).** Write `N = |S(L)₊¹|`. (a) Every
canonical FDFA of `L` — periodic, syntactic, or recurrent [AF16] — has at
most `N + N²` states. (b) The converse fails exponentially: for every `n`
there is a co-safety `L_n` over a fixed five-letter alphabet with a
deterministic acceptor of `n + 2` states, a recurrent FDFA of size `O(n)`
and a syntactic FDFA of size `O(n²)`, but `N ≥ (n+1)^n`.

*Proof.* (a) `≈_L` refines every congruence an FDFA is built from. Leading:
`u ≈_L v` gives agreement under every continuation `y·t^ω` (the linear shape
at `x = ε`), and residual languages are ω-regular, hence determined by their
lassos [PP04] — so `u ~_L v`, and the leading automaton has at most `N`
states. Progress, at a leading class `[u]`: if `v ≈_L v'` then `vw ≈_L v'w`
for every `w`, and the ω-power shape at `x = u`, `y = ε` gives
`u·(vw)^ω ∈ L ⟺ u·(v'w)^ω ∈ L` — exactly the periodic progress congruence;
the syntactic and recurrent congruences add only clauses of the forms
`uv ~_L uv'` and `uvw ~_L u`, which `≈_L`-equal words satisfy equally. So
each progress automaton has at most `N` states, and there is one per leading
state. (b) Take four letters acting on `{1, …, n}` and generating the monoid
`PT_n` of all partial transformations (two generate the permutations, one
lowers rank, one restricts the domain; undefined images go to a rejecting
sink `⊥`), plus a letter `c` sending state `1` to an accepting sink `⊤` and
every other state to `⊥`; let `L_n` be "the run reaches `⊤`". Distinct
partial maps `f ≠ g` are `≈_{L_n}`-inequivalent: pick `q` with
`f(q) ≠ g(q)`, reach `q` from `1` by a permutation word `x` (action letters
never touch `⊤`, so nothing commits en route), and append a permutation `π`
carrying `f(q)` to `1`, then `c`: the linear context `x·_·π·c·(c)^ω` accepts
through `f` and rejects through `g`. Hence `N ≥ |PT_n| = (n+1)^n`. For the
FDFAs, the leading congruence has `n + 2` classes (the current state, or
committed, or doomed), and for a co-safety language the progress clauses
*collapse*: if `u` is uncommitted and `uvw ~_L u`, the loop returned to
`u`'s state without ever committing, so `u·(vw)^ω ∉ L` — the ω-clause is
constantly false. The recurrent conjunction is therefore constant on every
leading class (false on uncommitted and doomed, true on committed), giving
`O(1)` progress states each; the syntactic congruence reduces to its
`uv ~_L uv'` clause, giving at most `n + 2` each. ∎

Read as economics, Proposition 5.3 closes the size question the honest way:
an FDFA never pays more than a quadratic premium over the algebra, while the
algebra can cost exponentially more than any acceptor — on `L_n`, an FDFA
learner spends queries polynomial in `n` where ours spends queries
polynomial in `(n+1)^n`. That is not an inefficiency to engineer away; it is
the price of the deliverable. The algebra `L_n` owns *is* that large, every
definability read-off consumes it, and any route to it — learned here,
constructed in [SωS26] — pays `N`. Output-polynomial in `N`
(Proposition 5.2) is the strongest guarantee compatible with delivering the
object. The unsaturated stall of §4.2, for its part, is no longer a
conjecture: Proposition 4.4's `a → Xa` is the smallest exhibit an exhaustive
census of one-atom automata can produce — found exactly as §6's protocol
prescribes, by running the ablated learner over the census and treating its
surviving stalls as first-class output.

## 6. Evaluation

*⟨Structure in place; E0/E1/E2 — including the census-backed ablation — E5,
and the named-case E3/ROLL baseline have landed and their values are filled
below; the values still marked ⟨TBD-M4: …⟩ await the full-census N-spread
(E1's scatter and the census-wide ROLL medians) — nothing below is
predicted.⟩*

The algorithm of §3–5 is implemented as a pure query learner: its only source
of truth is the teacher interface, and no automaton is ever visible to it. The
evaluation answers three questions, each measured against the canonical target
`N = |S(L)₊¹|`. **Q1 — cost:** do measured queries track the
output-polynomial bounds of Proposition 5.2? **Q2 — the ablation:** how often
does the learner without saturation stall, and are the stalls §4.2's — is
saturation load-bearing across a corpus, not only on Proposition 4.4's two
specimens? **Q3 — the baseline:** against an established FDFA learner on
identical teachers, what does the algebra cost, and what does it buy? A
fourth, smaller question calibrates a constant: how sensitive is the cost to
the teacher's counterexample policy — the `log(N·ℓ)` term of Proposition 5.2.
⟨TBD-M4: one-sentence headline of the campaign's outcome, echoed in the
abstract and conclusion.⟩

### 6.1 Protocol

**Teacher.** As fixed in §2.3: membership is one deterministic run,
`O(|u| + |Q|·|v|)`; equivalence is exact, by the product with the
transformation closure of the hypothesis; counterexamples are minimal
(shortest stem, then shortest loop, then shortlex). One lasso membership is
one query; equivalence queries are counted separately (§2.1).

**Corpus.** The exhaustive census of the smallest deterministic Emerson–Lei
automata over one atomic proposition — ⟨TBD-M4: the shape families and their
counts⟩ — with ground truth computed by the construction of [SωS26]: the
reference `𝓘(L)`, its class count `N`, its LTL verdict; nondeterministic
inputs are determinized on import. The triptych is mandatory in every
experiment, as are the two permanent-stall specimens of §4.2.
⟨TBD-M4: corpus size after deduplication by language — … automata presenting
… distinct languages, `N` ranging …–…⟩ ⟨TBD-M4: if the stretch set of random
automata (larger `|Q|`, `|AP|`, acceptance) survives its budgets, one
paragraph and the largest solved instance; else cut.⟩

**Reproducibility and validation.** Runs are deterministic — the sweep's scan
order is pinned (§4.3) and counterexamples are minimal — so every transcript
is byte-reproducible, and the traces of §3–5 are not illustrations but the
transcripts of the corresponding runs, which the implementation is gated to
reproduce. Validation is Theorem 5.1 exercised end-to-end: on every corpus
case the learned invariant must be byte-equal to the constructed reference
⟨TBD-M4: n/n cases, zero mismatches⟩. The campaign's first stage (E0)
validates the named cases — the triptych, the two §4.2 specimens, and two
distinct automata for `GF(aa)` — ahead of the full census: ten runs, zero
mismatches, gate green. The two `GF(aa)` presentations return byte-identical
split ledgers and signature matrices, so Theorem 5.1's canonicity —
presentation-independence — is witnessed on the *learner's* side and not only
the construction's: a metamorphic check the algorithm passes for free. Beyond
the named cases, the census tier has been run *exhaustively* over the smallest
shapes that admit a non-LTL language — `2state1ap1acc` and its parity twin,
**258 languages** — and the learned invariant is byte-equal to the constructed
reference on **all 258**, zero mismatches. End-to-end validation of Theorem 5.1
thus holds not on a sample but on a complete enumeration of the frontier shape.

### 6.2 Cost against the canonical target (Q1)

For every case we record membership queries by phase — table fill,
counterexample harvest, saturation, the `P`-cache — plus equivalence queries,
splits, and columns by sort, against `N`. Two rows are already fixed by §5's
ledgers (`Even`: 51 queries as 32/4/7/8 over `N = 5`; `EvenBlocks`: 99 as
67/4/14/14 over `N = 8`); the campaign extends them corpus-wide. On the named
cases measured so far both designed bounds hold on every row — `splits ≤ N`
(the count is `N − |𝒞_T|_initial`, at most five at `N = 8`) and the table fill
inside the `N²·|Σ|` envelope — with harvest and saturation adding the
counterexample-analysis term on top.
⟨TBD-M4: scatter of total membership queries vs `N`, the `O(N²·|Σ|)`
envelope overlaid, over the full-census N-spread.⟩ ⟨TBD-M4: the triptych's full metric rows as a table.⟩
The reading the design predicts and the figure must confirm or refute: the
fill term dominates, harvest stays logarithmic, saturation costs a small
constant per split. ⟨TBD-M4: verdict sentence; a wall-time note — census
cases complete in … at most.⟩

### 6.3 The saturation ablation (Q2)

Everything runs twice — with and without the sweep, the ablated leg under the
exact oracle, so that every *surviving* stall is permanent by definition —
and each case is classified: **none** (the first fixpoint is already
canonical), **transient** (a non-canonical fixpoint later broken by a
counterexample), **permanent** (the exact oracle certifies a non-canonical
fixpoint). §4.2 fixes the anchors: `a → Xa` and `a ∧ XG¬a` must land
permanent, the triptych and `F(a ∧ Xa)` transient. The two anchors are
already measured, ahead of the frequency sweep: under the ablation with the
exact oracle each certifies its non-canonical fixpoint with *no*
counterexample — four classes for `a → Xa`, three for `a ∧ XG¬a` — and under
saturation each reaches its canonical algebra, five and four. `a → Xa` is the
extreme point: with the sweep on it reaches the canonical five-class algebra
with **zero counterexamples and a single equivalence query**, the query-free
saturation doing the entire job the oracle provably cannot (Proposition 4.4).
On this language the ablation's difference is not a smaller query count but
the algebra itself. ⟨TBD-M4: the frequency
table — stall class against structural features: prefix-independence,
acceptance type, `N`.⟩ More valuable than any frequency, every *new*
permanent specimen is reported individually — each is a further language
whose canonical algebra is unreachable from membership and equivalence
queries alone, i.e. fresh evidence for §4.2's finding.

The census answers this in the strong direction, and it is the section's main
result. Run exhaustively over the smallest shapes that admit a non-LTL
language — `2state1ap1acc` and its parity twin, 258 languages — the ablation
with the exact oracle finds **44 distinct languages** on a permanent stall,
every one exact-certified and every one recovered to its canonical algebra by
saturation (which is why the saturated learner is byte-exact on all 258, §6.1).
The two specimens of §4.2 are not isolated exhibits: they are the two smallest
members of a populated, *exhaustively enumerated* family. And the stall is not
cosmetic — the gap between the stalled right congruence and the syntactic
algebra reaches **five classes** already at this shape (a language with
`N = 13` stalls at 8, another with `N = 15` at 10), recovered by one
counterexample and up to five saturation escalations. The gap distribution over
the 44 languages:

| gap `N − stall` | 1 | 2 | 3 | 4 | 5 |
|---|:--:|:--:|:--:|:--:|:--:|
| languages | 26 | 8 | 3 | 5 | 2 |

Permanence is therefore not a curiosity of two hand-picked languages but
*generic* at the LTL frontier — the strongest form of §4.2's finding, and the
reason the saturation sweep is not an optimization but part of the
construction: on 44 of the 258 smallest-shape languages, no membership-and-
equivalence learner without it reaches the algebra at all. ⟨TBD-M4: the
frequency table's structural-feature breakdown (prefix-independence, acceptance
type) over the 44, closing the table above's remaining axis.⟩

### 6.4 The FDFA baseline (Q3)

The baseline is ROLL, the classification-tree FDFA learner [LCZL21,
LSTCX19], in its periodic / syntactic / recurrent modes, on the same census
languages under the same counting rule (one lasso = one membership query;
protocol adaptations documented, never adjusted away). Two adaptations are
disclosed as design, not discovered after the fact. First, ROLL learns the
language of a *Büchi automaton*, so it is fed a state-based Büchi presentation
of each language (Spot's `SBAcc`; a transition-based Büchi ROLL misreads as
trivial) — the target language is the same, but the presentation is ROLL's, so
absolute membership counts are presentation-sensitive and the robust axes of
comparison are output size and capability, not raw queries. Second, the two
learners answer their equivalence queries by *different but both exact*
mechanisms: ours by the transformation-closure product on the Cayley
hypothesis (§2.3), ROLL's by its native automaton equivalence (RABIT). The
comparison is therefore not exact-versus-bounded — both certifications are
complete — but the oracles are not identical, and that is stated with the
numbers rather than hidden.

The named-case paired table (census-wide medians ⟨TBD-M4⟩); ROLL's size is the
summed states of its FDFA, leading plus progress DFAs:

| case | ours `N` (MQ/EQ) | ROLL periodic | syntactic | recurrent |
|---|---|:--:|:--:|:--:|
| `GF(aa)` | 6 (74/2) | 4 | 4 | 4 |
| `Even` | 5 (51/2) | 12 | 15 | 9 |
| `EvenBlocks` | 8 (99/2) | 8 | 8 | 8 |
| `a → Xa` | 5 (43/1) | 12 | 14 | 9 |
| `a ∧ XG¬a` | 4 (35/2) | 8 | 10 | 7 |

Every entry sits inside Proposition 5.3(a)'s `N + N²` envelope, as it must;
within it the two objects trade places — the algebra is *smaller* on `Even`,
`a → Xa`, `a ∧ XG¬a` (5 vs 9–15, 5 vs 9–14, 4 vs 7–10), *larger* on `GF(aa)`
(6 vs 4), tied on `EvenBlocks`. This is exactly the picture Proposition 5.3
predicts and no more: the census is far too small to reach the exponential
separation of 5.3(b), where the algebra is unboundedly larger than a smallest
acceptor, so the honest reading is *competitive within the quadratic envelope*,
not *smaller* — the size comparison is a wash, and the deliverable is not size.

The deliverable is the capability column, the point of the comparison: from
the learned invariant, LTL-definability is a read-off (the aperiodicity/group
test of §2.2), answered on every case and checked against ground truth
⟨TBD-M4: n cases, agreement — must be total⟩; from any of ROLL's three FDFAs
the same question is not answerable without a further construction. One learner
returns the language's algebra, from which definability is read; the other
returns an acceptor, from which it is not. That asymmetry — not a query
count — is the result of the comparison.

### 6.5 Counterexample sensitivity

Proposition 5.2 depends on the teacher only through the `log(N·ℓ)` harvest
term. The corpus is re-run under counterexample policies — minimal
(the default), first-found, and adversarially padded, stem and loop pumped
by factors 2 to 32 — comparing total and harvest-only membership queries.
The measured trend confirms the design: as the loop is pumped from length 3
to 96 (a factor of 32), the harvest term grows from 4 to 9 queries — exactly
**one query per doubling**, `harvest ≈ log₂ ℓ`, the binary search over the
stem/loop chain — while the learned invariant is unchanged on every run.
Padding buys only query cost, never a different outcome. (The first-found
policy *coincides* with minimal for the minimal-order oracles used here — both
enumerate the shortlex-least disagreeing cell — so it contributes no separate
series; the comparison is effectively minimal-or-padded, two curves not three.)

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
algebraic clothing — permanently, already on `a → Xa` (Proposition 4.4) — the
right-congruence obstruction reborn one level up, and
dissolved by the same slot collapse. The learner's limit is not an acceptor
chosen from a family but the canonical invariant of the language — the object
definability questions are read from — so learning and classification cease to
be separate activities. An exhaustive census of the smallest non-trivial shape
bears this out: the learner reconstructs all 258 canonical invariants
byte-for-byte, and on 44 of them — a family whose right congruence provably
falls short, by up to five classes — only the saturation sweep reaches the
algebra, the two-example finding of §4.2 made generic at the LTL frontier.

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
- **[MO22]** J. Michaliszyn, J. Otop. *Learning infinite-word automata with
  loop-index queries.* Artif. Intell. 307 (2022) 103710.
- **[MP95]** O. Maler, A. Pnueli. *On the learnability of infinitary regular
  sets.* Inf. Comput. 118 (1995).
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for ω-languages.* TCS
  183 (1997) 93–112 (rev. 2008).
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups, Logic
  and Games.* Elsevier, 2004.
- **[RS93]** R. L. Rivest, R. E. Schapire. *Inference of finite automata using
  homing sequences.* Inf. Comput. 103 (1993).
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing the
  syntactic ω-semigroup from a deterministic Emerson–Lei automaton.* Working
  draft, 2026.
- **[US20]** H. Urbat, L. Schröder. *Automata learning: an algebraic approach.*
  LICS 2020.
- **[Vaa17]** F. Vaandrager. *Model learning.* Commun. ACM 60(2) (2017)
  86–95.
- **[vHSS17]** G. van Heerdt, M. Sammartino, A. Silva. *CALF: categorical
  automata learning framework.* CSL 2017.
- **[Wil93]** T. Wilke. *An algebraic theory for regular languages of finite and
  infinite words.* Int. J. Algebra Comput. 3(4) (1993) 447–489.
