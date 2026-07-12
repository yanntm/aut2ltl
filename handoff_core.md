# Handoff — sos_core (object-first restructure of the SωS paper)

## Task

Flesh out `research_notes/sos_core.md` (approved outline) into full paper text. The
reservoir is `research_notes/sos_constructed.md` — borrow prose, tables, figures, and
proofs from it freely, reorganized to fit the new structure. The reservoir is
read-only: never edit it. The outline's structure is fixed; flesh within it, don't
reorder sections without user validation.

## Role

Theory/writing thread. No code. Byte-for-byte claims in captions must stay true to
tool output already in the reservoir.

## State

§2 and §3 are fully fleshed, polished, and user-reviewed. §§1, 4–11 and the abstract
are still bullets-only outline.

Figures: delivered, user-approved, and **integrated into §3** — the paper embeds
`sos_core_figs/img/core_F0…F3.png` with captions matching the actual ink. The
artifact is `research_notes/sos_core_figs/` (its `figures.md` says what the ink
means, `reproduction.md` is the rebuild authority); `sos_core_figures.md` is now
just a pointer, no longer a spec. Ink conventions the text must respect: letters
are written on arrows (no dash coding), the root is stub-marked and a source,
key-tree arrows slightly thicker, `P` typeset beneath the drawing on all figures
(pairs are part of the object), monochrome cycles named in prose but NOT inked.
Idempotent bolding is REMOVED (user edits the figs): idempotents are computed,
not part of the data, so no ink; the text never mentions bold idempotents. Node
and edge labels are to be bracketed on the figs (`[a·b]`, `[a]`) — labels are
members of `𝒞`. Spec-style lesson: requests state goals and point at
approved references; no byte-stability or assert rigidity, engineering picks
the means.

## TODO queue (next action first)

1. **§7 rotation lemma** — state the general slot-action form before instantiating on
   `EM(D)` (reservoir Lemma 4.4 is the instance). NOTE: the algebra-level rotation
   lemma is already fully stated and proved in §3.2 (Lemma 3.3); §7 re-reads it at
   the level of Arnold's two-sided contexts, as §3.2's closing paragraph promises.
   Keep the proof at three lines; factual MS97/CPP08 discussion; only the two
   template remarks we can back (AF21 observation-table discipline; one-sided
   symbolic fixpoint). Name stays bare: "rotation lemma".
2. **§8 Theorem A** — NEW theorem, correctness `L(𝓘(D)) = L(D)` plus well-formedness
   (saturation *proved* for the constructed `P`, not assumed), self-contained from
   the skeleton lemma (reservoir 3.2) and the collapse (reservoir 4.1), no Arnold.
   Theorem B (= reservoir Thm 4.5) separately: the constructed object is Arnold's.
3. **§5 Canonicity** — Arnold's congruence recalled (reservoir §2 block), two-shapes
   independence (reservoir Prop 4.6), complete invariant (reservoir Thm 5.1), ending
   on the shapes as the specification handed to Part B.
4. **§6 Construction I** — near-verbatim transfer of reservoir §3 (`EM`, skeleton
   lemma, Prop 3.4 necessity, Table 2) plus the automaton preliminaries from
   reservoir §2 (the `D` block, Fig 1) which first appear here.
5. **§4 What the object unlocks** — teaser only: identity band, LTL=aperiodicity
   read-off, condensed taxonomy table, the one-paragraph replace-the-automaton
   suggestion. Forward-references Thm 5.1.
6. **§1 Intro + §9–11 + Abstract** — last, once the body is stable. §9 splits the two
   costs (object quadratic in `|𝒞|`; construction exponential in `|Q|`; `|𝒞|`
   intrinsic, PSPACE). Abstract leads with the object and names the rotation lemma.
7. **Propagate the §2–3 design to the rest of the paper and downstream.** The
   `⟨𝒜, P⟩` split (algebra vs acceptance layer) and the §2–3 vocabulary are the
   approved formalization; §§4–11 bullets and the companion/downstream documents
   still speak the older idiom. Explicitly deferred — a separate session's job, do
   not update dependents en passant.

Work section by section; present each fleshed section to the user before starting
the next. Commit per increment.

## Decisions already made (do not relitigate)

- **`⟨𝒜, P⟩` split fully approved**: the object is a pair — algebra `𝒜 = (𝒞, λ, M)`
  holding structure, acceptance layer `P` selecting the language. Figures draw `𝒜`
  alone; `P` is typeset as a line beneath (the split made visible).
- **The identity is _adjoined_** — explicit Definition 3.1 axiom (`⟦w⟧ = [ε]` iff
  `w = ε`), the semigroup-theory S¹ term; the word "fresh" is banned. The Cayley
  root is a source (no in-edges). Def 3.1 lists `λ` before `M`.
- **Group visibility on the Cayley graph = monochrome cycles only** (a cycle traced
  by repeating one word); mixed-letter cycles prove nothing — `GF(aa)` is the
  counterexample. Never state the naive "any non-self-loop cycle" version.
- **Vocabulary**: the word "specimen" is banned. `a*·b^ω` is §2's single worked
  example (the mod-12 aside is gone); worked paragraphs are labeled `*Example.*`;
  §2 and the `a*·b^ω` paragraphs never forward-reference the running examples by
  name (bare "§3.5" pointers at most).
- **Master-2 accessible, no automaton background** in Part A: language setting only,
  audible without Perrin–Pin. Standing style rule — but NO announcement sentence in
  the text (that proposal was rejected).
- Object first, construction second; §4 sits *before* canonicity.
- Minimal-recognizer claim DROPPED. Only two minimality senses survive: coarsest
  congruence (Arnold); unique canonical complete invariant (Thm 5.1).
- NO prospects beyond material we have; parked: reservoir §6 (finite words / LTLf)
  except at most a one-line degeneration remark; reservoir §7 development beyond
  the §4 teaser.
- Rotation lemma is the paper's central mathematical contribution — headlined in
  abstract and intro, general form first.
- "40 years unseen" is conveyed as fact pattern (MS97, CPP08), never as a boast.
- Machine formats (serialization, integer tables) stay out of Part A — §3.5 defers
  them to Part B; examples are letter-action rows + Cayley figures.

## Blockers

None. Figures are delegated, not blocking prose; §7 can start now.
