### 4.2 Self-served: the legality escalations

Re-stabilizing after a split — the interior of every align call, §4.3 —
the learner re-runs the two legality checks of §3.2. A clean pass
certifies the export; a violation is a discordance caught without the
teacher, escalated to a split by the same chain.

**Stamp escalation.** The check compares, for every table word `u` with
key `v := u_{⟨u⟩}`, `u ≠ v`, and every class `d` with key `r := u_d`, the
actions `d·u` and `d·v` — zero queries.

**Lemma 4.3 (stamp escalation).** If `d·u =: c_a ≠ c_b := d·v`, then two
membership queries and at most one chain yield a new separating column
and a class split.

*Proof.* Since `c_a ≠ c_b`, some existing column `κ` separates their keys —
distinct classes differ on some column, by definition of `≡_T`; say
`κ = (x°, y°, t°)` linear, so the table already holds
`[κ[u_{c_a}]] ≠ [κ[u_{c_b}]]` (for the ω-sort `κ = (x°, y°)`, read
`[x°·(u_c·y°)^ω]` throughout). Query the two candidate words under the
same context: `A = [κ[r·u]]`, `B = [κ[r·v]]`.

- If `A ≠ B`: mint the column that reproduces "`r·w` under `κ`" as a bit on
  the bare candidate `w` — and the two sorts here differ. For a *linear* `κ`
  the candidate sits in the finite prefix, so `r` prepends there:
  `(x°·r, y°, t°)`. For an *ω* `κ` the candidate rides in the period, and
  peeling one `r` off the repeating block gives
  `x°·(r·w·y°)^ω = x°·r·(w·y°·r)^ω`: `r` must seed *both* the prefix and
  the period's tail — `(x°·r, y°·r)`. (The bare-prefix form `(x°·r, y°)`
  keeps the period `w·y°` unchanged and need not separate at all: for a
  prefix-independent `L` its added prefix is vacuous outright,
  Proposition 4.5.) Either way the minted column separates `u` from `v`
  directly — a genuine Arnold context — splitting their shared class.
- If `A = B`: the bits `A, B` cannot both agree with the two differing
  key bits; say `A ≠ [κ[u_{c_a}]]`, where
  `c_a = d·u = ([ε]·r)·u = [ε]·(r·u) = ⟨r·u⟩` — the action composing
  over the literal concatenation `r·u`. So the segment `r·u` and its own
  class's key behave differently under `κ`: exactly Lemma 4.1's
  precondition, with context `κ` and segment `r·u`. The chain

  ```
      χ_j = [ x° · u_{⟨(r·u)[1..j]⟩} · (r·u)[j+1..] · y°·t°^ω ]
  ```

  runs from `χ_0 = A` to `χ_{|ru|} = [κ[u_{c_a}]] ≠ A`; the flip exists,
  binary search finds it, and the minted column
  `(x°, (r·u)[j+2..]·y°, t°)` — `κ`'s own prefix kept in place, the
  unconsumed segment migrating into the middle component — splits the
  frontier word `u_{⟨(r·u)[1..j]⟩}·(r·u)[j+1]` from the row
  `u_{⟨(r·u)[1..j+1]⟩}`. Either way one class splits. ∎

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

Escalate the fired cell (Lemma 4.3): `u = b·a`, `v = b`, `d = ⟨a⟩`,
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
side disagrees with its own class's key? `⟨a·b·a⟩ = c_a = ⟨aa⟩`, whose
key `aa` holds κ-bit `1 ≠ A` — the `u`-side. Run the chain in `κ`'s own
context on the segment `r·u = a·b·a` (here `x° = ε`, so `κ` contributes
no prefix; a genuinely frozen prefix arises when it carries one):

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
one four-class table exercises both branches of Lemma 4.3, and the fixpoint
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
conjugacy steps, and its escalation is Theorem 4.2 run on a discordance
the learner finds itself:

**Lemma 4.4 (pair escalation).** Let the stabilized table be stamp-legal,
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
lassos bearing one name with differing teacher bits: exactly the
discordance shape, and Theorem 4.2 applies verbatim — junction query,
binary search, flip, split. The chain lengths are `O(|𝒞_T|²)`: keys have
length `O(|𝒞_T|)` (Definition 3.2) and the normalization power is at most
`2|𝒞_T|`, so the search costs `O(log |𝒞_T|)` queries. ∎

The escalation needs no new machinery and no equivalence query: the learner
noticed, by pure table inspection, that its own acceptance layer gives one
ω-word two verdicts — the well-formedness law of [SωS26, Prop 4.1] violated
— and referees the contradiction with one membership query. This is the
use the discipline makes of the teacher's cheapest interface: the belief's
legality is *tested from inside*.
