# Handoff — sos_core (object-first restructure of the SωS paper)

## Task

Flesh out `research_notes/sos_core.md` (approved outline, bullets only) into full
paper text. The reservoir is `research_notes/sos_constructed.md` — borrow prose,
tables, figures, and proofs from it freely, reorganized to fit the new structure.
The reservoir is read-only: never edit it. The outline's structure is fixed; flesh
within it, don't reorder sections without user validation.

## Role

Theory/writing thread. No code. Figures and tables are reproduced from the existing
exports (`sos_figs/`, the serialization in current Fig 2) — byte-for-byte claims in
captions must stay true to the tool output already in the reservoir.

## TODO queue (next action first)

1. **§3 The object** — the load-bearing section and the only one with new mathematics
   in Part A: state the well-formedness axioms (associativity, letter-generated,
   fresh `[ε]`, conjugacy-saturated `P`), the membership-query semantics, and prove
   the NEW well-definedness lemma (query is a function of the lasso, not its
   presentation, iff `P` is saturated — currently implicit in reservoir Lemma 3.2).
   Move Prop 5.3 (residuals derived), Def 5.2 (Cayley graph), Fig 2 (format),
   Table 3 (the three tables) here. Examples are met as tables, no automata yet.
2. **§7 rotation lemma** — state the general slot-action form before instantiating on
   `EM(D)` (reservoir Lemma 4.4 is the instance); keep the proof at three lines;
   write the factual MS97/CPP08 discussion; only the two template remarks we can
   back (AF21 observation-table discipline; one-sided symbolic fixpoint). Name stays
   bare: "rotation lemma".
3. **§8 Theorem A** — NEW theorem, correctness `L(𝓘(D)) = L(D)` plus well-formedness
   (saturation *proved* for the constructed `P`, not assumed), self-contained from
   the skeleton lemma (reservoir 3.2) and the collapse (reservoir 4.1), no Arnold.
   Theorem B (= reservoir Thm 4.5) separately: the constructed tuple is Arnold's.
4. **§5 Canonicity** — Arnold's congruence recalled (reservoir §2 block), two-shapes
   independence (reservoir Prop 4.6), complete invariant (reservoir Thm 5.1),
   ending on the shapes as the specification handed to Part B.
5. **§6 Construction I** — near-verbatim transfer of reservoir §3 (`EM`, skeleton
   lemma, Prop 3.4 necessity, Table 2) plus the automaton preliminaries from
   reservoir §2 (the `D` block, Fig 1) which first appear here.
6. **§2 Background** — reservoir §2 minus Arnold's congruence and minus the automaton
   block (both moved); lassos, monoid+ω-power, linked pairs.
7. **§4 What the object unlocks** — teaser only: identity band, LTL=aperiodicity
   read-off (reservoir §7.1 compressed), condensed taxonomy table (one sentence per
   row + companion pointers), the one-paragraph replace-the-automaton suggestion.
   Forward-references Thm 5.1.
8. **§1 Intro + §9–11 + Abstract** — last, once the body is stable. §9 splits the two
   costs (object quadratic in `|𝒞|`; construction exponential in `|Q|`; `|𝒞|`
   intrinsic, PSPACE). Abstract leads with the object and names the rotation lemma.

Work section by section; present each fleshed section to the user before starting
the next. Commit per increment.

## Decisions already made (do not relitigate)

- Object first, construction second; §4 sits *before* canonicity (motivation early,
  one forward reference).
- Minimal-recognizer claim DROPPED (a 2-state DBA beats the 6-class `S(GF(aa))`).
  Only two minimality senses survive: coarsest congruence (Arnold); unique canonical
  complete invariant (Thm 5.1).
- NO prospects beyond material we have: no prophetic extraction, no learning-paper
  promises beyond the two factual remarks in §7. We don't sell what we don't have.
- Not transferred (parked, user decides later): reservoir §6 (finite words / LTLf)
  except at most a one-line degeneration remark; reservoir §7 development beyond
  the §4 teaser (lives in companion papers).
- Rotation lemma is the paper's central mathematical contribution — headlined in
  abstract and intro, own section, general form first.
- "40 years unseen" is conveyed as fact pattern (MS97 displayed the split, CPP08
  saturated triples, neither took the conjugation), never as a boast.

## Blockers

None. Outline is user-approved. Each fleshed section gates on user review before
the next.
