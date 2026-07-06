# The two engines — imported vocabulary, laws, and proof discipline

**Status:** working quarry for `sos_toltl.md` §5. This note absorbs, once and
for all, the useful content of the two automaton-level construction notes
(the single-state peel and the k-window SCC transcription of the aut2ltl
portfolio) so that the paper can define its engines on `𝓘(L) = (𝒞, λ, M, P)`
directly, with no reference to any prior automaton construction. Everything
here is either (i) already transposed to the Cayley machine `Cay(L)` (states
`𝒞`, edges `c →^a M(c, λ(a))`, layers = R-classes), or (ii) recorded in its
letter-level form because its transposition *is* one of the paper's open
tasks (Def 5.5, the exactness theorem). Items marked **DIES** are recorded
only to say why they do not come along.

Throughout, "letter" means a class of the λ-quotient alphabet `Σ_λ = λ(Σ)`;
in an emitted formula a letter renders as the Boolean disjunction of the
concrete letters in its class (atomic propositions restored last). All
per-class letter sets below are subsets of `Σ_λ`, and all emptiness/overlap
tests are set operations — the automaton originals' symbolic guard calculus
(BDD disjointness, rectangle covers) is the concrete-alphabet shadow of these
sets and stays an implementation concern.

## 1 — The per-layer letter split (the walk engine's raw data)

Fix a layer `R` (an R-class of `S(L)₊¹`) and a class `c ∈ R`. Every letter
`a ∈ Σ_λ` does exactly one thing at `c` — the action is a function, there is
no guard nondeterminism to manage:

```
L(c) = { a : c·a = c }            -- stutter at c
M(c) = { a : c·a ∈ R, c·a ≠ c }   -- move within the layer
E(c) = { a : c·a ∉ R }            -- exit: strict R-descent (Lemma 5.3)
A(c) = { a : ∃ c' ∈ R, c' ≠ c, c'·a = c }   -- anchors: letters entering c
I(c) = L(c) ∪ A(c)                -- letters consistent with "the run sits at c"
```

**Promotion, absorbed by the diagonal.** The automaton construction had a
build-time *promotion*: a self-loop letter with no other occurrence inside
the component "names its state" and is reclassified as entering. On the
algebra this is exactly why Def 5.4 (anchored layer, k = 1) allows the
partial-constant-fixing-its-own-target case: a letter that stutters at `c`
and touches no other class of `R` is a reset onto `c`. The promoted split is
the definition; no separate promotion pass exists. What remains in `L(c)`
after the (definitional) promotion are the **necessary** stutter letters —
those also live at another class of `R`, which no stateless observer can
attribute. Def 5.4 then reads: every letter's within-layer action is a
partial identity (shared idleness allowed) or a partial constant (diagonal
allowed); *mixed* actions — stuttering at one class while moving another
class of `R` within `R` — are what condition (A) at `k = 1` excludes.

**Derived facts (transpose verbatim, same one-line proofs).**
- *Sharp sojourn ends:* `L(c) ∩ M(c) = ∅` — trivially, the action is a
  function. (In the automaton this needed P2; determinism of `Cay(L)` gives
  it outright.)
- *Anchors partition:* under (A), a letter in `M(c)` is a reset, so its
  target is one class, uniformly over sources — the P1 of the original,
  now a consequence of "partial constant".
- *Tightness:* for `|R| ≥ 2` strong connectivity gives every class a
  non-self in-edge inside `R`, so `A(c) ≠ ∅`.

## 2 — The k = 1 brick set (the walk engine's label, acceptance excised)

The transcription of one layer `R`, entered at a class `r` (see §5 for why
the entry class is always known), under (A) at `k = 1`. The **stem-side**
bricks, transposed with their motivating readings:

```
sojourn(c)  =  L(c) W M(c)∨E(c)-guards…      -- see the E-note below
step        =  ⋀_{c ∈ R} ( A(c) → X sojourn(c) )      -- the anchored law
leave(c)    =  L(c) U ⋁_{a ∈ E(c)} ( a ∧ X φ_{c·a} )  -- stutter, then exit to the child
LEAVE       =  leave(r)  ∨  ( sojourn(r) ∧ ( step U ⋁_{c ∈ R} ( A(c) ∧ X leave(c) ) ) )
```

- `sojourn(c) = L(c) W M(c)`: having just anchored into `c`, stutter on
  `c`'s necessary letters until a move carries the walk onward — or forever:
  the weak arm makes parking *legal*; whether a parked tail *accepts* is
  the window engine's business, never the law's. This split (legality in
  the law, acceptance elsewhere) is what keeps every `U`-vs-`W` case
  analysis out of the law. **E-note:** in the original, exit letters are
  not in the sojourn's strong arm; the `W`'s arms here are `L(c)` vs
  `M(c)`, and an exit letter simply ends the in-layer obligation — the
  `LEAVE` branch owns it. (When rewriting §5, state the sojourn as
  `L(c) W (M(c) ∨ ⋁E(c))` or handle exits by the `U`-escape as the
  original does; decide once, prove once.)
- `step`: **the trigger identifies, the consequence legislates.** The
  anchor (trigger) fires exactly at its target — that is condition (A) —
  and the consequence constrains the next letters to actual Cayley edges of
  the identified class. This division of labor is the load-bearing idea of
  the whole transcription and survives every widening (§4).
- `φ_d` is the memoized child label rooted at class `d = c·a`: at most
  `|𝒞|` distinct children ever, the output DAG is class-indexed.
- `child handoff:` the exit brick `a ∧ X φ_d` *names* `d` deterministically
  (`d = c·a` is a table entry), so the child starts with certainty of its
  root class — the transposed and strengthened form of the original's
  "initial state known at position 0" (its exits could be nondeterministic;
  ours cannot).

**What is excised.** The original's acceptance machinery — per-state colors
`F_i`, `F_all`, the fairness `⋀ GF(⋁ anchors-into-F_i)`, park terms
`A(s) ∧ XG L(s)` with color-membership verdicts — has **no counterpart**:
Lemma 5.2(ii) proves no condition on recurring classes or Cayley edges
recognizes `L`. Every acceptance decision routes through `P`:

- **Park, re-based on pairs.** A tail parked at `c` on a single stutter
  letter `a ∈ L(c)` has accepting pair `(c, λ(a)^π)` — `c·λ(a) = c` gives
  linkage — so the park verdict is the lookup `(c, λ(a)^π) ∈ P`, and a
  park *term* is emitted only when the lookup accepts. A park on a *mix*
  of stutter letters is already the general window problem: the pair
  depends on which loop words recur, i.e. on condition (B) at the parked
  class. Parks are the width-1 fringe of the window engine, not a separate
  mechanism.
- **STAY∞, re-based on windows.** The stay-forever branch of a final layer
  is the window engine's output (§3), guarded by the walk's bricks only
  for legality.

**Construction-time reductions (needed for exact-minimal output; both are
table tests, not formula rewrites):**

- *Sojourn-tautology collapse.* If `L(c) ∪ M(c) ∪ E(c) = Σ_λ` — every
  letter legal at `c`, which on the complete machine `Cay(L)` is **always
  true** — the sojourn `L(c) W M(c)` is a tautology only when its arms
  exhaust the alphabet; with exits present the collapse test is
  `L(c) ∪ M(c) = Σ_λ`. Collapsed sojourns delete their law rows. This is
  the mechanism by which `GF(aa)`'s law evaporates entirely and E0's
  predicted output is literally `GF(a ∧ Xa)` with no simplifier: on
  `Cay(GF(aa))` every class has all letters in-machine, the frozen layer's
  windows carry the whole content.
- *Park-subsumption drop.* If `L(c) ⊆ A(c)` (every stutter letter of `c`
  also anchors `c` — after the definitional promotion this means the
  parked run re-fires `c`'s entering trigger at every position), the
  recurrence disjunct already covers the park and its term is dropped.
  Graded version: `Stay_k(c) ⊆ Enter_k(c)`.

**Degeneracies (no special-casing — the equation covers them):** a final
layer with no accepting pair `(s, e) ∈ P`, `s ∈ R` has `STAY∞ = false`
(the paper's `GF(aa)` moving layers); a terminal layer (no exits) has
`LEAVE = false`; a singleton layer with `A = M = ∅` degenerates to
`park-or-leave` — the frozen case, §3; the initial layer `{[ε]}` is always
transient and stutter-free (no letter maps to or fixes the fresh identity),
so the original's elaborate start policy at the automaton's `q0`
evaporates: the walk's position 0 is the singleton `[ε]` with pure exits.

## 3 — The frozen-class closed form (the window engine's shape)

The single-state peel's closed form, transposed to a frozen class `c` (all
letters neutral — the walk stabilized), generalizing its petals to windows:

```
Final(c)   =  STAY∞(c)  ∨  LEAVE(c)
STAY∞(c)   =  G(σ) ∧ WindowAccept(c)         -- σ = ⋁ L(c): stay legal (on Cay: σ = ⊤)
LEAVE(c)   =  σ U ⋁_{a ∈ E(c)} ( a ∧ X φ_{c·a} )
```

with `WindowAccept(c)` the (B)-engine's output: a Boolean combination of
`GF(w)` / `FG(¬w)` over length-`k′` windows `w`, selected by which recurring
window sets fold from `c` to loop idempotents `e` with `(c, e) ∈ P`. The
peel's original `⋀_i GF(σ_i)` — one petal disjunction per acceptance set —
is the width-1, generalized-Büchi instance: its per-petal transition marks
are the letter-visible shadow of `P`'s pairs, and its insistence on
transition-based acceptance ("a single state encodes a different petal set
per acceptance set, which state-based marking cannot express") is the
automaton shadow of ω-acceptance being a set of *pairs*, not a subset of
classes. Two design commitments carry:

- **Acceptance lives on the loop content, read per petal/window** — never
  on the state/class. (The algebra's petals are inherently `k`-windows:
  the "marks" are class values of words, and single letters are only the
  degenerate rung.)
- **Union absorbed by disjunction.** Overlapping ways to accept are a `∨`,
  never a determinization: on the algebra, each accepting pair `(c, e) ∈ P`
  is one more disjunct, never a constraint on the others.

Degeneracies transpose: no exits ⟹ `LEAVE = false`; no accepting pair at
`c` ⟹ `STAY∞ = false` and the run must leave (the strong `U` forces it);
`P` trivial at `c` (every idempotent accepts) ⟹ `WindowAccept = ⊤` and
`STAY∞ = G σ` — condition (B) at width 0, the "weak" stratum of §5.6(2).

## 4 — The graded window ladder (raw material for Def 5.5)

The widening from letters to `k`-windows, recorded in full because freezing
its algebraic form *is* Def 5.5's open task.

- **The trap, and the fix.** "The last `k` *anchors*, with stutter
  stretches between them" does not work: stretches are unbounded, the
  trigger would need `U`-nesting and the law would stop being `X`-shaped.
  The window is over **adjacent letters**, and a stutter stretch is
  absorbed by weakening a context letter's constraint from `A(v)` ("just
  entered `v`") to `I(v) = L(v) ∪ A(v)` ("consistent with sitting at
  `v`") — the **stutter abstraction**. The window stays rigid; the law
  stays `X`-shaped:
  `I(v₁) ∧ X I(v₂) ∧ … ∧ X^{k−1} a → X^k sojourn(target)`.
- **The pair data (k = 2), as sets of letter pairs:**
  `Enter₂(c) = ⋃ { I(v) × {a} : v·a = c, v ∈ R }` (a diagonal/promoted
  entry contributes `I(c) × {a}`), and `Stay₂(c) = I(c) × L(c)`. Both are
  unions of rectangles with one-letter components; every test decomposes
  rectangle-wise and the label never materializes a product alphabet.
- **The graded preconditions:** P1ᵏ — the `Enter_k(c)` partition
  (pairwise disjoint over `c ∈ R`); P2ᵏ — `Stay_k(c)` meets no foreign
  `Enter_k(c′)`; the diagonal overlap `Stay_k(c) ∩ Enter_k(c)` is exempt
  (either reading lands at `c`). Level `k` passing implies level `k + 1`
  passing: the ladder is monotone, first-fit adopts the smallest passing
  level, and **no equivalence gate exists at any level** — each level's
  label is exact by construction. For Def 5.5 the candidate equational
  form: products of `k` within-layer actions, stutter positions
  `I`-weakened, act as constants — local `k`-definiteness of the layer's
  action semigroup modulo its neutral part.
- **What k = 2 strictly gains:** a letter may stutter at `v` and move
  `u → t` (`u ≠ v`) provided `I(v) ∩ I(u) = ∅` — the predecessor letter
  disambiguates the current one. The phase becomes a function of the last
  two letters where it was not of the last one.
- **The trigger table (the graded emitter's whole structure).** Windows at
  position `p ≥ k` are **full** (`k` adjacent letters ending on an
  entering edge, `I`-weakened context); positions `0 < p < k` use
  **truncated windows rooted at the entry class** — actual Cayley paths of
  length `p` out of the layer's entry class, the certainty of the entry
  standing in for missing context (on the algebra the entry class is
  *known exactly*: the parent's exit brick named it — §2). Each window
  class contributes `(trigger, offset, target)` rows; full rows generate
  the `G`-wrapped law, the `GF` fairness disjuncts, the park terms
  (`trigger ∧ X^offset G L(target)`, pair-verdict-gated per §2) and the
  `LEAVE` witnesses (`trigger ∧ X^offset leave(target)`); truncated rows
  generate the same four shapes one-shot, not `G`-wrapped. `k = 1` is the
  level where the truncated range `0 < p < 1` is empty and the table
  collapses to §2's label clause for clause — one production graded by
  `k`, no hand-matching between levels.
- **Cost note:** per-edge at `k = 2`, per-path beyond — cap `k` at 2–3
  (the experiments spec's cap).

## 5 — The phase lemma and the exactness discipline (the proof scheme)

The exactness theorem of §5.2 ((A) on traversed layers + (B) on final
layers ⟹ the label defines `L`) should be proved by the imported scheme:

- **The phase lemma.** Under the level-`k` preconditions, at every position
  of a word confined so far to `R`, the occupied class is the target of
  the last full-or-truncated entering window, and every letter since lies
  in that class's necessary stutter set. On `Cay(L)` the walk itself is
  deterministic, so the lemma's content is purely about *letter-visible
  recovery* of the walk, not about run uniqueness.
- **The license for eager triggers (the lemma's corollary — keep this
  paragraph, it is the deepest sentence in the import).** A trigger may
  fire *spuriously* — the window looks like an entry into `c` while the
  walk sits elsewhere — but the preconditions force every look-alike
  window to tell the same truth about the next class, so the promise made
  is true anyway. This matters because LTL has no state: a law cannot be
  conditioned on "the walk is at `c`" — the phase is what the formula is
  *transcribing*, not something it can consult — so any per-edge law is
  necessarily eager. P1ᵏ/P2ᵏ are exactly the price of that eagerness: the
  eager law is not a tolerable over-approximation, it *is* the
  transcription, and no tighter law exists to compare it against.
- **Three legs.** *Uniqueness*: immediate on `Cay(L)` (deterministic,
  complete — the original needed its phase lemma here; we get it by
  construction). *Completeness*: an accepting word either stays in some
  final layer forever — its walk satisfies the sojourns and laws (spurious
  firings harmless by the license), and its tail's recurring windows are
  (B)-accepted — or descends; each descent step is a `LEAVE` witness with
  the child taking over at a named class. *Soundness*: the formula forces
  the walk by induction along the word, one window at a time — each active
  sojourn confines the next letter to actual Cayley edges, each trigger
  hands over to the entered class's rows, `WindowAccept` certifies the
  pair against `P` under (B), and the assembled path *is* the walk of the
  word. The argument never consults whether a layer is accepting,
  rejecting, or terminal — each branch transcribes one run shape exactly,
  and the union of shapes is everything a word can do. That is why the
  degeneracies of §2–3 need no cases and why no equivalence gate exists.
- **Where the fragment ends (the (A)-fail stratum, stated honestly).** A
  genuinely shared *moving* window — `Enter_k(c) ∩ Enter_k(c′) ≠ ∅`,
  `c ≠ c′`, at every affordable `k` — means the phase is not a function of
  the word's recent letters at all. Disambiguating with a fresh
  proposition is not legal *inside* LTL (projecting it out lands in QPTL);
  as an *output wrapper* the move is legitimate — that is §6's
  definitional format, and the distinction (illegal inside the
  transcription, legitimate as an export) deserves the remark §6 already
  reserves for it.

## 6 — Literature anchors to keep (for §9, replacing the internal citations)

**⚠ Provenance caveat:** the attributions below are inherited from the source
construction note, *not yet verified against the library* — none of these
papers is in `papers/` at the time of writing. Per the citation rule, each
must be read before it enters `sos_toltl.md`; until then this list is a
shopping list, not a bibliography.

- The `k = 1` precondition is a stuttering relaxation of **local automata**
  (all transitions on a letter share their target — Chomsky–Schützenberger
  1963; Berstel–Pin 1996): erase each class's stutter letters and the
  layer is local on its anchors. "Definite modulo stuttering."
- The graded ladder relaxes **k-definite** (Perles–Rabin–Shamir 1963) and
  **locally testable** (Brzozowski–Simon 1973) recognizability the same
  way: the law is the allowed-factor constraint (digrams at `k = 1`,
  trigrams at `k = 2`), the entry rows the allowed-prefix constraint, the
  window fairness the ω-substitute for allowed suffixes, `I(v)` the
  stutter abstraction keeping the window rigid over unbounded sojourns.
  Algebraic counterparts: varieties `D`, `LI`, locally testable — our
  per-layer equations are their localizations to R-classes.
- The frozen-class closed form is exact on the **very-weak (1-weak)**
  fragment locally (a frozen class is a 1-weak component of `Cay(L)`);
  the walk+frozen assembly is the cascade of such bricks down the R-order
  (the Krohn–Rhodes reset-brick connection §5.2 already flags).

## 7 — What DIES in the import (recorded so nobody goes looking)

- **The `Label = Some | NotLTL | ⊥` plumbing.** On the algebra, step 0
  decided aperiodicity before any engine runs: no child ever returns a
  non-LTL verdict inside §5, and "decline" is not a value but the
  dispatch to the next stratum ((A)-fail ⟹ layer-internal decomposition /
  DG fallback; (B)-fail ⟹ DG on the tail algebra) — measured, not
  propagated.
- **Both witness lifts** (the peel's restricted-guard left-quotient lift;
  the SCC production's reaching-word lift with all-other-target
  subtraction, and its `PROBABLY_NOT_LTL` degradation). Certificates are
  born canonical at step 0 (§4.4); there is no boundary to lift across.
- **The state-based/transition-based form negotiation.** The original pair
  split along acceptance-visibility lines (state colors vs petal marks) —
  the algebra's conditions (A) and (B) are that split stated once,
  cleanly, as properties of the language; no form is requested from
  anyone.
- **The daisy test (`hasNonSelfIncoming`) and the initial-SCC restriction.**
  Subsumed by the R-order: Lemma 5.3 hands every layer, not just the
  initial one, and the frozen case is detected by `L(c) = Σ_λ`, not by
  edge-shape inspection.
- **Form dependence itself** — "an input can pass in one form and fail in
  another". On `Cay(L)` the tests are evaluated on the canonical object;
  pass/fail is a function of `L`. (The paper states no comparison with
  automaton-level transcription at all — that construction does not exist
  in its world; the E3/E4c experiments keep the comparison alive as
  internal diagnostics only, and a reverse instance — algebra strictly
  harder than some form — would be a research finding to bring back.)
- **The virtual-history surgery** (prepending `k−1` letters to uniformize
  the start): unnecessary — the fresh identity `[ε]` makes the global
  start trivial (§2), and layer entries are certainty-rooted by the parent
  handoff.
