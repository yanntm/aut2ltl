# Learning the Syntactic ω-Semigroup — reboot skeleton

**Status.** Shadow outline of the rebooted paper (started 2026-07-19). This
folder is a fresh start; `../sos_learning.md` and its `../sos_learning/`
parts are the **reservoir** — we copy from them, we never edit them. In this
file: plain bullets = content to be written; blocks introduced by
`[RESERVOIR §x]` are carried text (verbatim or lightly adapted), already
selected for keeping; `[proof carries]` means the reservoir proof transfers
with at most notation touch-ups. Numbers quoted from the old §6 are
placeholders — to be regenerated after the code refactor (the census-scale
*facts* are expected to stand; per-phase query counts will shift with the
new pair-escalation mechanism).

---

## Decisions of record (design discussion, 2026-07-19)

1. **The belief is a language.** The learner's epistemic state, whenever a
   conclusion is drawn from it or it is shown to the teacher, is a
   *well-formed invariant* — hence, by [SωS26, Prop 4.1], an ω-regular
   language, held in canonical (syntactic) form: `𝓘_i = 𝓘(K_i)`, the
   syntactic invariant of the belief language `K_i`. No hypothesis that is
   not a language is ever posed.
2. **The table is private bookkeeping.** Rows, two-sorted columns, bits,
   open slots: the refinement-support structure, tracking progress and
   holding the ≈_L-witnesses. It never crosses the wall to the teacher.
3. **Hygiene = legality of the export, two checks, both query-free.**
   (a) *Stamp level*: the fold kernel is a two-sided congruence — the old
   sweep, with old Lemma 5.2 as its completeness ("the check decides
   congruence"). (b) *Pair level*: the pair set is saturated under
   conjugacy — new check; mid-run, two conjugate pairs can hold differing
   teacher bits while the stamp is still coarser than `≈_L`. An unsaturated
   export denotes no language and is not presentable.
4. **One split mechanism, three sources.** Every split is the same event:
   *two concrete lassos bearing one name whose teacher bits differ*,
   interpolated by the representative chains to a flip, minting an Arnold
   context that witnesses the split. Sources: (i) the teacher's equivalence
   counterexample (harvest); (ii) a sweep escalation's probe pair; (iii) a
   pair-saturation violation — the conjugate pairs' common lasso
   ([SωS26, Lem 4.1]) queried once, disagreeing with one side's
   representative lasso: a *self-posed* equivalence query, caught without
   the teacher's help.
5. **Renormalize always.** After hygiene, canonicalize the export by
   [SωS26, Thm II] — zero queries — and present `𝓘(K_i)` itself.
   Theorem II preserves the denoted language, so any counterexample
   against the view is a misprediction of the table's fold, processable by
   the chains. Merges happen only in the view; the table keeps the
   witnesses, so no progress is lost.
6. **The oracle is a product of stamps.** Both sides of an equivalence
   query are genuine invariants; membership factors through the product
   stamp on both sides, so EQ is a total exact scan of the product's linked
   pairs, and the shortest counterexample is a BFS on the product. The old
   functionality guard, fallback product, and work caps are deleted.
7. **The stall is a theorem, not a plot twist.** A well-formed invariant
   denotes exactly one language, so an exact oracle can never falsely
   assent: permanent stalls are impossible *by typing*. The old §4.2/§5.3
   material (Prop 4.4, `a → Xa`, non-associative export, Thm 5.3) moves to
   a "necessity" section: relax the belief type to an acceptor and the
   stall returns — the reason acceptor-typed strategies are inherently
   incomplete.
8. **The day-frame animation.** The stabilized exports between events form
   the belief sequence `𝓘_0, 𝓘_1, …` — each frame an ω-regular language,
   drawn with the core paper's conventions and where possible *named* by a
   formula (`Even`'s run opens at `b·Σ^ω`; `EvenBlocks`' at `FG¬a`). Old
   Figure 4, promoted from footnote to organizing picture.
9. **Soundness conditions verified in discussion** (no open theory issue):
   pair escalation reduces to harvest chains on a self-generated
   disagreement (one extra query + `O(log)`); Thm II's language
   preservation keeps counterexample processing sound; no-false-assent
   consumes EQ exactness (bounded-oracle caveat kept as a remark, as in the
   old §5).

**New proof obligations** (the only genuinely new mathematics):

- *Pair-escalation lemma* (§4): from a saturation violation, one membership
  query and one chain yield a witnessed class split. (Sketch fixed in
  decision 4(iii); write it in Lemma 4.5's style.)
- *Legality theorem* (§5): at every equivalence query the presented object
  is a well-formed invariant — congruence from the sweep (old Lemma 5.2 ⟸),
  saturation from the pair check, `P` total by construction.
- Everything else *shortens*: the old Theorem 5.1's canonicity argument
  collapses to a paragraph consuming [SωS26, Thm I, Cor 4.2, Thm II].

---

## Title page

Title: **Learning the Syntactic ω-Semigroup** (unchanged).
Authors, shadow-draft banner, provenance sentence as in reservoir.

## Abstract — draft

The syntactic ω-semigroup of a regular ω-language `L` is its canonical
algebra, recently materialized as a computable, serializable invariant
`𝓘(L)` [SωS26]. This paper shows the invariant is learnable, in Angluin's
MAT model, from lasso membership and equivalence queries alone. The design
principle is a typing discipline: the learner's belief is at all times an
ω-regular language, held in canonical form — every hypothesis it presents
is a well-formed invariant, the syntactic invariant of its own belief
language. The discipline has a structural payoff: a well-formed invariant
denotes exactly one language, so an exact equivalence oracle can never
falsely assent, and the permanent stalls that afflict acceptor-typed
learners are impossible by construction. Keeping the belief legal is
cheap: two query-free checks — the fold kernel a congruence, the pair set
saturated under conjugacy — and every violation is a free progress signal,
a disagreement the learner catches on its own and converts, by the same
chain mechanism that processes the teacher's counterexamples, into a
witnessed class split. The fixpoint is `𝓘(L)` itself, byte-equal to the
constructed reference, at output-polynomial query cost. The discipline is
also necessary: relaxing the belief type to a bare acceptor stalls the
learner permanently — already on `a → Xa`, certified by an exact oracle,
on classes that provably carry no algebra at all. On a complement-closed
census of 6222 languages the learner reconstructs every syntactic
invariant byte-for-byte; half the census is unreachable by any
acceptor-typed strategy; and LTL-definability is read off each learned
invariant — a question no family of acceptors answers.

*(Tune length/claims after §5–§6 are written; the "half the census"
number carries from the reservoir ablation.)*

## 1. Introduction

- Opening move: active learning *is* the reconstruction of a canonical
  invariant through queries (L\*/Myhill–Nerode framing — reservoir §1's
  first paragraph carries nearly verbatim, it is already solution-shaped).

[RESERVOIR §1, para 1] Active learning asks a machine to reconstruct an
unknown language *exactly*, from experiments alone. … (keep the L\* /
MAT / canonicity paragraph as is.)

- What breaks at ω: no minimal deterministic acceptor [AF21]; history of
  substitute targets, all acceptors (condense reservoir §1 para 2).
- The canonical object exists and is now *material*: `𝓘(L)` of [SωS26] —
  two sentences, the core paper carries the weight.
- **The thesis, stated up front**: this paper's learner never poses a
  hypothesis that is not a language. Its belief is a well-formed
  invariant at every step; the teacher sees ω-regular languages in
  canonical form and nothing else. From that typing discipline the rest
  follows: two-sided error signal, no stalls, convergence to `𝓘(L)`.
- The one-sentence contrast with the field: every prior ω-learner poses
  hypotheses that are not canonical objects of any language — and the
  stalls, patches, and family-of-acceptor targets of the literature are
  the price (forward-pointer to necessity §6 and related work §8).
- Contributions (rewrite of reservoir's three, reordered):
  1. The learner: table as bookkeeping, belief as well-formed invariant,
     one split mechanism with three sources; limit byte-equal to [SωS26]'s
     construction (§3–§4).
  2. The typing theorem: legal beliefs make the error signal two-sided —
     no false assent — and the discipline is *necessary*: acceptor-typed
     relaxation stalls permanently on a two-letter LTL formula, on classes
     carrying no algebra (§5–§6).
  3. Experiments: census-scale byte-exact reconstruction, the ablation as
     type relaxation, ROLL baseline, definability read-offs (§7).
- Closest prior work: [US20] identified the target, no effective instance
  (infinite alphabet of ω-power letters); the rotation lemma supplies the
  finiteness (condensed from reservoir §1; details in §8).

## 2. Background

### 2.1 The MAT model

[RESERVOIR §2.1] — carries nearly verbatim: "Exact learning from
queries", "L\* in one paragraph", "Why it converges: a canonical target",
"What survives at ω, and what breaks", "Conventions". These paragraphs
are already written for the reboot's framing (canonical-invariant view of
L\*); only the forward-pointers change.

### 2.2 The invariant, recalled from [SωS26]

- Much leaner than reservoir §2.2: the core paper now exists and is cited
  wholesale. One paragraph per notion, no re-derivation:
  lassos; stamp `(𝒞, λ, ·)` with fresh `[ε]` (and why freshness matters to
  the learner: non-empty representative loops); linked pairs name lassos;
  the invariant `⟨𝒮, P⟩` and lasso membership; **denoting** and
  **well-formed** ([SωS26, Defs 4.1, 4.2]); the two facts the learner
  consumes: [SωS26, Prop 4.1] (well-formed ⟺ one verdict per lasso;
  denotes exactly one language, its own), [SωS26, Cor 4.2] (invariants
  denoting `L` live exactly at stamps refining `≈_L`, pair set forced);
  the rotation lemma [SωS26, Lem 4.1] and the membership tests
  [SωS26, Def 4.3, Lems 4.2–4.3]; canonicalization [SωS26, Thm II] —
  quotient by partition refinement, zero queries, *language-preserving*.
- `N` convention (classes incl. `[ε]`) — reservoir sentence carries.
- Shortlex/serialization convention — reservoir sentence carries.

### 2.3 Running examples and the teacher

[RESERVOIR §2.3] — the three running examples (`GF(aa)`, `Even`,
`EvenBlocks`) with Figures 1–2 (automata + target invariants) carry as
is, including figure files.

- The stall specimens (`a → Xa`, `a ∧ XG¬a`) move: introduced only
  briefly here (or not at all), presented fully in §6 where they are
  used. Decide at drafting time whether Figure 3 stays here or moves.
- **The teacher, simplified**: membership = one deterministic run;
  equivalence = exact scan of the product of two stamps — the hypothesis
  is a genuine invariant, so both verdicts factor through the product,
  every cell decided by its keyed lasso, *no functionality assumption*.
  Shortest counterexample = BFS on the product (shortest stem, shortest
  loop, shortlex). The reservoir's guard/fallback/self-check apparatus is
  deleted; keep the trust-anchor honesty note (oracle and validation both
  anchored on constructed `𝓘(L)`; independence via random-lasso
  cross-check).

## 3. The learner's state

### 3.1 The table (bookkeeping)

[RESERVOIR §3] — Definition 3.1 (two-sorted table: linear columns
`(x, y, t)`, ω-columns `(x, y)`), Definition 3.2 (closed, consistent,
access words, minting), Lemma 3.3 (coherence; fold `ψ`; folds compose
over literal concatenation) — all carry with proofs. The framing changes:
the table is introduced *as bookkeeping* — "the machine's private ledger
of witnesses" — not as the hypothesis.

- The two sorts divide the labor as Arnold's shapes do (`Even` vs
  `EvenBlocks` paragraph carries).
- Day-one tables (reservoir Tables 1–2) carry — but now each is
  immediately followed by its *export*, making the day-one beliefs the
  first frames of the animation.

### 3.2 The export: belief as a well-formed invariant

- Definition: export of a stabilized table = `⟨𝒮_T, P⟩` (product
  `c·c' := fold(c, rep(c'))`, `λ`, `P` = teacher truths on representative
  lassos of all linked pairs), then canonicalized by [SωS26, Thm II].
- **Legality checks** (the hygiene, both query-free):
  - stamp legality: `fold(d, u) = fold(d, w_ψ(u))` for all table words
    `u`, classes `d` — old Lemma 5.2 carries with proof ("the sweep check
    decides congruence");
  - pair legality: `P` saturated under conjugacy steps
    `(s, (cd)^π) ∼ (s·c, (dc)^π)` — checked on the table's classes,
    `O(|𝒞_T|³)` table work.
- The belief language `K_i := L(𝓘_i)`; by [SωS26, Prop 4.1] it is the
  unique language the belief denotes. Prediction on a lasso = the
  invariant's own lasso membership (the reservoir's fold-orbit
  prediction, now *defined* as Definition 3.4 of [SωS26] applied to the
  export — one object, one semantics).
- Figure (promoted old Figure 4): the day-one beliefs of `Even` and
  `EvenBlocks`, drawn — `b·Σ^ω` and `FG¬a` — the first animation frames.
- The `P`-cache paragraph (reservoir §3 "cache of teacher truths")
  carries: `P` is never wrong, only indexed by classes that may split.

## 4. The loop: reap and sow

### 4.1 The split mechanism (one lemma, three sources)

- State the unified mechanism first: *two concrete lassos, one name, two
  teacher bits* → representative chains → flip → minted Arnold context →
  class split. Then the three sources as three short subsections.

[RESERVOIR §4.1] — the chains display (`γ_i` stem chain, `δ_i` loop
chain), Lemma 4.1 (stem harvest), Lemma 4.2 (loop harvest), Theorem 4.3
(harvest: one split per counterexample, `O(log(|w| + |𝒞_T|·|z|))`
queries) — carry with proofs. The normalization paragraph carries.

- Worked example: reservoir's twin first-counterexamples example
  (`Even` gets `(ε, aab)` → stem chain; `EvenBlocks` gets `(ε, b·aa)` →
  loop chain; "Arnold's two shapes, run backwards") carries with
  Tables 3(a)–(d).

### 4.2 Sow: the legality escalations

- Sweep escalation: [RESERVOIR §4.3] Lemma 4.5 (two branches, the
  ω-mint's reseeded-period shape) carries with proof and remark; the
  full worked sweep on `Even` (Tables 4–6) carries — it is the best
  pedagogy in the reservoir.
- **Pair escalation (new)**: state and prove the new lemma — a
  saturation violation `(s,(cd)^π) ∈ P ⊕ (s·c,(dc)^π) ∈ P` yields, via
  the common lasso of [SωS26, Lem 4.1] built on representatives, a
  disagreeing lasso pair with one name; one membership query + one chain
  splits a class. Style and length of Lemma 4.5.
- Prefix-independence results: [RESERVOIR §4.3] Prop 4.6 (the two shapes
  and vacuous prefixes), Cor 4.7 (a prefix-independent gap is ω-sorted;
  sort discipline of every run), Lemma 4.8 (prefix-independence needs
  depth) — carry with proofs; they now read as structure of the *sow*
  phase.

### 4.3 The loop, assembled

- Pseudocode (rewrite of reservoir's box):

```
    R ← {ε} ∪ Σ;  E_ω ← {(ε, ε)};  E_lin ← ∅
    repeat:
        fill entries; repair closedness and consistency      (queries)
        stamp legality: sweep check; escalate → split, restart
        fill P on all linked pairs                           (queries)
        pair legality: saturation check; escalate → split, restart
        𝓘_i ← canonicalize ⟨𝒮_T, P⟩          ([SωS26, Thm II], no queries)
        pose EQ(𝓘_i)
        if yes: output 𝓘_i  — it is 𝓘(L)
        else: harvest the returned lasso → split
```

- The animation: the frames `𝓘_0, 𝓘_1, …` for the running examples —
  `EvenBlocks` run as the split ledger (reservoir Table 8 carries,
  re-annotated with the belief language per frame where nameable) and its
  final signature matrix.
- Per-phase ledgers (reservoir's Even/EvenBlocks query table) — numbers
  to regenerate: the pair-legality phase adds a column.

## 5. Correctness and complexity

- **Legality theorem** (new, small): at every equivalence query the
  presented object is a well-formed invariant; `K_i = L(𝓘_i)` is the
  unique language it denotes. (Congruence: sweep-clean + Lemma 5.2.
  Saturation: pair check. `P` total on linked pairs by construction.)
- **No false assent + fixpoint canonicity** (the old Theorem 5.1,
  collapsed): exact EQ assents ⟺ `K_i = L` ⟺ `𝓘_i = 𝓘(L)` byte-equal —
  one paragraph, consuming [SωS26, Thm I, Cor 4.2, Thm II]. The
  bounded-oracle remark carries (sweep, not oracle, delivers
  two-sidedness; denotation certified only as far as the oracle checked).
- **Progress and termination**: every split — promotion, consistency
  mint, sweep escalation, pair escalation, harvest — is witnessed by an
  Arnold context separating two concrete words, so `|𝒞_T| ≤ N` at all
  times and the loop terminates after ≤ N splits, ≤ N equivalence
  queries. (Old Thm 5.1's termination paragraph, plus one clause for
  pair escalations.)
- **Query complexity**: [RESERVOIR §5] Prop 5.4 carries with one added
  bullet (*per pair escalation* — one query + `O(log N)` chain, absorbed);
  restate the itemization. Output-polynomial-in-`N` yardstick paragraph
  carries.
- **Sizes cut one way**: [RESERVOIR §5] Prop 5.5 (FDFA ≤ N + N²;
  `PT_n` witness with `N ≥ (n+1)^n`) carries verbatim with proof, plus
  the "economics" paragraph.
- (Old Lemma 5.2 has moved to §3.2; old Thm 5.3 moves to §6.)

## 6. Necessity: acceptor-typed learning stalls

*The old §4.2 + Thm 5.3, reframed: not "a gap we discovered" but "what
the typing discipline is provably protecting against". Register change
throughout: theorem-exhibit, not discovery narrative.*

- Setup: relax the belief type — pose the bare Cayley hypothesis
  (fold + pair cache), skip legality. Membership's error signal is then
  one-sided (predictions fold literal words, never a class under a left
  context) — condensed from reservoir §4.2 opening.
- [RESERVOIR §4.2] Proposition 4.4 (the stall, realized: `a → Xa`,
  four-class certified fixpoint, zero counterexamples, no counterexample
  exists) — carries with proof. The second specimen (`a ∧ XG¬a`)
  paragraph and the two-exhibit table carry.
- The export of a stall is not an algebra: non-associativity display
  (`([a]·[a])·[a] ≠ [a]·([a]·[a])`), one-lasso-two-verdicts reading of
  `a^ω` — carries, condensed; Figure 5 (canonical vs stalled export,
  drawn) carries.
- [RESERVOIR §5] Theorem 5.3 (certified fixpoints: canonical or no
  algebra) — carries with proof, stated here as the section's closing
  theorem: a certified stall's partition is *never* a congruence; what
  the relaxed learner delivers is a correct acceptor and provably
  nothing more.
- Specimen provenance: exhaustive census of smallest one-atom shapes
  found `a → Xa` minimal — one paragraph (down from the reservoir's
  recurring motif).
- Close on the field: this is [AF21]'s obstruction one level up, and the
  structural reason no observation-table route to the algebra existed —
  the missing ingredient was never a cleverer column format but the
  belief type (condensed from reservoir §4.2).

## 7. Evaluation

*Structure carries from reservoir §6 (Q1 cost / Q2 ablation / Q3 ROLL /
Q4 sensitivity) — all numbers to be regenerated after the refactor;
expectations below.*

- **Protocol**: teacher as in §2.3 (product-scan oracle — protocol text
  gets much shorter with the guard gone); corpus paragraph (6222
  complement-closed census) carries verbatim; reproducibility =
  byte-equality on all languages + deterministic traces; two-automata
  presentation-independence check carries.
- **Q1 cost**: named-case table + per-`N` medians + LTL-cut split —
  regenerate; expect fill-dominated as before, plus a small pair-legality
  phase. `splits ≤ N` and envelope claims re-checked.
- **Q2 ablation = the type relaxation**: run the §6-relaxed learner
  (no legality) under the exact oracle — this is exactly the reservoir
  ablation; 3137 permanent stalls / gap table / prefix-independence
  structure (231 at transfinite degrees; Cor 4.7 certificates) expected
  to carry as-is since the relaxed leg is unchanged. Lemma 5.2's
  congruence check as classifier (zero off-diagonal mass) carries.
- **Q3 ROLL**: paired table + census aggregates + capability paragraph
  (LTL read-off on all 6222 vs not answerable from an FDFA) carry; sizes
  a wash inside the `N + N²` envelope; group-bearing languages favor the
  FDFA (Prop 5.5(b)'s mechanism) — re-check numbers only.
- **Q4 counterexample sensitivity**: harvest ≈ `log₂ ℓ` under padding —
  carries; now doubles as a robustness note for the product-oracle's
  BFS-minimal policy.
- New measurement worth adding: per-run count of pair escalations vs
  sweep escalations vs harvests — the three sources of decision 4,
  measured; and frames-per-run (animation depth) for the examples
  section.

## 8. Related work

[RESERVOIR §7] — carries nearly verbatim (it is already written
solution-side): MP95 / CNP93+FCC / FDFA line (AF16, ABF18, LCZL21,
LSTCX19) / AF21 obstruction / BL21, BL22 passive / MO22 loop-index
queries ("no canonical syntactic automaton — true of automata, precisely
the gap the algebra fills") / CALF / **US20 precise comparison**
(syntactic algebra as target, infinite ω-power alphabet, rotation lemma
supplies the finiteness) / algebra provenance (Wilke, PP04, Arn85, MS97,
SωS26). Reframe only the topic sentences to the typing thesis: each
prior target is an acceptor, i.e. an object outside the belief type this
paper enforces.

## 9. Conclusion

- The syntactic ω-semigroup was constructible [SωS26]; it is learnable by
  a student who refuses to believe anything that is not a language.
- The rotation lemma's two services at query level: harvest (the teacher's
  counterexamples pay), legality (the learner's self-checks are free).
- Necessity: the typing is not hygiene for its own sake — dropping it
  loses half the census permanently, on classes carrying no algebra.
- Learning and classification cease to be separate activities: the limit
  is the object definability is read from.

## References

[RESERVOIR] — reference list carries as-is (ABF18, AF16, AF21, Ang87,
Arn85, BL21, BL22, CNP93, FCC+08, LCZL21, LSTCX19, MO22, MP95, MS97,
PP04, RS93, Sta83, SωS26, US20, Vaa17, vHSS17, Wil93).

---

## Out-of-paper TODO (spec/report companions, later)

- New spec (`sos_learning2_spec.md` or revision in place): the refactor
  milestones — (1) pair-legality check + escalation in the learner;
  (2) product-scan oracle replacing guard/fallback; (3) per-frame belief
  export for the animation figures (+ formula naming of aperiodic
  frames); (4) rerun census: Q1/Q3/Q4 regeneration, Q2 expected
  invariant; (5) figure regeneration (day frames, stall exhibit).
- Report: numbers land there first, paper quotes report, as per house
  rules.
- Hand-run sanity check before coding: the day-by-day belief sequence on
  `Even` and `a → Xa` under the new discipline (predict: on `a → Xa` the
  legal learner splits `C₁` via a legality escalation *before* the first
  EQ — the belief presented is never the stalled acceptor).
