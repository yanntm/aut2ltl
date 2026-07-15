# sos_core2 — Materializing the Syntactic ω-Semigroup (paper folder)

Working draft of the "core" paper, split per section. The legacy monolith
`../sos_core.md` is kept untouched as the base this version restructures.

## Reading order / status

| File | Content | Status |
|---|---|---|
| `s0_front.md` | title, abstract, §1 introduction | abstract + intro bullets |
| `s2_background.md` | §2 background | drafted prose |
| `s3_invariant.md` | §3 the invariant `𝓘 = ⟨𝒮, P⟩` | drafted prose |
| `s4_construction.md` | §4 construction from an automaton | placeholder bullets |
| `s5_end.md` | §5 complexity, §6 uses, §7 related work, §8 conclusion | placeholder bullets |
| `bib.md` | bibliography | reconstructed — verify against `../papers/` |
| `notation.md` | notation conventions (editors' note, not paper text) | stable |

Concatenating `s0 s2 s3 s4 s5_end bib` in order reproduces the paper.

## Conventions

- All sections obey `notation.md`; numbering is per-section (Definition 3.x
  lives entirely in `s3_invariant.md`); cross-references are name+number
  ("the rotation lemma (3.11)") so they survive edits and file boundaries.
- Figures live in `../sos_core_figs/` and `../sos_figs/`; paths from these
  files start with `../`. Figure 1 uses the no-`[ε]` rendering
  (`core_F0_astar_bomega_b.png`); figure regeneration / caption check pending.
- Didactic goal: standalone — readable by an M2 student with background but
  without Perrin–Pin as a prerequisite. Every classical notion used is
  restituted in §2 or §3, and each is presented as what it is: algebra on
  finite sets, nothing deep. Keep the worked examples; when in doubt, add one.
