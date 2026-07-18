# sos_core — Materializing the Syntactic ω-Semigroup (paper folder)

Working draft of the "core" paper, split per section. `make` assembles the parts
into the single-file paper [`../sos_core.md`](../sos_core.md) — that file is a
**build artifact**, do not edit it by hand; edit the parts here and re-run
`make`. (The assembler strips one `../` from figure paths and drops the
`examples.md` TOC, since the Ex_* pages are inlined right after it.)

## Reading order / status

| File | Content | Status |
|---|---|---|
| [`s0_front.md`](s0_front.md) | title, abstract, §1 introduction | restructure applied — abstract middle + contributions rewritten (well-formed, canonicalization), abstract pending author review |
| [`s2_background.md`](s2_background.md) | §2 background | drafted prose — §3 refs to re-check after restructure |
| [`s3a_object.md`](s3a_object.md) | §3 intro, §3.1 syntax, §3.2 semantics (Defs 3.1–3.4) | drafted prose |
| [`s3b_canonicity.md`](s3b_canonicity.md) | §3.3 canonicity (Defs 3.5–3.6, Lemma 3.1, **Theorem I**) | drafted prose |
| [`s4a_rotation.md`](s4a_rotation.md) | §4 opening (Def 4.1 denoting) + §4.1 rotation, saturation, well-formedness (Lemma 4.1, Def 4.2, Cor 4.1, Prop 4.1) | new restructure — [PP04, Ch. I] primitive-period cite in Prop 4.1 to verify |
| [`s4b_canonicalization.md`](s4b_canonicalization.md) | §4.2 canonicalization (Def 4.3, Lemmas 4.2–4.3, **Theorem II**, Cor 4.2) | new restructure — first draft |
| [`s3_invariant.md`](s3_invariant.md) | **reservoir** — pre-split §3, out of the build; `rm` when s3a/s3b/s4a/s4b are stable | retired from PARTS |
| [`s5a_entry.md`](s5a_entry.md) | §5 intro; §5.1 EL automata (Def 5.1); §5.2 the automaton invariant (Def 5.2–5.3, Prop 5.1, Lemma 5.1 collapse, Cor 5.1 denotes) | new restructure — first draft |
| [`s5b_theorem.md`](s5b_theorem.md) | §5.3 compression (Prop 5.2, algorithm); §5.4 **Theorem III**, Cor 5.2, Figure 2 | new restructure — first draft |
| [`s5_construction.md`](s5_construction.md) | **reservoir** — pre-rewrite §5, out of the build; `rm` when s5a/s5b are stable | retired from PARTS |
| [`s6_uses.md`](s6_uses.md) | §6 uses: identity band + LTL frontier | drafted prose — serialization block verbatim from tool export ([`../sos_core_figs/sources/gf_aa.sos`](../sos_core_figs/sources/gf_aa.sos)); headings renumbered 5.x→6.x, body refs stale |
| [`s7_end.md`](s7_end.md) | §7 related work, §8 perspectives, §9 conclusion | drafted prose — headings renumbered, body refs stale |
| [`bib.md`](bib.md) | bibliography | reconstructed — verify against [`../papers/`](../papers/) |
| [`notation.md`](notation.md) | notation conventions (editors' note, not paper text) | stable |

The [`Makefile`](Makefile) concatenates, in order,
`s0 s2 s3a s3b s4a s4b s5a s5b s6_uses s7_end`
then the worked examples (`examples.md` + the four `Ex_*.md`) then `bib`;
`README.md`, `notation.md` and the reservoirs `s3_invariant.md` and
`s5_construction.md` stay out of the paper.

## Worked examples

Index: [`examples.md`](examples.md) — TOC + reading key. One page per language,
each a five-axis table (informal / ω-regular / formula / Det. Emerson–Lei `D` /
invariant `𝓘`) plus reading prose:

| Page | Language | Formula | Status |
|---|---|---|---|
| [`Ex_aUGb.md`](Ex_aUGb.md) | `a*·b^ω` | LTL `a U G !a` | done |
| [`Ex_GFaa.md`](Ex_GFaa.md) | `GF(aa)` | LTL `G F(a ∧ X a)` | done |
| [`Ex_Even.md`](Ex_Even.md) | `(aa)*·b·(a\|b)^ω` | PSL/SERE `{ {a[*2]}[*] ; !a }!` | done |
| [`Ex_EvenBlocks.md`](Ex_EvenBlocks.md) | `(a\|b)*·((aa)*·b)^ω` | PSL/SERE `GF!a ∧ FG(…)` | done |

Each page opens on a classification block — three rows: LTL (+ stutter),
Geometry (MP92 ladder rung), Recognizer (weakest deterministic acceptance) —
stated as fact, friendly wording. Values computed 2026-07-16 by
`sosl.sos.classify` on
[`../sos_core_figs/sources/`](../sos_core_figs/sources/)`*.sos`; the `.cat`
sidecars committed beside them are the trace (exact Wagner degrees included —
kept out of the paper boxes).

Each page closes on a construction block — the table of the automaton
congruence classes (`𝒞_D`, one row per class = its two maps) with its fold
onto `𝒞` — pasted verbatim from the generated
[`../sos_figs/sources/`](../sos_figs/sources/)`*.emtable.md`
(`make -C ../sos_figs` refreshes the reports then renders the paper notation
via `em_table.py`, rename `!a` → `b`; the generator and its files keep the
historical `EM`/emtable naming). Marks are transition-based, placed on
recurring edges only.

## Conventions

- All sections obey `notation.md`. Numbering: **per-type counters, scoped per
  section** — Definitions 3.1–3.6, Lemma 3.1 (§3); Definitions 4.1–4.3,
  Lemmas 4.1–4.3, Proposition 4.1, Corollaries 4.1–4.2 (§4); Definitions
  5.1–5.4, Lemma 5.1, Propositions 5.1–5.2, Corollaries 5.1–5.2 (§5) —
  every index single-digit. The **main theorems are lettered globally in
  roman**: Theorem I (canonicity, §3.3), Theorem II (canonicalization,
  §4.2), Theorem III (the construction, §5.4).
  Cross-references are name+number with the type spelled out ("the rotation
  lemma (Lemma 4.1)", "canonicity (Theorem I)") so they survive edits and
  file boundaries. Vocabulary ladder: invariant (Def 3.3) → denoting `L`
  (Def 4.1) → well-formed (Def 4.2) ⟺ owns a language (Prop 4.1) →
  canonical (Theorem I), reached by canonicalization (Theorem II).
- Figures live in [`../sos_core_figs/`](../sos_core_figs/) and
  [`../sos_figs/`](../sos_figs/); paths from these files start with `../`. §2 is
  figure-free (classes computed by hand). Two numbered figures only: Figure 1,
  the two-panel pair in §3.1 — stamp core with `λ` as entry arrows and pairs
  drawn on top (`core_F0_astar_bomega_b_pairs.png`) | monoid completion
  (`core_F0_astar_bomega.png`); Figure 2, the reset presentation of `GF(aa)`
  in §5.4 (`gf_aa_reset.png`). All other drawings live on the example pages,
  numbered Ex. 1–4 and cited that way from the prose.
- Didactic goal: standalone — readable by an M2 student with background but
  without Perrin–Pin as a prerequisite. Every classical notion used is
  restituted in §2 or §3, and each is presented as what it is: algebra on
  finite sets, nothing deep. Keep the worked examples; when in doubt, add one.
