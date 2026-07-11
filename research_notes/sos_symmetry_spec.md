# SoS Symmetry — Implementation Specification

**Status (2026-07-11).**

| item | state |
|---|---|
| SY1: signed permutations, the single-symmetry check, the kernel read-off (§3) | **OPEN — the commissioned milestone.** Specified to the function level; start here and stop here. |
| SY2: the group computation, asymmetry witness, symmetrization (§4) | SPECIFIED — do not start before SY1 acceptance |
| SY3: relational read-offs (invisible letters, stutter, `k`-ladder, `Î_L`) (§5) | SPECIFIED — needs only SY1's fold helpers; do not start before SY1 acceptance |
| SY4: group spectrum + LTL hull/kernel (§6) | SPECIFIED — doubles as a theory probe (the paper flags `θ_ap` as ⟨TBD⟩); after SY1 |
| SY5: the Y-series campaigns (§7) | Y0a/Y1 need SY2; Y0b/Y0c need SY4; **Y2 is BLOCKED on a ToLTL engine hook — do not start it, do not build the hook yourself** |

An implementer starting cold reads, in order: this header, §0–§2, the
section for the milestone at hand, §8 (expected failures) before filing
any bug, §9 (traps) before writing any code. Revision history lives in
git and `docs/HISTORY.md`, not here.

**Normative math.** `research_notes/sos_symmetry.md` (the symmetry
paper). Section map: paper §3 → SY1 + SY2; paper §4 → SY3; paper §6 →
SY4; paper §9 (measurement plan) → SY5. Behind it,
`research_notes/sos_calculus.md` [CAL26] for the calculus and its spec
`sos_calculus_spec.md` for the package you are building on. Where this
document and the paper disagree, STOP and report — do not reconcile
silently (the paper is a working draft with flagged ⟨TBD⟩s; a
disagreement is a finding, see the report contract §10).

**One-line goal.** `sosl.sos.symmetry` — a new package at
`sosl/sosl/sos/symmetry/` — answers, on canonical invariants and
exactly: is `σ(L) = L` (and `= L^c`) for a signed permutation `σ`;
what is the full signed symmetry group; which atomic propositions are
inert; which factor rewritings `u ↔ v` the language tolerates
(stutter, invisibility, the independence relation `Î_L`); what is the
group spectrum; and what are the LTL hull and kernel.

**Layering law (hard).** `sosl.sos.symmetry` imports `sosl.sos`
(objects, io), `sosl.sos.calculus` (Table, align, materialize,
surgery, decide, reduce, witness), `sosl.sos.classify` (the stutter
read-off, the aperiodicity/definability pass) — and NOTHING else in
the repo. Never `sosl.learn`, `sosl.teacher`, `sosl.experiment`,
`tests.*`. Test scripts under `sosl/tests/symmetry/` may import what
they need (spot, replay hooks), like the calculus gates do. No
cross-package addition is commissioned for SY1; SY4 may need one
promotion in `classify` (§6.1) — that one function, nothing else
moves.

**The one theorem you must keep in your head.** Paper Thm 3.1 (iii):
`σ(L) = L` iff the canonical keying of `(𝒞, λ∘σ, M, P)` is byte-equal
to `𝓘(L)`. The check is one λ-rewire plus one reduce (keying only)
plus one byte comparison — no product, no language query. Its runtime
shadow, the **kernel law**: if `λ∘σ = λ` cellwise (a pure read-off on
the fibers), then the full check MUST come back true; a violation is
an upstream bug (reduce/keying), never a fact about `L` — report the
case, do not work around.

---

## 0. Prerequisites (all DONE, all reused, none reimplemented)

From `sosl.sos.calculus` (see its spec for contracts):

- `Table` — `(𝒞, λ, M)` + memoized `fold` / `idem` / linked pairs /
  canonical keys; `reduce(table, P) -> Invariant`, the canonical
  re-quotient whose keys are the byte-equality oracle of
  [SωS26, Thm 5.1].
- `align / materialize` — the product route. In this package it is
  used ONLY for the asymmetry witness (§4.2), symmetrization (§4.3),
  and sampled cross-oracles; every headline check in SY1/SY3/SY4 is
  product-free by design — that claim is the paper's, and the code
  must exhibit it.
- `surgery.complement` — flip `P` within the linked pairs (free).
- `decide`: `member / is_empty / included / equivalent /
  intersecting_word` — witness-carrying, discipline scan order, so
  every witness is the globally minimal lasso.
- `witness.Witness` with `replay(oracle)`.

From `sosl.sos.classify`: `is_stutter_invariant(inv)` (the
`λ(a)² = λ(a)` read-off) and the aperiodicity/definability pass of
[SωSX26] (SY4 reuses its group `H`-class walk — §6.1).

Corpus: `genaut/corpus/flat_canon/` — 3 938 canonical `.sos`
invariants + paired det HOA, `.cat` sidecars carrying the Wagner
coordinates, the LTL bit, and the `stutter:` tag. Alphabet strata as
in calculus spec §8.2. Every invariant carries its AP list in a fixed
order — that order is the indexing convention for everything below.

---

## 1. Package shape

```
sosl/sosl/sos/symmetry/
    __init__.py     re-exports SignedPerm, apply_perm, is_symmetry,
                    is_antisymmetry, inert_aps, and the later entry points
    sigma.py        SY1: SignedPerm + action, apply_perm, the checks,
                    the kernel read-off
    stabilizer.py   SY2: group enumeration/search, witness, symmetrization
    relations.py    SY3: word folds, rewriting closure, invisible letters,
                    k-ladder, independence relation
    spectrum.py     SY4: maximal subgroups, composition factors, Spec
    reflect.py      SY4: θ_ap, P♯/P♭, hull and kernel invariants

sosl/tests/symmetry/
    fixtures.py         builds + caches the four fixture DELAs (§3.4, §6.3)
    sigma_gate.py       SY1 acceptance
    group_gate.py       SY2 acceptance
    relations_gate.py   SY3 acceptance (incl. the corpus stutter oracle)
    spectrum_gate.py    SY4 acceptance (incl. the corpus LTL-bit oracle)
    y0_census.py        SY5 campaigns (Y0a/Y0b/Y0c/Y1)
    logs/               working logs (never /tmp)
```

Library only, no CLI. Type-annotate every public signature (params and
return; `typing.Optional/Tuple/FrozenSet`, `Protocol` where a contract
is behavioral) — house rule.

---

## 2. Objects

**Minterms.** A letter is a minterm over the invariant's AP list: a
bit vector `m` of length `n = |AP|`, bit `i` = truth of AP `i` *in the
invariant's stored AP order*. Never sort, never re-derive that order.

**SignedPerm (frozen dataclass, `sigma.py`).**

```
@dataclass(frozen=True)
class SignedPerm:
    perm: Tuple[int, ...]    # image position of AP index i
    flip: Tuple[bool, ...]   # polarity flip applied to source AP i
```

Action on a minterm: `(σ·m)[perm[i]] = m[i] XOR flip[i]` for every
`i`. Constructors `identity(n)`, `transposition(n, i, j)`,
`polarity_flip(n, i)`; methods `compose(other)` (meaning `self ∘
other`: apply `other` first), `inverse()`, `__call__(m)`, and
`act_word(w)` (letterwise on tuples of minterms). The convention is
pinned by gates, not prose (§3.5.1); if your implementation passes
the pin equations, it is right.

---

## 3. SY1 — signed permutations, the single check, the kernel read-off (THE MILESTONE)

Normative math: paper §3.1–§3.2 (Thm 3.1, the two-level fiber
structure, the signed group and anti-symmetries — *single-candidate
checks only*; the group computation is SY2). Everything here is
prescribed; if an ambiguity remains, choose the reading that matches
the paper and say so in the report.

### 3.1 `apply_perm`

```
apply_perm(inv: Invariant, sigma: SignedPerm) -> Invariant
```

Steps, in order:

1. **Assert arity**: `len(sigma.perm) == |inv.AP|`. Do not adapt, do
   not pad — a mismatch is a caller error: raise.
2. Build the rewired letter map `λ'(m) := λ(σ(m))` — a table of
   `2^n` class ids, nothing else changes: same `𝒞`, same `M`, same
   `P`. This is the free inverse substitution of [CAL26] §3.2; the
   result presents `𝓘(σ⁻¹L)` (paper Thm 3.1 (iii); which of
   `σ`/`σ⁻¹` you get is immaterial for the checks below but is pinned
   by gate §3.5.2 — do not "fix" the direction if that gate passes).
3. `reduce`. Because `σ` permutes `Σ`, `λ'(Σ) = λ(Σ)`: the generators
   are the same set, no re-quotient can occur, reduce is keying only.
   **Assert `|𝒞|` unchanged** — a merge here convicts the input (not
   syntactic) or reduce; STOP and report (§8/K1).
4. Return the reduced invariant.

Cost: `O(2^n)` for the rewire + one keying pass. No align, no
materialize, anywhere in SY1.

### 3.2 The checks

```
is_symmetry(inv, sigma)      -> bool   # keys(apply_perm(inv,σ)) == keys(inv)
is_antisymmetry(inv, sigma)  -> bool   # keys(apply_perm(inv,σ)) == keys(complement(inv))
in_kernel(inv, sigma)        -> bool   # ∀m: λ(σ(m)) == λ(m) — pure fiber read-off
inert_aps(inv)               -> FrozenSet[int]   # {i : in_kernel(inv, polarity_flip(n,i))}
anti_possible(inv)           -> bool   # 2·|P| == |linked| — the pair-count obstruction
```

- `is_symmetry` / `is_antisymmetry` compare **canonical keys only**
  (byte equality) — never raw class ids across two invariants (trap
  #3). `complement` is the free `P`-flip + reduce; never any
  automaton-level complement.
- `in_kernel` is one pass over the `2^n` letters. It is **sufficient
  only** (`in_kernel ⟹ is_symmetry`, the kernel law): a symmetry can
  hold with `λ∘σ ≠ λ` (fixture C's swap does exactly that). It is a
  law and a read-off, NOT a shortcut: in this package the full check
  always runs; `in_kernel` runs beside it as an assertion (§3.5.3).
- `inert_aps` is the paper's §3.1 Example A reified — the
  corpus-curation observation that a semantically redundant AP shows
  up as a polarity flip inside the kernel `K`. It must equal
  `{i : is_symmetry(inv, polarity_flip(n, i)) and in_kernel(...)}`
  by the kernel law; the gate checks the full-route agreement.
- `anti_possible` is the paper's §3.2 pair-count obstruction: an
  anti-symmetry's `ρ` bijects `P` onto `linked ∖ P`, so unequal
  halves refute every anti-candidate at once. It is a **law**
  (`is_antisymmetry(inv, σ) ⟹ anti_possible(inv)`, asserted in the
  gates) and a legitimate campaign fast path (skip the anti passes
  when False — the only sanctioned shortcut in SY1).

### 3.3 Candidate enumeration helper (used by gates and the campaign)

```
generators_b_ap(n) -> Tuple[SignedPerm, ...]   # all transpositions + all flips
all_b_ap(n)        -> Iterator[SignedPerm]     # the full group, |B_n| = 2^n · n!
```

`all_b_ap` is for `n ≤ 3` only in SY1 (48 elements at `n = 3`); it
raises for `n > 3` (SY2 owns the larger `n` policy — do not lift the
guard, trap #6).

### 3.4 The fixture triple (build FIRST — everything gates on it)

`fixtures.py` builds the DELAs, writes them under
`sosl/tests/symmetry/logs/fixtures/`, canonizes each with
`genaut/gen/canonize.py` (trust its defaults; head its pydoc for the
output flag only), and caches the resulting `.sos` paths. The names
match the paper's worked examples (paper §3 Examples A–C; the
predictions below are paper §9 P1–P3 — a mismatch is a to-theory
finding, not a local patch). SY1 uses FIX_A/B/C; FIX_E (`EvenHead`)
is built here too but consumed by SY4 (§6.3).

- **FIX_A** (paper Example A) — `ℒ = GF a` over `AP = {a, b}`.
  **Hand-built HOA mandatory** — `ltl2tgba` drops the unused `b`
  (trap #7). One state `q0`, self-loops on all four minterms, marks
  `{0}` on `a&b` and `a&¬b`, acceptance `Inf(0)`.
- **FIX_B** (paper Example B) — `ℒ = GF a ∧ GF b`, `AP = {a, b}`.
  Via `ltl2tgba -D 'GFa & GFb'` (bounded); both APs occur, no drop.
- **FIX_C** (paper Example C) — `ℒ = a·Σ^ω` ("a at the first
  instant"), `AP = {a}`. Via `ltl2tgba -D 'a'` (bounded) or by hand:
  `q0 --a--> T`, `q0 --¬a--> R`, `T --⊤--> T` acc, `R --⊤--> R` rej.

Expected facts to assert (each failure = STOP and report, §8/E1):

- `|𝒞(FIX_A)| == 3` — `[ε]`, [contains an `a`-letter] (absorbing),
  [contains none]. Paper predicts `P = {(F, F)}` in its class names —
  record `|P|` and `|linked|` as data.
- `|𝒞(FIX_B)| == 5` — `[ε]` plus the four (seen `a`?, seen `b`?)
  flag combinations; the table is componentwise OR; paper predicts
  `|P| == 1`.
- `|𝒞(FIX_C)| == 3` — `[ε]`, [first letter `a`], [first letter `¬a`]
  (the class of a nonempty word is its first letter's class); paper
  predicts 4 linked pairs of which `P` is exactly half (P3).

The candidate truth tables — paper §9 P2 (assert every cell; `n=1`
has 2 candidates in `B_1`, `n=2` has 8 in `B_2` — enumerate with
`all_b_ap`):

| fixture | symmetric candidates | anti-symmetric candidates | `inert_aps` |
|---|---|---|---|
| FIX_A | `{id, flip_b}` | `∅` (note `σ_a(GFa) = GF¬a ≠ FG¬a = L^c`) | `{b}` |
| FIX_B | `{id, swap_ab}` | `∅` | `∅` |
| FIX_C | `{id}` | `{flip_a}` (first letter flips, `L ↦ L^c`) | `∅` |

Additionally: `in_kernel(FIX_A, flip_b)` is True (the fiber
read-off sees it — the paper's Example A), while
`in_kernel(FIX_B, swap_ab)` is **False** although
`is_symmetry(FIX_B, swap_ab)` is True (`λ` is injective on FIX_B's
four minterms, so the kernel is trivial and the symmetry lives in
`Aut(𝒞, M, P)` proper). Assert both — together they separate the two
levels of paper §3.1. Pair-count obstruction (P3):
`anti_possible(FIX_C)` True, `anti_possible(FIX_A)` and
`anti_possible(FIX_B)` False (§3.2).

### 3.5 SY1 semantic gates (in `sigma_gate.py`)

1. **Group-law + convention pin.** For each `n ∈ {1..5}`: 100 seeded
   random triples `(σ, τ, m)`:
   `compose(σ, τ)(m) == σ(τ(m))`; `σ.inverse().compose(σ) ==
   identity`; involutions: `transposition²  == identity`,
   `polarity_flip² == identity`. The pin equation at `n = 2`:
   `swap_ab ∘ flip_a == flip_b ∘ swap_ab` (as functions on all four
   minterms). If your flip/perm ordering fails the pin, fix the
   action, not the gate.
2. **Direction pin for `apply_perm`.** For every fixture, every
   `σ ∈ B_n`, and every lasso `(u, v)` with `|u|, |v| ≤ 3`
   (exhaustive at `n ≤ 2`):
   `member(apply_perm(inv, σ), u, v) == member(inv, σ(u), σ(v))`.
   This crosses the rewire boundary and is the gate that catches an
   inverted action.
3. **Kernel law**, on every candidate everywhere (fixtures and
   campaign): `in_kernel(inv, σ) ⟹ is_symmetry(inv, σ)`. Violation:
   STOP (§8/K1).
4. **Metamorphic symmetry check.** Whenever `is_symmetry(inv, σ)`:
   `member(inv, u, v) == member(inv, σ(u), σ(v))` for all lassos
   `|u|, |v| ≤ 3` (exhaustive at `n ≤ 2`, ≥ 500 seeded samples at
   `n ≥ 3`). Whenever the fixture table says False, assert a
   disagreeing lasso exists within the same bound (it does for all
   three fixtures — record it; e.g. FIX_A/`flip_a`: a loop on the
   `a`-minterm vs its flip).
5. **Anti/complement commutation + obstruction law.** On fixtures +
   50 seeded corpus cases: `keys(apply_perm(complement(inv), σ)) ==
   keys(complement(apply_perm(inv, σ)))`, and
   `is_antisymmetry(inv, σ) == (keys(apply_perm(inv, σ)) ==
   keys(complement(inv)))` via both routes; and the law
   `is_antisymmetry(inv, σ) ⟹ anti_possible(inv)` on every anti
   check everywhere (campaign included, before applying the fast
   path).
6. **Cross-oracle via the product route** (sampled — product-priced):
   on the fixtures and 50 seeded corpus cases × their `B_AP`
   generators: `is_symmetry(inv, σ) == decide.equivalent(inv,
   apply_perm(inv, σ))`. The align-based route is independent of the
   keying route; disagreement convicts one of them — STOP.
7. **Corpus campaign (SY1 acceptance body).** Over all 3 938
   `flat_canon` invariants: per case, run `inert_aps`, plus
   `is_symmetry` and `is_antisymmetry` for every generator from
   `generators_b_ap(n)` (that is `n(n−1)/2 + n` candidates, two
   keying passes each — cheap); at `n ≤ 3` additionally the full
   `all_b_ap` sweep. Record one CSV row per case:
   `case, n_aps, |𝒞|, inert_set, sym_generator_hits,
   anti_generator_hits, wall_ms` →
   `sosl/tests/symmetry/logs/sy1_generators.csv`. Seed `20260711`;
   per-case budget 15 s (blown budget = skip, record, never wait);
   checkpoint file; `--one <case>` mode (house rules, calculus spec
   §8.1 verbatim).

**SY1 acceptance:** `sigma_gate.py` green on the fixture triple
(every truth-table cell) and the full 3 938-case campaign with zero
kernel-law violations and zero unexplained rows; the CSV committed
under `logs/`; findings F1–F4 of the report filled (the inert-AP
frequency, F3, is a paper §9 number — carry it verbatim). Nothing in
`calculus`/`classify` touched.

---

## 4. SY2 — the group, the witness, symmetrization

Normative math: paper §3.1 (cost remark), §3.2–§3.4.

- `sym_group(inv) -> SymGroup` where `SymGroup` carries the element
  list (or generators) of `Sym_AP(L)` and the anti coset, i.e.
  `Sym±(L)` as pairs `(SignedPerm, is_anti: bool)`. Policy by arity:
  `n ≤ 4` — brute enumeration of `B_n` (≤ 384 elements, one keying
  pass each; measure, it is expected sub-second); `n = 5` — filter
  first by the two cheap invariants (fiber-cardinality profile must
  be `σ`-stable; `in_kernel` members are free wins), then enumerate
  the survivors; if a case blows the 15 s budget, skip, record, and
  file the case (the backtracking stabilizer search of paper §3.1 is
  the *stretch* upgrade, commissioned only if the Y0a campaign
  reports a skip rate above 1%).
- Gates: closure (`compose` of two members is a member), inverse
  closure, `|Sym±|` divides `2·|B_n|`; fixtures: `Sym_AP(FIX_A) =
  {id, flip_b}`, empty anti coset; `Sym_AP(FIX_B) = {id, swap_ab}`,
  empty anti coset; `Sym_AP(FIX_C) = {id}` with anti coset
  `{flip_a}`.
- `asymmetry_witness(inv, sigma) -> Optional[Witness]`: `None` if
  symmetric; else align `inv` with `apply_perm(inv, σ)`, scan the
  symmetric difference (two surgeries on the materialized product),
  return the minimal lasso. Gates: the witness replays as a member of
  exactly one side (`member` on both invariants — always; bounded HOA
  replay where the det HOA exists); on FIX_A/`flip_a` the witness
  loop must be a single minterm (record which).
- `symmetrize(inv, generators, mode=∩|∪) -> Invariant` (paper §3.4):
  fixpoint of align+intersect(/union)+reduce over the generators.
  Orbit cap 16: if the fixpoint has not closed after 16 alignments,
  stop, record the partial orbit size, file it (the orbit price is a
  paper claim — the cap protects the harness, the recorded size feeds
  F7). Gates: the result passes `is_symmetry` for every generator;
  `mode=∩` result `included` in `inv` `included` in `mode=∪` result
  (align-based, sampled); a symmetric input is its own fixpoint in
  one round (byte-equal).

**SY2 acceptance:** group gates green on fixtures + 300 seeded corpus
cases; witness replay clean on every asymmetric generator of the
sample; symmetrization laws green on 50 seeded cases (product-priced —
keep the sample small); findings F5–F7 filled.

---

## 5. SY3 — relational read-offs

Normative math: paper §4 (Thm 4.2, its instances, Thm 4.4). All
product-free: folds and table lookups only. Entry points in
`relations.py`:

- `word_class(inv, w) -> ClassId` — fold `λ` over a tuple of
  minterms (reuse `Table.fold`).
- `is_closed(inv, u, v) -> bool` — `word_class(u) == word_class(v)`:
  Theorem 4.2 as one function. Everything below is a wrapper around
  it; keep it that way (the code should exhibit the paper's "one
  principle, many instances" shape).
- `invisible_letters(inv) -> FrozenSet[minterm]` — `{m : λ(m) ==
  unit}` (`[ε]`'s class id). NOTE this is NOT `inert_aps` — an
  invisible letter is `[c] = 1`; an inert AP is a fiber equality;
  neither implies the other (trap #9). The gate has a case for each
  side.
- `stutter_rung(inv, k) -> bool` — `∀ class-words w over Σ_λ, |w| ≤
  k: [w] == [ww]`. Enumerate over letter CLASSES (`Σ_λ`), not
  letters — `|Σ_λ|^k` folds, budget-capped; `k ∈ {1, 2, 3}` only.
  `k = 1` must equal `classify.is_stutter_invariant` (same equation).
- `ladder_entry(inv) -> Optional[int]` — least `k ≤ 3` with
  `stutter_rung(k)`; `None` if none (record, this is the F11 datum).
- `independence(inv) -> FrozenSet[Tuple[ClassId, ClassId]]` — `Î_L`
  on `Σ_λ`: `{(c, d) : M(c,d) == M(d,c), c ≠ d}` — paper Thm 4.4,
  `O(|Σ_λ|²)` lookups; provide `independence_letters(inv)` lifting to
  minterm pairs through the fibers.

Gates (`relations_gate.py`):

1. **The corpus stutter oracle (decisive — run FIRST):** over all
   3 938 invariants, `stutter_rung(inv, 1) == (.cat stutter tag)`.
   The tag is semantic ground truth from the census; a disagreement
   is a real bug or a real theory problem — mixed failures: STOP,
   smallest case to the report (slot F8).
2. **Metamorphic rewriting:** for 200 seeded corpus cases and 20
   seeded `(u, v)` pairs each with `is_closed(u, v)` true: for lassos
   `|x|, |y| ≤ 3`, membership is invariant under replacing one
   `u`-occurrence by `v` in the stem and in the loop (construct the
   rewritten lassos explicitly). For pairs with `is_closed` false: a
   distinguishing context exists — find it by the bounded scan and
   record it (Thm 4.2's ⟸ and ⟹ both exercised).
3. **Fixture expectations (paper §9 P4):** FIX_A and FIX_B tables
   are commutative (OR of flags) ⟹ `independence` is total on
   distinct classes; FIX_C: `M([a·], [¬a·]) = [a·] ≠ [¬a·] =
   M([¬a·], [a·])` ⟹ `independence(FIX_C) = ∅`. FIX_A is
   stutter-invariant (`ladder_entry == 1`); FIX_C is too (`a·Σ^ω` —
   first letter survives destuttering; assert, and if this surprises
   you, that is the point of gates). `invisible_letters` empty on all
   three;
   contrast case: build `FIX_D = ltl2tgba -D 'F a'` over `AP={a}` —
   no invisible letter either, but `unit`-mapped letters exist in the
   corpus: report their census frequency instead of asserting on
   fixtures (F9).
4. **Independence swap gate:** for 100 seeded cases and each
   `(c, d) ∈ Î_L` sampled: bounded lassos with one adjacent `cd`
   block swapped to `dc` keep membership; for `(c, d) ∉ Î_L`: a
   distinguishing swap context exists in the bound or is recorded as
   not-found-within-bound (do NOT assert absence — the witness
   construction is SY2 machinery + a ⟨TBD⟩ in the paper §4.3; out of
   scope here).

**SY3 acceptance:** stutter oracle 3 938/3 938 explained; gates green;
`ladder_entry` and `|Î_L|` density distributions recorded to
`logs/sy3_relations.csv`; findings F8–F11 filled.

---

## 6. SY4 — the group spectrum and the LTL hull/kernel

Normative math: paper §6 (Spec, Prop 6.4) — **§6.2 carries explicit
⟨TBD⟩s; this milestone is deliberately their experimental probe.**
Disagreements land in the report, not in silent workarounds.

### 6.1 `spectrum.py`

- `maximal_subgroups(table) -> Tuple[Group, ...]`: the group
  `H`-classes at idempotents. The definability pass in
  `sosl.sos.classify` already walks these ([SωSX26]); **promote its
  routine to a shared helper rather than writing a second one** —
  that promotion is the single commissioned `classify` change, with
  its own one-line gate (every returned `H`-class is a group: closed,
  has identity `e`, has inverses).
- `composition_factors(g: Group) -> Multiset[str]`: brute force is
  fine at table sizes (find a maximal proper normal subgroup by
  subgroup enumeration, recurse); hard cap: group order ≤ 512, above
  it skip + record (none expected on the census; one would be an F13
  headline).
- `spec(inv) -> FrozenSet[str]`: union of simple factors over all
  maximal subgroups, names normalized (`"Z/2"`, `"Z/3"`, `"S3"`…).

### 6.2 `reflect.py`

- `aperiodic_reflection(table) -> (QuotientTable, q)`: iterate — 
  collapse every nontrivial maximal subgroup onto its idempotent,
  close to a congruence (the union-find + worklist pattern of the
  stutter quotient, calculus side — reuse the shared shortlex
  re-keying), re-detect groups, repeat until aperiodic. Assert the
  fixpoint is aperiodic. **Whether this is the LEAST aperiodic
  congruence `θ_ap` is the paper's ⟨TBD⟩** — do not claim it; name
  the function honestly and record the iteration count (F14 datum).
  The ω-sort: after each collapse round, saturate the pair structure
  (`linked_pair_of` renormalization) so the quotient is an
  ω-congruence; forgetting this yields non-language pair sets and
  the saturation law convicts you.
- `hull(inv) -> Invariant` / `kernel(inv) -> Invariant`: `P♯ =
  q⁻¹(q(P))`, `P♭ = {p : q⁻¹(q(p)) ⊆ P}` computed on the quotient,
  then `reduce`.

### 6.3 FIX_E — the worked non-LTL fixture (`EvenHead`, paper §6.2 / §9 P5)

`ℒ = { a^{2n}·b^ω : n ≥ 0 }` over `AP = {a}`, `b := ¬a`. **Hand-built
HOA mandatory** (the language is not LTL — `ltl2tgba` cannot produce
it): states `q0` (even, initial), `q1` (odd), `qb` (in the `b`-run),
`D` (dead sink). Transitions: `q0 --a--> q1`, `q0 --b--> qb`,
`q1 --a--> q0`, `q1 --b--> D`, `qb --b--> qb` mark `{0}`,
`qb --a--> D`, `D --⊤--> D`. Acceptance `Inf(0)`. Deterministic,
complete. Built in `fixtures.py` beside FIX_A/B/C.

Expected facts (each is paper §9 P1/P2/P5; failure = §8/E1
escalation): `|𝒞| == 7`; over `B_1`: symmetric `{id}`, anti `∅`,
`anti_possible` recorded; `spec == {"Z/2"}`; the reflection has
exactly 5 classes and stabilizes in one collapse round (assert both);
`hull(FIX_E)` byte-equals the canonized invariant of
`ltl2tgba -D 'FG!a & G(!a -> G!a)'` and `kernel(FIX_E)` that of
`ltl2tgba -D 'G!a'` (bounded calls, E1 escalation on mismatch);
gap membership: for `1 ≤ n ≤ 6`, the lasso `(a^n, b)` is a `member`
of the hull and not of the kernel, and `member(FIX_E, a^n, b)` is
true iff `n` is even.

Gates (`spectrum_gate.py`):

1. **The corpus LTL-bit oracle (decisive — run FIRST):**
   `spec(inv) == ∅` iff the `.cat` LTL bit, over all 3 938. A
   disagreement in either direction is a to-theory event (slot F12):
   STOP on the smallest case.
2. Spectrum sanity: FIX_E per §6.3, and `EvenBlocks` (by census name)
   has `spec == {"Z/2"}`.
3. Hull/kernel laws, on 200 seeded cases (align-priced — sampled):
   `included(kernel(inv), inv)` and `included(inv, hull(inv))`;
   `spec(hull(inv)) == spec(kernel(inv)) == ∅` (they are LTL);
   on every LTL corpus row (`spec == ∅`), reflection is trivial and
   `hull == kernel == inv` byte-equal — this one runs corpus-wide,
   it is key-comparison only.
4. **Witness-in-gap** (paper §6.2 expectation): on `EvenBlocks`, the
   counting family `u·vⁿ·x` instances for `n ≤ 6` are members of
   `hull` and non-members of `kernel` (`member` on the tables).
5. Optimality probe (bounded, honesty required): we CANNOT gate
   leastness of the reflection cheaply. Record instead, per non-LTL
   case: `|𝒞/θ|` vs `|𝒞|` and whether a SECOND aperiodic congruence
   strictly between exists among the ≤ 64-class quotients found by
   single-collapse variants (if one is found, the reflection was not
   least: to-theory verbatim, slot F14 — this is the probe the paper
   asked for).

**SY4 acceptance:** LTL-bit oracle 3 938/3 938 explained; laws green;
gap columns recorded to `logs/sy4_gap.csv`; findings F12–F14 filled.

---

## 7. SY5 — the Y-series campaigns

House rules of calculus spec §8.1 apply verbatim (budgets, seeds,
checkpoints, output headers, CSV+md shape, `reference/` promotion).
Deliverables under `reference/symmetry/`, one `.md` + `.csv` each;
every number the paper later cites in pure form comes from here.

- **Y0a — the `Sym±` column** (`y0_sym.py`; needs SY2). Over all
  3 938: `|Sym_AP|`, `|anti coset|`, `|inert_aps|`, kernel share.
  Paper §9 expects fat kernels and small semantic groups — the
  campaign confirms or corrects (F15). Skip policy per §4; skip rate
  reported.
- **Y0b — the `Spec` column** (`y0_spec.py`; needs SY4). Over the
  1 698 non-LTL rows: spectrum values, cross-tabulated with the
  Wagner coordinates from `.cat`. Expected overwhelmingly `{Z/2}`;
  any nonabelian or non-solvable specimen is a headline find — file
  it the moment it appears, do not wait for campaign end.
- **Y0c — the gap column** (`y0_gap.py`; needs SY4). `|𝒞/θ|` vs
  `|𝒞|` distribution; hull/kernel collapse rate on LTL rows (must be
  100% — it is gate 3, re-verified in campaign shape); witness-in-gap
  spot checks on 20 seeded non-LTL rows.
- **Y1 — orbit deduplication** (`y1_dedup.py`; needs SY2, `n ≤ 4`
  rows only, record the rest). Orbit representative := the
  lexicographically least canonical key over `{apply_perm(inv, σ) :
  σ ∈ B_n}` ∪ the complemented orbit. Deliverable: the dedup map
  (`case → representative`) and the shrink factor — the paper §9
  deduplication axis (F16).
- **Y2 — orbit-folded extraction** (paper Thm 5.1 (ii)). **BLOCKED**:
  needs the ToLTL engine hook and the renderer-equivariance clause
  resolved by the theory thread (paper §5 ⟨TBD⟩). Do not start, do
  not build the hook, do not resolve the clause yourself. When it
  unblocks, a protocol revision of this spec will accompany it.
  Until then Y2 does not exist for you.

**SY5 acceptance (Y0+Y1):** the four reference files committed with
headers, zero unexplained failure rows, summary tables present;
findings F15–F16 filled.

---

## 8. Expected failures — read before filing a bug

| # | check | expectation | on failure |
|---|---|---|---|
| K1 | kernel law (`in_kernel ⟹ is_symmetry`) | always green | upstream (reduce/keying) or the action convention — re-run gate §3.5.1/§3.5.2 first; then report the case, never work around |
| K2 | `apply_perm` preserves `\|𝒞\|` | always green | input not syntactic, or reduce merged — report, do not continue |
| E1 | fixture class counts (3 / 5 / 3 / 7) and truth tables | must hold | first suspect the HOA encoding (the FIX_A and FIX_E hand-builds especially); then canonize; only then the paper's hand counts (§9 P1–P5) — that escalation is a to-theory finding |
| T1 | corpus stutter oracle (SY3) | green | mixed disagreement ⟹ STOP, smallest case to report (F8) |
| T2 | corpus LTL-bit oracle (SY4) | green | either direction of disagreement is a to-theory event (F12): STOP on the smallest case |
| T3 | reflection leastness probe (SY4 gate 5) | may find a between-congruence | that is the experiment working — dossier to F14, do NOT patch the reflection to dodge it |
| T4 | symmetrization orbit cap | may hit 16 | record the partial orbit, skip, file (F7) — the orbit price is a paper claim under test |
| F1 | Spot cross-checks / replay | MAY disagree | dictionary/naming first; only a failed `member` replay makes it a bug |
| F2 | Spot timeout | allowed | skip, record, never wait |

## 9. The trap list (each traces to a section)

1. **AP order is the invariant's stored order** — never sort, never
   re-derive; two invariants with the same APs in different order are
   different strata (§2).
2. **Pin the action by equations, not by prose** — gate §3.5.1's
   composition/involution/pin equations decide the convention; if
   they pass, stop second-guessing the direction (§2, §3.5.1).
3. **Canonical keys are the only cross-invariant equality** — never
   compare class ids of two invariants (§3.2).
4. **`complement` is the free `P`-flip** — no automaton complement,
   ever (§3.2).
5. **`σ` vs `σ⁻¹` is immaterial for the checks** — `σL = L ⟺ σ⁻¹L =
   L`; the direction only matters to `apply_perm`'s contract and gate
   §3.5.2 pins it (§3.1).
6. **`all_b_ap` is guarded at `n ≤ 3` in SY1** — the larger-`n`
   policy belongs to SY2; do not lift the guard for coverage (§3.3).
7. **`ltl2tgba` drops unused APs, and cannot express FIX_E at all**
   — FIX_A and FIX_E are hand-built or they are wrong (§3.4, §6.3).
8. **Invisible letter ≠ inert AP** — `[c] = 1` vs a fiber equality;
   the gates have a case for each; conflating them is the expected
   novice bug of SY3 (§5).
9. **Enumerate rungs over `Σ_λ`, not `Σ`** — `|Σ|^k` folds is the
   wrong complexity class at 4–5 APs; the fibers were quotiented for
   a reason (§5).
10. **Saturate after every collapse round in the reflection** — an
    unsaturated quotient pair set is not a language; the saturation
    law convicts (§6.2).
11. **Product-priced calls are sampled, never corpus-wide** — align
    appears only in §3.5.6, §4, and the sampled SY4 laws; a
    corpus-wide align sweep is a review reject (§0).
12. **Per-case budget 15 s, checkpoints, `--one` mode, seeds in
    headers** — calculus spec §8.1 verbatim (§3.5.7, §7).
13. **Reuse the shared shortlex re-keying and the classify group
    walk** — one implementation each; a second copy is a review
    reject (§6).

## 10. Report contract

`research_notes/sos_symmetry_report.md` is the channel back to the
theory thread; its skeleton (with pre-named finding slots F1–F16) is
committed next to this spec. Rules: every milestone acceptance writes
its findings into the named slots; every to-theory item (E1
escalations, T1/T2 oracle failures, the T3 leastness dossier, orbit-cap
hits, anything where this spec and the paper disagree) goes into the
report's **To theory** section the moment it is found — that section
is read by the thread that owns the paper; it is how you talk to us.
Findings state numbers with their `reference/`/logs path and regen
command; the paper cites numbers in pure form only after they appear
in the report (the calculus split, `sos_calculus_spec.md` §8.9,
applies verbatim).
