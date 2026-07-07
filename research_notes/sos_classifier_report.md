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
| **K4** derivation + campaign | component 3.4, X1–X3 | **open** — PARTIAL emitted correctly; `∂𝒜` + census campaign not wired |

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
| **4.5** witness replay (vs `--hoa`) | replay against a presentation's teacher | **not wired** — `--certificates` reserved |
| **4.4** Spot cross-checks | safety / weak / DBA / parity-index vs Spot over the census | **not run** — needs the census campaign |

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
  No triptych case exercises this; a deliberate `m≥1, n⁺=n⁻` specimen is needed to
  test it once wired.

- **The census campaign (X1, X3).** The engines are ready to run over the
  genaut-enumerated census (`sos_census.md`); what remains is the driver that builds
  each census language's `.sos`, classifies it, and tabulates the distribution of
  rungs, parity lengths, `(m,n)` pairs, and degrees — the first measured Wagner-degree
  profile of a systematically enumerated class — plus the cost curves of X3. This is
  the highest-signal next step and is read-only over the invariants.

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
