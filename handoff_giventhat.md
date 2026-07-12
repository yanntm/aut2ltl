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

- **GT1 / GT2 DONE.** `interval.py` (the interval + endpoints + choose),
  `ladder.py` (the five `exists_*`, `rec_hull`, `rung_of`, chain
  read-offs). GT1 is steps 1–2 of the operation; GT2's rungs are output
  metrics + optional constraints. F1–F8 filled.
- **GT3 / GT4 BUILT (the cake).** `quotient.py` (`Quotient`,
  `congruence`, `syntactic_congruence`, `compose`, `hull`, `admits`,
  `least_member` / `greatest_member`), `stutter.py` (YES/UNKNOWN),
  `simplify.py` (the greedy), `__main__.py` (the CLI). `syntactic_blocks`
  promoted public in `calculus.reduce`. **The tool runs:**
  `python3 -m sosl.sos.giventhat NEG_PHI.sos K.sos -o B.sos`.
  F13 **CONFIRMED** — the three §6 examples all reach `|𝒞(B)| = 3`
  (syntactic seed, relax); fairness `B` is byte-equal to `𝓘(GF b)`.
  Soundness law `B ∩ P_K == P_min` green on emission.
- Prerequisites harness-green: the calculus package and
  `sosl.sos.classify`. Reuse, never reimplement — spec §0.

## TODO — engineering (next session starts here)

The engine works on the paper's three examples; what is owed is the
*validation* the recentering deferred, then the demonstration.

1. **The GT3 oracle gates (`quotient_gate.py`, spec §5.5) — the one that
   matters is gate 3 (F9).** On `bits ≤ 12`: enumerate `2^F`, keep the
   `is_recognized` members, confirm nonempty **iff** `admits`, and
   `least_member`/`greatest_member` = their intersection/union. A
   disagreement convicts Prop 4.2 → **To theory**, never patch the hull.
   Plus gate 1 (morphism, `[ε]` singleton), gate 4 (F10, Prop 4.1 at
   runtime), gate 6 (F11, the Thm 5.7 fixture: stutter quotient `n == 2`,
   `sc(p_min)` universal, verdict UNKNOWN).
2. **F12's remaining half — the corpus sweep (`simplify_gate.py`).** The
   fixture + a small same-stratum sample: the §6.3 language-level
   cross-check `equivalent(reduce(B ∩ P_K), reduce(P_min))` on every
   case, byte-stability of the emitted `.sos`, and the `REFUTED` witness
   leg. Copy the `--one` + `--campaign` + 15 s watchdog pattern.
3. **GT5 (spec §7) — the demonstration.** ~200 small same-stratum pairs;
   the size table; the five headlines (incl. greedy-vs-exhaustive gap,
   *a heuristic quality, not evidence on Conj 4.5*).

Do **not** build: stutter tier 2, the Wagner brute probe, the W-series
(spec §8). Do not fetch MCC data.

## TODO — theory

Nothing pending. F13 is confirmed (see report). Next items land when
engineering files F9 (the Prop 4.2 oracle — the one result that can
falsify the core) or F14 (the headline rate — if ~0, the paper's central
claim is empty and theory must know first).

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
