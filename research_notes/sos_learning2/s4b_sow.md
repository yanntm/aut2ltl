### 4.2 Sow: the legality escalations

Re-stabilizing after a split, the learner re-runs the two legality checks
of §3.2. A clean pass certifies the export; a violation is a disagreement
caught without the teacher, escalated to a split by the same chain
mechanism. This subsection gives the two escalations, then the structure
prefix-independence imposes on both.

**Stamp escalation.** The check compares, for every table word `u` with
key `v := u_{⟨u⟩}`, `u ≠ v`, and every class `d` with key `r := u_d`, the
actions `d·u` and `d·v` — zero queries.

**Lemma 4.4 (stamp escalation).** If `d·u =: c_a ≠ c_b := d·v`, then two
membership queries and at most one frozen-prefix binary search yield a new
separating column and a class split.

*Proof.* Since `c_a ≠ c_b`, some existing column `κ` separates their keys —
distinct classes differ on some column, by definition of `≡_T`; say
`κ = (x°, y°, t°)` linear, so the table already holds
`[x°·u_{c_a}·y°·t°^ω] ≠ [x°·u_{c_b}·y°·t°^ω]` (for the ω-sort
`κ = (x°, y°)`, read `[x°·(u_c·y°)^ω]` throughout). Query the two candidate
words under the same context: `A = [x°·r·u·y°·t°^ω]`,
`B = [x°·r·v·y°·t°^ω]` (ω-sort: `A = [x°·(r·u·y°)^ω]`,
`B = [x°·(r·v·y°)^ω]`).

- If `A ≠ B`: mint the column that reproduces "`r·w` under `κ`" as a bit on
  the bare candidate `w` — and the two sorts here differ. For a *linear* `κ`
  the candidate sits in the finite prefix, so `r` prepends there:
  `(x°·r, y°, t°)`. For an *ω* `κ` the candidate rides in the period, and
  peeling one `r` off the repeating block gives
  `x°·(r·w·y°)^ω = x°·r·(w·y°·r)^ω`: `r` must seed *both* the prefix and
  the period's tail — `(x°·r, y°·r)`. (The bare-prefix form `(x°·r, y°)`
  keeps the period `w·y°` unchanged and need not separate at all: for a
  prefix-independent `L` its added prefix is vacuous outright,
  Proposition 4.6.) Either way the minted column separates `u` from `v`
  directly — a genuine Arnold context — splitting their shared class.
- If `A = B`: the bits `A, B` cannot both agree with the two differing
  key bits; say `A ≠ [x°·u_{c_a}·y°·t°^ω]`, where
  `c_a = d·u = ([ε]·r)·u = [ε]·(r·u)` — the action composing over the
  literal concatenation `r·u`. So the word `r·u` and its own class's key
  behave differently under `x°·_·y°·t°^ω`. Run the stem chain of §4.1 on
  the segment `r·u` with the prefix `x°` **frozen** in place:
  `γ''_j = [ x° · u_{⟨(r·u)[1..j]⟩} · (r·u)[j+1..] · y°·t°^ω ]`, from
  `γ''_0 = A` to `γ''_{|ru|} = [x°·u_{c_a}·y°·t°^ω] ≠ A`. The flip exists,
  binary search finds it, and Lemma 4.1's argument applies verbatim with
  `x°` frozen: the flip at position `j` separates the frontier word
  `u_{⟨(r·u)[1..j]⟩}·(r·u)[j+1]` from the row `u_{⟨(r·u)[1..j+1]⟩}` by the
  column `(x°, (r·u)[j+2..]·y°, t°)` — the prefix is `x°` alone, the
  unconsumed segment migrating into the middle component. Either way one
  class splits. ∎

*Remark (the ω-mint's shape matters).* Implemented with the bare-prefix
form `(x°·r, y°)`, the escalation on `GF(aa)` — prefix-independent, so the
added prefix is swallowed — separates nothing and never converges; only the
reseeded period of `(x°·r, y°·r)` carries `r`'s left action into the loop.

*Example (a stamp-legality pass on `Even`, in full).* Resume `Even` after
§4.1's split: four classes `[ε], ⟨a⟩, ⟨b⟩, ⟨aa⟩`, with `a·b` still merged
into `⟨a⟩` — the doomed word still passing for an alive one. The check's
subjects are the five table words that are not keys; against the four
classes `d`, that is twenty comparisons, each a pure table computation.
Table 4 is the *entire* check phase — zero membership queries on this page.
(The scan order is pinned, for reproducible traces: subjects in shortlex
order, classes in key order; a different order changes which cell fires
first — never the fixpoint.)

| `u` (vs its key `v`) | `d = [ε]` | `d = ⟨b⟩` | `d = ⟨a⟩` | `d = ⟨aa⟩` |
|---|:--:|:--:|:--:|:--:|
| `b·b` (vs `b`) | `⟨b⟩` | `⟨b⟩` | `⟨a⟩` | `⟨b⟩` |
| `b·a` (vs `b`) | `⟨b⟩` | `⟨b⟩` | **`⟨aa⟩` ≠ `⟨a⟩`** | `⟨b⟩` |
| `a·b` (vs `a`) | `⟨a⟩` | `⟨b⟩` | **`⟨b⟩` ≠ `⟨aa⟩`** | `⟨a⟩` |
| `aa·b` (vs `b`) | `⟨b⟩` | `⟨b⟩` | `⟨a⟩` | `⟨b⟩` |
| `aa·a` (vs `a`) | `⟨a⟩` | `⟨b⟩` | `⟨aa⟩` | `⟨a⟩` |

**Table 4.** The stamp-legality check on `Even`'s four-class table: cell
`(u, d)` compares `d·u` against `d·u_{⟨u⟩}`; a single value means they
agree. Twenty comparisons, zero queries, two hits — both at `d = ⟨a⟩`, both
symptoms of the one wrong merge. In scan order the first to fire is
`(b·a, ⟨a⟩)`.

Escalate the fired cell (Lemma 4.4): `u = b·a`, `v = b`, `d = ⟨a⟩`,
`r = a`, diverging actions `c_a = ⟨a⟩·(b·a) = ⟨aa⟩` and
`c_b = ⟨a⟩·b = ⟨a⟩`. Pause on what fired: `b·a` is *correctly* merged with
`b` — the divergence arises because its action from `⟨a⟩` walks through the
wrong merge, not because the subject is misplaced. The escalation convicts
the guilty word anyway. The column separating `u_{⟨aa⟩} = aa` from
`u_{⟨a⟩} = a` is the harvested `κ = (ε, b, aab)`, and the two probe
queries — the escalation's only queries — are

```
    A = [ a·b·a ·b·(aab)^ω ] = 0        (r·u under κ's context)
    B = [ a·b   ·b·(aab)^ω ] = 0        (r·v under κ's context)
```

`A = B`: the first branch yields nothing, so we are in the second. Which
side disagrees with its own class's key? `[ε]·(a·b·a) = c_a = ⟨aa⟩`, whose
key `aa` holds κ-bit `1 ≠ A` — the `u`-side. Run the frozen-prefix chain on
the segment `r·u = a·b·a` inside κ's context (here `x° = ε`, so the freeze
is invisible; a genuinely frozen prefix arises when κ carries one):

| `j` | prefix of `a·b·a` | its key | queried lasso | bit |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `aba·b·(aab)^ω` | `0` |
| 1 | `a` | `a` | `a·ba·b·(aab)^ω` | `0` |
| 2 | `a·b` | `a` | `a·a·b·(aab)^ω` | **`1`** |
| 3 | `a·b·a` | `aa` | `aa·b·(aab)^ω` | `1` |

**Table 5.** The escalation's chain: replace a growing prefix of `a·b·a` by
its class's key, query under κ's context. The flip at `j = 1 → 2` hands
over the frontier word `a·b` (that is, `u_{⟨a⟩}·b`) and the row `a` (that
is, `u_{⟨a·b⟩}`), separated by the minted **linear column `(ε, ab, aab)`**
— entries `0` for `a·b`, `1` for `a`. The doomed word leaves `⟨a⟩`.

Two membership bits and a two-probe chain did the work of an equivalence
round. One remark completes the picture: the *other* hit, `(a·b, ⟨a⟩)`,
escalates through the **first** branch — there `c_a = ⟨b⟩`, `c_b = ⟨aa⟩`,
the separating column is the original ω-column `κ = (ε, ε)`, and the probes
`A = [(a·ab)^ω] = 1 ≠ 0 = [(a·a)^ω] = B` differ, minting the ω-column
`(a, a)` directly — the left factor absorbed into the prefix *and* reseeded
at the period's tail, branch 1's ω-form in action. Same split, other arm:
one four-class table exercises both branches of Lemma 4.4, and the fixpoint
is the same five classes either way — only the *trace* needs the pinned
order. Table 6 shows the resulting table, which is final.

| word | `(ε,ε)_ω` | `(ε,b,aab)_lin` | **`(ε,ab,aab)_lin`** | class |
|---|:--:|:--:|:--:|---|
| `a` | `0` | `0` | **`1`** | `⟨a⟩` |
| `b` | `1` | `1` | **`1`** | `⟨b⟩` |
| `aa` | `0` | `1` | **`0`** | `⟨aa⟩` |
| **`a·b`** | `0` | `0` | **`0`** | **`⟨ab⟩`** |

**Table 6.** `Even` at the fixpoint (minted column and promoted row in
bold; `ε`-row omitted). The four bit-signatures are pairwise distinct —
with `[ε]`, the `N = 5` classes of `𝓘(Even)` — and every frontier word now
lands cleanly: `a·b·a` carries the all-zero signature of the absorbing
reject and joins `⟨ab⟩`; `aa·b` carries the all-one signature of the
committed accept and joins `⟨b⟩`.

**Pair escalation.** The second check compares cached teacher bits across
conjugacy steps, and its escalation is the harvest run on a self-generated
counterexample:

**Lemma 4.5 (pair escalation).** Let the stabilized table be stamp-legal,
with `P` total on the linked pairs of the induced product, and let a
conjugacy step connect `p₁ = (s, (cd)^π)` and `p₂ = (s·c, (dc)^π)` with
`P(p₁) ≠ P(p₂)`. Then one membership query and one chain yield a witnessed
class split, at `O(log |𝒞_T|)` further queries.

*Proof.* Instantiate the rotation lemma [SωS26, Lem 4.1] on the keys: the
concrete lasso `w := u_s·(u_c·u_d)^ω` is named `p₁` by its presentation
`(u_s, (u_c·u_d)^π)` and `p₂` by `(u_s·u_c, (u_d·u_c)^π)` — one ω-word, two
names, and the cached bits of the two names differ. Query `b₀ :=
teacher[w]`; `b₀` disagrees with `P(p₁)` or with `P(p₂)` — say `P(p₁)`,
the teacher's bit on the keyed lasso of `p₁`. Then `w`, normalized on the
presentation naming `p₁`, and the keyed lasso of `p₁` are two concrete
lassos bearing one name with differing teacher bits: exactly the harvest's
situation, and Theorem 4.3 applies verbatim — junction query, binary
search, flip, split. The chain lengths are `O(|𝒞_T|²)`: keys have length
`O(|𝒞_T|)` (Definition 3.2) and the normalization power is at most
`2|𝒞_T|`, so the search costs `O(log |𝒞_T|)` queries. ∎

The escalation needs no new machinery and no equivalence query: the learner
noticed, by pure table inspection, that its own acceptance layer gives one
ω-word two verdicts — the well-formedness law of [SωS26, Prop 4.1] violated
— and referees the contradiction with one membership query. This is the
use the discipline makes of the teacher's cheapest interface: the belief's
legality is *tested from inside*.

**Prefix-independence and the two shapes.** The left contexts the
escalations enforce come in Arnold's two shapes, and prefix-independence
silences exactly one of them:

**Proposition 4.6 (prefix-independence and the two shapes).** Let `L` be
prefix-independent (`w ∈ L ⟺ σ·w ∈ L` for every finite `σ`). Then the
prefix slot `x` of every Arnold context is vacuous —
`x·u·y·t^ω ∈ L ⟺ u·y·t^ω ∈ L` and `x·(u·y)^ω ∈ L ⟺ (u·y)^ω ∈ L` — so the
*linear* shape degenerates to pure right extensions: a linear context
separates `u` from `v` iff one with `x = ε` does. The *ω-power* shape does
not degenerate: in `(u·y)^ω` every occurrence of `u` after the first is
preceded by `y`, so the context acts on `u` from the left through the
wrap-around — a left action that is a rotation of the loop, not a deletable
prefix.

*Proof.* The vacuity of `x` is prefix-independence applied to the finite
prefix `x`. For the wrap-around: `(u·y)^ω = u·(y·u)^ω`, so by
prefix-independence `(u·y)^ω ∈ L ⟺ (y·u)^ω ∈ L` — the membership constraint
on `u` under the ω-context `(_·y)^ω` is exactly its behavior under the left
factor `y`, read as a rotation (§2.2), which deleting finite prefixes never
touches. ∎

**Corollary 4.7 (a prefix-independent gap is ω-sorted).** Let `L` be
prefix-independent. (a) `u ≈_L v` iff `u` and `v` agree under every pure
right extension (`u·y·t^ω ∈ L ⟺ v·y·t^ω ∈ L` for all `y ∈ Σ*, t ∈ Σ⁺` —
that is, `u ~_L v`, the right congruence) *and* under every bare ω-power
(`(u·y)^ω ∈ L ⟺ (v·y)^ω ∈ L` for all `y ∈ Σ*`). Consequently two words the
right congruence identifies but `≈_L` separates are separated by ω-power
contexts *only*. (b) On the learner's side the sort discipline is absolute:
every column of every run on `L` is of the ω-sort.

*Proof.* (a) By Proposition 4.6 the prefix `x` is vacuous in both shapes.
The linear shape's remaining contexts `y·t^ω` range over the lassos of the
residual languages, which are ω-regular and hence determined by them
[PP04] — agreement under all of them is exactly `u ~_L v` — and the ω-power
shape's remaining contexts are the bare ω-powers. If `u ~_L v` and
`u ≉_L v`, the separating Arnold context is therefore of the ω-power shape.
(b) By induction over the run. The initial column is the ω-column `(ε, ε)`,
and every mint inherits the sort of the column it derives from: consistency
mints by Definition 3.2, both branches of a stamp escalation by Lemma 4.4
(branch 1 reproduces `κ` in `κ`'s own sort; branch 2's frozen chain mints
`κ`'s sort, the segment migrating into the middle component). The remaining
sources of columns are chains — the harvest's (Theorem 4.3) and the pair
escalation's (Lemma 4.5, the same chains) — and on a prefix-independent
language every stem chain is *flat*: its bits belong to words differing
only in their finite prefixes, so every flip lands in the loop chain, and
Lemma 4.2 mints an ω-column. ∎

Table 7's run is the corollary performed — four columns, all ω — and §7.3
uses it in the other direction, as a certificate: a permanent stall of a
prefix-independent language must be recovered entirely by ω-sort mints, a
machine-checkable signature of every such census witness.

Prefix-independence also has a floor, which bounds where such witnesses can
live at all:

**Lemma 4.8 (prefix-independence needs depth).** A prefix-independent
language that is topologically closed — a safety language — is `∅` or
`Σ^ω`; dually for open. A nontrivial prefix-independent language is
therefore neither closed nor open.

*Proof.* Let `L` be closed, prefix-independent, and nonempty, and pick
`w ∈ L`. Every `x ∈ Σ^ω` is the limit of the words `x[0..n]·w`, each in `L`
by prefix-independence; closedness puts the limit in `L`, so `L = Σ^ω`. An
open prefix-independent language has a closed prefix-independent
complement. ∎

### 4.3 The loop, assembled

```
    R ← {ε} ∪ Σ;   E_ω ← {(ε, ε)};   E_lin ← ∅
    repeat:
        fill entries (membership queries)
        repair closedness (promote) and consistency (mint) to fixpoint
        stamp legality: check; on violation escalate (Lemma 4.4):
            split, restart loop
        fill P on all linked pairs of the induced product (memoized queries)
        pair legality: check; on violation escalate (Lemma 4.5):
            split, restart loop
        𝓘_i ← canonicalize ⟨𝒮_T, P⟩          ([SωS26, Thm II], zero queries)
        pose EQ(𝓘_i)
        if yes: output 𝓘_i — it is 𝓘(L) (§5) — and stop
        else: normalize the counterexample; junction query; binary-search
              the flip; mint the harvested column (Lemma 4.1 or 4.2); split
```

Legality checks are free; escalations are bounded by the total number of
splits. A certified round — both checks clean — is exactly the round whose
export is a well-formed invariant (§3.2): the belief sequence
`𝓘_0, 𝓘_1, …` is the run's *frame sequence*, each frame an ω-regular
language, opening at Figure 3 and closing at Figure 2.

*Example (the `EvenBlocks` run, as frames).* Beyond the counterexample
traced in §4.1, two stamp escalations carry the table from four to its
eight classes — keys `ε, b, a, b·a, a·b, a·a, b·a·b, a·b·a`, the count and
keys fixed by the reference invariant. Table 7 is the run as a split
ledger, one row per event, from the implementation's transcript —
deterministic under the pinned scan and minimal-counterexample policies,
and reproducing §4.1's row exactly. One reading note: a single mint can
split more than one class once the table re-stabilizes — rows 2 and 3 each
split two.

| # | trigger | chain | minted column | splits | `\|𝒞_T\|` after |
|:--:|---|---|---|---|:--:|
| 1 | EQ: `(ε, b·aa)` | loop | `(a, a)_ω` | `b·a` out of `⟨a⟩` | 4 |
| 2 | stamp escalation | frozen | `(a, b·a)_ω` | `aa` out of `⟨a⟩`; `a·b` out of `⟨b·a⟩` | 6 |
| 3 | stamp escalation | frozen | `(ε, b)_ω` | `a·b·a` out of `⟨b⟩`; `b·a·b` out of `⟨aa⟩` | 8 |

**Table 7.** The `EvenBlocks` run as a split ledger: trigger (equivalence
counterexample or legality escalation), the chain that processed it, the
minted column, the words separated. The day-one checks are clean — Figure
3(b) is a legal frame — so row 1, §4.1's split, is the run's first event;
rows 2–3 are the stamp check enforcing two-sidedness — no second
counterexample is ever needed, and the run's second equivalence query
certifies. Every one of the four columns is of the ω-sort:
prefix-independence in action (the linear shape is blind, Proposition 4.6,
so every separation lives in the loop). The final escalation mints
`(ε, b)` — the very column §3.1 exhibited by inspection. The resulting
bit-signatures are the fixpoint (the Table 6 analogue), pairwise
distinct — with `[ε]`, the `N = 8` classes of `𝓘(EvenBlocks)`:

| word | `(ε,ε)_ω` | `(a,a)_ω` | `(a,b·a)_ω` | `(ε,b)_ω` |
|---|:--:|:--:|:--:|:--:|
| `b` | `1` | `0` | `0` | `1` |
| `a` | `0` | `0` | `1` | `0` |
| `b·a` | `0` | `1` | `0` | `0` |
| `a·b` | `0` | `1` | `1` | `0` |
| `a·a` | `0` | `0` | `0` | `1` |
| `b·a·b` | `0` | `0` | `0` | `0` |
| `a·b·a` | `1` | `0` | `0` | `0` |
