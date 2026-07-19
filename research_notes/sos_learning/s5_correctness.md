## 5. Correctness and complexity

**Theorem 5.1 (saturated fixpoint = the syntactic ω-semigroup).** The loop
terminates after at most `N` class splits. At its fixpoint — closed,
consistent, left-saturated, equivalence granted — the kernel of `ψ` on `Σ⁺` is
exactly `≈_L`, the map `c ↦ [rep(c)]_{≈_L}` identifies `𝒞_T` with the classes
of the target, identity included, and the export

```
    c·c' := fold(c, rep(c')),    λ, P as maintained,
    keys: shortlex-least word reaching each class — a BFS on the fold automaton
```

is exactly the finite presentation `(𝒞, λ, ·, P)` of `𝓘(L)` — in particular
byte-equal to the output of any construction of it [SωS26, Thms I, III].

*Proof.* *Termination.* Every mechanism that keeps a round going adds a class:
a promotion introduces a frontier word differing from every row on some column,
a consistency minting separates the violating pair on the minted column, a
saturation escalation and a counterexample harvest each split a class
(Theorem 4.3, Lemma 4.5). Every such witness is an Arnold context separating
two concrete words, so distinct classes are `≈_L`-distinct at all times, and
`|𝒞_T| ≤ N` bounds the total.

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

*The export is an invariant, and it denotes `L`.* On `Σ⁺` the kernel is then
a two-sided congruence of finite index, so `ψ` restricted to the non-empty
words is a stamp `𝒮_T : Σ⁺ → 𝒞_T ∖ {[ε]}` [SωS26, Def 3.1] — surjective onto
the non-identity classes, `[ε]` being the permanent singleton — whose
multiplication is the exported table: `c·c' = fold(c, w_{c'}) = ψ(w_c·w_{c'})`,
folds composing over literal concatenation. The export `⟨𝒮_T, P⟩` is
therefore an invariant, and the prediction of §3 computes exactly its lasso
membership [SωS26, Def 3.4]: multiplicativity makes the fold orbit the power
sequence — `c_j = ψ(z^j) = ψ(z)^j` — so the stabilization test `c_{2k} = c_k`
reads `(ψ(z)^k)² = ψ(z)^k`: the orbit's stable value is the idempotent power
of `ψ(z)`, unique among its powers, and the predicting pair
`(ψ(w·z^k), c_k) = (𝒮_T(w)·e, e)` is Definition 3.4's queried name; the
cached bit is the teacher's verdict on a lasso bearing that name.
Equivalence granted, predictions agree with `L` on every lasso, through
every presentation: the export **denotes** `L` [SωS26, Def 4.1].

*Canonicity, by [SωS26, Cor 4.2].* An invariant denoting `L` has a kernel
refining `≈_L`, and carries the forced pair set — the names of the accepted
lassos, nothing else. Termination's witnesses give the reverse inclusion —
distinct classes are `≈_L`-distinct — so the kernel is exactly `≈_L`: `𝒮_T`
*is* the syntactic stamp, its pair set *is* `P(L)`, and the export is
`𝓘(L)`. The shortlex keys are recovered exactly because the fold is a
deterministic automaton: the shortlex-least word reaching class `c` under
BFS is the shortlex-least word of its `≈_L`-class. Byte equality with any
other construction of `𝓘(L)` is canonicity plus shortlex keying
[SωS26, Thm I]. ∎

The theorem earns the paper's title: nothing about the *language* forced the
fixpoint to be canonical — §4.2 exhibits the non-canonical stall — it is the
saturation rule, i.e. the rotation lemma's slot collapse, that pins the fixpoint
to the syntactic object. The step
*the export denotes `L`* consumes the equivalence oracle's exactness. Under
a bounded oracle the fixpoint is still a two-sided congruence (the sweep, not
the oracle, delivered left-invariance) and every split still witnesses a
genuine `≈_L`-separation, so the export is a well-defined finite algebra with
`≈_L`-distinct classes — but denotation of `L`, hence the coincidence with
`𝓘(L)` that [SωS26, Cor 4.2] extracts from it, is certified only as far as
the oracle checked.

The dual question — the fixpoint an exact oracle *did* certify, but the
sweep never touched — closes the unsaturated stall's account: such a
fixpoint is not merely short of the algebra; certified, it cannot carry an
algebra at all. The instrument is the sweep's own check, which turns out to
be a complete congruence test:

**Lemma 5.2 (the sweep check decides congruence).** On a closed, consistent
table, the kernel of `ψ` on `Σ*` — a right congruence by construction, being
the reachability kernel of the deterministic automaton `step` — is a
two-sided congruence iff the saturation sweep's check phase is clean:
`fold(d, u) = fold(d, w_{ψ(u)})` for every table word `u` and class `d`.

*Proof.* (⟸) Write `(S)` for the check's instances at frontier words:
`fold(d, w_c·a) = fold(d, w_{step(c,a)})` for all `d, c ∈ 𝒞_T`, `a ∈ Σ` — all
table words, so a clean check includes them. Induction on `|u|` extends the
check to every word, `fold(d, u) = fold(d, w_{ψ(u)})`: the base case is `(S)`
at `c = [ε]`, and the step is
`fold(d, u'·a) = step(fold(d, u'), a) = step(fold(d, w_{ψ(u')}), a)
= fold(d, w_{ψ(u')}·a) = fold(d, w_{ψ(u'·a)})`, the last equality by `(S)` at
`c = ψ(u')`. Left-invariance follows as in Theorem 5.1's proof; right-
invariance is automatic. (⟹) Two-sidedness makes
`fold(d, u) = ψ(w_d·u)` a function of `(d, ψ(u))`, and `ψ(u) = ψ(w_{ψ(u)})`
on table words is coherence (Lemma 3.3). ∎

(The forward direction is the claim inside Theorem 5.1's proof, extracted;
the lemma adds its converse, making the check a *classifier*: zero queries,
run on any fixpoint, saturated or not.)

**Theorem 5.3 (certified fixpoints: canonical or no algebra).** Let a
closed, consistent table's hypothesis be certified by an exact equivalence
oracle — its prediction agrees with `L` on every lasso. Then the following
are equivalent: (i) the kernel of `ψ` is a congruence (Lemma 5.2's check is
clean); (ii) the export of Theorem 5.1 is exactly `𝓘(L)`, byte-equal after
re-keying. In particular a certified *non-canonical* fixpoint — a permanent
stall — is never a congruence: its product `c·c' = fold(c, w_{c'})`
genuinely depends on the choice of representatives, and no operation on its
classes recognizes anything. What the ablation of §6.3 delivers is the
Cayley hypothesis itself — a correct acceptor — and, provably, nothing more.

*Proof.* (ii)⟹(i): `𝓘(L)`'s classes form a monoid. (i)⟹(ii): Theorem 5.1's
last two steps consume exactly these hypotheses and nothing else. With the
kernel a congruence — (i), via Lemma 5.2 — the export is an invariant whose
lasso membership is the hypothesis's prediction, and the certification makes
it denote `L`; [SωS26, Cor 4.2] then forces the kernel to refine `≈_L` and
the pair set to be the names of `L`'s accepted lassos. Every split —
promotion, consistency mint, harvest — was witnessed by an Arnold context
(saturation escalations, absent here, were only ever one more witnessed
mechanism), so `≈_L` refines the kernel; the two inclusions pin the kernel
to `≈_L`, and the export is `𝓘(L)` — byte-equal after re-keying (with (i),
`mult` by letter classes *is* `step`, so the two BFS orders coincide, and
`P` — teacher bits on representative lassos — is the forced pair set). *In
particular*: by (i)⟹(ii), a certified fixpoint whose kernel were a
congruence would be canonical; a certified stall is non-canonical, so its
kernel is no congruence, its product depends on representatives, and no
operation on its classes recognizes anything. ∎

Note the asymmetry the exactness buys: under a bounded oracle a congruent
unsaturated fixpoint may still be a genuine algebra strictly coarser than
the syntactic quotient — a correct-so-far quotient the oracle was too weak
to refute. Exactness closes that door: congruent and certified *forces*
canonical — [SωS26, Cor 4.2]'s *nowhere else*, met from below — so
the two-sided/one-sided divide of §4.2 is also the algebra/no-algebra
divide. Proposition 4.4's non-associative display is Theorem 5.3 made
concrete on the smallest specimen — the display shows *how* the product
breaks; the theorem says it always does.

*Example (the run, completed, on `Even`).* After §4.3's split the table is
Table 6, and the next sweep and equivalence query are clean. The whole run,
Tables 1 → 3(b) → 6: five classes from **two splits — one per mechanism** (the
stem chain split `aa` from `a`, the saturation escalation split `a·b` from
`a`) — on **three columns** (`(ε,ε)_ω` initial, `(ε, b, aab)_lin` harvested,
`(ε, ab, aab)_lin` saturated). The BFS re-keying returns
`ε, b, a, ab, aa`, and the exported table `c·c' = fold(c, w_{c'})` is

```
  ·      [ε]  [b]  [a]  [ab]  [aa]
  [ε]     0    1    2    3     4
  [b]     1    1    1    1     1
  [a]     2    3    4    1     2
  [ab]    3    3    3    3     3
  [aa]    4    1    2    3     4
```

— cell for cell the syntactic table of [SωS26], computed there from a
deterministic automaton and here from lasso queries alone: Theorem 5.1,
performed. Two read-offs complete the export (Table 7): the accepting pairs,
and the aperiodicity check.

*(a) linked pairs `(s, e)`, `e` ranging over the idempotents; cell = the
accept bit of `w_s·(w_e)^ω`, `–` = not linked (`s·e ≠ s`):*

| `s` \ `e` | `[b]` | `[ab]` | `[aa]` |
|---|:--:|:--:|:--:|
| `[b]` | **1** | **1** | **1** |
| `[a]` | – | – | `0` |
| `[ab]` | `0` | `0` | `0` |
| `[aa]` | – | – | `0` |

*(b) power orbits `c, c², c³, …`:*

| `c` | `c²` | `c³` | eventual period |
|---|:--:|:--:|:--:|
| `[b]` | `[b]` | `[b]` | 1 |
| `[a]` | `[aa]` | `[a]` | **2** |
| `[ab]` | `[ab]` | `[ab]` | 1 |
| `[aa]` | `[aa]` | `[aa]` | 1 |

**Table 7.** The learned `𝓘(Even)`'s two read-offs. (a) Eight linked pairs,
three accepting — the whole `[b]` stem row: once the good prefix has
happened, every loop accepts; this is `P`. (b) Power iteration of every
class: a single orbit of period two, `[a] → [aa] → [a]` — the genuine `Z₂` —
so `Even` is **not** LTL-definable, read off the learned object in four
lines (the aperiodicity read-off, [SωS26, Thm 6.1]). Five classes is exactly
`N = 5`, and the exported invariant is byte-equal to the construction from
the automaton — the harness's final check.

`EvenBlocks` completes the same way, and entirely in the ω-sort: beyond the
counterexample traced in §4.1, two saturation escalations carry the table
from four to its eight classes — keys
`ε, b, a, b·a, a·b, a·a, b·a·b, a·b·a`, the count and keys fixed by the
reference invariant. Table 8 is the run as a split ledger, one row per event,
from the implementation's transcript — deterministic under the pinned scan
and minimal-counterexample policies, and reproducing §4.1's row exactly. One
reading note: a single sweep mint can split more than one class once the
table re-stabilizes — rows 2 and 3 each split two.

| # | trigger | chain | minted column | splits | `\|𝒞_T\|` after |
|:--:|---|---|---|---|:--:|
| 1 | EQ: `(ε, b·aa)` | loop | `(a, a)_ω` | `b·a` out of `[a]` | 4 |
| 2 | sweep escalation | frozen | `(a, b·a)_ω` | `aa` out of `[a]`; `a·b` out of `[b·a]` | 6 |
| 3 | sweep escalation | frozen | `(ε, b)_ω` | `a·b·a` out of `[b]`; `b·a·b` out of `[aa]` | 8 |

**Table 8.** The `EvenBlocks` run as a split ledger: trigger (equivalence
counterexample or sweep escalation), the chain that processed it, the minted
column, the words separated. The day-one sweep is clean — every fold check
on Table 2's three-class table agrees, the computation Table 4 spells out
for `Even` — so row 1, §4.1's split, is the run's first event; rows 2–3 are the sweep
enforcing two-sidedness — no second counterexample is ever needed, and the
run's second equivalence query certifies. Every one of the four columns is
of the ω-sort: prefix-independence in action (the linear shape is blind —
Proposition 4.6 — so every separation lives in the loop). The final sweep mints `(ε, b)` — the very
column §3 exhibited by inspection. The resulting bit-signatures are the
fixpoint (the Table 6 analogue), pairwise distinct — with `[ε]`, the `N = 8`
classes of `𝓘(EvenBlocks)`:

| word | `(ε,ε)_ω` | `(a,a)_ω` | `(a,b·a)_ω` | `(ε,b)_ω` |
|---|:--:|:--:|:--:|:--:|
| `b` | `1` | `0` | `0` | `1` |
| `a` | `0` | `0` | `1` | `0` |
| `b·a` | `0` | `1` | `0` | `0` |
| `a·b` | `0` | `1` | `1` | `0` |
| `a·a` | `0` | `0` | `0` | `1` |
| `b·a·b` | `0` | `0` | `0` | `0` |
| `a·b·a` | `1` | `0` | `0` | `0` |

The per-phase membership ledgers of the two runs ground Proposition 5.4's
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

**Proposition 5.4 (query complexity).** Recall `N` — the class count of the
canonical target, identity included (§2.2) — and write `ℓ` for the
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
smallest acceptor (Proposition 5.5 makes both directions of the size
comparison exact), and §6 measures exactly that.

The converse of the yardstick is the selling point: on languages with trivial or
near-trivial right congruence — `EvenBlocks`, `FG(a ∨ Xa)` [AF21], and
generically tail properties — the right-congruence-seeded part of any FDFA
degenerates while nothing here does, because nothing here is seeded by the right
congruence: the ω-columns query the loop structure directly. The historical arc
makes the point structural: [MP95] is exactly the fragment where the right
congruence is the whole story, and every extension since has been a workaround
for its failure — this one replaces the seed rather than patching it.

The size relationship between the two kinds of target can be settled exactly
rather than empirically, and it cuts one way:

**Proposition 5.5 (sizes cut one way).** (a) Every
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
lowers rank, one restricts the domain — a standard generating set; undefined
images go to a rejecting sink `⊥`), plus a letter `c` sending state `1` to an
accepting sink `⊤` and every other state to `⊥`; let `L_n` be "the run
reaches `⊤`" — a run *commits* when it does, is *doomed* at `⊥`, and is
*uncommitted* otherwise. Distinct
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

Read as economics, Proposition 5.5 settles the size question in both directions:
an FDFA never pays more than a quadratic premium over the algebra, while the
algebra can cost exponentially more than any acceptor — on `L_n`, an FDFA
learner spends queries polynomial in `n` where ours spends queries
polynomial in `(n+1)^n`. That is not an inefficiency to engineer away; it is
the price of the deliverable. The algebra `L_n` owns *is* that large, every
definability read-off consumes it, and any route to it — learned here,
constructed in [SωS26] — pays `N`. Output-polynomial in `N`
(Proposition 5.4) is the strongest guarantee compatible with delivering the
object. The unsaturated stall of §4.2, for its part, is not an isolated
artifact: Proposition 4.4's `a → Xa` is the smallest exhibit an exhaustive
census of one-atom automata can produce, and §6.3 measures the family at
census scale.
