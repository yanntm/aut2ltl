# sos_core — Materializing the Syntactic ω-Semigroup (paper folder)

Working draft of the "core" paper, split per section. `make` assembles the parts
into the single-file paper [`../sos_core.md`](../sos_core.md) — that file is a
**build artifact**, do not edit it by hand; edit the parts here and re-run
`make`. (The assembler strips one `../` from figure paths and drops the
`examples.md` TOC, since the Ex_* pages are inlined right after it.)

## Reading order / status

| File | Content | Status |
|---|---|---|
| [`s0_front.md`](s0_front.md) | title, abstract, §1 introduction | abstract + intro bullets |
| [`s2_background.md`](s2_background.md) | §2 background | drafted prose |
| [`s3_invariant.md`](s3_invariant.md) | §3 the invariant `𝓘 = ⟨𝒮, P⟩` | drafted prose |
| [`s4_construction.md`](s4_construction.md) | §4 construction from an automaton | drafted prose — review pending; `EM₊` counts to re-verify |
| [`s5_complexity.md`](s5_complexity.md) | §5 complexity | drafted prose |
| [`s6_uses.md`](s6_uses.md) | §6 identity band + LTL frontier | drafted prose — serialization block to re-verify against tool export |
| [`s7_end.md`](s7_end.md) | §7 related work, §8 perspectives, §9 conclusion | drafted prose |
| [`bib.md`](bib.md) | bibliography | reconstructed — verify against [`../papers/`](../papers/) |
| [`notation.md`](notation.md) | notation conventions (editors' note, not paper text) | stable |

The [`Makefile`](Makefile) concatenates, in order,
`s0 s2 s3_invariant s4 s5_complexity s6_uses s7_end`
then the worked examples (`examples.md` + the four `Ex_*.md`) then `bib`;
`README.md` and `notation.md` stay out of the paper.

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

## Conventions

- All sections obey `notation.md`; numbering is per-section (Definition 3.x
  lives entirely in `s3_invariant.md`); cross-references are name+number
  ("the rotation lemma (3.11)") so they survive edits and file boundaries.
- Figures live in [`../sos_core_figs/`](../sos_core_figs/) and
  [`../sos_figs/`](../sos_figs/); paths from these files start with `../`. §2 is
  figure-free (classes computed by hand). Two numbered figures only: Figure 1,
  the two-panel pair in §3.1 — stamp core with `λ` as entry arrows and pairs
  drawn on top (`core_F0_astar_bomega_b_pairs.png`) | monoid completion
  (`core_F0_astar_bomega.png`); Figure 2, the reset presentation of `GF(aa)`
  in §4.4 (`gf_aa_reset.png`). All other drawings live on the example pages,
  numbered Ex. 1–4 and cited that way from the prose.
- Didactic goal: standalone — readable by an M2 student with background but
  without Perrin–Pin as a prerequisite. Every classical notion used is
  restituted in §2 or §3, and each is presented as what it is: algebra on
  finite sets, nothing deep. Keep the worked examples; when in doubt, add one.
