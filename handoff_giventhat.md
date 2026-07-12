# Handoff — SoS given-that

## The goal, in one line

    simplify( 𝓘(¬φ), 𝓘(K) )  →  𝓘(B)

Two `.sos` in, one **smaller** `.sos` out: `ℒ(B) ∩ ℒ(K) = ℒ(¬φ) ∩ ℒ(K)`
(legal, [DPT25] Thm 1) and `|𝒞(B)| ≤ min(|𝒞(¬φ)|, |𝒞(P_min)|,
|𝒞(P_max)|)` (never a regression). It is the algebraic double of
[DPT25]'s *Bounded-by-Minato*: they pick a simpler Boolean *label*
between per-transition bounds, we pick a smaller *table* between
language bounds. Everything is in service of that operation, or is
decommissioned (spec §8).

## The three documents

- **Spec (the work order):** `research_notes/sos_giventhat_spec.md` —
  milestones, algorithms to the function level, gates, traps §10,
  expected failures §9. Where spec and paper disagree: STOP and report.
- **Paper (normative math):** `research_notes/sos_giventhat.md`. Map:
  §3 → GT1; §4 (**Prop 4.1, 4.2, 4.3, Thm 4.4**) → GT3; §4.6 + Lemma 5.2
  → GT4; §5.2 → GT2; §6 → the fixture prediction; §7 → GT5. Appendix A
  is decommissioned material — do not build from it.
- **Report (your channel back):** `research_notes/sos_giventhat_report.md`
  — slots F1–F8 delivered, F9–F15 pending and re-cut. Anything
  surprising goes to **To theory** the moment it is found.

## The one proposition to keep in your head

*Paper Prop 4.2.* For **any** congruence `π` of the aligned table,

    hull_π(Q) := π⁻¹( sat_{T/π}( forced_π(Q) ) )

is the least `π`-recognizable superset of `Q`. Hence the interval
contains a `B` recognized by `T/π` **iff** `hull_π(P_min) ⊆ P_max`, and
`hull_π(P_min)` is then that least `B`. One cell pass + one saturation
on the quotient. Run inside a greedy that merges classes while it can
(Prop 4.3 licenses exactly that), this is the entire engine.

## State

- **GT1 DONE** — `giventhat/interval.py` (`Interval`, `given_that`,
  `k_settles_phi` / `k_refutes_phi`, `choose` / `decompose`),
  `conjugacy_classes` in `calculus.surgery`. It *is* steps 1–2 of the
  operation. Gates green (fixture + 700-pair campaign). F1–F4 filled.
- **GT2 DONE, re-scoped** — `giventhat/ladder.py` (the five `exists_*`,
  `forced`, `h_below`, `rec_hull`, the chain read-offs), `r_classes` in
  `calculus.surgery`. Rung oracle 6 222/6 222. The rungs are **no longer
  the deliverable**: they are output metrics (rung of `¬φ` → rung of
  `B`) and optional constraints (spec §6.5, via Lemma 5.2). F5–F8 filled.
- Prerequisites harness-green: the calculus package (align, materialize,
  surgery incl. `saturate` / hulls, `reduce`, `decide`, witnesses) and
  `sosl.sos.classify`. Reuse, never reimplement — spec §0 lists exactly
  what you get.

## TODO — engineering (next session starts here)

1. **GT3 (spec §5) — the bounded quotient engine.** `quotient.py`:
   `congruence(table, seeds)` (union-find + letter-worklist; quotient
   table via **`Table.of_raw`**, which already is the shared shortlex
   BFS — no new BFS), then `forced` / `hull` / `admits` /
   `least_member` / `greatest_member` / `is_recognized`. Plus a thin
   `stutter.py` (the stutter seeds are one instance; verdict YES/UNKNOWN,
   **never NO**) and one commissioned addition:
   `syntactic_congruence` promoted out of `reduce._blocks`. Gate hard on
   the `bits ≤ 12` oracle (spec §5.5 gate 3) — that is what makes
   Prop 4.2 falsifiable.
2. **GT4 (spec §6) — the simplifier and the tool.** `simplify.py` (the
   greedy; seeds `π_{¬φ}` / identity / stutter; relax **and** restrict;
   pick the best against the three reference points) and a thin
   `__main__.py`: `python3 -m sosl.sos.giventhat A.sos K.sos -o B.sos`.
   The soundness law `B ∩ P_K == P_min` is asserted on every emission.
3. **GT5 (spec §7) — the demonstration.** ~200 small same-stratum corpus
   pairs; the size table; the headline rate.

Do **not** build: stutter tier 2, the Wagner brute probe, the W-series
(spec §8 — reasons given there). Do not fetch MCC data.

## TODO — theory

Nothing pending. Next items land when engineering files F9 (the Prop 4.2
oracle), F13 (the paper §6 prediction: a guarantee `B` with `< 5`
classes on [DPT25]'s own example) or F14 (the headline rate — if it is
~0, the paper's central claim is empty and theory must know first).

## Operational facts (save the rediscovery)

- Run from `sosl/` as modules: `cd sosl && python3 -m tests.giventhat.X`.
  Tests in `sosl/tests/giventhat/`, logs in its `logs/` (gitignored),
  never `/tmp`.
- Corpus: `genaut/corpus/flat_canon/` — `sos/*.sos` (canonical,
  complement-closed), `det/*.hoa` (same basename), `sos/*.cat` sidecars
  (`sosl.sos.classify.io.parse_cat`). Counts move under concurrent
  regeneration — recompute, never hardcode.
- **Alphabet strata:** `align` asserts equal alphabets; sample pairs
  WITHIN one stratum (calculus spec §8.2).
- Reuse pointers: `_Corpus` in `sosl/tests/calculus/v1_align.py`
  (invariant cache, strata, complement-partner map — never guess
  partners from filenames); `check_pair` in `tests/giventhat/
  interval_gate.py` is the per-pair gate pattern; the fixture pair builds
  via `tests.giventhat.fixtures.build()`.
- Load/dump only through `sosl.sos.io` (`load_invariant` /
  `dump_invariant`) — never hand-parse `.sos`.
- Spot 2.14.5 importable, bounded-or-skipped, never waited on.
- Experiment pattern: copy `sosl/tests/calculus/v2_stutter.py` (`--one`
  + `--campaign`, 15 s per-case watchdog, checkpoint file); validated
  `.md`/`.csv` promoted to `reference/giventhat/` with the 4-line header.
- Type-annotate every public signature — house rule.

## Gotchas

- **Concurrent sessions** commit here. Unfamiliar modified files are NOT
  yours — commit ONLY your files by explicit path, never `git add -A`,
  never touch history.
- **Layering law:** `sosl.sos.giventhat` imports `sosl.sos`,
  `sosl.sos.calculus`, `sosl.sos.classify` — nothing else. Test scripts
  may import anything.
- Read the trap list (spec §10) BEFORE coding — several traps are bugs
  that type-check and pass casual testing: saturating on `T` instead of
  the quotient, inserting a raw image pair without `linked_pair_of`,
  a stutter verdict of NO, a second Tarjan, and **claiming minimality**
  (the greedy achieves, it does not minimize).
- House conventions: `__init__.py` carries re-exports ONLY (docs live in
  `README.md` + `algorithm.md`); no `functools.lru_cache` (an operation
  cache is an explicit memo slot on the owning object — `Table._linked` /
  `_conjugacy` are the idiom); prefer new files over editing existing.
