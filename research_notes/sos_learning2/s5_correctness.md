## 5. Correctness and complexity

**Theorem 5.1 (legality).** At every equivalence query, the presented
object `𝓘_i` is a well-formed invariant: the syntactic invariant of its
belief language `K_i = L(𝓘_i)`, the unique language it denotes.

*Proof.* The loop reaches an equivalence query only with both checks
clean. Stamp legality makes the induced product well defined and `𝒮_T`
(restricted to `Σ⁺`) a stamp (Lemma 3.4) — surjective onto the non-identity
classes, `[ε]` the permanent singleton. `P` is total on the linked pairs of
that product by construction, so `⟨𝒮_T, P⟩` is an invariant
([SωS26, Def 3.3]); pair legality is precisely saturation, so it is
well-formed ([SωS26, Def 4.2]). Canonicalization carries a well-formed
invariant onto the syntactic invariant of its own language, preserving that
language ([SωS26, Thm II]), and a well-formed invariant denotes exactly one
language, its own ([SωS26, Prop 4.1]). ∎

**Theorem 5.2 (no false assent; the limit is `𝓘(L)`).** The loop terminates
after at most `N` class splits and at most `N + V` equivalence queries,
`V` the number of grounding events — a speculative word verified, each of
its cells at most once (§3.1), so `V` is finite and `V = 0` on a run whose
proxies are all truthful. An exact equivalence oracle assents *iff*
`K_i = L`; when it assents, the belief is exactly `𝓘(L)` — byte-equal,
under shortlex keys, to the output of the construction of [SωS26],
whatever automaton the teacher held.

*Proof.* *Progress.* Every mechanism that keeps a round going splits a
class or permanently grounds speculation: a promotion introduces a
verified frontier word differing from every row on some column, a
consistency mint separates the violating pair on real bits at the minted
column, a stamp escalation (Lemma 4.4), a pair escalation (Lemma 4.5), and
a harvest (Theorem 4.3) each split a class — or, when the convicted word
was speculative, ground it: its corrected bits re-merge it elsewhere,
witnessed at the minted column, and a grounded cell never speculates
again. Every split's witness is an Arnold context separating two concrete
queried words, so distinct classes are `≈_L`-distinct at all times, and
`|𝒞_T| ≤ N` bounds the splits; grounding events are bounded by the cells,
each grounded once. Each equivalence query either assents or funds a
harvest event, so at most `N + V` are posed. *No false assent.* By Theorem 5.1 the presented belief denotes
exactly `K_i`; two ω-regular languages agreeing on all lassos are equal
(§2.2), so an exact oracle assents iff `K_i = L`. *Canonicity.* When it
assents, the belief — the syntactic invariant of `K_i` (Theorem 5.1) — is
the syntactic invariant of `L`; byte equality is canonicity plus shortlex
keying [SωS26, Thm I]. ∎

The theorem earns the paper's title with an argument whose weight sits
entirely in the typing discipline: nothing about the *language* forces a
learner's fixpoint to be canonical — §6 exhibits certified non-canonical
fixpoints — it is the legality of the belief that pins every certified
fixpoint to the syntactic object. Note also the division of labor: the
*discipline* (the learner's own work, query-free checks and cheap
escalations) delivers "the belief is always some language's canonical
algebra"; the *oracle's exactness* is consumed only by the last step, the
identification `K_i = L`. Under a bounded oracle the belief is still a
well-formed invariant — still the syntactic algebra of a genuine ω-regular
language, one that agrees with `L` on everything the oracle checked — and
every split still witnesses a genuine `≈_L`-separation; only the
coincidence with `𝓘(L)` is certified no further than the oracle checked.

**Proposition 5.3 (query complexity).** Recall `N` — the class count of the
canonical target, identity included (§2.2) — write `ℓ` for the longest
counterexample returned, and `k ≤ |Σ|` for the number of letter classes of
the target. The learner poses at most `N + V` equivalence queries
(Theorem 5.2) and `O(N²·|Σ| + N·log(N·ℓ))` membership queries — the entry
term `O(N²·k + N·|Σ|)` when every proxy is truthful — itemized by
mechanism:

- *table entries* — `O(N·k + |Σ| + V)` queried table words: at most `N`
  rows, each with its `k`-rep frontier, the letters themselves, and one
  grounding per verified cell (the collapse, §3.1) — never more than the
  `O(N·|Σ|)` full frontier, since a cell is queried or grounded at most
  once — against `O(N)` columns (one initial; every other column is minted
  by an event that also splits a class or grounds a word, so at most one
  per such event);
- *per harvest split* (at most one per equivalence query) — one junction
  query and one binary search over a chain of length
  `|w'| + |z'| = O(N·ℓ)` (the normalization power is at most `2N`), so
  `O(log(N·ℓ))` queries;
- *per stamp escalation* — two probe queries and at most one frozen-prefix
  binary search over the segment `r·u`, of length `O(N)` since keys and
  table words are access words of length `O(N)` (Definition 3.2), so
  `O(log N)` queries;
- *per pair escalation* — one query on the rotated lasso and one chain over
  key-built words of length `O(N²)`, so `O(log N)` queries (Lemma 4.5);
- *the `P`-cache* — one membership query per linked pair of the final
  table, at most `N²`, memoized by lasso across rounds and absorbed by the
  entry term.

All queried words have length polynomial in `N`, `ℓ`, and the column
lengths — themselves harvested substrings of counterexamples, or
`O(N)`-long segments contributed by escalations. Output-polynomial in the
canonical target `N` is the honest yardstick — `N` can be exponentially
larger than a smallest acceptor (Proposition 5.4 makes both directions of
the size comparison exact), and §7 measures exactly that.

The two counts trade against each other through `V`: a proxy that is wrong
costs its grounding and possibly the equivalence query that pointed at it,
a proxy that is right costs nothing at all — `k/|Σ|` is the entry factor a
run earns on the languages whose letters genuinely collapse. §7 measures
both sides on the corpus.

The converse of the yardstick is the selling point: on languages with
trivial or near-trivial right congruence — `EvenBlocks`, `FG(a ∨ Xa)`
[AF21], and generically tail properties — the right-congruence-seeded part
of any FDFA degenerates while nothing here does, because nothing here is
seeded by the right congruence: the ω-columns query the loop structure
directly. The historical arc makes the point structural: [MP95] is exactly
the fragment where the right congruence is the whole story, and every
extension since has been a workaround for its failure — this one replaces
the seed rather than patching it.

The size relationship between the two kinds of target can be settled
exactly rather than empirically, and it cuts one way:

**Proposition 5.4 (sizes cut one way).** (a) Every canonical FDFA of `L` —
periodic, syntactic, or recurrent [AF16] — has at most `N + N²` states.
(b) The converse fails exponentially: for every `n` there is a co-safety
`L_n` over a fixed five-letter alphabet with a deterministic acceptor of
`n + 2` states, a recurrent FDFA of size `O(n)` and a syntactic FDFA of
size `O(n²)`, but `N ≥ (n+1)^n`.

*Proof.* (a) `≈_L` refines every congruence an FDFA is built from. Leading:
`u ≈_L v` gives agreement under every continuation `y·t^ω` (the linear
shape at `x = ε`), and residual languages are ω-regular, hence determined
by their lassos [PP04] — so `u ~_L v`, and the leading automaton has at
most `N` states. Progress, at a leading class `[u]`: if `v ≈_L v'` then
`vw ≈_L v'w` for every `w`, and the ω-power shape at `x = u`, `y = ε` gives
`u·(vw)^ω ∈ L ⟺ u·(v'w)^ω ∈ L` — exactly the periodic progress congruence;
the syntactic and recurrent congruences add only clauses of the forms
`uv ~_L uv'` and `uvw ~_L u`, which `≈_L`-equal words satisfy equally. So
each progress automaton has at most `N` states, and there is one per
leading state. (b) Take four letters acting on `{1, …, n}` and generating
the monoid `PT_n` of all partial transformations (two generate the
permutations, one lowers rank, one restricts the domain — a standard
generating set; undefined images go to a rejecting sink `⊥`), plus a letter
`c` sending state `1` to an accepting sink `⊤` and every other state to
`⊥`; let `L_n` be "the run reaches `⊤`" — a run *commits* when it does, is
*doomed* at `⊥`, and is *uncommitted* otherwise. Distinct partial maps
`f ≠ g` are `≈_{L_n}`-inequivalent: pick `q` with `f(q) ≠ g(q)`, reach `q`
from `1` by a permutation word `x` (action letters never touch `⊤`, so
nothing commits en route), and append a permutation `π` carrying `f(q)` to
`1`, then `c`: the linear context `x·_·π·c·(c)^ω` accepts through `f` and
rejects through `g`. Hence `N ≥ |PT_n| = (n+1)^n`. For the FDFAs, the
leading congruence has `n + 2` classes (the current state, or committed, or
doomed), and for a co-safety language the progress clauses *collapse*: if
`u` is uncommitted and `uvw ~_L u`, the loop returned to `u`'s state
without ever committing, so `u·(vw)^ω ∉ L` — the ω-clause is constantly
false. The recurrent conjunction is therefore constant on every leading
class (false on uncommitted and doomed, true on committed), giving `O(1)`
progress states each; the syntactic congruence reduces to its `uv ~_L uv'`
clause, giving at most `n + 2` each. ∎

Read as economics, Proposition 5.4 settles the size question in both
directions: an FDFA never pays more than a quadratic premium over the
algebra, while the algebra can cost exponentially more than any acceptor —
on `L_n`, an FDFA learner spends queries polynomial in `n` where ours
spends queries polynomial in `(n+1)^n`. That is not an inefficiency to
engineer away; it is the price of the deliverable. The algebra `L_n` owns
*is* that large, every definability read-off consumes it, and any route to
it — learned here, constructed in [SωS26] — pays `N`. Output-polynomial in
`N` (Proposition 5.3) is the strongest guarantee compatible with delivering
the object.

*Remark (an FDFA is the invariant, sliced).* The proof of (a) is worth
reading structurally. The leading congruence is agreement under the
*linear* membership tests at the single slot `d = [ε]`, and each progress
congruence, at leading class `[u]`, is built from the tests read at the
single slot `d = 𝒮(u)` — the ω tests for the periodic flavor, with
per-flavor linear clauses added ([SωS26, Def 4.3]). A canonical FDFA is
thus the algebra's test data *sliced per slot*: canonical quotients of the
invariant, one per component, computable from it by table scans — with the
composition discarded, and with it the idempotents, power orbits, and
group content the read-offs consume. Recovering the invariant from the
family runs the other way only through a full reconstruction, at the
exponential price (b) makes exact. We suspect, without pursuing it here,
that the completeness of the canonical families [AF16] can itself be
reread this way — each flavor a scheme by which the per-slot slices
jointly exhaust the tests — and leave the question open.

*Example (the run, completed, on `Even`).* After §4.2's split the table is
Table 6, and the next round's checks and equivalence query are clean. The
whole run, Tables 1 → 3(b) → 6: five classes from **two splits — one per
source** (the stem chain split `aa` from `a`, the stamp escalation split
`a·b` from `a`) — on **three columns** (`(ε,ε)_ω` initial, `(ε, b, aab)_lin`
harvested, `(ε, ab, aab)_lin` escalated). The BFS re-keying returns
`ε, b, a, ab, aa`, and the exported product *is* Figure 2(b), edge for
edge — the same drawing, computed there from a deterministic automaton and
here from lasso queries alone: Theorem 5.2, performed. Two read-offs
complete the export (Table 8): the accepting pairs, and the aperiodicity
check.

*(a) linked pairs `(s, e)`, `e` ranging over the idempotents; cell = the
accept bit of `u_s·(u_e)^ω`, `–` = not linked (`s·e ≠ s`):*

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

**Table 8.** The learned `𝓘(Even)`'s two read-offs (classes written `[·]`:
the run is certified, so these are the syntactic classes). (a) Eight linked
pairs, three accepting — the whole `[b]` stem row: once the good prefix has
happened, every loop accepts; this is `P`. (b) Power iteration of every
class: a single orbit of period two, `[a] → [aa] → [a]` — the genuine
`Z₂` — so `Even` is **not** LTL-definable, read off the learned object in
four lines (the aperiodicity read-off, [SωS26, Thm 6.1]). Five classes is
exactly `N = 5`, and the exported invariant is byte-equal to the
construction from the automaton — the harness's final check.

The per-phase membership ledgers of the two runs ground Proposition 5.3's
itemization in the two small instances (`fill` — table entries; `harvest` —
junction and chain probes; `legality` — escalation probes and frozen
chains; `P` — the pair cache):

| run | fill | harvest | legality | `P`-cache | total | EQ | escalations | columns lin/ω |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `Even` | 32 | 4 | 7 | 8 | **51** | 2 | 1 | 2 / 1 |
| `EvenBlocks` | 67 | 4 | 14 | 14 | **99** | 2 | 2 | 0 / 4 |

Both runs finish on a *single* counterexample — every other split is an
escalation's, two-probe repairs in place of whole equivalence rounds — and
both exported invariants are byte-equal to the reference construction.
