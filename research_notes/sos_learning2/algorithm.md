# The legal learner — design in brief

Editors' note, not paper text. This file is the self-contained statement of
the algorithm and its design decisions: read it, then the assembled paper
(`../sos_learning2.md`), and you have the whole thread — no other document
is needed.

## The one-sentence design

**The learner never poses a hypothesis that is not a language.** Its belief
is at all times a *well-formed invariant* in the sense of [SωS26]
(`../sos_core.md`): a stamp (finite semigroup quotient of `Σ⁺`, with a
fresh identity `[ε]`) plus a conjugacy-saturated set of accepting linked
pairs — which, by [SωS26, Prop 4.1], denotes exactly one ω-regular
language, its own. Held canonicalized ([SωS26, Thm II], zero queries), the
belief is the syntactic invariant of the belief language: learning is a
walk through the space of ω-regular languages, from a day-one guess to
`𝓘(L)`, each step forced by one disagreement.

## State

- **Table** (private bookkeeping, never shown to the teacher): rows =
  access words; two column sorts matching Arnold's two context shapes —
  linear `(x, y, t)` reading `[x·u·y·t^ω ∈ L]`, ω `(x, y)` reading
  `[x·(u·y)^ω ∈ L]`; every entry one lasso membership query. Closed /
  consistent as in L\*. Classes `⟨u⟩`, each keyed by its shortlex-least
  row `u_c`. The table defines a **letter action** of `Σ*` on classes
  (`c·a` := class of `u_c·a`; well defined by closed+consistent) — *not
  yet* a morphism.
- **Belief** (the interface object): exported only when two query-free
  **legality checks** pass —
  1. *stamp legality*: `d·u = d·u_{⟨u⟩}` for every table word `u`, class
     `d` — the action factors through classes ⟺ the induced product
     `⟨u⟩·⟨v⟩ := ⟨u·v⟩` is well defined ⟺ the evaluation is a semigroup
     morphism (complete check: paper Lemma 3.4);
  2. *pair legality*: `P` — teacher bits on the keyed lassos
     `u_s·(u_e)^ω` of *all* linked pairs, memoized by lasso — is
     saturated under conjugacy `(s,(cd)^π) ∼ (s·c,(dc)^π)`.
  Then canonicalize ([SωS26, Thm II]) and present `𝓘_i = 𝓘(K_i)`.

## One split mechanism, three sources

Every class split is the same event: *two concrete lassos bearing one name
(pair of classes), whose teacher bits differ*, interpolated by a chain
that substitutes growing prefixes by their class keys; the chain's bit
flip convicts a frontier word against a row and mints the separating
Arnold context as a new column (Rivest–Schapire binary search, O(log)
queries). Sources:

1. **Harvest** — the teacher's equivalence counterexample vs the keyed
   lasso of its name (paper Thm 4.3; stem chain mints linear columns,
   loop chain mints ω-columns — Arnold's two shapes run backwards).
2. **Stamp escalation** — a stamp-legality violation `d·u ≠ d·u_{⟨u⟩}`:
   two probe queries under an existing separating column; either they
   differ (mint directly — for an ω-column the left factor must seed
   prefix *and* period tail, `(x°·r, y°·r)`) or a frozen-prefix chain
   finds the flip (paper Lemma 4.4).
3. **Pair escalation** — a pair-legality violation: the two conjugate
   pairs' common rotated lasso (rotation lemma on keys,
   `u_s·(u_c·u_d)^ω`) is queried once; its bit contradicts one side's
   cached bit; harvest chains apply verbatim (paper Lemma 4.5). A
   *self-posed equivalence query*: the learner referees its own
   inconsistency, no teacher EQ spent.

## Why it converges (paper §5)

- *Legality theorem*: every presented hypothesis is a well-formed
  invariant ⟹ denotes exactly one language `K_i`.
- *No false assent*: exact EQ assents ⟺ `K_i = L`; then the belief,
  being syntactic for `K_i`, IS `𝓘(L)`, byte-equal ([SωS26, Thm I,
  Thm II]). The stall is impossible **by typing**.
- *Progress*: every split (promotion, mint, either escalation, harvest)
  is witnessed by a genuine Arnold context ⟹ classes pairwise
  `≈_L`-distinct ⟹ ≤ N splits, ≤ N EQs, output-polynomial
  (paper Prop 5.3). Canonicalization only merges *in the view*; the
  table keeps witnesses, so nothing un-learns.

## The boundary (paper §6)

Relax the belief type — pose the bare classifier (classes + letter action
+ on-demand pair cache), skip legality — and the error signal turns
one-sided: predictions read literal words through the action, never a
class under a left context. Realized stall: `a → Xa`, four classes vs
`N = 5`, zero counterexamples, certified by an exact oracle — and the
stalled partition is *not a congruence*: its forced export is
non-associative, defines no language. Dichotomy theorem: an
exactly-certified fixpoint is canonical iff its kernel is a congruence —
certified stalls carry **no algebra at all** (paper Thm 6.2). Census
scale: 3137 of 6222 languages sit beyond the boundary. Framing (matters):
[AF21] — the right congruence under-determines the language — is a
*shared observation*, not a defect we fix; the FDFA line is complete for
acceptors on the near side, we cross to the algebra with self-posed
legality queries; Thm 6.2 is [AF21] refined in tighter vocabulary. Keep
§6 slim; the discipline is motivated by typing, not by the stall.

## The oracle (simplification the discipline buys)

Both sides of an equivalence query are genuine invariants, so membership
factors through the *product of the two stamps* on both sides: EQ is a
total exact scan of the product's linked pairs, one keyed lasso per cell,
and the minimal counterexample is a BFS on the product. No functionality
guard, no fallback machinery.

## Engineering deltas (code refactor pending — code derives from paper)

The census data quoted in paper §7 was measured with the pre-reboot
pipeline. The refactor should make the code match the paper, then rerun:

1. **Pair legality** in the learner: fill `P` on all linked pairs each
   round (memoize queries by lasso string); saturation scan
   (`O(|𝒞_T|³)` on triples `s,c,d` with `s·(cd)^π = s`); escalation =
   harvest on the self-generated counterexample. *This check is new
   behavior* — the previous learner never tested pair conjugacy mid-run.
2. **Canonicalize before EQ**: partition refinement on the export
   ([SωS26, Thm II] as implemented in the core pipeline); present the
   quotient.
3. **Product-scan oracle**: replace the guarded align-and-scan + fallback
   by the total product scan (both sides invariants); BFS-minimal
   counterexamples.
4. **Frame export** for the animation figures: dump the belief invariant
   at every certified round (`𝓘_0, 𝓘_1, …`); name aperiodic frames by a
   formula where feasible (day-one frames: `Even` opens at `b·Σ^ω`,
   `EvenBlocks` at `FG¬a`).
5. **Census rerun**: regenerate §7's per-phase counts (fill / harvest /
   legality / P; new: escalations by source). Expected invariants of the
   rerun: byte-equality on all 6222; the §7.3 relaxed-leg classification
   unchanged (it is the §6 learner, untouched); `a → Xa` still 1
   escalation / 0 cex / 1 EQ. Also new measurement: splits by source,
   frames per run.
6. Purge `fold`/`rep` vocabulary from the refactored code to match the
   paper: letter action, keys, candidate stamp.

Report companion to be created alongside the refactor; paper quotes the
report, per house rules.
