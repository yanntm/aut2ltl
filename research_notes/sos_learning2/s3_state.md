## 3. The learner's state

The learner's state has two layers, and keeping them apart is the design.
The **table** (§3.1) is private bookkeeping: rows, columns, membership
bits — the ledger where separations are recorded, open slots tracked, and
witnesses stored. The **belief** (§3.2) is what the learner actually
holds true: a well-formed invariant, exported from the table once two
legality checks pass, and held in canonical form. Conclusions are drawn
from the belief; the teacher sees the belief; the table never crosses the
wall.

### 3.1 The observation table

**Definition 3.1 (table).** A table is `T = (R, E_lin, E_ω)` where `R ⊆ Σ*` is a
finite set of **rows** containing `ε`, observed together with its
frontier `R·Σ`, and the columns are of two sorts:

- `E_lin ⊆ Σ* × Σ* × Σ⁺` — **linear columns**; the entry of row `u` at
  `(x, y, t)` is the bit `[ x·u·y·t^ω ∈ L ]`;
- `E_ω ⊆ Σ* × Σ*` — **ω-columns**; the entry of row `u` at `(x, y)` is the bit
  `[ x·(u·y)^ω ∈ L ]`.

Rows `u, v` are **table-equivalent**, `u ≡_T v`, when all entries agree.

Every entry is one membership query. By construction `≈_L` refines `≡_T` for
any column set — columns are particular Arnold contexts — so learning is the
business of growing `E_lin ∪ E_ω` until `≡_T` *is* `≈_L` on the rows, and
growing `R` until the rows exhaust `𝒞_L`. In the vocabulary of §2.2, the
columns are the membership tests of [SωS26, Def 4.3] sampled at word level —
a linear column `(x, y, t)` reads `Λ(𝒮_L(x), 𝒮_L(t)^π)` at the right
extension `𝒮_L(y)`, an ω-column `(x, y)` reads `Ω(𝒮_L(x))` — except that the
learner owns no stamp of `L`: its slots and extensions are concrete words it
has queried, and [SωS26, Lem 4.2] is the guarantee that some finite family
of such tests characterizes `≈_L`.

The two sorts divide the labor exactly as Arnold's two shapes do. On `Even`,
linear columns already separate everything — the stem decides membership. On
`EvenBlocks`, *every* linear column is a constant row-function
(prefix-independence: a stem mutation is swallowed), and the entire language
lives in the ω-sort: the column `(ε, b)` separates rows `a` and `aa`, since
`(a·b)^ω ∉ L` and `(aa·b)^ω ∈ L`. A learner without the ω-sort cannot even
represent what distinguishes them — this is [AF21]'s obstruction, met
head-on. (§4.1 shows the learner *finding* a rotated cousin, `(a, a)`,
unaided — and the last legality escalation mints `(ε, b)` itself, Table 7.)

**Definition 3.2 (closed, consistent; access words; keys; minting).** The
table is observed on its **words** `W(T) = R ∪ R·Σ` (rows and frontier).
`T` is **closed** when every frontier word is `≡_T` to some row (else the
offending frontier word is promoted to `R`), and **consistent** when
`u ≡_T v` implies `u·a ≡_T v·a` for all rows `u, v` and letters `a` — §2.1's
notions, with two sorts of experiments in place of suffixes. Rows are
maintained as **access words**: `R` starts as `{ε}`, and every other row is
a promoted frontier word `u_c·a` — letters included, promoted from `ε`'s
own frontier (§4.5) — where the **key** of a class `c`,
written `u_c`, is its shortlex-least row. Two structural facts follow and
are used below: every letter-prefix of a row is itself a row (rows are only
ever created by extending a row with one letter), and each promotion adds
one letter to an existing row while creating a new class, so rows — hence
keys — have length `O(|𝒞_T|)`. A consistency violation at column `c`
**mints** a new column by migrating the letter into the column: for
`c = (x, y, t)` linear, the column `(x, a·y, t)`; for `c = (x, y)` ω, the
column `(x, a·y)`. Minting is sound bookkeeping — the entry of `u` at the
minted column *is* the entry of `u·a` at `c`, by the identities
`x·u·(a·y)·t^ω = x·(u·a)·y·t^ω` and `x·(u·(a·y))^ω = x·((u·a)·y)^ω` — so the
minted column separates `u` from `v` exactly because `c` separated their
`a`-successors. The empty word is kept as a permanent row for the adjoined
identity `[ε]` (it seeds the evaluation and is never compared), matching the
fresh-identity convention of the target (§2.2).

**Lemma 3.3 (the letter action).** On a closed and consistent table, setting
`c·a := (the class of the table word u_c·a)` defines a **letter action** of
`Σ` on the classes `𝒞_T`, and the action agrees on every member of a class:
for any row `u` of class `c`, the table word `u·a` has class `c·a`. The
action extends letterwise to all finite words, `c·w`, and every table word
`u` satisfies `⟨u⟩ = [ε]·u`, writing `⟨u⟩` for the class of `u`; the kernel
of `⟨·⟩` is a right congruence on rows.

*Proof.* *Well-definedness:* `u_c·a` is a table word (a row, or a frontier
word), and closedness assigns every table word the class of some row.
*Agreement:* for a row `u` of class `c` we have `u ≡_T u_c`, both rows, so
consistency gives `u·a ≡_T u_c·a`, i.e. the class of `u·a` is `c·a`.
*Coherence* (`⟨u⟩ = [ε]·u`), by induction on `|u|` over table words. Base:
`⟨ε⟩ = [ε]` by definition. Step: every non-empty table word is `u = p·a`
with `p` a row — a frontier word extends a row by definition, and a
non-empty row was created as a one-letter extension of a row
(Definition 3.2's access discipline) — and `p`, a shorter table word, is
covered by the induction hypothesis:
`[ε]·u = ([ε]·p)·a = ⟨p⟩·a = ⟨p·a⟩ = ⟨u⟩`, the third equality by agreement.
*Right congruence:* for rows `u ≡_T v` and a letter `a`, agreement twice
gives `⟨u·a⟩ = ⟨u⟩·a = ⟨v⟩·a = ⟨v·a⟩`. ∎

The action composes over *literal* concatenation — `d·(x·y) = (d·x)·y`,
immediately from the letterwise definition — a small identity used
repeatedly below. Note carefully what it does *not* say: nothing yet
relates `d·u` to `d·u_{⟨u⟩}` — the action of a word against the action of
its class's key. That gap is exactly where an acceptor can hide inside an
algebra's clothing, and §6 turns on it.

**The candidate stamp.** A closed, consistent table thus presents a
**candidate stamp**: the classes `𝒞_T` (written with weak brackets `⟨u⟩`,
kept apart from the target's syntactic classes `[u]`), the letter map
`λ(a) = ⟨a⟩`, and the evaluation `𝒮_T(u) := [ε]·u` — a letterwise
classifier of all finite words. It is *not yet a stamp*: a stamp is a
morphism, `𝒮_T(u·v) = 𝒮_T(u)·𝒮_T(v)`, and no product of classes has even
been defined — let alone one the evaluation respects. Turning the candidate
into a genuine algebra is not a formality; it is the first legality check
below, and §6 shows what happens to a learner that skips it.

*Example (day one, on `Even` and `EvenBlocks`).* `Even = (aa)*·b·Σ^ω` over
`Σ = {b, a}` — an even block of `a`, then `b`, then anything; membership of
any word is fixed by the parity of the `a`-count before its first `b`.
Initialize `R = {ε, a, b}`, `E_ω = {(ε, ε)}`, `E_lin = ∅`; Table 1 is the
whole state of knowledge. `a` and `b` split at once, and every frontier word
merges into one of them by its single bit. Two of these merges are quietly
wrong — `aa ≉_L a` (alive with opposite parity) and `a·b ≉_L a` (`a·b` is
doomed: its first `b` closed an odd block) — and the single column cannot
see either. The run below catches both, by two different mechanisms (§4.1,
§4.2). On `EvenBlocks` — infinitely many `b`, and eventually every completed
`a`-block even — day one has the same shape with one telling difference:
`b·a` lands with `a` (`(b·a)^ω` completes an odd block forever, bit `0`), so
`⟨a⟩` is absorbing and the candidate's worldview is "have I read an `a`
yet".

*(Table 1 — day one on `Even`; Table 2 — day one on `EvenBlocks`. Rows
above the frontier line, one ω-column — the entry of word `p` is
`[p^ω ∈ L]` — and `→` the class each frontier word joins.)*

| word | `(ε,ε)_ω` | class |
|---|:--:|---|
| `ε` | — | `[ε]` |
| `a` | `0` | `⟨a⟩` |
| `b` | `1` | `⟨b⟩` |
| *frontier:* | | |
| `a·a` | `0` | → `⟨a⟩` ✗ |
| `a·b` | `0` | → `⟨a⟩` ✗ |
| `b·a` | `1` | → `⟨b⟩` |
| `b·b` | `1` | → `⟨b⟩` |

**Table 1.** Day one on `Even`. The two merges marked `✗` are wrong
(`≉_L`) but invisible: no observed context separates the words yet.

| word | `(ε,ε)_ω` | class |
|---|:--:|---|
| `ε` | — | `[ε]` |
| `a` | `0` | `⟨a⟩` |
| `b` | `1` | `⟨b⟩` |
| *frontier:* | | |
| `a·a` | `0` | → `⟨a⟩` |
| `a·b` | `0` | → `⟨a⟩` |
| `b·a` | `0` | → `⟨a⟩`  (≠ `Even`!) |
| `b·b` | `1` | → `⟨b⟩` |

**Table 2.** Day one on `EvenBlocks`: same shape, one telling difference —
`b·a` joins `⟨a⟩`, so `⟨a⟩` is absorbing under the letter action.

**The letter collapse.** Every class is already a speculation — the absence
of a separating column — and the fill can spend that trust instead of
re-checking it cell by cell: where two letters share their full signature,
the congruence-to-be predicts `u·b ≡ u·â` (the degenerate, one-letter case
of left invariance), so real queries go only to the rows, the letters, and
the frontier extensions by each letter class's least member; every other
cell records its cousin's bit as a **proxy**, a bit already in evidence
overriding it. A contradicted prediction is the learner's ordinary food:
the contradicting bit lands in the very cell it was predicted for and the
repairs of §4 fire unchanged, with blame well-founded by two-sidedness —
`u·b ≉_L u·â` implies `b ≉_L â`, a split the always-queried letter rows
exhibit as soon as any column separates the pair. Three disciplines keep
the checks honest: a proxy is never evidence (not replayed, recomputed at
every fill), never witnesses a structural event (a pure proxy witness
mirrors its rep cousins, so nothing is lost), and a promoted word is
grounded first — rows carry real bits, so keys and every split's witness
stay genuine. Legality is untouched: a wrong proxy makes the belief wrong,
never ill-formed; §5 counts the saving and the deferral.

### 3.2 The belief: a well-formed invariant

**Stamp legality.** The first check asks whether the candidate is an
algebra at all:

```
    for every table word u and class d:      d·u  =  d·u_{⟨u⟩}
```

— the action of every table word agrees with the action of its class's
key. A pure table computation, zero queries. The check is complete:

**Lemma 3.4 (the check decides morphism-hood).** On a closed, consistent
table, the induced product `⟨u⟩·⟨v⟩ := ⟨u·v⟩` on `𝒞_T` is well defined —
equivalently, the kernel of `𝒮_T` on `Σ*` is a two-sided congruence,
making `𝒮_T` restricted to `Σ⁺` a stamp — iff the stamp-legality check is
clean.

*Proof.* (⟸) Write `(S)` for the check's instances at frontier words:
`d·(u_c·a) = d·u_{c·a}` for all `d, c ∈ 𝒞_T`, `a ∈ Σ` — frontier words are
table words, so a clean check includes them. Induction on `|u|` extends the
check to *every* word `u ∈ Σ*` (not only table words): the base is `(S)` at
`c = [ε]`, and the step is
`d·(u'·a) = (d·u')·a = (d·u_{⟨u'⟩})·a = d·(u_{⟨u'⟩}·a) = d·u_{⟨u'·a⟩}`,
the last equality by `(S)` at `c = ⟨u'⟩` (coherence, Lemma 3.3, gives
`⟨u_{⟨u'⟩}·a⟩ = ⟨u'⟩·a = ⟨u'·a⟩`). Now the kernel is two-sided: right
invariance is Lemma 3.3; for left invariance, if `𝒮_T(u) = 𝒮_T(v)` then
for any `x`,
`𝒮_T(x·u) = ([ε]·x)·u = 𝒮_T(x)·u = 𝒮_T(x)·u_{⟨u⟩} = 𝒮_T(x)·v_{...} = 𝒮_T(x·v)`
— the extended check makes the action of a word a function of its class.
The induced product is then well defined and `𝒮_T` multiplicative by
construction: `𝒮_T(u·v) = 𝒮_T(u)·v = 𝒮_T(u)·𝒮_T(v)`. (⟹) With the product
well defined, `d·u = d·𝒮_T(u)` is a function of `(d, ⟨u⟩)` for every word
`u` reaching class `d` — and `⟨u_{⟨u⟩}⟩ = ⟨u⟩` on table words is coherence
(Lemma 3.3), so `d·u = d·u_{⟨u⟩}`. ∎

**Pair legality.** With stamp legality in hand the table's classes carry a
genuine finite semigroup, and its acceptance layer is filled from the
teacher: for every linked pair `(s, e)` of the induced product,

```
    P(s, e)  :=  teacher[ u_s·(u_e)^ω ]
```

— one membership query per pair, on the **keyed lasso** the pair's shortlex
keys spell, memoized by lasso across the whole run. `P` is a cache of
teacher truths: never "wrong," only indexed by classes that may later
split. The second check asks whether `⟨𝒮_T, P⟩` is *well-formed*: `P`
saturated under the conjugacy steps `(s, (cd)^π) ∼ (s·c, (dc)^π)`
([SωS26, Def 4.2]) — a scan of the triples `s, c, d ∈ 𝒞_T` with
`s·(cd)^π = s`, `O(|𝒞_T|³)` table work, zero queries beyond the `P`
entries themselves. Mid-run the check can genuinely fail: two conjugate
pairs name a common lasso, but their *keyed* lassos are different concrete
ω-words, and while the stamp is still coarser than `≈_L` the teacher may
answer them differently. Such a violation is not a defect to paper over but
a gift — §4.2 converts it into a class split.

**The export, and the belief.** When both checks are clean, `⟨𝒮_T, P⟩` is a
well-formed invariant. Its canonicalization

```
    𝓘_i  :=  ⟨𝒮_T, P⟩ / ∼        ([SωS26, Thm II] — partition refinement,
                                   zero queries, language-preserving)
```

is the **belief**: the syntactic invariant of the **belief language**
`K_i := L(𝓘_i)`, the unique language the belief denotes
([SωS26, Prop 4.1]). The belief — not the table — is what conclusions are
drawn from, and what the teacher receives at every equivalence query. Note
what the discipline buys even before any correctness argument: at every
stage the learner's epistemic state is an actual ω-regular language, in the
same canonical form as the target; learning is a walk through the space of
languages, each step forced by one disagreement. Canonicalizing costs no
queries and loses nothing: merges happen only in the exported view, while
the table underneath keeps every witnessed separation.

**How the belief answers a lasso.** Prediction is not a new definition — it
is lasso membership [SωS26, Def 3.4] evaluated on the belief: for `w·z^ω`,
set `e := 𝒮_T(z)^π` (iterate the loop's class to its idempotent power),
`s := 𝒮_T(w)·e`, and answer `P(s, e)` — by construction the teacher's own
bit on the keyed lasso `u_s·(u_e)^ω`, a genuine lasso since no class but
the permanent singleton `[ε]` contains the empty word (§2.2's fresh
identity earning its keep). That definition is deliberate: a disagreement
is therefore always **two concrete lassos bearing one name** — the queried
lasso and the keyed lasso of its name — on which the *teacher's own bits*
differ. §4's single split mechanism consumes exactly this shape.

*Example (day one's beliefs, exported).* Both day-one tables pass both
checks — each induced product is a two-sided congruence, each two-pair
acceptance layer is conjugacy-closed — so each exports a well-formed
invariant, drawn in Figure 3: the learner's opening beliefs are themselves
ω-regular languages, rougher than the targets they will be revised into.
`Even`'s day-one belief denotes `b·Σ^ω` — "the first letter decides";
`EvenBlocks`' denotes `FG¬a` — "finitely many `a`". The two algebras differ
in a single edge — `⟨b⟩·⟨a⟩`, Table 2's telling entry, drawn.

<table>
<tr>
<td align="center"><img src="../sos_core_figs/img/sosl_even_day1_pairs.png" alt="Even day-one belief" width="260"></td>
<td align="center"><img src="../sos_core_figs/img/sosl_evenblocks_day1_pairs.png" alt="EvenBlocks day-one belief" width="260"></td>
</tr>
<tr>
<td align="center"><b>(a) day one on <code>Even</code></b> (Table 1).<br><code>x·y = x</code>: the stem decides.<br>Denotes <code>b·Σ^ω</code> — "the first letter decides."</td>
<td align="center"><b>(b) day one on <code>EvenBlocks</code></b> (Table 2).<br><code>⟨a⟩</code> absorbing: "have I read an <code>a</code> yet".<br>Denotes <code>FG¬a</code> — "finitely many <code>a</code>".</td>
</tr>
</table>

**Figure 3.** The opening frames: the day-one beliefs of Tables 1 and 2 as
handed to the first equivalence query, drawn with Figure 2's conventions.
Each is a well-formed invariant — a language — and the runs of §4 revise
them, frame by frame, into Figure 2 (b) and (c).

*Example (a name, and its crack).* On `EvenBlocks`' day-one belief, take
the lasso `(ε, b·aa)`. The loop's class: `𝒮_T(b·aa)` walks
`[ε] →_b ⟨b⟩ →_a ⟨a⟩ →_a ⟨a⟩` — crossing the telling entry — and `⟨a⟩` is
idempotent here, so `e = ⟨a⟩`, `s = [ε]·e = ⟨a⟩`: the belief **names** the
lasso by the pair `(⟨a⟩, ⟨a⟩)` — the same name it gives `a·a^ω`, `(a·b)^ω`,
`(b·a)^ω`, and every other lasso whose classes collapse into `⟨a⟩` — and one
name gets one verdict: `P(⟨a⟩, ⟨a⟩)` is the teacher's bit on the keyed lasso
`a·a^ω`, which is `0` — no `b` at all. But `(b·aa)^ω ∈ EvenBlocks`:
infinitely many `b`, every completed block `aa`. The belief gave one name to
two lassos that the language distinguishes; the teacher's minimal-
counterexample policy returns exactly this lasso (every shorter loop
happens to be named truthfully), and §4.1 shows the harvest turning it into
the column that cracks the name.
