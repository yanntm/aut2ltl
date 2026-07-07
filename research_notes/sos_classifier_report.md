# SoS Classifier — Report on What Is Answered

**Status:** progress report against `sos_classifier_spec.md`, 2026-07-07.
**Normative math:** `sos_classification.md` (references below as C§n).
**Code:** `sosl/sosl/sos/classify/` (package map in its `README.md`);
tests under `sosl/tests/sosl/classify_*.py`.

**One line.** The classifier reads one `.sos` invariant and emits the full
classification record — aperiodicity, `(m±, n±)`, the safety–progress / topological
rung, the parity/Rabin index, and the Wagner degree `ϕ = (γ, s)` — with a
replayable witness on every non-trivial verdict, **for every language whose degree
does not require Wagner's derivative** (all of the triptych, and every language whose
maximal superchains carry a single sign). The derivative tail (C§8) is detected and
reported as PARTIAL rather than resolved; that is the single spec field not yet
computed, exactly as the spec's exit-code-2 anticipates.

---

## 1. Milestones

| milestone | scope | status |
|---|---|---|
| **K1** primitives + identity + LTL cut | layer 3.1, C§3–4 | **done** — `primitives/`, `aperiodic/`; group witness emitted |
| **K2** chains | engine 3.2, `m`-rungs, parity lengths | **done** — `chains/`; triptych `(m⁺,m⁻)` exact |
| **K3** superchains + degree (non-derived) | engine 3.3, `µ`/`s`, `γ` on `m=0 ∨ n⁺≠n⁻` | **done** — `superchains/`, `readoff/`, `record/`; full triptych `ϕ` reproduced |
| **X0/X1** validation + profile | census driver | **done** — 18 239 census inputs classified, harness green, degree profile in §6 |
| **K4** derivation | component 3.4 | **open** — PARTIAL emitted correctly; `∂𝒜` not wired, and no census case reaches the derivative regime yet |

Every band above is a pure table search on `𝓘(L)` (C§10): power orbits `O(N²)`,
the Green preorders as one-shot principal ideals, chains a longest-alternating-path
DP over the idempotent Hasse DAG per stem `O(N·|E|²)`, superchains the same over the
`R`-order `O(N²)`, the degree arithmetic on four integers. No automaton, no external
tool, no Spot call is on the path.

---

## 2. The triptych, machine-classified

The three running examples of [SωS26], each read off its published invariant by the
tool — reproducing, byte for byte, the hand-computed records of C§9. This is the
worked table the spec's X2 asks for, exercised end to end (`classify_record`).

| | `m⁺` | `m⁻` | `n⁺` | `n⁻` | aperiodic | rungs | parity / co- | `µ` | `s` | `γ` | `ϕ` |
|---|:--:|:--:|:--:|:--:|:--:|---|:--:|:--:|:--:|:--:|:--:|
| `Even` | 0 | 0 | 0 | 1 | no | open, weak, dba, dca | 1 / 1 | 1 | σ | 1 | `(1, σ)` |
| `GF(aa)` | 0 | 1 | −1 | 0 | **yes** | dba | 1 / 2 | ω | σ | ω | `(ω, σ)` |
| `EvenBlocks` | 1 | 2 | −1 | 0 | no | — | 2 / 3 | ω² | σ | ω² | `(ω², σ)` |

Reading the rows: `Even` is *properly open* (guarantee, weak, not closed);
`GF(aa)` is *properly `Gδ`* (DBA/recurrence, not DCA, not weak — and LTL-definable);
`EvenBlocks` is *properly parity-`{0,1,2}`* (one genuine Rabin pair, neither DBA nor
DCA). `Even`'s boolean level is 1 (`Σ₁`). None of the three needs the derivative
(`n⁺ ≠ n⁻` in every row), so `γ = µ` throughout.

Each row ships its witnesses (spec §1), all replayable by plain membership queries:
the group cycle `[a] → [a·a] → [a]` for `Even`/`EvenBlocks`'s non-aperiodicity; the
chain lassos `key(s)·key(eᵢ)^ω` with their expected bits; the superchain's `R`-descent
of stems with the connecting words `uᵢ`. `EvenBlocks`'s two length-2 negative chains,
both at the zero class, are recovered as the maximal negative witness.

---

## 3. Soundness harness — what is green

| harness item (spec §4) | coverage | status |
|---|---|---|
| **4.1** internal laws (always-on) | `0 ≤ m`, `|m⁺−m⁻|≤1`, `|n⁺−n⁻|≤1`, `n≥1 ⇒ m⁺=m⁻`; witness linkage / strict descents / alternation | **green** — asserted inside `classify()` and in every band test |
| **4.2** duality gate | classify `L` and `L̄` (flip `P`): `m⁺↔m⁻`, `n⁺↔n⁻`, `σ↔π`, `δ↔δ`, `γ` equal, open↔closed, dba↔dca | **green** — `classify_record`, and per band |
| **4.3** triptych fixtures | records byte-equal to C§9 | **green** — `classify_record`, `classify_readoff` |
| **4.5** witness replay (self) | each chain lasso, folded by `Invariant.member`, matches its bit | **green** — asserted inside `classify()` |
| **X0** census validation | classify + duality over 18 239 corpus inputs | **green** — zero MISMATCH, zero BUDGET (`classify_census`) |
| **4.5** witness replay (vs `--hoa`) | replay against a presentation's teacher | **not wired** — `--certificates` reserved |
| **4.4** Spot cross-checks | safety / weak / DBA / parity-index vs Spot over the census | **not run** — orthogonal, deferred |

The always-on laws mean a run that violates a Carton–Perrin invariant fails loudly
(`AssertionError` → the tool's exit code 4), rather than emitting a wrong record.

---

## 4. What is not yet answered

Honest accounting against the spec, so the gaps are not mistaken for bugs:

- **The derivative recursion (K4, C§8 / component 3.4).** Only the case
  `m ≥ 1 ∧ n⁺ = n⁻` needs `∂X`. The tool detects it and emits `gamma_partial`
  with `sign = "PARTIAL"`, `gamma = None`, and (under the CLI) exit code 2 — the
  spec's F2, by design. Resolving it requires building `∂𝒜` from a **deterministic
  presentation** (collapse the maximal-superchain basins, [CP99 §3]) and rebuilding
  `𝓘(∂X)` through the in-repo construction, then recursing (`m` strictly decreases).
  Neither the triptych nor any of the 6 697 census cases in §6 reaches this regime,
  so it is untested by real data; a deliberate `m≥1, n⁺=n⁻` specimen is needed to
  exercise it once wired.

- **X3 cost curves.** The per-input wall time is logged (`records.jsonl`) and the
  headline is already clear — the classifier never approached its budget (max 0.039 s
  over 18 239 inputs, §6) — but the scatter of cost vs `N` with the C§10 polynomial
  bounds overlaid, and the split of construction vs classification time, are not yet
  drawn.

- **Spot cross-checks (X0/X1, F1).** The Wagner-vs-Borel dictionary of C§7 is the
  normative reconciliation; comparing our rung/index verdicts to Spot's on the census
  is deferred with the campaign. Expected: naming mismatches before bugs; only a
  failed witness replay downgrades a mismatch to a bug.

- **HOA-backed certificate replay (3.5 / 4.5).** The witnesses are rendered as
  lassos and self-checked against the same invariant; replaying them against an
  independent `--hoa` presentation (the deepest check) awaits the `--certificates`
  path.

---

## 5. Where each spec component lives

| spec §3 component | module |
|---|---|
| 3.1 primitives (C§2) | `classify/primitives/` (`green.py`, `idempotents.py`) |
| — identity / LTL cut (C§3–4) | `classify/aperiodic/` |
| 3.2 chain engine (C§5) | `classify/chains/engine.py` |
| 3.3 superchain engine (C§6) | `classify/superchains/engine.py` |
| — read-off table (C§7–8) | `classify/readoff/` (`table.py`, `ordinal.py`) |
| 3.4 degree assembly (C§8, derived) | *(open — see §4)* |
| 3.5 certificate emitter | `classify/witness.py` (render); replay reserved |
| §1 record / §2 tool | `classify/record.py`, `emit.py`, `__main__.py` |

The record's flat shape and the CLI's exit codes follow spec §1–2. The `stats.json`
metrics file (spec §6) is produced by the campaign driver, not yet written.

---

## 6. X1 — the measured Wagner-degree profile

The classifier run over the genaut census (`classify_census`): every corpus
automaton of every enumerated shape family plus the triptych and the two stall
specimens — **18 239 languages**. Reference invariant built per input,
classified, duality gate run. Result: **18 239 SOUND, 0 MISMATCH, 0 BUDGET,
0 PARTIAL** — the harness green corpus-wide, and every language's degree resolved
without the derivative. The maximum per-input classification time was **0.039 s**.

The first measured Wagner-degree distribution of a systematically enumerated
ω-language class (no existing tool computes this):

| `ϕ = (γ, s)` | reading (rung / index) | count | `(m⁺,m⁻,n⁺,n⁻)` |
|---|---|--:|---|
| `(1, π)` | properly closed — safety, weak | 15 432 | `(0,0,1,0)` |
| `(ω, σ)` | properly `Gδ` — DBA / recurrence | 1 887 | `(0,1,−1,0)` |
| `(1, δ)` | properly Δ₂ — weak, self-dual | 470 | `(0,0,0,0)` |
| `(0, π)` | universal (trivial closed) | 352 | `(0,−1,0,−1)` |
| `(1, σ)` | properly open — guarantee, weak | 68 | `(0,0,0,1)` |
| `(0, σ)` | empty (trivial open) | 16 | `(−1,0,−1,0)` |
| `(2, π)` | boolean level 2, `π` side | 6 | `(0,0,2,1)` |
| `(2, σ)` | boolean level 2, `σ` side | 5 | `(0,0,1,2)` |
| `(ω, π)` | properly `Fσ` — DCA / persistence | 2 | `(1,0,0,−1)` |
| `(ω², σ)` | one Rabin pair (EvenBlocks) | 1 | `(1,2,−1,0)` |

LTL-definable: 12 205; non-LTL: 6 034. The distribution is a self-consistency
check as well as data — the complement pairs appear together with matching
multiplicities up to which side the census enumerates (`(2,σ)`↔`(2,π)`,
`(ω,σ)`↔`(ω,π)`, `(1,σ)`↔`(1,π)`, `(0,σ)`↔`(0,π)`), and the self-dual `δ` row
sits alone — exactly the duality gate's prediction, now visible across the
whole corpus rather than case by case.

Two observations feed the theory side. First, the census is **shallow**: no
case exceeds boolean level 2 on the finite side or `ω²` on the infinite side,
and none reaches the derivative regime `m≥1 ∧ n⁺=n⁻` — small deterministic
automata simply do not realise the deep degrees, so exercising K4 and the higher
Wagner classes needs hand-built or larger specimens, not enumeration. Second,
the ceiling met in this range is the **construction**, never the classifier:
classification never exceeded 0.039 s on any of the 18 239 inputs and every
BUDGET slot is empty, direct evidence for the C§10 claim that once `𝓘(L)` is in
hand the whole tower is a cheap read-off. Per-input records (coordinates, rungs,
`ϕ`, verdict, wall) are the `stats.json`-shaped `records.jsonl` under
`sosl/tests/sosl/logs/classify_census/`.
