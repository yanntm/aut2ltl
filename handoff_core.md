# Handoff — sos_core (the SωS paper, canonicity-first reboot)

## Task

Flesh `research_notes/sos_core.md` into full paper text, section by section, with
user review of each increment. Reservoir: `research_notes/sos_constructed.md` —
borrow freely, never edit it. Dependents adapt to us, never the reverse.

## State

**§2 through §3.2 are approved**; sanctioned edits only (the Figure 1/1′ block is
landed). Everything after §3.2 is unvetted draft: **at its turn it is replaced, not
patched — no debt owed to current text**; do not queue micro-fixes against it.
Figures 1–4 draw the full multiplication table (fused labels; `[ε]` elided from
Fig 1′ on; `𝒞` marks an all-classes edge). The `aUGb` automaton figure is placed in
§4.1, caption a placeholder. The **§3.3 paragraph-by-paragraph review is the open
activity** (¶1 commented, verdict pending). User is refactoring the tgba/automata
to letters `{a, b}` (letter lists on edges) — the `{!a, a}` transliteration caveats
retire with it.

## TODO queue (next action first)

1. §3.3 review, paragraph by paragraph; user rules on each.
2. §2 cite upgrades proposed in chat, awaiting sanction (vetted territory):
   Thm 2.1 → Thm 2.2 (Ramsey, morphism form); §7 → Thm 7.5; the two bare
   `[PP04, Ch. II]` on the ω-semigroup definition → `Ch. II, §4`.
3. Figure 5 (`aUGb` automaton) proper caption — deferred by user.

## PP04 coordinates (papers/Perrin_Pin_2004_Book.txt; verified this session)

Numbering resets per chapter and is shared across Thm/Prop/Cor within a section;
definitions are unnumbered prose. Cite = `[PP04, Ch. N, Prop/Thm/Cor x.y]`;
section cite only for unnumbered definitions.

- Ch. I, Cor. 9.8 — lassos determine a regular language (already pinned in text).
- Ch. II, Thm 2.1 — Ramsey, coloring form; **Thm 2.2** — morphism form: linked pair
  `(s, e)`, `s·e = s`, `e² = e`, block factorization. 2.2 is the fit for §2's use.
- Ch. II, Prop. 2.6 — conjugacy is an equivalence (definition in prose just above,
  §2.2, p. 79); **Prop. 2.8** — any two linked-pair factorizations of one ω-word
  are conjugate; **Cor. 2.9** — for surjective `φ`: conjugate ⟺ the simple sets
  `φ⁻¹(s)(φ⁻¹(e))^ω` intersect.
- Ch. II, Thm 5.1 — finite ω-semigroup determined by the ω-power; Wilke's axiom
  `s(ts)^ω = (st)^ω` displayed in its hypotheses; checked verbatim.
- Ch. II, Thm 7.5 — ω-rational ⟺ recognizable ⟺ recognized by a finite (ordered)
  ω-semigroup.
- Ch. II, §8 — syntactic congruence; its `CF/CI` context sets are the two shapes of
  our Def 3.5. Arnold's original [Arn85] remains unchecked.

## Decisions (user rulings; do not relitigate)

- The object carries the **full** `M : 𝒞 × 𝒞 → 𝒞`; figures draw the full table,
  parallel edges fused into one arrow listing their labels — the letter-classes
  projection is dead. `[ε]` elided from Fig 1′ on (identity makes its row and
  column definitional); `𝒞` marks an edge carrying every class of the algebra;
  Figure 1 (with `[ε]` and the reading root) serves the §2–3 walkthroughs, side by
  side with Fig 1′.
- **No §3.1 reopen.** Letter-generation stays a proven fact of `𝓘(L)`/`𝓘(D)`,
  never an axiom or standalone definition.
- Unvetted sections are replaced at their turn, not patched; the handoff carries no
  fix-queues against them.
- PP04 cites: chapter + numbered statement; section only for unnumbered
  definitions.
- Vocabulary: **classes** (never bins/types; "equivalence classes" spelled out only
  at §2's organizing sentence); classify/assign, never metaphorical "sorting"; `φ`
  is "the morphism"; algebraic **sort** reserved for the two-sorted structure.
- `𝓘` is **the invariant** (Def 3.2's term); "the object" is banned paper-wide.
  Binding text (§2–3.2) is clean; indicative sections still carry it — purge at
  their rewrite, including Def 3.4's competing "**object**" definition.
- §2 is PP04-faithful: `S₊` is a **semigroup** on `Σ⁺` (`ε` has no ω-power); the
  identity is adjoined only in §3. Morphism is `φ = (φ₊, φ_ω)`, equations
  displayed; after the "second sort not carried" hinge, `φ` means `φ₊`.
- Worked paragraphs are labeled `*Example.*` and anchored ("On Figure 1
  (`aUGb`), …"); no bare "In general". No individual non-lasso words as specimens.
- Identity **adjoined** (S¹; "fresh" banned); "specimen" banned; shortlex keys;
  Cayley root a source; `P` typeset beneath figures; monochrome cycles only as
  group evidence; no idempotent ink.
- Symbols: letters are valuations over one atom; a dedicated
  interpretation-of-symbols paragraph is wanted; its text and placement are the
  user's call — §2 is NOT to be touched without explicit sanction.
- Master-2 accessible, no automata in Part A (Arnold's congruence is
  language-level, hence admissible in §3.3); no announcement sentences; object
  first, construction second; two minimality senses only; rotation lemma is the
  central contribution; "40 years unseen" as fact pattern, never boast; machine
  formats in Part B.

## Blockers

None. Next action: verdict on the §3.3 ¶1 comment, then continue the review.
