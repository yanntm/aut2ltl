# Handoff — sos_core (the SωS paper, canonicity-first reboot)

## Task

Flesh `research_notes/sos_core.md` into full paper text, section by section, with
user review of each increment. Reservoir: `research_notes/sos_constructed.md` —
borrow freely, never edit it. Dependents adapt to us, never the reverse.

## State

**§2 through §3.2 are approved.** **§3.3 (canonicity: Arnold Def 3.5, `𝓘(L)`
Def 3.6, substitution 3.7, canonicity Thm 3.8, rotation 3.9 in shared-lasso form,
saturation 3.10, Cor 3.11) and §3.4 (the examples, as invariants — old §3.6 adapted)
are landed, pending user review.** Old §3.3–3.5 (moves apparatus, acceptance-layer
definition, residuals) and the old §5 outline are deleted; residuals dropped without
relocation. Everything else — old §4 "unlocks" outline included — is indicative at
most, rewritten when its turn comes.

## TODO queue (next action first)

1. **User review of §3.3–§3.4 and §4** as landed. §4 structure: 4.1 EL recall +
   the four machines; 4.2 `EM(D)` (Def 4.2, skeleton 4.3, Cor 4.4 refines Arnold,
   necessity 4.5); 4.3 the quotient (collapse 4.6, relations 4.7, rotation-on-runs
   4.8, prefix-independence 4.9); 4.4 `𝓘(D)` Def 4.10, **Thm 4.11
   `⟨u⟩ ∼ ⟨v⟩ ⟺ u ≈_L v` hence `𝓘(D) = 𝓘(L)`**, Cor 4.12 (correctness +
   presentation-independence as corollaries — the old two-theorem split is gone),
   GF(aa) two-presentation exhibit, algorithm paragraph. Tail renumbered: 5
   complexity, 6 unlocks (outline), 7 related work, 8 conclusion.
2. **Engineering: regenerate the automata figures over `{a, b}`** (Figures 5–6
   currently hijack `sos_figs/img/{gf_aa,even,evenblocks,gf_aa_reset}.png`, drawn
   over `{!a, a}` with shortlex `!a < a`; captions carry the caveat). An `aUGb`
   three-state automaton figure is missing entirely — text describes it.
3. Parked, bites when §3.1 reopens: Def 3.1's isolation only constrains `λ`; the S¹
   axiom (word classes closed under `M`, i.e. `⟦u⟧ = [ε] ⟺ u = ε`) is still missing.
   §3.3's Lemma 3.9 sidesteps it via the explicit letter-generated hypothesis.
4. PP04 is searchable (`papers/Perrin_Pin_2004_Book.txt`, OCR artifacts, readable).
   §2 cites audited and pinned (Ch. I Cor 9.8; Ch. II Thm 2.1, Thm 5.1, §7). Still
   to read: Ch. II §8 (syntactic congruence — cross-check Arnold's Def 3.5), §2.2
   (conjugacy of linked pairs — pin the cite now used in §3.3), Thm 5.1 statement
   verbatim, §7's theorem number. Also [Arn85] itself: Def 3.5 is transcribed from
   the reservoir, not yet checked against the original.

## §3.3 spec (redraft from here if the draft is lost)

Numbering continues §3.2; next label is 3.5.

1. Inherited question: Def 3.4 reads one presentation; a lasso has many.
2. **Def 3.5** Arnold's congruence [Arn85] on `Σ⁺`, both shapes (linear / ω-power),
   in full; facts used: two-sided, finite index; coarsest = first minimality sense.
   Example on `aUGb`: `a ≉ b` (ω-power, empty paddings), `ab ≉ ba` (linear,
   `t = b`), `a ≈ aa`; the five Fig 1 classes.
3. **Def 3.6** `𝓘(L)`: `𝒞 = Σ⁺/≈_L` shortlex-keyed plus adjoined `[ε]`; `λ(x) = [x]`;
   `M` induced; `P(L)` = linked pairs of word classes tested on the representative
   lasso `w_s·(w_e)^ω ∈ L`. Remark: `⟦u⟧ = [u]` — letter-generated.
4. **Lemma 3.7** substitution: `u ≈ u'`, `v ≈ v'` (loops nonempty) ⟹ one verdict on
   `u·v^ω` / `u'·v'^ω`. Proof: ω-power shape at `x = u, y = ε` swaps the loop; linear
   shape at `x = y = ε, t = v'` swaps the stem. Replaces the moves apparatus.
5. **Thm 3.8** canonicity: rewrite `u·v^ω = (u·v^k)(v^k)^ω` with `⟦v⟧^k = e`, apply
   3.7 ⟹ every presentation gets `L`'s verdict; `L(𝓘(L)) = L`; complete invariant
   (byte-equal iff equal). Example: `Even`'s `a^ω` via `(ε,a)` vs `(a,a)` — distinct
   pairs, one verdict.
6. **Lemma 3.9** rotation, posed AFTER the theorem, on letter-generated algebras
   (hypothesis explicit), naming sentence first. **Def 3.10** saturation.
   **Cor 3.11** `P(L)` saturated. Close: saturation is the one law a layer must obey,
   table-checkable; §4 flips it, §7 re-reads rotation on two-sided contexts.

Open placement, decided with user when reached: the biconditional "saturated ⟺
well-defined for arbitrary `P`" (needs the moves lemma; consumers: complement flip,
construction's saturation obligation).

## Decisions (do not relitigate)

- Vocabulary: **classes** (never bins/types; "equivalence classes" spelled out only
  at §2's organizing sentence); classify/assign, never metaphorical "sorting"; `φ` is
  "the morphism"; algebraic **sort** reserved for the two-sorted structure.
- `𝓘` is **the invariant** (Def 3.2's term); "the object" is banned paper-wide.
  Binding text (§2–3.2) is clean; indicative sections still carry it — purge at
  their rewrite, including Def 3.4's competing "**object**" definition.
- §2 is PP04-faithful: `S₊` is a **semigroup** on `Σ⁺` (`ε` has no ω-power); the
  identity is adjoined only in §3. Morphism is `φ = (φ₊, φ_ω)`, equations displayed;
  after the "second sort not carried" hinge, `φ` means `φ₊`.
- Worked paragraphs are labeled `*Example.*` and anchored ("On Figure 1
  (`aUGb`), …"); no bare "In general". No individual non-lasso words as
  specimens — out of regular scope.
- Identity **adjoined** (S¹; "fresh" banned); "specimen" banned; shortlex keys;
  Cayley root a source; `P` typeset beneath figures; monochrome cycles only as group
  evidence; no idempotent ink.
- Symbols: letters are valuations over one atom; this paper's `b` stands for `!a`;
  orders differ (`a < b` here, `!a < a` machine-side) and shortlex data does not
  transliterate. A dedicated interpretation-of-symbols paragraph is wanted; its
  text and placement are the user's call — §2 is approved and NOT to be touched
  without explicit sanction (violated once this session, reverted). Figure 5/6
  captions carry the convention locally meanwhile.
- Master-2 accessible, no automata in Part A (Arnold's congruence is language-level,
  hence admissible in §3.3); no announcement sentences; object first, construction
  second; two minimality senses only; rotation lemma is the central contribution,
  general form first; "40 years unseen" as fact pattern, never boast; machine
  formats in Part B.

## Blockers

None. Next action: the §3.3 review.
