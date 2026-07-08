# SoS Classifier — Report on What Is Answered

**Status:** progress report against `sos_classifier_spec.md` **rev. 2**,
2026-07-08. Iteration 2: the X1 profile restated per **distinct language** with
the bench manifest, per-acceptance-family ventilation, weakest-first degree
ordering, and the C§7–8 dictionary naming the rev.-2 spec binds.
**Normative math:** `sos_classification.md` (references below as C§n).
**Code:** `sosl/sosl/sos/classify/` (package map in its `README.md`); tests under
`sosl/tests/sosl/classify_*.py`. Census + profile drivers `classify_census`,
`classify_profile`; the bench manifest is `genaut/manifest.py`.

**One line.** The classifier reads one `.sos` invariant and emits the full
classification record — aperiodicity, `(m±, n±)`, the safety–progress / topological
rung, the parity/Rabin index, and the Wagner degree `ϕ = (γ, s)` — with a
replayable witness on every non-trivial verdict, **for every language whose degree
does not require Wagner's derivative** (all of the triptych, and every language whose
maximal superchains carry a single sign). The derivative tail (C§8) is detected and
reported as PARTIAL rather than resolved; that is the single spec field not yet
computed, exactly as the spec's exit-code-2 anticipates — and, by Proposition 11.1,
no generalized-Büchi input can reach it, which the whole census confirms.

---

## 1. Milestones

| milestone | scope | status |
|---|---|---|
| **K1** primitives + identity + LTL cut | layer 3.1, C§3–4 | **done** — `primitives/`, `aperiodic/`; group witness emitted |
| **K2** chains | engine 3.2, `m`-rungs, parity lengths | **done** — `chains/`; triptych `(m⁺,m⁻)` exact |
| **K3** superchains + degree (non-derived) | engine 3.3, `µ`/`s`, `γ` on `m=0 ∨ n⁺≠n⁻` | **done** — `superchains/`, `readoff/`, `record/`; full triptych `ϕ` reproduced |
| **X0/X1** validation + profile | census + profile drivers | **done (rev. 2)** — 15 091 distinct languages over 19 exhaustive shapes + 1 live parity sample; harness green; per-language profile in §6, bench manifest in `genaut/MANIFEST.md` |
| **K4** derivation | component 3.4, `Fork` fixture | **open** — PARTIAL emitted correctly; `∂𝒜` not wired. No census case reaches the derivative regime (Prop 11.1); the `Fork` specimen (C§9, now fully presented) is the dedicated exercise, still to build |

Every band above is a pure table search on `𝓘(L)` (C§10): power orbits `O(N²)`,
the Green preorders as one-shot principal ideals, chains a longest-alternating-path
DP over the idempotent Hasse DAG per stem `O(N·|E|²)`, superchains the same over the
`R`-order `O(N²)`, the degree arithmetic on four integers. No automaton, no external
tool, no Spot call is on the classification path (Spot enters only as the independent
oracle of the spectrum cross-check, §3).

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
(`n⁺ ≠ n⁻` in every row), so `γ = µ` throughout. Each row ships its witnesses
(spec §1), all replayable by plain membership queries.

---

## 3. Soundness harness — what is green

| harness item (spec §4) | coverage | status |
|---|---|---|
| **4.1** internal laws (always-on) | `0 ≤ m`, `|m⁺−m⁻|≤1`, `|n⁺−n⁻|≤1`, `n≥1 ⇒ m⁺=m⁻`; witness linkage / strict descents / alternation | **green** — asserted inside `classify()` and in every band test |
| **4.2** duality gate | classify `L` and `L̄` (flip `P`): `m⁺↔m⁻`, `n⁺↔n⁻`, `σ↔π`, `δ↔δ`, `γ` equal, open↔closed, dba↔dca | **green** — every census case |
| **4.3** triptych fixtures | records byte-equal to C§9 | **green** — `classify_record`, `classify_readoff` |
| **4.5** witness replay (self) | each chain lasso, folded by `Invariant.member`, matches its bit | **green** — asserted inside `classify()` |
| **4.6** spectrum law (C§11) | every input whose *canonical* presentation is generalized-Büchi classifies with `m⁺ ≤ 0` — Spot's determinization vs. the Carton–Perrin chain algebra, two independent engines | **green** — 0 violations over 15 563 records |
| cross-abundance / cross-path | within one `𝓘`-hash bucket every record carries the same `ϕ` (a language invariant); a split convicts the classifier | **green** — 0 splits, incl. the same language reached via `gba` *and* `parity` enumeration |
| **X0** census validation | classify + all gates over the corpus | **green** — 15 563 records, all SOUND, 0 MISMATCH, 0 BUDGET, 0 PARTIAL |
| **4.5** witness replay (vs `--hoa`) | replay against a presentation's teacher | **not wired** — `--certificates` reserved |
| **4.4** Spot rung/index cross-checks | safety / weak / DBA / parity-index naming vs Spot | **partial** — the spectrum law (4.6) is the one Spot cross-check wired; the full rung-by-rung dictionary reconciliation is deferred |

The spectrum-law gate is the rev.-2 addition and the sharpest of the always-on
checks: it is not a self-consistency assertion but an agreement between two
independent constructions — Spot's determinization (which fixes the *canonical*
acceptance family) and our chain algebra (which fixes `m⁺`). Prop 11.1 says a
generalized-Büchi canonical presentation forces `m⁺ ≤ 0`; a disagreement is exit 4.
Zero fired.

---

## 4. What is not yet answered

Honest accounting against the spec, so the gaps are not mistaken for bugs:

- **The derivative recursion (K4, C§8 / component 3.4).** Only the case
  `m ≥ 1 ∧ n⁺ = n⁻` needs `∂X`. The tool detects it and emits `gamma_partial`
  with `sign = "PARTIAL"`, `gamma = None`, exit code 2 (spec F2, by design).
  **No census language reaches this regime** — not by luck but by Prop 11.1 for the
  generalized-Büchi inputs, and even the parity shapes stay off it (their deep
  degrees `(ω·2, π)`, `(ω², σ)` all have `n⁺ ≠ n⁻`; §6). The regime therefore
  remains untested by real data. Rev. 2 supplies the missing exercise: the `Fork`
  specimen `(a ∧ GF a) ∨ (¬a ∧ FG ¬a)`, coordinates `(1,1,0,0)`, `ϕ = (ω+1, δ)`,
  now fully presented in C§9 with its `.sos` and its 3-state EL HOA. Wiring `∂𝒜`
  (collapse the maximal-superchain basins, rebuild `𝓘(∂X)`, recurse) against that
  fixture is the next unit of work: exit 2 with `PARTIAL(ω)` from the `.sos` alone,
  `ϕ = (ω+1, δ)` and `n_derivations = 1` with `--hoa`.

- **Per-language enumeration abundance.** The §6 profile is per distinct language
  (dedup by `𝓘`-hash). Its **abundance** — how many enumerated automata realise
  each language — is reported per shape (`genaut/MANIFEST.md`, median / max from the
  build-time `census.md`), not per individual language: the compact `det/`/`sos/`
  tiers are already 1-per-language, so per-language abundance would require
  re-classifying the full `tgba/` presentation tier (deferred; the aggregate is
  authoritative and free).

- **X3 cost curves.** Per-input wall is logged; the headline holds (classification
  never approached budget — the ceiling is the construction, not the read-off). The
  cost-vs-`N` scatter with the C§10 bounds overlaid, and the construction-vs-classify
  split, are not yet drawn.

- **HOA-backed certificate replay (3.5 / 4.5)** and the **full Spot rung dictionary
  (4.4)** remain deferred, as in iteration 1.

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
| §5 bench manifest | `genaut/manifest.py` → `genaut/MANIFEST.md` |
| §5–6 census / profile | `tests/sosl/classify_census.py`, `classify_profile.py` |

---

## 6. X1 — the measured Wagner-degree profile, per language

### 6.1 The bench (spec §5)

The corpus is the genaut census: for a fixed **shape** `(n states, k APs, c
colours, acceptance family)`, every tiny automaton is enumerated, Spot-reduced,
deduplicated to presentations (`tgba/`), then canonicalized to one deterministic
automaton and one syntactic invariant `𝓘(L)` **per distinct language**
(`det/` / `sos/`, deduped by the `𝓘`-hash of [SωS26 Thm. 5.1]). The full
reduction funnel — combos → byte-distinct → kept → **languages**, the collapse
ratio, the enumeration abundance, and the algebra-size spread `N = |𝒞|` — is the
bench manifest `genaut/MANIFEST.md`, one row per shape × acceptance family. The
headline:

- **19 exhaustively censused shapes**, generalized-Büchi and parity families over
  `n ≤ 3`, `k ≤ 3`, `c ≤ 3` (under the tractability wall of `SHAPES.md`);
- **1 live non-exhaustive parity sample**, `2state1ap2acc_parity` (id-space
  `4.3·10⁹`), a uniform random probe still extracting — the report cites the folder's
  live language count, not `sample.json`'s in-run checkpoint;
- the compression the `𝓘` dedup buys ranges from `1.00x` (language-sparse shapes) to
  **`7.20x`** (`2state1ap1acc`: 929 presentations → 129 languages, one language
  realised by up to 331 automata);
- **15 563 classification records → 15 091 distinct languages** (the 472-record gap
  is the same language reached from more than one shape — folded by `𝓘`-hash, and a
  free cross-consistency check, §3).

The parity family is the whole reason the corpus reaches depth. Every bare
(generalized-Büchi) shape and every 1-colour parity shape canonically collapses to
generalized-Büchi; only the **2-colour parity** shapes produce genuinely deeper
canonical acceptance (`1state2ap2acc_parity`: 18 parity + 18 co-Büchi of 58
languages; the sampled `2state1ap2acc_parity`: 151 parity + 214 co-Büchi).

### 6.2 The degree profile — distinct languages, weakest-first

The first measured Wagner-degree distribution of a systematically enumerated
ω-language class, over **distinct languages** (spec §5(iv)), ordered by Wagner
degree with the trivial pair set apart and named by the C§7–8 dictionary:

| `ϕ = (γ, s)` | `(m⁺, m⁻, n⁺, n⁻)` | class (§7–8 dictionary) | languages |
|---|---|---|--:|
| `(0, σ)` | `(−1, 0, −1, 0)` | empty (trivial open) | 1 |
| `(0, π)` | `(0, −1, 0, −1)` | universal (trivial closed) | 1 |
| *— the trivial pair, set apart: the weakest class —* | | | *2* |
| `(1, δ)` | `(0, 0, 0, 0)` | **clopen — properly `Δ₁`** | 81 |
| `(1, σ)` | `(0, 0, 0, 1)` | properly open — guarantee | 6 |
| `(1, π)` | `(0, 0, 1, 0)` | properly closed — safety | 12 949 |
| `(2, σ)` | `(0, 0, 1, 2)` | properly `Σ₂` | 8 |
| `(2, π)` | `(0, 0, 2, 1)` | properly `Π₂` | 2 |
| `(ω, σ)` | `(0, 1, −1, 0)` | properly `Gδ` — DBA-proper | 1 642 |
| `(ω, π)` | `(1, 0, 0, −1)` | properly `Fσ` — DCA-proper | 232 |
| `(ω·2, π)` | `(1, 1, 1, 0)` | one Rabin pair, `π` side (superchain `n=1`) | 16 |
| `(ω², σ)` | `(1, 2, −1, 0)` | parity-`{0,1,2}`-proper | 153 |

LTL-definable: **9 712**; non-LTL: **5 379** — the aperiodic axis cuts across the
degree rows (C§7.1), independent of topological depth.

**The `(1, δ)` correction, owed to the theory team.** Iteration 1 misnamed this row
"properly `Δ₂`". Per C§8: `(1, δ)`, coordinates `(0,0,0,0)`, is the nontrivial
**clopen** class — both the open and the closed test of C§7 pass — properly
`Δ₁`, one notch *below* the properly open/closed pair. Properly `Δ₂` is `(2, δ)`,
coordinates `(0,0,1,1)`, which the census does not reach (it is a derivative-free
self-dual level requiring `n⁺ = n⁻ = 1`). Corrected here and in the driver's naming.

### 6.3 Ventilation by acceptance family (C§11 made visible, spec §5(i))

The same profile, split by the **canonical** acceptance family (read off the
deterministic presentation, not the enumeration tag — a parity-*enumerated*
language whose canonical form is generalized-Büchi lands in the gba bucket):

| canonical acceptance | degrees reached | languages | Prop 11.1 |
|---|---|--:|---|
| generalized-Büchi | `(0,σ)`, `(1,δ)`, `(1,σ)`, `(1,π)`, `(2,σ)`, `(2,π)`, `(ω,σ)` | 14 689 | **inside the list** — every one has `m⁺ ≤ 0`, ceiling `(ω,σ)` |
| trivial (`t`) | `(0,π)` | 1 | inside the list |
| co-Büchi | `(ω,π)` | 232 | `m⁺ = 1` — outside gba, exactly as allowed |
| genuine parity | `(ω·2,π)`, `(ω²,σ)` | 169 | `m⁺ = 1` — the deep band, parity-only |

This *is* Proposition 11.1, verified, and its converse demonstrated at scale.
Read the first two rows: no generalized-Büchi or trivial input — 14 690 languages,
**however many states, colours, or letters were enumerated** — escapes the
proposition's `{(0,σ),(0,π)} ∪ {(n,s):1≤n<ω} ∪ {(ω,σ)}` list, and none reaches the
derivative regime (`γ = µ` throughout, 0 PARTIAL). The bottom two rows are the
converse: `m⁺ = 1` — a genuine positive chain — appears **only** where the canonical
acceptance is co-Büchi or parity. Against iteration 1's generalized-Büchi-only
census, where `(ω, π)` and `(ω², σ)` each surfaced once or twice through hand-made
specimens, the parity family populates them **232** and **153** times, and adds the
new `(ω·2, π)` (16) — the cheapest door to depth is the acceptance family, before
the state count, precisely as C§11 argues.

### 6.4 Self-consistency and cost

The duality pairs appear together with matching multiplicities up to which side the
census enumerates (`(2,σ)`↔`(2,π)`, `(ω,σ)`↔`(ω,π)`, `(1,σ)`↔`(1,π)`,
`(0,σ)`↔`(0,π)`), and the self-dual `δ` rows sit alone — the duality gate's
prediction, visible corpus-wide. Classification never approached its budget; the
practical ceiling met throughout is the **construction** of `𝓘(L)`, never the
read-off — direct evidence for C§10's claim that once the invariant is in hand the
whole tower is cheap. Per-input records (coordinates, rungs, `ϕ`, verdict, wall) are
the `stats.json`-shaped ledgers under `sosl/tests/sosl/logs/rev2/`.

### 6.5 Reproduction

```
# 1. build / refresh the corpus tiers (genaut) — one-off per shape
python3 genaut/gen/rebuild.py                       # tgba -> det + sos, all shapes
python3 genaut/gen/sample.py 2,1,2,parity --target-langs 1024 --seed 0   # the sample

# 2. the bench manifest (parses the build-time census.md — recomputes nothing)
python3 genaut/manifest.py                          # -> genaut/MANIFEST.md

# 3. classify the det tier per shape (acceptance family + spectrum gate need the
#    presentation; the sos tier is faster but has no acceptance axis)
for tag in $(ls genaut/corpus/det/); do \
  python3 -m tests.sosl.classify_census genaut/corpus/det/$tag \
      --logs sosl/tests/sosl/logs/rev2/$tag ; done            # (run from sosl/)

# 4. aggregate the per-language profile over all ledgers
python3 -m tests.sosl.classify_profile sosl/tests/sosl/logs/rev2/*/records.jsonl \
    --out sosl/tests/sosl/logs/rev2
```

The parity sample is a moving target (extraction over a `4.3·10⁹` id-space runs on);
its counts are as of this report's run and grow monotonically — rerunning step 3–4
after more draws only adds languages to the deep rows, never moves an existing one.
