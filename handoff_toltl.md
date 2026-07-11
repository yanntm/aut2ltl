# Handoff — toltl thread (theory session)

*Untracked scratch. Everything durable is in the paper (`research_notes/
sos_toltl.md`), the spec (`sos_toltl_spec.md` — its head is the
done/todo map), the report (`sos_toltl_report.md` — results in force,
current-state only), and the figures spec/artifact. This file carries only
orientation, conventions, and priorities. Delete when consumed.*

## Where things stand (one paragraph)

The paper's §4–§5 theory is closed: Theorem 4.13 is complete (seam bricks),
the window engine has the anchored-park relaxation (B̃) with its normal form
(Prop 5.7) and graded lift, Thérien–Wilke is frozen from source ([TW01],
ω-valid, until-rank read-off exact), and the strata-variety alignment is
scoped out to the classification thread. Two open problems remain in the
conclusion (residual-stratum descent; realization hunts). Figures 1–4 are
in the paper with curated captions. The engine is sound catalogue-wide but
covers only the width-1 strata (1 114 of 2 240 LTL languages); the graded
engine (M3) is the coverage frontier.

## Priorities

1. **Dev (engineering, all specified):** M3 — graded engine with the seam
   bricks (`seam(c)` mandatory; the entry-rooted `U` sketch is UNSOUND, do
   not implement; gate = the report's `{2,5,8}` witness word). Then C6+E5
   (until-rank, budget-disciplined), C3 park split (+ H3 confirm on gafb).
2. **Conformance (gates paper text, stop-the-line on divergence):** H8 —
   the residual-floor witness `GF(a ∧ X((!a&!b) U a))` (paper §5.1 asserts
   ten classes, all layers 1-anchored, (ii)-failure at every width); E9-3a —
   `GFa ∧ FGb` (paper Example 3's stack is hand-only); Example 4 likewise.
3. **Measure:** E4 full + the sub-call addendum (decides whether the §2.3
   split-conjecture's poly half is worth proving); census-next `2state2ap`
   (H3/H8 minimality, E2 re-run).
4. **Theory/paper, next session:** react to 2 (adjudicate divergences);
   the §9 KR-cascade comparison ⟨TBD⟩ (Mal10 is read — draftable now); the
   biblio sweep ⟨TBD⟩ (library largely complete); §5.1's width-bound-by-
   definiteness-degree ⟨TBD⟩ (open math); §2.3 arena bound (open, gated
   on 3).

## Library

In `papers/` with .txt siblings. Still missing: Thérien–Weiss, *Graph
congruences and wreath products*, JPAA 35 (1985) 205–215 (C6's procedure —
the RAIRO 1986 file is their categories paper, not this); an ω-word
locally-testable source (BP91 defers ω; Wilke '93 doesn't carry it).

## Working conventions (the user corrected/set these)

- **Roles:** this session is theory. Paper lock is ours; we do math and read
  `papers/`; menial/engineering work is delegated through the specs to other
  sessions. The report is engineering's to fill but now under the
  current-state contract (spec §6 footer states it).
- **Commit without asking** (granted this session), `git commit -F -`,
  terse messages, several files per commit OK. Never rewrite history.
  Pushing still needs explicit ask.
- **Cite only what was read**: find the paragraph first; bibliographic
  records from the source's own reference list. No citing from memory.
- **Specs/report are current-state only**: done/todo delineated, no
  narrative of how we got there; git holds history. Reproduce numbers
  before correcting them (`e0_dg` pattern).
- **The paper is science only**: no tool names outside §8's oracle
  sentence, no probe/provenance talk; image `src` paths fine.
- Read engineering drops by `git diff` against the last-integrated report
  commit, not by re-reading sections.
- Root files (TODO/STATUS/README, docs/HISTORY.md) are the user's — do not
  edit. No memory files. Never git restore/checkout — the tree holds the
  user's parallel work (`sos_classification.md`, `sos_calculus*`,
  `sos_symbolic*`, `sos_sdd`, `sosl` are not ours).
- Scope rule vs the classification paper: toltl keeps strata operational
  with kinship citations only; variety-alignment theorems belong to the
  classification thread. The size-vs-depth measurement (E5) is toltl's.
