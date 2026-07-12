# SoS Given-That — Implementation Specification

**Status (2026-07-12). Re-aimed.** The goal is **one operation**:

    simplify( 𝓘(¬φ), 𝓘(K) )  →  𝓘(B)
      with  ℒ(B) ∩ ℒ(K) = ℒ(¬φ) ∩ ℒ(K)      (legal: [DPT25] Thm 1)
      and   |𝒞(B)| ≤ min( |𝒞(¬φ)|, |𝒞(P_min)|, |𝒞(P_max)| )   (never a regression)

Two `.sos` files in, one **smaller** `.sos` file out. It is the
algebraic double of [DPT25]'s *Bounded-by-Minato*: they pick a simpler
Boolean *label* between per-transition bounds, we pick a smaller *table*
between language bounds. Everything in this spec either builds that
operation, measures it, or is explicitly decommissioned (§8).

| item | state |
|---|---|
| GT1: the interval object + endpoint decisions (§3) | **DONE** — `sosl/sosl/sos/giventhat/interval.py`, `conjugacy_classes` in `calculus.surgery`; gates green on fixture + 700-pair campaign. It is step 1–2 of the operation. |
| GT2: the ladder tests (§4) | **DONE** — `ladder.py`, `r_classes` in `calculus.surgery`; rung oracle 6 222/6 222. Re-scoped: the rungs are now **constraints and output metrics**, not the deliverable. |
| GT3: the bounded quotient engine (§5) | **SPECIFIED — the next milestone.** `quotient.py` + `stutter.py`. This is the exact primitive the operation searches with. |
| GT4: the simplifier and the tool (§6) | **SPECIFIED — the deliverable.** `simplify.py` + `__main__.py`. |
| GT5: the demonstration (§7) | SPECIFIED — small corpus pairs, the size table. |
| Decommissioned (§8) | stutter tier 2, band-minimal Wagner degree, the W-series campaigns. Do not build. |

An implementer starting cold reads: this header, §0–§2, then the section
for the milestone at hand, then §9 (expected failures) and §10 (traps)
before writing any code.

**Normative math.** `research_notes/sos_giventhat.md` (restructured
2026-07-12). Section map: paper §3 → GT1; paper §5.2 → GT2; **paper §4
(Prop 4.1, Prop 4.2, Prop 4.3, Thm 4.4) → GT3**; **paper §4.6 + §5.1 +
Lemma 5.2 → GT4**; paper §6–§7 → GT5. Where this document and the paper
disagree, STOP and report (§11) — do not reconcile silently.

**Layering law (hard).** `sosl.sos.giventhat` imports `sosl.sos`
(objects, io), `sosl.sos.calculus` (Table, align, materialize, surgery,
decide, reduce, witness) and `sosl.sos.classify` (the stutter read-off,
the `primitives` toolkit) — and NOTHING else in the repo. Never
`sosl.learn`, `sosl.teacher`, `sosl.experiment`, `tests.*`. Test scripts
under `sosl/tests/giventhat/` may import anything.

**The two sentences to keep in your head.**

1. *Paper Prop 3.1.* On the materialized product table,
   `P_max \ P_min = P_K^c`, and the legal `B`s are exactly
   `P_min ⊔ (a union of conjugacy classes of linked pairs outside P_K)`.
   Runs as an always-on assertion; if it fires the bug is upstream
   (align / materialize / saturate).
2. *Paper Prop 4.2.* For **any** congruence `π` of the table,
   `hull_π(Q) := π⁻¹(sat_{T/π}(forced_π(Q)))` is the least
   `π`-recognizable superset of `Q`; hence the interval contains a `B`
   recognized by `T/π` **iff** `hull_π(P_min) ⊆ P_max`. This one test,
   run inside a greedy, is the whole engine.

---

## 0. Prerequisites (all DONE, all reused, none reimplemented)

From `sosl.sos.calculus`:

- `Table` — `(𝒞, λ, M)` + memoized `fold` / `idem` / `linked` / keys +
  `val(P)`. Pair sets are immutable sets of linked-pair ids.
- **`Table.of_raw(alphabet, identity, letter_class, mult)`** — a table
  from a raw algebra in any numbering: restricts to the reachable part
  and **re-keys by the shared shortlex BFS**, returning `(table, remap)`.
  This *is* how you build a quotient table. There is no second BFS to
  write (trap #13).
- `align(A, B) -> Aligned`, `materialize(aligned, A, B) -> Product` —
  the product table carrying **both** pair sets (`pairs_a`, `pairs_b`).
  Given-that operates on the *materialized* product (trap #2).
- `surgery`: `complement / union / intersection / difference`,
  `saturate` (with the mandatory `linked_pair_of` renormalization),
  `is_saturated`, `conjugacy_classes`, `r_classes`, `safety_closure`,
  `interior`, `is_safety`, `is_cosafety`, `is_obligation`, `live`.
- `decide`: `member / is_empty / is_universal / included / equivalent /
  intersecting_word` — witness-carrying, minimal-lasso.
- `reduce(table, P, check=…) -> Invariant` — the canonical re-quotient.
  **`reduce` is also how you obtain a congruence**: its `_blocks` is the
  syntactic congruence of `L(P)` on `T` (see §5.4 — promote it, do not
  re-derive it).
- `witness.Witness` with `replay(oracle)`.

From `sosl.sos.classify`: `is_stutter_invariant(inv)`.
From `sosl.sos.io`: `load_invariant` / `dump_invariant` (the tool's I/O;
never hand-parse `.sos`).

Corpus: `genaut/corpus/flat_canon/` — canonical `.sos` + paired det HOA
+ `.cat` sidecars. Sample pairs WITHIN one alphabet stratum (calculus
spec §8.2) — `align` asserts equal alphabets (trap #1).

---

## 1. Package shape

```
sosl/sosl/sos/giventhat/
    __init__.py    re-exports only (house rule; docs live in README.md)
    interval.py    GT1 (DONE): Interval, given_that, endpoints, choose
    ladder.py      GT2 (DONE): rung tests, forced, rec_hull, read-offs
    quotient.py    GT3: Quotient, congruence, forced, hull, admits,
                   least_member / greatest_member, is_recognized
    stutter.py     GT3: stutter_seeds, sc, exists_stutter_invariant (YES/UNKNOWN)
    simplify.py    GT4: the greedy driver — THE OPERATION
    __main__.py    GT4: the CLI (thin: argv, load, call, print, dump)

sosl/tests/giventhat/
    fixtures.py        the two fixture DELAs (DONE)
    interval_gate.py   GT1 (DONE)
    ladder_gate.py     GT2 (DONE)
    quotient_gate.py   GT3
    simplify_gate.py   GT4
    gt5_demo.py        GT5 campaign
    logs/              working logs (never /tmp)
```

Type-annotate every public signature (params + return) — house rule.

---

## 2. Objects

**`Quotient`** (frozen dataclass, `quotient.py`):

```
@dataclass(frozen=True)
class Quotient:
    table: Table                  # T/π, canonically keyed by Table.of_raw
    pi: Tuple[int, ...]           # T-class id -> T/π-class id
    source: Table                 # T (the congruence's domain)
    @property
    def n(self) -> int: ...       # len(T/π classes) — the greedy's score
```

Invariants asserted at construction: `pi[T.identity] == quot.table.identity`
and that block is a **singleton** (trap #8); `pi` is a monoid morphism
(`pi[M(c,d)] == M_q(pi[c], pi[d])` — gate-side, `O(n²)`, not in the hot
loop); `pi` is surjective.

**`Simplification`** (frozen dataclass, `simplify.py`): see §6.4.

---

## 3. GT1 — the interval (DONE, unchanged)

`given_that(neg_phi, k) -> Interval` with fields `table, p_neg_phi, p_k,
p_min, p_max, freedom`, `bits = len(freedom)`; `k_settles_phi` /
`k_refutes_phi` (the latter as emptiness of a complement — **no separate
universality scan**, trap #4); `choose` / `decompose`. Prop 3.1 asserted
on every construction. Gates in `interval_gate.py`.

In the operation this is steps 1–2 (paper §4.6). Nothing changes.

---

## 4. GT2 — the ladder (DONE, re-scoped)

`exists_safety / exists_cosafety / exists_obligation / exists_recurrence
/ exists_persistence(iv) -> (bool, member, refusal)`, `forced`,
`h_below`, `is_recurrence` / `is_persistence`, `rec_hull`. Gates in
`ladder_gate.py`.

**Re-scope (2026-07-12).** These are no longer the deliverable. They are:

- **output metrics** — `simplify` reports the Manna–Pnueli rung of `¬φ`
  and of the emitted `B`; a strict drop is a headline (§7);
- **optional constraints** — via paper Lemma 5.2 (composition), the
  least `B` that is *both* `π`-recognizable *and* on a given rung is the
  joint fixpoint of `hull_π` alternated with that rung's closure. §6.5
  specifies the constrained mode. Do not build new hulls: alternate the
  existing ones.

A `rung_of(table, pairs) -> str` helper (safety / cosafety / obligation
/ recurrence / persistence / above) belongs in `ladder.py` — it is the
one addition GT2 takes, and it is a pure read-off composition of the
existing predicates.

---

## 5. GT3 — the bounded quotient engine (THE EXACT PRIMITIVE)

Normative math: paper §4.2–§4.4 (Prop 4.1, Prop 4.2, Prop 4.3) and
§5.3 (Prop 5.6, Thm 5.7).

### 5.1 `congruence(table, seeds) -> Quotient`

The least monoid congruence identifying every seed pair
`(x, y) ∈ seeds`.

- Union-find over `table.n` classes. Worklist of merged pairs; on
  merging `x ∼ y`, enqueue `(M(g,x), M(g,y))` and `(M(x,g), M(y,g))` for
  every **letter class** `g ∈ set(table.letter_class)`. Drain to
  fixpoint.
- *Letters suffice* — every class is a product of letters, so
  single-letter two-sided stability propagates by induction (the same
  argument `reduce._blocks` step 2 already runs). Closing over all
  classes is also correct but quadratically wasteful; the `O(n²)`
  full-congruence check lives in the gate, not the loop.
- `[ε]` can never merge: it is adjoined, so no product of non-identity
  classes returns to it, and the seeds are non-identity. **Assert it; do
  not special-case it** (trap #8).
- Build the quotient table with `Table.of_raw(table.alphabet,
  block_of[identity], [block_of[lc] for lc in letter_class],
  block_mult)` — this re-keys by the shared shortlex BFS and returns the
  `remap`; compose `block_of` with `remap` to get `pi`. **No new BFS.**

Cost `O(n·|Σ|·α(n))` per seed batch.

### 5.2 The hull, the test, the members

```
pullback(quot, pairs_q) -> PairSet        # on T
    { (s,e) in source.linked : quot.table.val(pairs_q, pi[s], pi[e]) }

forced(quot, table, q) -> PairSet         # on T/π
    for each cell (c, d) of table with table.val(q, c, d):
        insert linked_pair_of(quot.table, pi[c], pi[d])
    # linked_pair_of renormalizes through the QUOTIENT's idempotent —
    # inserting the raw image pair is unsound (trap #3)

hull(quot, table, q) -> PairSet           # on T
    pullback(quot, saturate(quot.table, forced(quot, table, q)))
    # saturate on the QUOTIENT, then pull back. Pulling back first and
    # saturating on T is a different, wrong set (trap #15)

admits(quot, iv) -> bool
    hull(quot, iv.table, iv.p_min) <= iv.p_max            # paper Prop 4.2

least_member(quot, iv)    -> PairSet   = hull(quot, iv.table, iv.p_min)
greatest_member(quot, iv) -> PairSet   = complement(hull(quot, iv.table,
                                                    complement(iv.p_max)))

is_recognized(quot, table, pairs) -> bool     # gate-side
    pairs == pullback(quot, image of pairs under pi)
```

### 5.3 Stutter invariance is one seed set (`stutter.py`, thin)

- `stutter_seeds(table) -> [(M(la, la), la) for la in set(letter_class)]`
- `sc(table, q) = hull(congruence(table, stutter_seeds(table)), table, q)`
  — paper Prop 5.6's `sc`, recovered as the instance.
- `exists_stutter_invariant(iv) -> (Verdict, Optional[PairSet])` with
  `Verdict ∈ {YES, UNKNOWN}` — **never NO** (paper Thm 5.7: the hull can
  escape the table; trap #11). On YES the witness is `least_member`.

Paper §5.4's AP shedding is the same engine under seeds
`λ(ℓ) ∼ λ(ℓ')`. Not commissioned; the API must not foreclose it.

### 5.4 The syntactic congruence as a seed (needed by §6.2)

`reduce._blocks(table, pairs)` already computes the syntactic congruence
of `L(pairs)` on `table`. Promote it to a public
`syntactic_congruence(table, pairs) -> Quotient` in `calculus.reduce`
(the **one** commissioned cross-package addition of GT3; nothing else
moves in `calculus`), returning a `Quotient` rather than a block dict.
Assert `quot.n == len(𝒞(reduce(table, pairs)))` — the two must agree,
and that assertion is paper Prop 4.1 running at runtime.

### 5.5 GT3 gates (`quotient_gate.py`)

1. **Congruence law.** `pi` is a morphism on **all** class pairs
   (`O(n²)`) — this checks the letters-suffice induction actually held.
   `[ε]`'s block is a singleton.
2. **Closure-operator laws for `hull`.** Extensive (`q ⊆ hull(q)`),
   monotone, idempotent, output saturated, output `is_recognized`.
3. **The bounded oracle — this is what makes Prop 4.2 testable.** On
   cases with `bits ≤ 12`: enumerate all `2^F` members of the interval
   (`choose` over the freedom classes), keep those with
   `is_recognized(quot, ·)`, and check
   (a) the kept set is nonempty **iff** `admits(quot, iv)`;
   (b) when nonempty, `least_member` == their intersection and
       `greatest_member` == their union.
   Exact agreement required. A disagreement convicts Prop 4.2 (or the
   code) — a **To theory** event, not a patch. Cap at 12; never raise it
   (trap #6).
4. **Prop 4.1 at runtime.** For sampled saturated `q`:
   `syntactic_congruence(table, q).n == |𝒞(reduce(table, q))|`, and `q`
   is recognized by it.
5. **Stutter instance.** `is_stutter_invariant(reduce(sc(q)))` always;
   `sc(q) == q` iff `is_stutter_invariant(reduce(q))` on sampled
   saturated `q`.
6. **Fixture (E2 — paper Thm 5.7's counterexample).** On the §3.5
   fixture pair: the stutter quotient collapses to `{[ε], Z}`
   (**assert `quot.n == 2`**), `sc(p_min) == table.linked` (assert
   universal), and `exists_stutter_invariant` returns **UNKNOWN**.
   Thm 5.7, executed as a regression.

**GT3 acceptance:** gates 1–6 green on the fixture and on a small
same-stratum corpus sample; the `bits ≤ 12` oracle exact on every probed
case.

---

## 6. GT4 — the simplifier and the tool (THE DELIVERABLE)

Normative math: paper §4.6 (the algorithm), §4.1 (the objective and the
three reference points), Lemma 5.2 (composition).

**Honesty rule, enforced in review.** Exact minimization is conjectured
NP-hard (paper Conj 4.5). The greedy is a **heuristic with an exact test
inside it**. Its output is `|𝒞|` *achieved*, never `|𝒞|` *minimal*.
Claiming minimality in code, docstring, report or paper is a reject.

### 6.1 The three reference points (compute them first, always)

- `|𝒞(¬φ)|` — the input. `P_{¬φ}` is in the interval, so identity is a
  legal answer.
- `|𝒞(L(P_min))|`, `|𝒞(L(P_max))|` — [DPT25]'s `min|K` / `max|K`. Legal
  members too, and usually *larger* than the input.

`simplify` must never emit anything worse than the best of these three
(§6.4 step 4 enforces it by construction).

### 6.2 The greedy (`simplify.py`)

```
simplify(iv, opts) -> Simplification

1. endpoints (GT1):
     k_settles_phi(iv) -> SETTLED, witness, no B
     k_refutes_phi(iv) -> REFUTED, witness, no B

2. seeds := [ syntactic_congruence(iv.table, iv.p_neg_phi),   # π_¬φ
              congruence(iv.table, []),                        # identity
              congruence(iv.table, stutter_seeds(iv.table)) ]  # if opts.stutter
   # π_¬φ is ALWAYS admissible: P_¬φ is π_¬φ-recognizable and in the
   # interval, so hull ⊆ P_¬φ ⊆ P_max. Seeding there is what makes the
   # never-regress contract free (paper §4.6). ASSERT its admissibility.

3. for each admissible seed π₀:
       π := π₀
       loop:
           cands := { close(π, merge(b, b')) : b ≠ b' non-identity blocks of π }
           good  := [ π' in cands if admits(π', iv) ]
           if not good: break
           π := argmin over good of (π'.n, key-order of the merged blocks)
       record least_member(π, iv) and greatest_member(π, iv)

4. B := argmin over { all recorded members } ∪ { P_¬φ, P_min, P_max }
        of |𝒞(reduce(iv.table, ·, check=False))|
   (ties: prefer relax over restrict, then the earlier seed — deterministic)

5. assert intersection(B, iv.p_k) == iv.p_min          # §6.3
   return Simplification(..., invariant=reduce(iv.table, B, check=True))
```

Merging *in the current quotient* and composing the maps is equivalent
to re-closing from `T` (a congruence of `T/π` is a congruence of `T`
coarser than `π`) and is how it must be implemented — do not re-close
from `T` every round.

Determinism is mandatory: candidate blocks are enumerated in the
discipline order of their least representative's key.

### 6.3 The soundness law (always on)

[DPT25] Thm 1, on the table, is a **set identity**:

    intersection(B, P_K) == P_min        ⟺        P_min ⊆ B ⊆ P_max

Asserted on every emission. Cross-checked once per case on a *different
decision path*: `equivalent(align(reduce(B ∩ P_K), reduce(P_min)))` —
languages, not pair sets. A failure is a hard stop (upstream bug), never
a workaround.

### 6.4 `Simplification` (frozen dataclass)

```
verdict:   "SETTLED" | "REFUTED" | "SIMPLIFIED"
witness:   Optional[Witness]        # on SETTLED / REFUTED
b:         Optional[PairSet]        # on SIMPLIFIED
invariant: Optional[Invariant]      # reduce(b) — what gets dumped
side:      Optional[str]            # "relax" | "restrict" | "reference"
seed:      Optional[str]            # "syntactic" | "identity" | "stutter"
bits:      int                      # |F|
classes:   Dict[str, int]           # neg_phi, k, table, p_min, p_max, b
rung:      Tuple[str, str]          # rung of ¬φ, rung of B
stutter:   Tuple[bool, bool]        # stutter-invariance of ¬φ, of B
stutter_verdict: str                # "YES" | "UNKNOWN" (paper §5.3)
```

### 6.5 Constrained mode (paper Lemma 5.2)

`opts.require ∈ {None, "safety", "cosafety", "obligation", "recurrence",
"persistence", "stutter"}`. When set, the admissibility test in step 3
uses the **joint** closure: alternate `hull_π` with that rung's existing
closure operator (`safety_closure`, `rec_hull`, the R-class forcing …)
to a fixpoint, then compare to `P_max`. At most `|linked|` rounds
(Lemma 5.2). Build no new hull — alternate the ones GT2 already has.

### 6.6 The tool (`__main__.py`, thin)

    python3 -m sosl.sos.giventhat NEG_PHI.sos K.sos [-o B.sos]
            [--stutter] [--require RUNG] [--json REPORT.json]

Loads with `load_invariant`, dumps with `dump_invariant`, prints:

| row | meaning |
|---|---|
| `¬φ` | `\|𝒞(𝓘(¬φ))\|` — the input |
| `K` | `\|𝒞(𝓘(K))\|` |
| `T` | `\|𝒞\|` of the materialized product |
| `P_min` / `P_max` | `\|𝒞(reduce(·))\|` — **the [DPT25] reference points** |
| **`B`** | `\|𝒞(reduce(B))\|` — **must beat all of the above to count** |
| `bits` | `\|F\|`, the freedom searched |
| rung | Manna–Pnueli class of `¬φ` → of `B` |
| stutter | stutter bit of `¬φ` → of `B` (+ YES/UNKNOWN) |

On `SETTLED` / `REFUTED` it prints the verdict and the minimal witness
lasso and emits no `.sos` (the model-checking problem is answered).

**GT4 acceptance:** the tool runs end to end on the §3.5 fixture and on
small corpus pairs; §6.3 green on every case; the emitted `.sos`
re-reads with `load_invariant` and is byte-stable under `reduce`; and
the paper's §6 prediction confirmed or refuted **in writing** (the
[DPT25] example: a guarantee `B` with `< 5` classes is predicted — if it
does not appear, that is a To-theory finding, not a bug to hide).

---

## 7. GT5 — the demonstration

**Performance is out of scope.** No wall-clock claims, no budget tables,
no model-checker comparison. We show the freedom is *leverageable*.

- **Sample.** Same-stratum corpus pairs, both sides small
  (`|𝒞| ≤ 12` each, product table `≤ 60`), N ≈ 200, seeded. Small on
  purpose: `bits ≤ 12` on a large share, so the exhaustive optimum is
  computable and the greedy can be **scored**.
- **Row.** The §6.6 rows + the exhaustive `2^F` optimum where
  `bits ≤ 12`.
- **Headlines.** (1) Fraction with `|𝒞(B)| <` all three reference points.
  (2) Median `|𝒞(B)| / |𝒞(¬φ)|`. (3) Rung-drop rate. (4) Stutter-gained
  rate + UNKNOWN frequency. (5) Greedy-vs-exhaustive gap — *a measured
  quality of our heuristic*, and **not** evidence about Conj 4.5. Say so
  in the summary, in those words.
- **First gate, before any table:** the Thm 5.7 fixture (stutter
  UNKNOWN, free greedy still emits a `B`) and the [DPT25] example of
  paper §6.

**GT5 acceptance:** `reference/giventhat/gt5_demo.md` + `.csv` with the
4-line header (date, git rev, seed, corpus), zero §6.3 violations, the
five headlines stated with their `n`.

---

## 8. Decommissioned (do NOT build)

Parked deliberately, with reasons. Un-parking is a theory decision.

- **Stutter tier 2 / the self-alignment** (paper Appendix A.1). Exact,
  but on YES the witness is `SC(L(P_min))`, which Thm 5.7 shows need not
  be on the table — the operation would have **nothing to emit**. It is
  a diagnostic, not a simplification. Un-park with off-table re-entry.
- **Band-minimal Wagner degree** (paper Appendix A.2). Prop is a sketch;
  the objective is `|𝒞|`, and degree is at best a tie-break. Do not
  enumerate `2^F` to check a sketched proposition — that is proving a
  conjecture by trial and error.
- **The W-series campaigns** (paper Appendix A.3, A.5). W0 is a
  frequency census, W1 needs MCC data and stays **blocked — do not fetch
  it**. Both are downstream of a working operation.
- `degree.py`, `w0_*.py`: not built.

---

## 9. Expected failures — read before filing a bug

| # | check | expectation | on failure |
|---|---|---|---|
| A1 | Prop 3.1 runtime law | always green | upstream bug (align/materialize/saturate) — report the pair, never work around |
| A2 | §6.3 soundness law | always green | upstream bug; hard stop |
| A3 | `π_¬φ` admissible (§6.2 step 2) | always green | convicts Prop 4.2 or `syntactic_congruence` — To theory |
| E2 | fixture: stutter quotient `n == 2`, tier UNKNOWN | must hold | first suspect the HOA encoding, then canonize, then the paper's Thm 5.7 hand count — that escalation is a To-theory finding |
| Q1 | GT3 gate 3 (bounded oracle vs `2^F`) | must be exact | convicts Prop 4.2 — **To theory**, do not patch the hull to match |
| G1 | greedy `|𝒞(B)|` vs exhaustive optimum | **may be worse** | that is a heuristic being a heuristic — record the gap, do not tune the greedy toward the oracle |
| G2 | `\|𝒞(B)\|` not strictly below the reference points | allowed on a case | only a *rate* is claimed (§7); a 0% rate over the sample is a finding, report it |
| F1 | Spot cross-checks | MAY disagree | dictionary/naming first; only a failed witness replay is a bug |
| F2 | Spot timeout | allowed | skip, record, never wait |

## 10. The trap list (each traces to a section)

1. **Alphabet strata** — `align` asserts equal alphabets; sample within
   strata (§0).
2. **Endpoints live on the MATERIALIZED product** — `Aligned` is
   decision-only (§3).
3. **Never insert a raw conjugate/image pair** — always renormalize
   through `linked_pair_of` **on the table you are inserting into**
   (§5.2 `forced`).
4. **No universality scan** — `k_refutes_phi` is emptiness of a
   complement (§3).
5. **Saturate on the QUOTIENT, then pull back** — pulling back first and
   saturating on `T` gives a different, wrong set (§5.2 `hull`).
6. **Brute oracles cap at `bits ≤ 12`** — skip and record above; never
   raise the cap (§5.5, §7).
7. **Per-case budget 15 s, checkpointed campaigns, `--one` mode** —
   calculus spec §8.1 verbatim.
8. **`[ε]` never merges** — assert, do not special-case (§5.1).
9. **The greedy merges in the CURRENT quotient**, composing maps — not
   by re-closing from `T` each round (§6.2).
10. **Horn hull without `saturate` is not a language** — alternate to a
    joint fixpoint (§4, §6.5).
11. **The stutter verdict is YES/UNKNOWN, never NO** (paper Thm 5.7;
    §5.3).
12. **Do not build `SC`'s automaton** — decommissioned (§8).
13. **Reuse the shortlex BFS (`Table.of_raw`) and the SCC pass
    (`r_classes`)** — one implementation each; a second BFS or a second
    Tarjan is a review reject (§0, §5.1).
14. **`reduce(check=True)` is quadratic** — `check=False` inside the
    greedy loop, `check=True` once on the emitted `B` (§6.2).
15. **Never claim minimality** — the greedy achieves, it does not
    minimize (§6).

## 11. Report contract

`research_notes/sos_giventhat_report.md` is the channel back to theory.
Every milestone acceptance writes its findings into the named slots;
every to-theory item (Q1 / A3 escalations, the §6 prediction outcome,
anything where this spec and the paper disagree) goes into the report's
**To theory** section the moment it is found. Findings state numbers
with their `reference/` path and regen command; the paper cites numbers
in pure form only after they appear in the report.
