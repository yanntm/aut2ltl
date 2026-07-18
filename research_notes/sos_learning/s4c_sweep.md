### 4.3 The repair: left-saturation over class representatives

The missing ingredient is the other half of the rotation lemma (§2.2): a left
factor acts only by re-indexing a slot, and slots are finitely many
[SωS26, Lem 4.3]; on the
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
  the period `w·y°` unchanged and need not separate at all: for a
  prefix-independent `L` its added prefix is vacuous outright,
  Proposition 4.6.) Either way the minted column
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

*Remark (the ω-mint's shape matters).* Implemented with the bare-prefix form
`(x°·r, y°)`, the sweep on `GF(aa)` — prefix-independent, so the added prefix
is swallowed — separates nothing and never converges; only the reseeded
period of `(x°·r, y°·r)` carries `r`'s left action into the loop.

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
and §4.2's permanent stall is caught by nothing else. One
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
`[ε]`, the `N = 5` classes of `𝓘(Even)` — and every frontier word now folds
cleanly: `a·!a·a` carries the all-zero signature of the absorbing reject and
joins `[a!a]`; `aa·!a` carries the all-one signature of the committed accept
and joins `[!a]`.

Saturation checks are free; escalations are bounded by the total number of
splits. The sweep runs after closedness and consistency, before each equivalence
query; a clean sweep certifies that `ψ`'s kernel is a **left** congruence on
table words — and it was a right congruence by Lemma 3.3.

The left contexts the sweep enforces come in Arnold's two shapes, and
prefix-independence silences exactly one of them:

**Proposition 4.6 (prefix-independence and the two shapes).** Let `L` be
prefix-independent (`w ∈ L ⟺ σ·w ∈ L` for every finite `σ`). Then the prefix
slot `x` of every Arnold context is vacuous — `x·u·y·t^ω ∈ L ⟺ u·y·t^ω ∈ L`
and `x·(u·y)^ω ∈ L ⟺ (u·y)^ω ∈ L` — so the *linear* shape degenerates to pure
right extensions: a linear context separates `u` from `v` iff one with `x = ε`
does. The *ω-power* shape does not degenerate: in `(u·y)^ω` every occurrence
of `u` after the first is preceded by `y`, so the context acts on `u` from the
left through the wrap-around — a left action that is a rotation of the loop,
not a deletable prefix.

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
residual languages, which are ω-regular and hence determined by them [PP04] —
agreement under all of them is exactly `u ~_L v` — and the ω-power shape's
remaining contexts are the bare ω-powers. If `u ~_L v` and `u ≉_L v`, the
separating Arnold context is therefore of the ω-power shape. (b) By
induction over the run. The initial column is the ω-column `(ε, ε)`, and
every mint inherits the sort of the column it derives from: consistency
mints by Definition 3.2, both saturation branches by Lemma 4.5 (branch 1
reproduces `κ` in `κ`'s own sort; branch 2's frozen chain mints `κ`'s sort,
the segment migrating into the middle component). The only source of a
linear column left is the harvest's stem chain (Lemma 4.1) — and on a
prefix-independent language the stem chain is *flat*: its bits `γ_i` belong
to words that differ only in their finite prefixes, so `γ_0 = ⋯ = γ_n`,
every flip lands in the loop chain, and Lemma 4.2 mints an ω-column. ∎

Table 8's run is the corollary performed — four columns, all ω — and §6.3
uses it in the other direction, as a certificate: a permanent stall of a
prefix-independent language must be recovered entirely by ω-sort mints, a
machine-checkable signature of every such census witness.

Prefix-independence also has a floor, which bounds where such witnesses
can live at all:

**Lemma 4.8 (prefix-independence needs depth).** A prefix-independent
language that is topologically closed — a safety language — is `∅` or
`Σ^ω`; dually for open. A nontrivial prefix-independent language is
therefore neither closed nor open.

*Proof.* Let `L` be closed, prefix-independent, and nonempty, and pick
`w ∈ L`. Every `x ∈ Σ^ω` is the limit of the words `x[0..n]·w`, each in
`L` by prefix-independence; closedness puts the limit in `L`, so
`L = Σ^ω`. An open prefix-independent language has a closed
prefix-independent complement. ∎

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
