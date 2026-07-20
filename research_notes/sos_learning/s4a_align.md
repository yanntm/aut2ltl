## 4. Alignment: from discordance to belief

Every answer the teacher returns is one of two signals. A **concordant**
bit — the answer the belief already predicts — is recorded, in the table
or in the pair cache, and confirms the worldview: no learning happens. A
**discordant** bit contradicts a prediction, and only there does the
belief move. Agreement confirms, error teaches — and the learner runs
this engine with exactly one process, **alignment**: from one
discordance, by membership queries alone, through a cascade of witnessed
class splits, to the next belief — the table re-certified legal, its
export again a well-formed invariant.

By §3.2's prediction rule, every discordance in the entire algorithm has
one shape:

> **Two concrete lassos bear one name, and the teacher's bits on them
> differ.**

The sources differ only in who finds the lassos, and the learner finds
most of them itself: by **rereading its evidence** — a bit already
witnessed that the current belief contradicts, lasso and verdict both
in hand (§4.3); by **probing** — posing a lasso on its own initiative
and catching the answer contradicting its belief, the bootstrap sweep
of §4.5; and through its **legality checks**, which
catch two kinds by pure table inspection, zero queries: a stamp
violation, a divergence of actions escalated through two probe queries;
a pair violation, two conjugate pairs with differing cached bits,
refereed on their common rotated lasso (§4.2). The last source is
**teacher-found**: the lasso returned by a failed equivalence query
(§4.5), the one discordance the learner cannot locate itself. All feed
the same mechanism (§4.1): the name
is a pair `(s, e)` of current classes; a *chain* interpolates between
the two lassos, substituting, position by position, a growing prefix by
its class's key; the chain's bits flip at some adjacent step; the flip
convicts a frontier word against a row — currently one class, provably
`≈_L`-distinct — and mints the separating Arnold context as a new
column. §4.3 assembles the whole into alignment — a fixpoint over the
learner's evidence; §4.4 gives the structure prefix-independence
imposes on what alignment mints; §4.5 closes the loop around it —
bootstrap, then alternation with the teacher.

### 4.1 The chain: one discordance, one split

A **context** is a column read as a word-with-a-hole: a linear column
`C = (x, y, t)` evaluates `C[w] := x·w·y·t^ω`, an ω-column `C = (x, y)`
evaluates `C[w] := x·(w·y)^ω`; write `[C[w]]` for the teacher's bit on
the resulting lasso, and `⟨w⟩ := [ε]·w` for the letter action's class of
any finite word (Lemma 3.3). The chain compares a word against its own
class's key inside one context:

**Lemma 4.1 (substitution chain).** Let the table be closed and
consistent, `C` a context, and `s = s_1⋯s_k` a finite word with
`[C[s]] ≠ [C[u_{⟨s⟩}]]`. The **chain**

```
    χ_j  =  [ C[ u_{⟨s_1⋯s_j⟩} · s_{j+1}⋯s_k ] ]        j = 0..k
```

— replace a growing prefix of `s` by its class's key — runs from
`χ_0 = [C[s]]` to `χ_k = [C[u_{⟨s⟩}]]`: its endpoints differ, so some
adjacent pair flips, and a binary search finds a flip in `O(log k)`
membership queries. At a flip `χ_j ≠ χ_{j+1}`, the frontier word
`u = u_{⟨s_1⋯s_j⟩}·s_{j+1}` and the row `v = u_{⟨s_1⋯s_{j+1}⟩}` —
currently one class — are separated by the **minted column**
`(x, s_{j+2}⋯s_k·y, t)` (for the ω sort, `(x, s_{j+2}⋯s_k·y)`): a
genuine Arnold context, so `u ≉_L v`.

*Proof.* The two flipped bits are exactly the entries of `u` and `v` at
the minted column — substitute and compare, the context absorbing the
unconsumed suffix `s_{j+2}⋯s_k` into its middle component:
`C[u·s_{j+2}⋯s_k] = x·u·(s_{j+2}⋯s_k·y)·t^ω`, and for the ω sort
`x·(u·(s_{j+2}⋯s_k·y))^ω`, likewise for `v`. That `u` and `v` currently
share a class is Lemma 3.3: `⟨u⟩ = ⟨s_1⋯s_j⟩·s_{j+1} = ⟨s_1⋯s_{j+1}⟩ =
⟨v⟩` — agreement, coherence, and the action composing over literal
concatenation. The flip separates them at the minted column, an Arnold
context, so the separation is genuine. The endpoints: at `j = 0` the key
of `[ε]` is `ε`, so `χ_0 = [C[s]]`; at `j = k` the whole word is its
class's key. ∎

The lemma is instantiated four times in the paper — the two halves of
Theorem 4.2 below, the in-context probe of a stamp escalation
(Lemma 4.3), and the pair escalation's rotated lasso (Lemma 4.4) —
always the same search, only the context and the segment changing.

**Processing a discordant lasso.** Let `w·z^ω` be a lasso on which
teacher and belief disagree. **Normalize**
`(w', z') := (w·z^k, z^k)`, `k` least with `𝒮_T(z)^k` idempotent
(`k ≤ 2·|𝒞_T|`) — the same ω-word, now presented so that
`s = 𝒮_T(w')`, `e = 𝒮_T(z')` is the predicting name. Write `n = |w'|`,
`m = |z'|`. Two chain instances interpolate between the discordant lasso
and the keyed lasso of its name:

```
    stem chain  γ:  C = (ε, ε, z') linear, segment w' —
                    from γ_0 = [w'·z'^ω] to the junction γ_n = [u_s·z'^ω]
    loop chain  δ:  C = (u_s, ε) ω, segment z' —
                    from δ_0 = the junction to δ_m = [u_s·(u_e)^ω] = P(s, e)
```

**Theorem 4.2 (one discordance, one split).** The concatenated bit
sequence runs from the teacher's bit on the discordant lasso to the
belief's answer, so its endpoints differ; **one junction query** decides
which chain flips, and Lemma 4.1 splits one class — the frontier word
leaves the row's class — at `O(log(|w| + |𝒞_T|·|z|))` membership queries
in total (`n ≤ |w| + 2|𝒞_T|·|z|`, `m ≤ 2|𝒞_T|·|z|`). A stem flip mints a
linear column, a loop flip an ω-column; replacing a prefix *at the head
of the loop* and letting the ω-column's `(x, y)` format carry the rest
is the rotation lemma [SωS26, Lem 4.1] enacted — no search over
rotations is ever needed.

*Proof.* `γ_0 = [w'·z'^ω]` is the teacher's bit on the discordant lasso;
`γ_n = δ_0 = [u_s·z'^ω]` is the junction (the stem chain at `j = n`
replaces all of `w'` by `u_{⟨w'⟩} = u_s`, and the loop chain at `j = 0`
touches nothing); `δ_m = [u_s·(u_e)^ω]` is the belief's answer, the
cached `P(s, e)` (§3.2). The endpoints of the concatenation differ by
assumption, so one of the two chains has differing endpoints; the
junction query identifies it, and Lemma 4.1 supplies flip, mint, and
split. The cost is the junction query plus one binary search over `n`
resp. `m` positions, with the stated normalization bounds. ∎

*Example (two discordances, one wrong name, two shapes).* The running
examples' first *teacher-found* discordances — returned by the
alternation's first equivalence queries (§4.5), the bootstrap probes
already aligned — are `(ε, aab)` on `Even` and the shortlex-earlier
`(ε, b·aa)` on `EvenBlocks`; they carry the same failure: each lasso is named `(⟨a⟩, ⟨a⟩)`, i.e. answered through the
keyed lasso `a·a^ω`, and each is truly in its language. Normalization is
trivial in both (`k = 1`, so `w' = z'` is the loop itself), the stem key
is `u_s = a` in both, and the junction query routes them oppositely. On
`Even`, `[a·(aab)^ω] = 0` — the prepended `a` flips the parity — against
`γ_0 = [(aab)^ω] = 1`: the flip is in the **stem chain**, Table 3(a). On
`EvenBlocks`, `[a·(b·aa)^ω] = 1` — a prefix cannot harm a
prefix-independent language — equal to `γ_0`, so the stem chain is flat
and the flip is in the **loop chain**, Table 3(c). Both flips sit at
position `1 → 2` of their chains, but they convict different words: from
(a), the frontier word `u = u_{⟨a⟩}·a = aa` against the row
`v = u_{⟨aa⟩} = a`, minting the linear column `(ε, b, aab)`, entries `1`
for `aa` and `0` for `a` — the parity merge of day one, split; from (c),
the frontier word `u = u_{⟨b⟩}·a = b·a` against the row
`v = u_{⟨b·a⟩} = a`, minting the ω-column `(a, a)` — a rotated cousin of
the `(ε, b)` we exhibited in §3.1, found by the machinery rather than by
inspection. Tables 3(b) and 3(d) show the tables after the split. Two
lassos, one wrong name, Arnold's two shapes: discordance analysis is the
two-shape split of the congruence, run backwards.

*(a) `Even`, the stem chain `γ` — replace a growing stem prefix by its
key:*

| `i` | prefix | its key | queried lasso | `γ_i` |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `aab·(aab)^ω` | `1` |
| 1 | `a` | `a` | `a·ab·(aab)^ω` | `1` |
| 2 | `aa` | `a` | `a·b·(aab)^ω` | **`0`** |
| 3 | `aab` | `a` | `a·(aab)^ω` | `0` |

*(b) `Even`, after the stem split:*

| word | `(ε,ε)_ω` | **`(ε, b, aab)_lin`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `⟨a⟩` |
| `b` | `1` | **`1`** | `⟨b⟩` |
| **`aa`** | `0` | **`1`** | **`⟨aa⟩`** |
| *frontier:* | | | |
| `a·b` | `0` | **`0`** | → `⟨a⟩` ✗ still |
| `aa·b` | `1` | **`1`** | → `⟨b⟩` |

*(c) `EvenBlocks`, the loop chain `δ` — stem pinned to `u_s = a`, replace a
growing loop prefix by its key:*

| `i` | prefix | its key | queried lasso | `δ_i` |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `a·(b·aa)^ω` | `1` |
| 1 | `b` | `b` | `a·(b·aa)^ω` | `1` |
| 2 | `b·a` | `a` | `a·(a·a)^ω` | **`0`** |
| 3 | `b·aa` | `a` | `a·(a)^ω` | `0` |

*(d) `EvenBlocks`, after the loop split:*

| word | `(ε,ε)_ω` | **`(a, a)_ω`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `⟨a⟩` |
| `b` | `1` | **`0`** | `⟨b⟩` |
| **`b·a`** | `0` | **`1`** | **`⟨b·a⟩`** |

**Table 3.** The two first teacher-found discordances, processed (minted
column and promoted row in bold; `ε`-row and unchanged frontier
omitted). In both chains, row `i = 1` replaces a one-letter prefix by
its own key — a no-op, bit unchanged — and the flips sit at `1 → 2`. In
(a), row 3 is the junction `γ_3 = δ_0`, already `0`: the stem chain
flipped, minting a *linear* column. In (c) the junction is `1` and the
loop chain flips instead, minting an *ω-column*; note row 3's lasso is
`a·a^ω` — the keyed lasso of the name, i.e. the belief's answer, closing
the chain. (a) pulls `aa` out of `⟨a⟩`; (c) pulls `b·a` out — and in (b)
the doomed `a·b` still hides in `⟨a⟩`, which is §4.2's catch.
