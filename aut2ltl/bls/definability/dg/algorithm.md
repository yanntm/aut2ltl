# Synthesizing LTL from the syntactic ω-semigroup — the Diekert–Gastin route

**STATUS: DRAFT** — design document, pre-implementation. This is the companion
and consumer of `../oracle/algorithm.md`: the objects and notation defined
there (`D`, `EM(D)`, the quotient `S(L)₊ = EM(D)/~`, residual classes,
profiles `Aprof`, shortest representatives) are used here without being
redefined. Open points are collected in layer 11; nothing below them is
final.

## 0 — Why this exists

The oracle decides LTL-definability by materializing the syntactic
ω-semigroup — the canonical algebra of the language. On the negative side it
hands out a replayable certificate; on the positive side it answers **LTL**
with a theorem but no artifact (the trust asymmetry its layer 11 records).
This module makes the positive verdict constructive: from the aperiodic
quotient it **synthesizes a defining LTL formula**, by the local-divisor
induction of Diekert–Gastin. Three properties no other engine in the
portfolio has at once:

- **Complete on the fragment.** Every LTL-definable language gets a formula.
  There is no counter-free-presentation precondition: the construction runs
  on the canonical algebra, where a group exists iff the language is
  genuinely not LTL — the kr cascade's form constraint (a proven-LTL language
  whose given automaton still carries an encoding group) has nothing to
  attach to here.
- **Presentation-independent.** Any two inputs with the same language reach
  the identical quotient, and every choice the synthesis makes is pinned
  deterministic (layer 8). Same language ⟹ same formula — hash-consed
  identity, not mere equivalence. The output is a **normal form** for the
  LTL fragment of ω-regular, canonical modulo the fixed choices.
- **Self-certifying.** The formula, verified equivalent to the input, is the
  checkable certificate the LTL verdict lacked.

The theory is settled — the references of layer 10 prove this synthesis
exists — but the literature is proof, not construction-you-can-run: to our
knowledge the local-divisor synthesis has never been implemented, because it
consumes the syntactic ω-semigroup and nobody materializes that object. The
oracle now does. This module is the cash-out.

## 1 — Input contract

The synthesis starts strictly after the oracle, on an **LTL** verdict
obtained through the quotient (not only the screen), and consumes:

- the class set `S¹` (the quotient with identity adjoined), with one enriched
  representative per class;
- the letter map `h : Σ → S¹` (the class of each letter element);
- the profile and residual tables behind the seeds.

It materializes, once, two derived tables the oracle never needed:

- **The class multiplication table** `S¹ × S¹ → S¹`: compose the enriched
  representatives (the closure is the whole monoid, so the product is a
  dictionary hit in the element index), read the product's class. From here
  on the construction works in the quotient alone — `D` and `EM(D)` are out
  of the picture except through the next table.
- **The accepting-pair table** `P ⊆ S¹ × S`: `P(s, e)` = acceptance of any
  `u·z^ω` with `[u] = s`, `[z] = e` — one lookup,
  `Aprof(rep(e))[st_{rep(s)}(init)]`. Well-definedness on classes is exactly
  `~ω`. (Pairs, not linked pairs: the table is total, and the synthesis only
  ever reads it at pairs that arise from actual factorizations.)

Precondition, load-bearing: **the quotient is aperiodic**. The induction's
termination lever (layer 3) is that every non-identity element is a non-unit,
which is precisely the triviality of the group of units — false in any
group-bearing monoid. The module must refuse a non-aperiodic input rather
than loop.

## 2 — The statement implemented

**Theorem (Diekert–Gastin).** Let `h : Σ⁺ → S` be a morphism onto a finite
*aperiodic* semigroup recognizing `L ⊆ Σ^∞`. Then every finite-word class
`h⁻¹(t)` is definable in LTL over finite words, and `L` is definable in LTL
over `Σ^∞` — constructively, by induction on `(|S|, |Σ|)` lexicographic.

The recursion node contract, fixed now because everything below instantiates
it: a node is handed

```
( Δ,  T,  g : Δ → T,  target )
```

— a finite alphabet `Δ`, a finite aperiodic monoid `T`, the letter morphism,
and a target that is either a monoid element `t ∈ T` (*synthesize the
finite-word class formula*, in finite-word LTL) or an acceptance table
`P' ⊆ T¹ × T` (*synthesize the ω-formula* for `{w : the pair of w is in
P'}`). Both targets are served by the same pivot machinery; the root node is
`(Σ, S(L)₊¹, h, P)`.

## 3 — The pivot and the two letter cases

Each node picks a **pivot letter** `a ∈ Δ` (the deterministic rule is layer
8's business) and splits on its image `c = g(a)`.

- **Invisible pivot, `c = 1`.** The letter is transparent to the algebra:
  `g(u·a·v) = g(u)·g(v)`, so classes are insensitive to erasing `a` — with
  one ω-caveat: a word may end in `a^ω`, and erasure of an infinite tail is
  not erasure. The regime split `FG a` / `¬FG a` (both LTL over `{a}`)
  handles it: on `FG a` the word is prefix·`a^ω` with pair `(m, 1)`, a pure
  table bit `P'(m, 1)`; on `¬FG a` the erased word is a legitimate member of
  `(Δ∖{a})^∞`, the node recurses on `(Δ∖{a}, T, g, target)` — second
  induction coordinate strictly down — and the resulting formula is lifted
  back by relativizing to the `¬a`-positions (layer 6's machinery, with
  position filter `¬a`).
- **Visible pivot, `c ≠ 1`.** The **local divisor** is the smaller algebra
  the middle of the word lives in:

  ```
  T_c = cT ∩ Tc      x ∘ y := x·v  where  y = c·v      identity: c
  ```

  Well-defined (if `y = c·v = c·v′` then, writing `x = u·c`,
  `x·v = u·c·v = u·c·v′ = x·v′`), associative, a divisor of `T` — so
  **aperiodicity is inherited**. The **local divisor lemma**: if `c` is not a
  unit, `|T_c| < |T|` (were `1 ∈ cT ∩ Tc`, `c` would be invertible in a
  finite monoid). In an aperiodic monoid the group of units is trivial, so
  *every* visible pivot strictly shrinks the first induction coordinate.
  This is the single point where aperiodicity powers termination — and it is
  why layer 1 refuses group-bearing input.

## 4 — The factorization

Fix the visible pivot `a`, `c = g(a)`, and `B = Δ ∖ {a}`. Every word with at
least one `a` factors uniquely as

```
w  =  u₀ · [ a u₁ a u₂ ⋯ u_{k-1} a ] · u_k          u_i ∈ B*  (u_k ∈ B^∞ on the ω side)
```

— the `a`-free prefix, the segment from the first through the last `a`, the
`a`-free suffix. The middle evaluates in the local divisor: with the
**block letters**

```
γ_u  :=  c·g(u)·c  ∈ T_c        (u ∈ B*)
```

the middle's value is the `∘`-product `γ_{u₁} ∘ ⋯ ∘ γ_{u_{k-1}}
= c·g(u₁)·c ⋯ g(u_{k-1})·c`, and the **empty middle is the `∘`-identity
`c`** — a word with exactly one `a` needs no case: its middle is the empty
`Γ`-word. Altogether

```
g(w)  =  g(u₀) · mid · g(u_k)          mid ∈ T_c
```

Two sub-recursions serve this, one per induction coordinate:

- **blocks** — the classes `g⁻¹(n) ∩ B*` of `a`-free words: the node
  `(B, T, g, n)`, alphabet strictly down;
- **the compressed word** — the sequence of block letters as a word over the
  finite alphabet `Γ = {c·n·c : n ∈ g(B*)} ⊆ T_c`: the node
  `(Γ, T_c, id, ·)`, monoid strictly down.

The finite-word target `t ∈ T` is then the disjunction over the (finitely
many) factorizations `t = p · x · s` with `p, s ∈ g(B*)`, `x ∈ T_c`:
*prefix in class `p`* ∧ *middle compresses into class `x`* ∧ *suffix in
class `s`* — plus the `a`-free case `t ∈ g(B*)` guarded by "no `a`".

## 5 — The three regimes (the ω target)

The ω target `P'` splits on the pivot's recurrence — the guards are
themselves one-letter LTL:

- **`G ¬a`** — the word is `a`-free: recurse `(B, T, g, P')` directly.
- **`F a ∧ FG ¬a`** — finitely many `a`, at least one: the prefix through
  the *last* `a` has class `m = p · mid` (a finite-word synthesis, layer 4 —
  note `mid` absorbs the final `a`, no suffix term), and the `a`-free
  infinite tail is handled by the node `(B, T, g, P'_m)` with the *shifted
  table* `P'_m(s′, e′) := P'(m·s′, e′)`. The recursion's ω-target being a
  table, not a pair, is exactly what makes this step compositional.
- **`GF a`** — infinitely many `a`: cut at the `a`-positions; the word is
  `u₀ · (a u₁)(a u₂) ⋯` and the segment values `δ_i = c·g(u_i)` drive the
  pair. The compressed ω-word `γ_{u₁} γ_{u₂} ⋯` over `Γ` is synthesized by
  the node `(Γ, T_c, id, P″)` where `P″` is the table transported from `P'`:
  a `T_c`-pair `(x, f)` of the compressed word determines the `T`-pair of
  `w` by finite bookkeeping on the boundary `c`'s (`γ`-products are
  `δ`-products with one trailing `c`; the `T`-idempotent is the stabilized
  power of the `δ`-block product, which exists and is reached aperiodically).
  The exact transport formula is **open point O2** — the shape is fixed, the
  `c`-bookkeeping must be pinned against [DG08] before coding, not
  improvised in the implementation.

Everything above is table arithmetic in `T` and `T_c`; no automaton is
consulted anywhere.

## 6 — The substitution workhorse

The compressed recursion returns an LTL formula over the alphabet `Γ`; it
speaks about the sequence of `a`-blocks. Translating it to a formula over
`Δ` evaluated on `w` is the module where all the fiddliness of this
construction concentrates — the analog of the cascade read-off in `bls`.
Three translations:

- **`Γ`-atom `γ`** — "the current block has letter `γ`": at an
  `a`-position, the finite-word block formula for `n` (from the
  `(B, T, g, n)` node, `γ = c·n·c`) evaluated on the segment up to — not
  including — the next `a` (or the end of the word). This is a
  **finite-word formula relativized into the host**: the block nodes
  synthesize in finite-word LTL, and the relativization maps their
  end-of-word into "the next letter is `a` / the word ends", carrying the
  weak/strong next distinction explicitly. The internal finite-word
  representation and its boundary discipline are **open point O1**.
- **`Γ`-next** — "at the next `a`-position": `X(¬a U (a ∧ ·))` anchored at
  the current `a`.
- **`Γ`-until** — until over `a`-positions: the standard positional
  relativization, `(a → φ†) U (a ∧ ψ†)` with the anchoring conventions
  fixed once in this module and documented there, not here.

The same machinery with position filter `¬a` serves the invisible-pivot lift
of layer 3 — one relativizer, two clients.

Block formulas are substituted at *every* occurrence of their `Γ`-atom
across the whole compressed formula: this is precisely where the project's
hash-consed DAG is load-bearing. The flat form of the output may be large;
the DAG shares every repeated block.

## 7 — Base cases

- **`|T| = 1`** — every class is everything or nothing: finite-word target
  `⊤`/`⊥` by identity, ω target by the single table bit `P'(1, 1)`.
- **`Δ = ∅`** — only the empty word exists; finite-word target: `ε`'s class
  is the identity; no ω-word exists, the ω target is `⊥`.
- **The identity class** contains `ε`; finite-word formulas are synthesized
  in finite-word LTL where the empty word is a model, so no special case —
  the boundary discipline of O1 owns this.

## 8 — Canonicity: the fixed choices

The claim of layer 0 — same language, same DAG — holds exactly when every
choice below is a function of the algebra alone, never of `D`:

- **Class identity.** The oracle's class ids come from the closure BFS,
  which is an artifact of `D`. This module re-keys every class by its
  **shortlex-least representative word** (total order on `AP` = input
  declaration order, `Σ = 2^AP` lexicographic) — a language invariant.
  All enumerations below use this key.
- **The pivot rule.** v0: erase invisible letters first, in letter order;
  then pivot on the least visible letter. (Deterministic alternatives that
  minimize `|T_c|` are open point O3 — they change the normal form, not
  its canonicity.)
- **Assembly order.** Factorization disjunctions in key order; connective
  shapes fixed by the DAG builder's existing normalizations.

Consequence, and the headline experiment: two different presentations of the
same language — `gf_aa_parity.hoa` and a fresh Spot translation of
`GF(a ∧ Xa)` — must synthesize the **identical DAG**, hash-consed. That
diff is a one-probe test and a paper-grade claim: no minimization-based
route can offer it, because no canonical minimal deterministic ω-automaton
exists — the algebra is canonical exactly where the automata are not.

## 9 — Cost and caps

Recursion depth is bounded by `|S¹| + |Σ|` (each node strictly shrinks one
lexicographic coordinate). Width: a finite-word node emits up to
`|T|²`-many factorization disjuncts; each `Γ`-atom substitution copies a
block formula reference (shared in the DAG). We commit to **no size bound**
here: the published proofs establish effectiveness, not economy, and this
project's rule is measure, then argue. The synthesis runs under caps (depth,
DAG size, time) and a blown cap is a **decline** — mirroring the oracle's
INCONCLUSIVE discipline: never a wrong formula, only a refusal. Upstream of
everything sits the oracle's own `|EM(D)|` materialization toll; this module
adds table arithmetic on the (smaller) quotient.

## 10 — Literature and positioning

- **Diekert–Gastin 2008, "First-order definable languages"** — THE reference
  implemented: the local-divisor proof of *aperiodic ⟹ LTL* over `Σ^∞`.
  Already cited by the oracle for the characterization chain; here its
  *proof* becomes the program.
- **Diekert–Kufleitner** (the local-divisor surveys) — the technique's
  history and the cleanest statements of the divisor lemma.
- **BLS FoSSaCS 2022** — the sibling systematic core (`aut2ltl/bls`): a
  Krohn–Rhodes cascade on the *transition monoid of the given form*. The
  comparison for the paper: presentation-dependent vs canonical input;
  form-preconditioned vs fragment-complete; holonomy machinery vs monoid
  induction. Neither dominates on size a priori — that is an A/B.
- Extend `../oracle/related_work.md` with the positioning digest for these
  when this lands; this document cites only what roots a definition.

## 11 — Open points (why this is a draft)

- **O1 — the finite-word discipline.** Block formulas are finite-word LTL
  relativized into the host (layer 6): fix the internal representation
  (weak/strong next, end-of-word) before any code.
- **O2 — the `GF` boundary transport.** The exact translation of the
  compressed `T_c`-pair to the host `T`-pair (layer 5): pin against [DG08]
  and record it here as a lemma with proof, then implement it.
- **O3 — pivot heuristics.** v0 pins least-letter; deterministic
  size-minimizing pivots are a later, measured change of normal form.
- **O4 — worked examples.** Hand-walk `fairness_example` (small, mixed
  acceptance) and `gf_aa_parity` (the flagship: the input whose cascade is
  form-blocked; `|S¹| = 6`). `tests/probes/oracle_dump.py` prints the
  classes; the walks go into this document as a layer of their own, in the
  oracle document's style.
- **O5 — module map** (draft, one role per module, mirroring the oracle):
  `morphism.py` (the two layer-1 tables + the canonical re-keying),
  `divisor.py` (the local divisor: carrier, `∘`, the strict-decrease
  assert), `blocks.py` (the `Γ` alphabet and block nodes), `relativize.py`
  (layer 6, both position filters), `dg.py` (the induction driver: pivot,
  regimes, assembly, caps — the only sequencing). Probe:
  `tests/probes/dg_probe.py`, one HOA per invocation, Spot-verifies the
  formula, ≤ 15 s.
- **O6 — wiring.** Whether this surfaces as a `Translator`, and where it
  sits relative to the gate (an LTL verdict with a formula attached), is
  the assembly's concern — out of scope here, exactly as gate wiring was
  for the oracle.

## Related ideas

**The Cayley construction → back into the current loop.** The quotient can
also be reified as an automaton: the right-Cayley automaton of `S(L)₊¹` —
states = classes, transitions = right multiplication by the letter classes,
acceptance derived from the profiles. Its transition monoid is the
right-regular representation of the quotient, faithful, hence counter-free
exactly when the verdict is LTL — a *canonical counter-free presentation* of
the language, on which the existing pipeline (the kr cascade, and for that
matter every translator in the portfolio) can be re-run when it declined the
original form. That makes the Cayley automaton a natural **fallback for
cascade declines**: not a rival to this module but a second consumer of the
same materialized algebra, re-entering the loop we already have instead of
building a new one. Its own open lemma is the acceptance condition — whether
an Emerson–Lei/Muller table on the Cayley transitions, filled from `Aprof`
via linked pairs, is well-defined from the infinity set alone (Maler–Staiger
1997 is the entry point; the residual quotient alone is provably too coarse
— `gf_aa_parity`'s is a single state). Parked here, not pursued: the DG
route needs none of those layers.
