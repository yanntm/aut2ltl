# sos_core — Materializing the Syntactic ω-Semigroup (paper folder)

Working draft of the "core" paper, split per section. `make` assembles the parts
into the single-file paper [`../sos_core.md`](../sos_core.md) — that file is a
**build artifact**, do not edit it by hand; edit the parts here and re-run
`make`. (The assembler strips one `../` from figure paths and drops the
`examples.md` TOC, since the Ex_* pages are inlined right after it.)

## Reading order / status

| File | Content | Status |
|---|---|---|
| [`s0_front.md`](s0_front.md) | title, abstract, §1 introduction | drafted prose — contributions to re-anchor on §3.5 |
| [`s2_background.md`](s2_background.md) | §2 background | drafted prose |
| [`s3a_object.md`](s3a_object.md) | §3 intro, §3.1 syntax, §3.2 semantics | drafted prose |
| [`s3b_canonicity.md`](s3b_canonicity.md) | §3.3 canonicity + Def 3.11 (denoting invariant) | drafted prose |
| [`s3c_rotation.md`](s3c_rotation.md) | §3.4 rotation, saturation, well-formedness (3.12–3.15) | new restructure — [PP04, Ch. I] primitive-period cite in 3.15 to verify |
| [`s3d_canonicalization.md`](s3d_canonicalization.md) | §3.5 canonicalization (3.16–3.21) | new restructure — first draft |
| [`s3_invariant.md`](s3_invariant.md) | **reservoir** — pre-split §3, out of the build; `rm` when s3a–s3d are stable | retired from PARTS |
| [`s4_construction.md`](s4_construction.md) | §4 construction from an automaton | drafted prose — awaiting §4 rewrite against §3.5 (entry = denoting invariant, slot compression); §3 cross-refs stale (3.11→3.12 etc.), sweep once §3 stable |
| [`s6_uses.md`](s6_uses.md) | §5 uses: identity band + LTL frontier | drafted prose — serialization block verbatim from tool export ([`../sos_core_figs/sources/gf_aa.sos`](../sos_core_figs/sources/gf_aa.sos)) |
| [`s7_end.md`](s7_end.md) | §6 related work, §7 perspectives, §8 conclusion | drafted prose — §3.4 refs to re-check after restructure |
| [`bib.md`](bib.md) | bibliography | reconstructed — verify against [`../papers/`](../papers/) |
| [`notation.md`](notation.md) | notation conventions (editors' note, not paper text) | stable |

The [`Makefile`](Makefile) concatenates, in order,
`s0 s2 s3a s3b s3c s3d s4 s6_uses s7_end`
then the worked examples (`examples.md` + the four `Ex_*.md`) then `bib`;
`README.md`, `notation.md` and the reservoir `s3_invariant.md` stay out of
the paper.

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

- All sections obey `notation.md`; numbering is per-section (Definition 3.x
  spans `s3a`–`s3d`, in order: 3.1–3.6 in `s3a`, 3.7–3.11 in `s3b`,
  3.12–3.15 in `s3c`, 3.16–3.21 in `s3d`); cross-references are name+number
  ("the rotation lemma (3.12)") so they survive edits and file boundaries.
  §3 vocabulary ladder: invariant (3.4) → denoting `L` (3.11) → well-formed
  (3.13) ⟺ owns a language (3.15) → canonical (3.10), reached by
  canonicalization (3.20).
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
