# SoS Classifier — Report on What Is Answered

**Status:** progress report against `sos_classifier_spec.md` **rev. 2**,
2026-07-11. **Iteration 4:** the reference catalogue has **widened** — a curated
beyond-the-wall sampling campaign (17 parity shapes, corpus-aware; selection
criteria in `genaut/README.md` §"Curating a campaign") added ~1000 languages and
lifted the Wagner ceiling from `ω²` to **`ω⁴`**: the catalogue is now **6220**
complement-closed languages (3212 primals). Every gate was rerun on the widened
corpus and is green. This iteration also **drops the json side-metadata**: the
`.cat` sidecar is the only per-language artifact, and every aggregate is a csv
ledger or a generated markdown table (`flat.json` / `flat_canon.json` /
`sample.json` removed; the study derives all composition counts from the corpus
filenames — `_c` marks an added complement, the `<tag>_<id>` name encodes the
origin shape).
**Normative math:** `sos_classification.md` (referenced below as C§n).
**Code:** classifier `sosl/sosl/sos/classify/` (package map in its `README.md`);
`.cat` io + batch tagging `sosl/sosl/sos/classify/io/`; study `genaut/flat_study.py`.

**One line.** The classifier reads one `.sos` invariant and emits the full
classification record — the **LTL / non-LTL cut** (aperiodicity), the
**stutter-invariant** (X-free) refinement, `(m±, n±)`, the safety–progress /
topological rung, the parity/Rabin index, and the Wagner degree `ϕ = (γ, s)` —
with a replayable witness on every non-trivial verdict, **for every language whose
degree does not require Wagner's derivative** (all of the triptych, and every one
of the 6220 catalogue languages, now spanning degrees up to `(ω⁴, ·)`). The
derivative tail (C§4) is detected and reported as PARTIAL rather than resolved;
that is the single spec field not yet computed, and no catalogue language reaches
it (0 PARTIAL) — see §4 for what the widened corpus does and does not say about
that regime.

---

## 1. Milestones

| milestone | scope | status |
|---|---|---|
| **K1** primitives + identity + LTL cut | layer 3.1, C§2, C§3.1–3.2 | **done** — `primitives/`, `aperiodic/`, `stutter.py`; group witness emitted |
| **K2** chains | engine 3.2, C§3.3, `m`-rungs, parity lengths | **done** — `chains/`; triptych `(m⁺,m⁻)` exact |
| **K3** superchains + degree (non-derived) | engine 3.3, C§3.4–3.5, `µ`/`s`, `γ` on `m=0 ∨ n⁺≠n⁻` | **done** — `superchains/`, `readoff/`, `record/`; full triptych `ϕ` reproduced |
| **X0/X1** validation + profile | census + `.cat` materialization + study | **done (iter. 4)** — the whole widened catalogue classified (6220 languages), one `.cat` per language, aggregated into `STUDY.md`; internal laws + duality symmetry + Spot spectrum gate green on the widened corpus |
| **K4** derivation | component 3.4, C§4, `Fork` fixture | **open** — PARTIAL emitted correctly; `∂𝒜` not wired. Still no catalogue language in the derivative regime (§4); the `Fork` specimen (C§5) is the dedicated exercise, still to build |

Every band above is a pure table search on `𝓘(L)` (C§6): power orbits `O(N²)`,
the Green preorders as one-shot principal ideals, chains a longest-alternating-path
DP over the idempotent Hasse DAG per stem, superchains the same over the `R`-order,
the degree arithmetic on four integers. No automaton, no external tool, no Spot
call is on the classification path — which is exactly why the category can be read
off the stored `.sos` alone and written as a sidecar (`sosl.sos.classify.io`; the
whole catalogue re-tags in ~2 s, §6.5). Spot enters only as the independent oracle
of the spectrum cross-check (§3), on the HOA tier.

---

## 2. The triptych, machine-classified

The three running examples of [SωS26], each read off its published invariant by the
tool — reproducing, byte for byte, the hand-computed records of C§5. This is the
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
membership queries. All three sit inside the catalogue's degree spectrum below —
which now extends two `ω`-powers past `EvenBlocks`.

---

## 3. Soundness harness — what is green

All rows below were **rerun on the widened 6220-language catalogue** (this
iteration); ledger under `sosl/tests/sosl/logs/classify_census/flat_canon_wide/`.

| harness item (spec §4) | coverage | status |
|---|---|---|
| **4.1** internal laws (always-on) | `0 ≤ m`, `|m⁺−m⁻|≤1`, `|n⁺−n⁻|≤1`, `n≥1 ⇒ m⁺=m⁻`; witness linkage / strict descents / alternation | **green** — asserted inside `classify()` on all **6220** categorizations (a failure raises; none did) |
| **4.5** witness replay (self) | each chain lasso, folded by `Invariant.member`, matches its bit | **green** — asserted inside `classify()`, corpus-wide |
| **4.2** duality gate | `L` and `L̄` swap `m⁺↔m⁻`, `n⁺↔n⁻`, `σ↔π`, open↔closed, dba↔dca; `γ` equal | **green — and structural**: the catalogue is complement-closed, so the degree profile is **exactly** duality-symmetric (every `(γ,σ)` row equals its `(γ,π)` dual, all ten mirror pairs; §6.3). The per-record gate also ran in `classify_census`: 6220/6220 |
| **4.6** spectrum law (C§7, Prop. 7.1) | a language whose *canonical* presentation is generalized-Büchi classifies with `m⁺ ≤ 0` — Spot's determinization vs. the chain algebra, two independent engines | **green** — `classify_census` over `flat_canon/det`: **6220 SOUND, 0 MISMATCH, 0 BUDGET**. The per-family ventilation (`classify_profile`) exhibits the law *and* its converse: canonical gen-Büchi presentations occupy exactly the `m⁺ ≤ 0` degrees, co-Büchi presentations sit at `(ω, π)`, and every deeper band is carried by parity presentations alone (§6.4) |
| **4.3** triptych fixtures | records byte-equal to C§5 | **green** — `classify_record`, `classify_readoff` |
| **4.5** witness replay (vs `--hoa`) | replay against a presentation's teacher | **not wired** — `--certificates` reserved |
| **4.4** Spot rung/index cross-checks | full rung-by-rung dictionary vs Spot | **partial** — the spectrum law (4.6) is the one Spot cross-check wired; the rung dictionary reconciliation is deferred |

Iteration 4 makes the reruns cheap to state: the `.cat` re-tag of the whole
catalogue is byte-identical to the tracked sidecars (a reproducibility check in
itself, since every `classify()` call re-asserts 4.1 and replays its witnesses),
and the census ledger agrees with the `.cat` aggregation number for number.

---

## 4. What is not yet answered

Honest accounting against the spec, so the gaps are not mistaken for bugs:

- **The derivative recursion (K4, C§4 / component 3.4).** Only the case
  `m ≥ 1 ∧ n⁺ = n⁻` needs `∂X`. The tool detects it and emits `gamma_partial`
  with `sign = "PARTIAL"`, `gamma = None`, exit code 2 (spec F2, by design).
  **No catalogue language reaches this regime** (0 PARTIAL of 6220). The
  statement is sharper than in iteration 3 and needs care: C§7's budget puts the
  regime's floor at the three-state, two-colour parity shape, and that shape
  (`3state1ap2acc_parity`) **is now in the corpus — but only as a sample**
  (51 curated languages of an id-space the wall forbids exhausting), and the
  sample happens to miss the regime. So the regime is no longer "past the
  corpus's reach by construction"; it is *unhit by the draws taken*, and absence
  on a sampled tier proves nothing. The `Fork` specimen
  `(a ∧ GF a) ∨ (¬a ∧ FG ¬a)`, coordinates `(1,1,0,0)`, `ϕ = (ω+1, δ)` (C§5),
  remains the dedicated exercise; wiring `∂𝒜` against it is the next unit of
  work, and a targeted hunt for a derivative-regime language in the
  `3state1ap2acc_parity` id-space would give it a second, corpus-native fixture.

- **The `.cat` is `.sos`-only.** The sidecar records the language's degree, cut,
  stutter bit, and coordinates — everything the read-off yields from the
  invariant. It does *not* store the *minimal deterministic acceptance family*
  (gen-Büchi / co-Büchi / parity), which is a Spot read-off of the `det/`
  presentation. §6.4 recovers the Büchi-vs-not split from the coordinates
  (Prop. 7.1, exact) without Spot; the finer minimal-acceptance ventilation stays
  on the HOA tier (`classify_census` over `flat_canon/det`), not in the
  auto-report.

- **Presentation abundance.** The `.cat`/`flat_canon` view is one entry per
  language (the irredundant catalogue). *How many automata* realize each language
  is a property of the presentation census (`genaut/corpus/SHAPES.md`,
  `genaut/corpus/MANIFEST.md`), not of this tier — deliberately: `flat_canon`
  measures languages, the `tgba/` tier measures presentations.

- **HOA-backed certificate replay (3.5 / 4.5)** and the **full Spot rung dictionary
  (4.4)** remain deferred.

---

## 5. Where each piece lives

| concern | module |
|---|---|
| 3.1 primitives (C§2) | `sosl/…/classify/primitives/` (`green.py`, `idempotents.py`) |
| — identity / LTL cut / stutter (C§3.1–3.2) | `sosl/…/classify/aperiodic/`, `stutter.py` |
| 3.2 chain engine (C§3.3) | `sosl/…/classify/chains/engine.py` |
| 3.3 superchain engine (C§3.4) | `sosl/…/classify/superchains/engine.py` |
| — read-off table (C§2.4–2.5, C§3.5) | `sosl/…/classify/readoff/` (`table.py`, `ordinal.py`) |
| 3.4 degree assembly (C§4, derived) | *(open — see §4)* |
| §1 record / emit | `sosl/…/classify/record.py`, `emit.py`, `__main__.py` |
| **`.cat` io** (writer + batch tagging, reader, Wagner vocabulary) | `sosl/…/classify/io/` — CLI `python3 -m sosl.sos.classify.io <sos-folder>`; also invoked at the end of `flatten.py --canon`, so a corpus rebuild tags itself |
| **auto-report** (LTL cut + stutter + degree profile) | `genaut/flat_study.py` → `flat_canon/STUDY.md` |
| presentation-tier census + HOA gates | `sosl/tests/sosl/classify_census.py`, `classify_profile.py` |

---

## 6. X1 — the measured profile over the reference catalogue

### 6.1 The bench

The corpus is the genaut **`flat_canon` catalogue** (`research_notes/genaut_corpus.md`,
`genaut/corpus/flat_canon/STUDY.md`): every ω-language a small automaton realizes,
**counted once**. It folds the three redundancies of an exhaustive automaton sweep
— sub-shape inclusion, unused APs, and AP renaming/polarity (`B_k` orbit-min of the
syntactic `𝓘`) — and is then **closed under complement**. Iteration 4's widening:
to the exhaustive census shapes below the tractability wall, a **curated
beyond-the-wall campaign** (corpus-aware uniform sampling of 17 parity shapes up to
4 states / 3 atoms / 3 colours, then a bounded, seed-independent selection — the
Wagner frontier in full plus minimal representatives per `(shape, degree,
LTL-class)` stratum; `genaut/README.md`) contributed ~1000 languages that lift the
degree ceiling from `ω²` to `ω⁴`:

- **5110** languages at a fixed AP labeling → **3212** up to renaming (the primals:
  1764 exhaustive + 1448 sampled) → **6220** once complement-closed (3212 primals +
  3008 added duals);
- one `.cat` per language, written by `sosl.sos.classify.io` reading each `.sos` —
  a pure read-off, no automaton, no Spot, ~2 s for all 6220;
- the sampled share is a **probe, not a census**: its languages are real, but
  absence proves nothing there (`STUDY.md` tags every origin shape accordingly).

### 6.2 The LTL cut — the line everyone asks about first

Is the language **LTL-definable** (star-free / first-order / aperiodic syntactic
ω-semigroup) or does it genuinely **count**? Over the complement-closed catalogue:

| definability | languages |
|---|--:|
| **LTL-definable** (aperiodic) | **3736** |
| **non-LTL** (genuine ω-counting) | **2484** |
| total | 6220 |

**40 % of the small ω-languages are beyond LTL** (43 % on the iteration-3
catalogue — the widening added LTL and non-LTL mass in nearly the old proportion).
The cut is complement-invariant (aperiodicity is a property of the semigroup `M`,
not of `accept`), so it splits the primals the same way — 1945 LTL / 1267 non-LTL
of 3212 — and it cuts *across* the Wagner degrees below: depth and countability
are independent axes (§6.3).

The `.cat` also carries the **stutter-invariant** (X-free) refinement of the cut
(C§3.2): **894** of the 6220 languages (14 %) are stutter-invariant, i.e. **24 %**
of the LTL-definable languages drop the `X` operator; like aperiodicity the bit is
complement-invariant (475 primals). The per-degree ventilation is the
`stutter-inv` column of §6.3.

### 6.3 The Wagner-degree profile — distinct languages, weakest-first

The Wagner-degree distribution of the systematically-enumerated small ω-language
class, stated over the **irredundant, complement-closed** catalogue — now spanning
**ten mirror pairs plus three self-dual rows** where iteration 3 had six and one.
`non-LTL` is the count in the row that fails the aperiodicity cut; `stutter-inv`
the stutter-invariant count; `primals` the shape-realized share (the rest are
added complements):

| `ϕ = (γ, s)` | `(m⁺, m⁻, n⁺, n⁻)` | class (C§2.4–2.5) | languages | non-LTL | stutter-inv | primals |
|---|---|---|--:|--:|--:|--:|
| `(0, σ)` | `(−1, 0, −1, 0)` | empty — trivial open | 1 | 0 | 1 | 1 |
| `(0, π)` | `(0, −1, 0, −1)` | universal — trivial closed | 1 | 0 | 1 | 1 |
| *— trivial pair (weakest), set apart —* | | | *2* | | | |
| `(1, δ)` | `(0, 0, 0, 0)` | clopen — properly Δ₁ | 82 | 0 | 10 | 49 |
| `(1, σ)` | `(0, 0, 0, 1)` | properly open — guarantee | 1430 | 704 | 44 | 83 |
| `(1, π)` | `(0, 0, 1, 0)` | properly closed — safety | 1430 | 704 | 44 | 1386 |
| `(2, δ)` | `(0, 0, 1, 1)` | properly Δ₂ | 18 | 2 | 0 | 9 |
| `(2, σ)` | `(0, 0, 1, 2)` | properly Σ₂ | 68 | 21 | 10 | 30 |
| `(2, π)` | `(0, 0, 2, 1)` | properly Π₂ | 68 | 21 | 10 | 41 |
| `(3, σ)` | `(0, 0, 2, 3)` | properly Σ₃ | 40 | 16 | 2 | 35 |
| `(3, π)` | `(0, 0, 3, 2)` | properly Π₃ | 40 | 16 | 2 | 6 |
| `(4, σ)` | `(0, 0, 3, 4)` | properly Σ₄ | 2 | 1 | 0 | 0 |
| `(4, π)` | `(0, 0, 4, 3)` | properly Π₄ | 2 | 1 | 0 | 2 |
| `(ω, σ)` | `(0, 1, −1, 0)` | properly Gδ — DBA-proper | 654 | 159 | 296 | 540 |
| `(ω, π)` | `(1, 0, 0, −1)` | properly Fσ — DCA-proper | 654 | 159 | 296 | 157 |
| `(ω·2, σ)` | `(1, 1, 0, 1)` | one Rabin pair — σ side | 49 | 22 | 10 | 8 |
| `(ω·2, π)` | `(1, 1, 1, 0)` | one Rabin pair — π side | 49 | 22 | 10 | 41 |
| `(ω², σ)` | `(1, 2, −1, 0)` | parity-`{0,1,2}` — proper | 169 | 90 | 23 | 121 |
| `(ω², π)` | `(2, 1, 0, −1)` | co-parity-`{0,1,2}` — proper | 169 | 90 | 23 | 50 |
| `(ω³, σ)` | `(2, 3, −1, 0)` | parity-`{0,…,3}` — proper | 613 | 201 | 56 | 234 |
| `(ω³, π)` | `(3, 2, 0, −1)` | co-parity-`{0,…,3}` — proper | 613 | 201 | 56 | 384 |
| `(ω⁴, σ)` | `(3, 4, −1, 0)` | parity-`{0,…,4}` — proper | 34 | 27 | 0 | 34 |
| `(ω⁴, π)` | `(4, 3, 0, −1)` | co-parity-`{0,…,4}` — proper | 34 | 27 | 0 | 0 |

Read the `languages` column against its mirror: **1 = 1, 1430 = 1430, 68 = 68,
40 = 40, 2 = 2, 654 = 654, 49 = 49, 169 = 169, 613 = 613, 34 = 34** — the profile
is *exactly* duality-symmetric on all ten pairs, the complement closure made
visible (§3); the `non-LTL` and `stutter-inv` columns are symmetric too (both
cuts are complement-blind). The self-dual rows `(1, δ) = 82` and `(2, δ) = 18`
stand alone — `(2, δ)` is new: the first properly-Δ₂ (self-dual beyond clopen)
languages the corpus holds. The **boolean (Hausdorff) hierarchy over open is now
inhabited four levels deep** (`(2,·)` through `(4,·)`), where iteration 3 stopped
at level 2. Total 6220; `γ` tops out at `ω⁴`; **0 PARTIAL** — no language reaches
Wagner's derivative (`γ = µ` throughout; §4 for the caveat on what that does and
does not establish). The `primals` column is *not* symmetric (`(ω, σ)`: 540 vs
`(ω, π)`: 157; `(ω⁴, σ)`: 34 vs 0) — it shows exactly which side the one-sided
enumeration reached and which the complement closure had to add.

**Depth ≠ countability, in the numbers.** The non-LTL count spreads over every
depth, not the deep end: half of *safety* (`(1, π)`: 704 / 1430) is already non-
star-free, while nearly half of the deepest `ω³` rows (412 of 1226) *is*
LTL-definable; only the `(ω⁴, ·)` rows are nearly all non-LTL (27 / 34 per side).
The aperiodicity axis and the Wagner axis are independent — the classifier
measures both, and the catalogue exhibits their full cross-product. The
stutter-invariant mass concentrates at the recurrence/persistence pair (`(ω, ·)`:
296 per side, two thirds of all 894) and thins to zero at the deepest bands.

### 6.4 Acceptance depth, read off the coordinates (Prop. 7.1)

The minimal deterministic acceptance family is a Spot read-off of the `det/`
presentation, but Prop. 7.1 (C§7) lets the **Büchi-vs-not** split be read straight
off the `.cat` coordinates — `m⁺ ≤ 0 ⟺ generalized-Büchi-realizable`:

| by `m⁺` | degrees | languages |
|---|---|--:|
| `m⁺ ≤ 0` — generalized-Büchi-realizable | `(0,·)`, `(1,·)`–`(4,·)`, `(ω, σ)` | 3836 |
| `m⁺ = 1, m⁻ = 0` — co-Büchi-proper | `(ω, π)` | 654 |
| `m⁺ ≥ 1 ∧ m⁻ ≥ 1` — genuine parity | `(ω·2, ·)`, `(ω², ·)`, `(ω³, ·)`, `(ω⁴, ·)` | 1730 |

So **2384** of 6220 languages sit genuinely above the generalized-Büchi ceiling,
and they are *exactly* the co-Büchi and parity degrees — Prop. 7.1's converse,
exhibited at catalogue scale without a single Spot call. The deep parity band
(`ω·2` and beyond) is reached only through the sampled parity shapes, each
complement side completed by closure (§6.3, `primals` column). The independent
Spot-vs-algebra gate agrees and refines the picture (ledger ventilation): of the
654 `(ω, π)` languages, 633 canonical presentations come out co-Büchi and 21
parity — the *canonical* presentation may carry more acceptance than the language
needs, which is exactly why the gate is one-directional and the coordinates, not
the presentation, are the classification.

### 6.5 Reproduction

The classification data lives *in* the benchmark (git-tracked `.cat` sidecars),
regenerated only when the languages change; every step below is idempotent and
byte-stable, so a clean rerun reproduces the tracked corpus exactly.

```
# 0. (only when the corpus changes) rebuild the catalogue into scratch, then adopt
#    per the genaut/README.md flow; the build's last step tags every language
python3 genaut/gen/flatten.py --canon --corpus genaut/corpus --out logs/genaut/X

# 1. re-tag an existing sos tier in place (pure read-off; ~2 s for all 6220;
#    byte-identical when the corpus is unchanged) — run from sosl/
python3 -m sosl.sos.classify.io ../genaut/corpus/flat_canon/sos

# 2. the language-level study: LTL cut + stutter + Wagner profile, aggregated
#    from the .cat sidecars (no classifier at report time; writes scratch by
#    default, --out genaut/corpus adopts)
python3 genaut/flat_study.py --corpus genaut/corpus --out genaut/corpus

# 3. the census gates (duality + Spot spectrum) on the HOA tier: needs the det/
#    HOAs, which .sos-only .cat cannot supply — the independent Spot oracle.
#    Run from sosl/; writes records.csv (the aggregation ledger) + PROFILE.txt
python3 -m tests.sosl.classify_census ../genaut/corpus/flat_canon/det \
    --logs tests/sosl/logs/classify_census/flat_canon_wide
python3 -m tests.sosl.classify_profile \
    tests/sosl/logs/classify_census/flat_canon_wide/records.csv
```

Steps 1–2 were rerun this iteration and are byte-identical to the tracked corpus;
step 3's ledger (6220 SOUND, 0 MISMATCH) is under
`sosl/tests/sosl/logs/classify_census/flat_canon_wide/`.
