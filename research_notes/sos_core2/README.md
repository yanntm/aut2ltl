# sos_core2 — Materializing the Syntactic ω-Semigroup (paper folder)

Working draft of the "core" paper, split per section. The legacy monolith
[`../sos_core.md`](../sos_core.md) is kept untouched as the base this version
restructures.

## Reading order / status

| File | Content | Status |
|---|---|---|
| [`s0_front.md`](s0_front.md) | title, abstract, §1 introduction | abstract + intro bullets |
| [`s2_background.md`](s2_background.md) | §2 background | drafted prose |
| [`s3_invariant.md`](s3_invariant.md) | §3 the invariant `𝓘 = ⟨𝒮, P⟩` | drafted prose |
| [`s3_examples.md`](s3_examples.md) | float pages: Fig 2 (four invariants), Fig 3 (five automata) — captions only | drafted; superseded for per-language detail by the worked examples below |
| [`s4_construction.md`](s4_construction.md) | §4 construction from an automaton | drafted prose — review pending; `EM₊` counts to re-verify |
| [`s5_end.md`](s5_end.md) | §5 complexity, §6 uses, §7 related work, §8 conclusion | placeholder bullets |
| [`bib.md`](bib.md) | bibliography | reconstructed — verify against [`../papers/`](../papers/) |
| [`notation.md`](notation.md) | notation conventions (editors' note, not paper text) | stable |

Concatenating `s0 s2 s3 s3_examples s4 s5_end bib` in order reproduces the
paper (`s3_examples` holds only floats — LaTeX will place them).

## Worked examples

Index: [`examples.md`](examples.md) — TOC + reading key. One page per language,
each a five-axis table (informal / ω-regular / formula / Det. Emerson–Lei `D` /
invariant `𝓘`) plus reading prose:

| Page | Language | Formula | Status |
|---|---|---|---|
| [`Ex_aUGb.md`](Ex_aUGb.md) | `a*·b^ω` | LTL `a U G !a` | table done; prose placeholder |
| [`Ex_GFaa.md`](Ex_GFaa.md) | `GF(aa)` | LTL `G F(a ∧ X a)` | table done; prose placeholder |
| [`Ex_Even.md`](Ex_Even.md) | `(aa)*·b·(a\|b)^ω` | PSL/SERE `{ {a[*2]}[*] ; !a }!` | table done; prose placeholder |
| [`Ex_EvenBlocks.md`](Ex_EvenBlocks.md) | `(a\|b)*·((aa)*·b)^ω` | PSL/SERE `GF!a ∧ FG(…)` | table done; prose placeholder |

## Conventions

- All sections obey `notation.md`; numbering is per-section (Definition 3.x
  lives entirely in `s3_invariant.md`); cross-references are name+number
  ("the rotation lemma (3.11)") so they survive edits and file boundaries.
- Figures live in [`../sos_core_figs/`](../sos_core_figs/) and
  [`../sos_figs/`](../sos_figs/); paths from these files start with `../`. §2 is
  figure-free (classes computed by hand); Figure 1 is a two-panel pair in §3.1 —
  stamp core (`core_F0_astar_bomega_b.png`) | monoid completion
  (`core_F0_astar_bomega.png`). Figure adaptation pending (λ as entry arrows
  agreed; further tweaks under discussion).
- Didactic goal: standalone — readable by an M2 student with background but
  without Perrin–Pin as a prerequisite. Every classical notion used is
  restituted in §2 or §3, and each is presented as what it is: algebra on
  finite sets, nothing deep. Keep the worked examples; when in doubt, add one.
