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
the rows exhaust `𝒞_L`. In the vocabulary of §2.2, the columns are the
membership tests of [SωS26, Def 4.3] sampled at word level — a linear column
`(x, y, t)` reads `Λ(𝒮_L(x), 𝒮_L(t)^π)` at the right extension `𝒮_L(y)`, an
ω-column `(x, y)` reads `Ω(𝒮_L(x))` — except that the learner owns no stamp:
its slots and extensions are concrete words it has queried, and
[SωS26, Lem 4.2] is the guarantee that some finite family of such tests
characterizes `≈_L`.

The two sorts divide the labor exactly as Arnold's two shapes do. On `Even`,
linear columns already separate everything —
the stem decides membership. On `EvenBlocks`, *every* linear column is a constant
row-function (prefix-independence: a stem mutation is swallowed), and the entire
language lives in the ω-sort: the column `(ε, b)` separates rows `a` and `aa`,
since `(a·b)^ω ∉ L` and `(aa·b)^ω ∈ L`. A learner without the ω-sort cannot even
represent what distinguishes them — this is [AF21]'s obstruction, met head-on.
(§4.1 shows the learner *finding* a rotated cousin, `(a, a)`, unaided — and the
final sweep mints `(ε, b)` itself, Table 8.)

*Example (day one, on `Even`).* `Even = (aa)*·b·Σ^ω` over `Σ = {b, a}` — an
even block of `a`, then `b`, then anything; membership of any word is fixed by
the parity of the `a`-count before its first `b`. Initialize `R = {ε, a, b}`,
`E_ω = {(ε, ε)}`, `E_lin = ∅`; Table 1 is the whole state of knowledge.
`a` and `b` split at once, and every frontier word folds into one of them by
its single bit. Two of these merges are quietly wrong — `aa ≉_L a` (alive with
opposite parity) and `a·b ≉_L a` (`a·b` is doomed: its first `b` closed an
odd block) — and the single column cannot see either. The run below catches
both, by two different mechanisms (§4.1, §4.3).

| word | `(ε,ε)_ω` | class |
|---|:--:|---|
| `ε` | — | `[ε]` |
| `a` | `0` | `[a]` |
| `b` | `1` | `[b]` |
| *frontier:* | | |
| `a·a` | `0` | → `[a]` ✗ |
| `a·b` | `0` | → `[a]` ✗ |
| `b·a` | `1` | → `[b]` |
| `b·b` | `1` | → `[b]` |

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
compared), matching the fresh-identity convention of the target (§2.2).

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
`p`, a shorter table word, is covered by the induction hypothesis:
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
keep it apart from the target's `𝒞_L`), `λ(a) = ψ(a)`, the transition
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
convention earning its keep. That definition is deliberate: a counterexample is therefore
always a pair of concrete lassos — the queried one and its representative
collapse — on which the *teacher's own bits differ*.

*Example (a prediction, and its miss).* We now run the prediction procedure in
slow motion, on `EvenBlocks`: infinitely many `b`, and eventually every
completed `a`-block has even length — a *block* being a maximal run of `a`,
*completed* when the next `b` closes it. Day one (Table 2) has the same shape
as `Even`'s: the single ω-column splits `a` from `b`, and every frontier word
merges by its one bit. One entry deserves a pause: `b·a` lands with `a` here,
not with `b` as it did in `Even` — `(b·a)^ω` completes an odd block forever,
bit `0`. So the hypothesis's worldview is: there are three kinds of finite
words — the empty one, the pure `b`-blocks, and *everything that has ever
seen an `a`*. Its `step` function says exactly that: from `[b]`, reading `a`
moves to `[a]`; from `[a]`, no letter ever leaves.

| word | `(ε,ε)_ω` | class |
|---|:--:|---|
| `ε` | — | `[ε]` |
| `a` | `0` | `[a]` |
| `b` | `1` | `[b]` |
| *frontier:* | | |
| `a·a` | `0` | → `[a]` |
| `a·b` | `0` | → `[a]` |
| `b·a` | `0` | → `[a]`  (≠ `Even`!) |
| `b·b` | `1` | → `[b]` |

**Table 2.** Day one on `EvenBlocks`: same shape as Table 1, one telling
difference — `b·a` folds to `[a]`, so `[a]` is absorbing and the fold sees
only "have I read an `a` yet".

<table>
<tr>
<td align="center"><img src="sos_core_figs/img/sosl_even_day1_pairs.png" alt="Even day-one invariant" width="260"></td>
<td align="center"><img src="sos_core_figs/img/sosl_evenblocks_day1_pairs.png" alt="EvenBlocks day-one invariant" width="260"></td>
</tr>
<tr>
<td align="center"><b>(a) day one on <code>Even</code></b> (Table 1).<br><code>x·y = x</code>: the stem decides.<br>Denotes <code>b·Σ^ω</code> — "the first letter decides."</td>
<td align="center"><b>(b) day one on <code>EvenBlocks</code></b> (Table 2).<br><code>[a]</code> absorbing: "have I read an <code>a</code> yet".<br>Denotes <code>FG¬a</code> — "finitely many <code>a</code>".</td>
</tr>
</table>

**Figure 4.** The day-one beliefs, drawn with Figure 2's conventions: the
hypotheses of Tables 1 and 2 as handed to the first equivalence query,
exported by §5's recipe `c·c' := fold(c, rep(c'))`. The export is legitimate
this early: both day-one kernels are already two-sided congruences
(Lemma 5.2's zero-query check — clean on both, mechanically confirmed), and
both pair sets are conjugacy-closed, so each drawing is a *well-formed
invariant* — the learner's belief is itself an ω-regular language, rougher
than the target it will be revised into (Figure 2 (b), (c)). The two algebras
differ in a single edge — `[b]·[a]`, Table 2's telling entry, drawn.

Now predict the lasso `(ε, b·aa)`, following the definition step by step.
*Fold the loop:* `ψ(b·aa)` walks `[ε] →_{b} [b] →_a [a] →_a [a]` — the
middle step crossing the telling entry above — so `c_1 = [a]`. *Find the
idempotent power:* `c_2 = ψ((b·aa)²)` continues the walk from `[a]` —
absorbed, so `c_2 = [a]` — and the least `k` with `c_{2k} = c_k` is `k = 1`:
the hypothesis believes `[a]` is already idempotent. *Form the pair:*
`s = ψ(ε·b·aa) = [a]`, `e = [a]`. This step is the whole point of a
prediction: the hypothesis has just **named** the queried lasso by the pair
`([a], [a])` — the same name it gives `a·a^ω`, `(a·b)^ω`, `(b·a)^ω`, and
every other lasso whose folds collapse into `[a]` — and one name gets one
verdict. *Look up the name:* the cache has no entry for `([a],[a])`, so it
costs one membership query on the shortlex keys,
`w_{[a]}·(w_{[a]})^ω = a·a^ω` — rejected, no `b` at all. Cached; prediction
`0`.

The miss: `(b·aa)^ω ∈ L` — infinitely many `b`, and every completed block it
ever closes is `aa`, length two. The hypothesis gave one name to two lassos
that the language distinguishes, and that is all a counterexample ever is in
this design: the queried lasso and its representative collapse, two concrete
lassos, teacher bits `1` and `0`.

The minimization policy of §2.3 explains why this exact lasso is the one
returned. Enumerating stems shortest-first and loops shortest-then-shortlex
(`b < a`): `(ε, b)`, `(ε, a)`, the four two-letter loops, and then
`(ε, bbb)`, `(ε, bb·a)`, `(ε, b·ab)` are all predicted correctly — each
folds to a name whose representative lasso the language happens to treat the
same way — and `(ε, b·aa)` is the first place the name `([a],[a])` cracks. A
misprediction is an equality the table wrongly believes; the harvest of §4.1
turns this one into the column that refutes it.
