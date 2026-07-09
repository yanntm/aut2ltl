# SoS Classifier — Report on What Is Answered

**Status:** progress report against `sos_classifier_spec.md` **rev. 2**,
2026-07-08. **Iteration 3:** the census is restated over the project's
irredundant reference benchmark — the **`flat_canon` catalogue** (every small
ω-language, deduped up to renaming and closed under complement) — and the
classification is now a **first-class corpus artifact**: every language carries a
`.cat` category sidecar next to its `.sos`, and the benchmark's auto-built study
(`genaut/corpus/flat_canon/STUDY.md`) aggregates them. The classifier is no
longer run as a separate campaign; its verdict ships with the corpus.
**Normative math:** `sos_classification.md` (references below as C§n).
**Code:** classifier `sosl/sosl/sos/classify/` (package map in its `README.md`);
categorizer + study `genaut/gen/categorize.py`, `genaut/flat_study.py`.

**One line.** The classifier reads one `.sos` invariant and emits the full
classification record — the **LTL / non-LTL cut** (aperiodicity), `(m±, n±)`, the
safety–progress / topological rung, the parity/Rabin index, and the Wagner
degree `ϕ = (γ, s)` — with a replayable witness on every non-trivial verdict,
**for every language whose degree does not require Wagner's derivative** (all of
the triptych, and every one of the 3938 catalogue languages). The derivative tail
(C§8) is detected and reported as PARTIAL rather than resolved; that is the single
spec field not yet computed, and — by Proposition 11.1 — no census language
reaches it, which the whole catalogue confirms (0 PARTIAL).

---

## 1. Milestones

| milestone | scope | status |
|---|---|---|
| **K1** primitives + identity + LTL cut | layer 3.1, C§3–4 | **done** — `primitives/`, `aperiodic/`; group witness emitted |
| **K2** chains | engine 3.2, `m`-rungs, parity lengths | **done** — `chains/`; triptych `(m⁺,m⁻)` exact |
| **K3** superchains + degree (non-derived) | engine 3.3, `µ`/`s`, `γ` on `m=0 ∨ n⁺≠n⁻` | **done** — `superchains/`, `readoff/`, `record/`; full triptych `ϕ` reproduced |
| **X0/X1** validation + profile | census + `.cat` materialization + study | **done (iter. 3)** — the whole `flat_canon` catalogue classified (3938 languages), one `.cat` per language, aggregated into `STUDY.md`; internal laws + duality symmetry green |
| **K4** derivation | component 3.4, `Fork` fixture | **open** — PARTIAL emitted correctly; `∂𝒜` not wired. No catalogue language reaches the derivative regime (Prop 11.1); the `Fork` specimen (C§9) is the dedicated exercise, still to build |

Every band above is a pure table search on `𝓘(L)` (C§10): power orbits `O(N²)`,
the Green preorders as one-shot principal ideals, chains a longest-alternating-path
DP over the idempotent Hasse DAG per stem, superchains the same over the `R`-order,
the degree arithmetic on four integers. No automaton, no external tool, no Spot
call is on the classification path — which is exactly why the category can be read
off the stored `.sos` alone and written as a sidecar (`categorize.py`). Spot enters
only as the independent oracle of the spectrum cross-check (§3), on the HOA tier.

---

## 2. The triptych, machine-classified

The three running examples of [SωS26], each read off its published invariant by the
tool — reproducing, byte for byte, the hand-computed records of C§9. This is the
worked table the spec's X2 asks for, exercised end to end (`classify_record`).

| | `m⁺` | `m⁻` | `n⁺` | `n⁻` | LTL | rungs | parity / co- | `µ` | `s` | `γ` | `ϕ` |
|---|:--:|:--:|:--:|:--:|:--:|---|:--:|:--:|:--:|:--:|:--:|
| `Even` | 0 | 0 | 0 | 1 | no | open, weak, dba, dca | 1 / 1 | 1 | σ | 1 | `(1, σ)` |
| `GF(aa)` | 0 | 1 | −1 | 0 | **yes** | dba | 1 / 2 | ω | σ | ω | `(ω, σ)` |
| `EvenBlocks` | 1 | 2 | −1 | 0 | no | — | 2 / 3 | ω² | σ | ω² | `(ω², σ)` |

Reading the rows: `Even` is *properly open* (guarantee, weak, not closed);
`GF(aa)` is *properly `Gδ`* (DBA/recurrence, not DCA, not weak — and LTL-definable);
`EvenBlocks` is *properly parity-`{0,1,2}`* (one genuine Rabin pair, neither DBA nor
DCA). None of the three needs the derivative (`n⁺ ≠ n⁻` in every row), so `γ = µ`
throughout. Each row ships its witnesses (spec §1), all replayable by plain
membership queries. All three sit inside the catalogue's degree spectrum below.

---

## 3. Soundness harness — what is green

| harness item (spec §4) | coverage | status |
|---|---|---|
| **4.1** internal laws (always-on) | `0 ≤ m`, `|m⁺−m⁻|≤1`, `|n⁺−n⁻|≤1`, `n≥1 ⇒ m⁺=m⁻`; witness linkage / strict descents / alternation | **green** — asserted inside `classify()` on all **3938** categorizations (a failure raises; none did) |
| **4.5** witness replay (self) | each chain lasso, folded by `Invariant.member`, matches its bit | **green** — asserted inside `classify()`, corpus-wide |
| **4.2** duality gate | `L` and `L̄` swap `m⁺↔m⁻`, `n⁺↔n⁻`, `σ↔π`, open↔closed, dba↔dca; `γ` equal | **green — and now structural**: the catalogue is complement-closed, so the degree profile is **exactly** duality-symmetric (every `(γ,σ)` row equals its `(γ,π)` dual; §6.3). The per-record gate also runs in `classify_census` |
| **4.6** spectrum law (C§11) | a language whose *canonical* presentation is generalized-Büchi classifies with `m⁺ ≤ 0` — Spot's determinization vs. the chain algebra, two independent engines | **green** on the HOA tier (`classify_census` over `det/`); and **visible in the catalogue read-off**: `m⁺ ≥ 1` occurs only at the co-Büchi/parity degrees (§6.4), Prop 11.1's converse |
| **4.3** triptych fixtures | records byte-equal to C§9 | **green** — `classify_record`, `classify_readoff` |
| **4.5** witness replay (vs `--hoa`) | replay against a presentation's teacher | **not wired** — `--certificates` reserved |
| **4.4** Spot rung/index cross-checks | full rung-by-rung dictionary vs Spot | **partial** — the spectrum law (4.6) is the one Spot cross-check wired; the rung dictionary reconciliation is deferred |

The duality result is the sharpest of the always-on checks and iteration 3
strengthens it: on the old one-sided per-shape census the gate could only assert
"pairs appear together up to which side the census enumerated". On the
complement-closed catalogue it is an **identity** — the profile's σ- and π-columns
are equal number by number (§6.3), a corpus-wide duality certificate that needs no
reclassification, just the two `.cat` of a language and its stored complement.

---

## 4. What is not yet answered

Honest accounting against the spec, so the gaps are not mistaken for bugs:

- **The derivative recursion (K4, C§8 / component 3.4).** Only the case
  `m ≥ 1 ∧ n⁺ = n⁻` needs `∂X`. The tool detects it and emits `gamma_partial`
  with `sign = "PARTIAL"`, `gamma = None`, exit code 2 (spec F2, by design).
  **No catalogue language reaches this regime** — not by luck but by Prop 11.1 for
  the generalized-Büchi inputs, and even the parity shapes stay off it (their deep
  degrees `(ω·2, ·)`, `(ω², ·)` all have `n⁺ ≠ n⁻`; §6.3). The regime therefore
  remains untested by real data. The `Fork` specimen `(a ∧ GF a) ∨ (¬a ∧ FG ¬a)`,
  coordinates `(1,1,0,0)`, `ϕ = (ω+1, δ)` (C§9), is the dedicated exercise. Wiring
  `∂𝒜` against it is the next unit of work.

- **The `.cat` is `.sos`-only.** The sidecar records the language's degree, cut,
  and coordinates — everything the read-off yields from the invariant. It does *not*
  store the *minimal deterministic acceptance family* (gen-Büchi / co-Büchi /
  parity), which is a Spot read-off of the `det/` presentation. §6.4 recovers the
  Büchi-vs-not split from the coordinates (Prop 11.1, exact) without Spot; the
  finer minimal-acceptance ventilation stays on the HOA tier
  (`classify_census --logs …` over `flat_canon/det/`), not in the auto-report.

- **Presentation abundance.** The `.cat`/`flat_canon` view is one entry per
  language (the irredundant catalogue). *How many automata* realize each language
  is a property of the presentation census (`SHAPES.md`, `genaut/MANIFEST.md`), not
  of this tier — deliberately: `flat_canon` measures languages, the `tgba/` tier
  measures presentations.

- **HOA-backed certificate replay (3.5 / 4.5)** and the **full Spot rung dictionary
  (4.4)** remain deferred.

---

## 5. Where each piece lives

| concern | module |
|---|---|
| 3.1 primitives (C§2) | `sosl/…/classify/primitives/` (`green.py`, `idempotents.py`) |
| — identity / LTL cut (C§3–4) | `sosl/…/classify/aperiodic/` |
| 3.2 chain engine (C§5) | `sosl/…/classify/chains/engine.py` |
| 3.3 superchain engine (C§6) | `sosl/…/classify/superchains/engine.py` |
| — read-off table (C§7–8) | `sosl/…/classify/readoff/` (`table.py`, `ordinal.py`) |
| 3.4 degree assembly (C§8, derived) | *(open — see §4)* |
| §1 record / emit | `sosl/…/classify/record.py`, `emit.py`, `__main__.py` |
| **category materialization** (`.cat` per language, class vocabulary) | `genaut/gen/categorize.py` |
| **auto-report** (LTL cut + degree profile) | `genaut/flat_study.py` → `flat_canon/STUDY.md` |
| presentation-tier census + HOA gates | `sosl/tests/sosl/classify_census.py`, `classify_profile.py` |

---

## 6. X1 — the measured profile over the reference catalogue

### 6.1 The bench

The corpus is the genaut **`flat_canon` catalogue** (`research_notes/genaut_corpus.md`,
`genaut/corpus/flat_canon/STUDY.md`): every ω-language a small automaton realizes,
**counted once**. It folds the three redundancies of an exhaustive automaton sweep
— sub-shape inclusion, unused APs, and AP renaming/polarity (`B_k` orbit-min of the
syntactic `𝓘`) — and is then **closed under complement**. From **19** census shapes
below the tractability wall plus **one** beyond-wall parity sample
(`2state1ap2acc_parity`, id-space `4.3·10⁹`):

- **3790** languages at a fixed AP labeling → **2007** up to renaming (the primals,
  1764 exhaustive + 243 sampled) → **3938** once complement-closed (2007 primals +
  1931 added duals);
- one `.cat` per language, written by `categorize.py` reading each `.sos` — a pure
  read-off, no automaton, no Spot, ~1 s for all 3938;
- superseding iteration 2's per-shape census (15 091 relabel-distinct, one-sided
  languages over the `det/` tiers): this is the **irredundant, complement-symmetric
  language count**, the honest denominator.

### 6.2 The LTL cut — the line everyone asks about first

Is the language **LTL-definable** (star-free / first-order / aperiodic syntactic
ω-semigroup) or does it genuinely **count**? Over the complement-closed catalogue:

| definability | languages |
|---|--:|
| **LTL-definable** (aperiodic) | **2240** |
| **non-LTL** (genuine ω-counting) | **1698** |
| total | 3938 |

**43 % of the small ω-languages are beyond LTL.** The cut is complement-invariant
(aperiodicity is a property of the semigroup `M`, not of `accept`), so it splits the
primals the same way — 1142 LTL / 865 non-LTL of 2007 — and it cuts *across* the
Wagner degrees below: depth and countability are independent axes (§6.3).

### 6.3 The Wagner-degree profile — distinct languages, weakest-first

The first Wagner-degree distribution of the systematically-enumerated small
ω-language class stated over the **irredundant, complement-closed** catalogue.
`non-LTL` is the count in the row that fails the aperiodicity cut; `primals` the
shape-realized share (the rest are added complements):

| `ϕ = (γ, s)` | `(m⁺, m⁻, n⁺, n⁻)` | class (C§7–8) | languages | non-LTL | primals |
|---|---|---|--:|--:|--:|
| `(0, σ)` | `(−1, 0, −1, 0)` | empty — trivial open | 1 | 0 | 1 |
| `(0, π)` | `(0, −1, 0, −1)` | universal — trivial closed | 1 | 0 | 1 |
| *— trivial pair (weakest), set apart —* | | | *2* | | |
| `(1, δ)` | `(0, 0, 0, 0)` | clopen — properly Δ₁ | 62 | 0 | 36 |
| `(1, σ)` | `(0, 0, 0, 1)` | properly open — guarantee | 1356 | 678 | 4 |
| `(1, π)` | `(0, 0, 1, 0)` | properly closed — safety | 1356 | 678 | 1356 |
| `(2, σ)` | `(0, 0, 1, 2)` | properly Σ₂ | 4 | 0 | 4 |
| `(2, π)` | `(0, 0, 2, 1)` | properly Π₂ | 4 | 0 | 1 |
| `(ω, σ)` | `(0, 1, −1, 0)` | properly Gδ — DBA-proper | 466 | 98 | 365 |
| `(ω, π)` | `(1, 0, 0, −1)` | properly Fσ — DCA-proper | 466 | 98 | 128 |
| `(ω·2, σ)` | `(1, 1, 0, 1)` | one Rabin pair — σ side | 12 | 12 | 0 |
| `(ω·2, π)` | `(1, 1, 1, 0)` | one Rabin pair — π side | 12 | 12 | 12 |
| `(ω², σ)` | `(1, 2, −1, 0)` | parity-`{0,1,2}` — proper | 99 | 61 | 99 |
| `(ω², π)` | `(2, 1, 0, −1)` | co-parity-`{0,1,2}` — proper | 99 | 61 | 0 |

Read the `languages` column top to bottom against its mirror: **1 = 1, 1356 = 1356,
4 = 4, 466 = 466, 12 = 12, 99 = 99** — the profile is *exactly* duality-symmetric,
the complement closure made visible (§3). The self-dual `δ` row `(1, δ) = 62` stands
alone. Total 3938; `γ` never exceeds `ω²`; **0 PARTIAL** — no language reaches
Wagner's derivative (`γ = µ` throughout, Prop 11.1). The `primals` column is *not*
symmetric (`(ω, σ)`: 365 vs `(ω, π)`: 128) — it shows exactly which side the
one-sided enumeration reached and which the complement closure had to add.

**Depth ≠ countability, in the numbers.** The non-LTL count spreads over every
depth, not the deep end: half of *safety* (`(1, π)`: 678 / 1356) is already non-
star-free, while a third of the deepest *parity-`{0,1,2}`* rows (`(ω²)`: 38 / 99 per
side) *is* LTL-definable. Only the one-Rabin-pair rows (`(ω·2)`: 12 / 12) are wholly
non-LTL. The aperiodicity axis and the Wagner axis are independent — the classifier
measures both, and the catalogue exhibits their full cross-product.

### 6.4 Acceptance depth, read off the coordinates (Prop 11.1)

The minimal deterministic acceptance family is a Spot read-off of the `det/`
presentation, but Prop 11.1 lets the **Büchi-vs-not** split be read straight off the
`.cat` coordinates — `m⁺ ≤ 0 ⟺ generalized-Büchi-realizable`:

| by `m⁺` | degrees | languages |
|---|---|--:|
| `m⁺ ≤ 0` — generalized-Büchi-realizable | `(0,·)`, `(1,·)`, `(2,·)`, `(ω, σ)` | 3250 |
| `m⁺ = 1`, one positive chain — co-Büchi-proper | `(ω, π)` | 466 |
| `m⁺ ≥ 1`, both signs positive — genuine parity | `(ω·2, ·)`, `(ω², ·)` | 222 |

So **688** of 3938 languages sit genuinely above the generalized-Büchi ceiling, and
they are *exactly* the co-Büchi and parity degrees — Prop 11.1's converse, exhibited
at catalogue scale without a single Spot call. The deep parity band (`(ω·2)`,
`(ω²)`) is reached only by the beyond-wall parity sample, its complement side added
by closure (§6.3, `primals` column). The independent Spot-vs-algebra spectrum gate
(4.6) runs on the `det/` tier and agrees.

### 6.5 Reproduction

```
# 1. build / refresh the catalogue (writes .sos, det HOA, and .cat sidecars)
python3 genaut/gen/flatten.py --canon              # -> corpus/flat_canon/

# 1b. or just (re)categorize an existing sos tier (pure read-off, no rebuild)
python3 genaut/gen/categorize.py                   # -> corpus/flat_canon/sos/*.cat

# 2. the language-level study: LTL cut + Wagner-degree profile, aggregated
#    from the .cat sidecars (no classifier at report time)
python3 genaut/flat_study.py                       # -> corpus/flat_canon/STUDY.md

# 3. (HOA tier, from sosl/) the presentation census + Spot spectrum gate: needs the
#    det/ HOAs, which .sos-only .cat cannot supply — the independent Spot oracle
python3 -m tests.sosl.classify_census genaut/corpus/flat_canon/det \
    --logs sosl/tests/sosl/logs/flat_canon
python3 -m tests.sosl.classify_profile sosl/tests/sosl/logs/flat_canon/records.csv
```

The `.cat` sidecars are git-tracked corpus artifacts, so step 2 (and any consumer
of the categories) is a pure text read-off of the corpus — the classification data
lives *in* the benchmark, regenerated only when the languages change.
