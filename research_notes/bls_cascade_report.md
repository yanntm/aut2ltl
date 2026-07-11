# Cascade ladder — Findings ledger (`bls_cascade_report.md`)

Ledger for `bls_cascade_spec.md` (K-series). Current-state only; git
holds history. Each finding: id, one-line claim, status
(`CONFIRMED | REFUTED | BUDGET | BLOCKED`), the exact command, and pointers to
git-tracked files only. `PAPER-EDIT:` flags a refuted prediction against its
draft location in `bls_cascade.md`.

**Machinery.** The config machine `M_k(R)` and the (C)/(B) decider (ALG-1/2/5/6)
live in `tests/cascade/config_machine.py`; probes in `tests/cascade/`. The
verdict oracle is `Val(s,d) = (M(s,π(d)),π(d)) ∈ P` off `sosl.sos.Invariant`.

## Status

Frame: `genaut/corpus/flat_canon` (6222 languages). Measurement data +
regen: `reference/cascade/k_series.md`.

- **K-E0 COMPLETE** (K-F1..F6): decider validated five independent ways;
  C.12/C.17 refuted (K-F2, Theorem C.12′ on paper).
- **K-E1 COMPLETE** (K-F7 coverage, K-F12 conflicts): 6610/8786 undecided
  layers decide at k≤2; 1021 genuine (C)@0-conflicts (806 aperiodic), 263
  persist at k=1 (246 aperiodic), 640 budget-open at k=1.
- **K-E7 COMPLETE** (K-F8): absorption + group only, 0 verdict-splitting
  `other` — no third mechanism.
- **K-E2 COMPLETE** (K-F9): the C.19 transfer specimen is a moving-layer
  floor inhabitant (beyond-frame construction).
- **K-E3 COMPLETE** (K-F10): pfxind ⟹ frozen final layer, 1104/1104;
  Cor C.9 stratum empty; one-sidedness 16/16/28/14 over 74 (up/down tie
  structural: complement closure).
- **K-E4 worked example done** (K-F11): emitter conformance-gated on
  `G(a→F b)`; production wiring open.
- **Open PAPER-EDIT (K-F12)**: the draft still says "floor empty on the
  census frame" (C.2/C.19/C.7) and carries old-cut numbers — sites and
  final numbers listed in `handoff_cascade.md` Theory todo 1.
- **Open experiments**: k=2 pass on the 640 budget-open layers; K-E4
  engine integration; K-E5; K-E6 — `handoff_cascade.md` Engineering todos.

---

## K-F1 — `G(a→F b)` is the width-0 config-(C) witness (draft step 5) — CONFIRMED

`𝓘(G(a→F b))` has a **non-frozen** terminal layer `{2,4}`, 1-anchored, with
exactly the draft's six edges and `(C)` holding at **width 0** while plain `(B)`
fails; the accepting family and verdict pattern match C.3 step 5.

- Terminal layer `{2,4}`: `b`(=!a&b)→reset(2), `a`(=a&!b)→reset(4),
  `s`(=!a&!b)→neutral. With `A:=4` (a-target), `B:=2` (b-target) the six k=0
  edges are exactly `(A,a)→A,(A,s)→A,(A,b)→B,(B,b)→B,(B,s)→B,(B,a)→A` — the
  draft's predicted set.
- `decide(inv,{2,4},k=0)`: **(C) holds** (0 conflicts, 22 collected F), plain
  **(B) fails** (1 conflict). Minimal accepted sets `{(B,s)→B}`, `{(B,b)→B}`,
  `{(B,a)→A,(A,b)→B}`: single-class-`B`(=2) accept, single-class-`A`(=4)
  reject, two-class accept — the C.3 step-5 pattern.
- Membership of five hand-picked lassos matches `inv.member` (identity of `𝓘`
  and `L`).

Command: `python3 -m tests.cascade.k_e0 gaFb` and
`python3 -m tests.cascade.k_e0_probe gaFb` and
`python3 -m tests.cascade.k_e0_verify gaFb`.
Logs: `tests/cascade/logs/k_e0_gaFb.txt`,
`tests/cascade/logs/k_e0_probe_gaFb.txt`,
`tests/cascade/logs/k_e0_verify_gaFb.txt`.

## K-F2 — the floor witness has a FROZEN terminal layer; (C) does NOT hold at width 0 — REFUTED

`PAPER-EDIT:` `bls_cascade.md` C.3 "The residual floor witness, worked"
(≈ lines 377–407), and C.0/§5.1's use of `GF(a∧X((!a∧!b)U a))` as *the*
config-normal-form floor witness at rung 0.

The canonical invariant `𝓘(GF(a∧X((!a∧!b)U a)))` diverges from the draft's
hand derivation at step 1:

- **Draft C.3:** terminal layer `R={A,B}`, two classes, 1-anchored non-frozen
  (`a`→const A, `b`→const B, `s`→identity), (C) at **width 0**, emitting
  `GF A_{(A,a)}` "with no descent of any kind."
- **Tool:** 7 classes, **prefix-independent**; `accept P={(6,6)}`; layers
  `{0}|{1}|{2,4}|{3,5}|{6}`. The terminal layer is the **single frozen class
  `{6}`** — every quotient letter (`s`,`b`,`a`) is *neutral* (a self-loop),
  `An=St=` all letters. `decide` gives **(C) fails at k=0** (2 conflicts, 7
  collected F) **and k=1** (16 conflicts); k=2 blows the 40 000-state budget.

The draft's non-frozen 2-class `{A,B}` machine *does* exist in `𝓘` — but as the
**transient** layers `{2,4}` and `{3,5}` (both →`{6}`), never terminal. Because
`L` is prefix-independent the pending-`a`/`b` bit washes out of the absorbing
class, leaving a frozen singleton. On a frozen layer `M_k(R)=SR_k` and the class
coordinate is absent, so (C) at width `k` = (B) at width `k+1` (draft Lemma
C.10 / C.6(2)); combined with §5.1's presupposed "(B̃) fails at every width",
(C) fails at **every** width. The config ladder never rescues this witness.

**Read (for the author to judge):** the two §5.1 witnesses' structural roles
are swapped. The six-edge non-frozen `{A,B}` config machine of C.3 is
`𝓘(G(a→F b))` (K-F1), the genuine width-0 config-(C) success; the
prefix-independent `GF(a∧X((!a∧!b)U a))` is a frozen-layer/window language the
config ladder does not decide. C.3's floor-witness derivation, C.9's
"residual floor witness below instantiates every hypothesis", and §10's
open-problem restatement all depend on this and need revisiting.

Commands: `python3 -m tests.cascade.k_e0 floor`,
`python3 -m tests.cascade.k_e0_probe floor`,
`python3 -m tests.cascade.k_e0_verify floor`.
Logs: `tests/cascade/logs/k_e0_floor.txt`,
`tests/cascade/logs/k_e0_probe_floor.txt`,
`tests/cascade/logs/k_e0_verify_floor.txt`.

## K-F3 — the (C)/(B) decider is cross-validated — CONFIRMED

The ALG-1/2/5/6 implementation reproduces the draft on the witness whose
structural model matches `𝓘` (`G(a→F b)`: (C)@0 holds, plain (B) fails), and
agrees with the C3/F13 fact that `G(a→F b)`'s terminal layer fails plain (B).
Membership round-trips on both witnesses confirm `𝓘 = L`. This bounds K-F2:
the floor divergence is the draft's, not a decider artifact.

## K-F4 — saturation reproduces raw exploration; CL(x) is closed (step 6) — CONFIRMED

At every entry cone / full-memory base of both witnesses' final layers, raw
ALG-5 `CL(x)` is closed under `(F₁,d₁),(F₂,d₂) ↦ (F₁∪F₂, M(d₁,d₂))`, and
saturating its **first-return loops** reproduces `CL(x)` exactly — the ALG-5
saturation route is sound. Checked on `gaFb` `{2,4}` k=0, and `floor` `{6}`
k=0 (|CL|=17) and k=1 (|CL| up to 262). (`first_returns` is the correct
generator set; a naïve edge-set-only prime extraction under-generates.)

Command: `python3 -m tests.cascade.k_e0_sat gaFb 0 | floor 0 | floor 1`.
Logs: `tests/cascade/logs/k_e0_sat_*.txt`.

## K-F5 — the sandwich scan detects both mechanisms (step 3) — CONFIRMED

The K-E7 sandwich scan over ALG-5's idempotent loop classes detects both
mandatory positive controls:

- **floor witness** (`{6}`, aperiodic): `absorption` — `e·z·e = z <_J e`, `e` an
  unflagged idempotent, `z=6` the zero (6 absorption + 2 non-splitting `other`
  at k=0; the mandatory absorption control fires).
- **`EvenBlocks`** (`{6}`, non-aperiodic): every failing pair is `group` —
  `f·z·f = z` (29 fails at k=2, 178 at k=3).

Mechanism (final classifier, K-F8): non-aperiodic ⟹ `group`; aperiodic with the
idempotent pair 𝒥-**comparable** (one dominates) ⟹ `absorption`; aperiodic with
the pair 𝒥-**equivalent** yet the sandwich still dropping ⟹ `other` (the
third-mechanism candidate, meaningful only when verdict-splitting). Scan is
`O(|E_id|²)` per `(x,F)` — piggybacks K-E1/E2.

Command: `python3 -m tests.cascade.k_e7_controls floor 0|floor 1|evenblocks 2|evenblocks 3`.
Logs: `tests/cascade/logs/k_e7_*.txt`.

## K-F6 — (B)-mode agrees with C3 wherever C3 decides (step 4) — CONFIRMED

The config decider's (B)-mode (window-projection grouping) matches C3
(`windows.realizable_verdicts`) at matching window width `k`: `GF(aa)` `{5}`
k=1 both FAIL, k=2 both PASS with **all 6 window-sets agreeing at the verdict
map level**; the floor `{6}` and `G(a→F b)` `{2,4}` layers both FAIL at k=0,1
on both sides. No disagreement; the F1 cap-false-PASS divergence (a known C3
limitation) does not arise on these layers.

Command: `python3 -m tests.cascade.k_e0_bcross`. Log:
`tests/cascade/logs/k_e0_bcross.txt`.

## K-F7 — (C)-coverage of the census-undecided stratum: everything that decides does so at k≤2 — CONFIRMED

Over the census (6222 languages), C3 leaves **8786** layer readings
`UNDECIDED` (cap/budget guard tripped), on 2114 languages. The exact config
(C)-decider, 60 s per language on the cluster:

| outcome | layers |
|---|--:|
| (C) decides at k=0 | 6105 |
| (C) decides at k=1 | 346 |
| (C) decides at k=2 | 159 |
| heavy stratum (language over 60 s; see K-F12) | 2176 |

**Every layer that decides does so at width ≤ 2**; 505 of them conflict at
k=0 yet decide at k=1/2 — the ladder's rungs doing real work. The heavy
remainder is *not* undecided noise: K-F12 resolves it into genuine
conflicts / clean / budget. (The earlier 4248-language cut of this
experiment decided its whole stratum with zero conflicts; that was a
property of the frame — its Wagner ceiling was ω² — not of the census
axis.)

Data + regen: `reference/cascade/k_series.md` (`k_e1_cluster.csv`; shard
driver `tests/cascade/k_e1_one.py`, cluster recipe in
`tests/cascade/README.md`).

## K-F8 — K-E7 census map: only absorption + group; no third verdict mechanism — CONFIRMED

The sandwich scan piggybacked on every decided K-E1 layer (K-F7's 6610),
with both mandatory controls green (K-F5). Failure-pair sums: **absorption
14050** (aperiodic, one idempotent 𝒥-below the other — the floor-witness
mechanism), **group 7387** (non-aperiodic), `other` 3076 (aperiodic,
𝒥-equivalent idempotents whose sandwich still drops) — and **0 of the
`other` are verdict-splitting**. A non-splitting sandwich failure is not a
(C)-conflict ("the identity is stronger than (C)", draft C.4); these are
ordinary aperiodic 𝒥-class drops, not a verdict mechanism.

**No verdict-splitting `other` anywhere ⟹ no third mechanism** —
consistent with C.4's two known mechanisms (group cancellation, zero
absorption). The K-F12 conflict stratum confirms the same dichotomy from
the other side: its aperiodic conflicts carry the verdict-splitting
absorption signature (type specimen below), its non-aperiodic ones the
group escape.

Data: `other`/`other_split` columns of `reference/cascade/k_e1_cluster.csv`.
Triage: `python3 -m tests.cascade.k_e7_triage <id> <layer> <k> other`.

## K-F9 — Prop C.19 transfer specimen: first moving-layer floor inhabitant — CONFIRMED

The transfer language `π₁⁻¹(GF(a∧X((!a&!b)U a))) ∩ π₂⁻¹(G(c→F d))` — over disjoint
AP sets, the conjunction `(GF(a∧X((!a&!b)U a))) ∧ (G(c→F d))` over `{a,b,c,d}` —
builds `𝓘` with 25 classes, aperiodic, and a **moving, 1-anchored terminal
layer `{21,24}`** (the predicted `{(z,2),(z,4)}`: the floor's frozen `z`
coordinate times `G(c→F d)`'s moving `{2,4}`).

The (C)-decider **conflicts at width 0 and width 1** (early-exit finder;
`|F|=2` then `6`, both based at class 21). ALG-7 verification on each: the two
reconstructed lassos share the recurring edge set yet **`inv.member` toggles**
(one accepts, one rejects — independent of the closure) and the induced linked
pairs are **non-conjugate** (Lemma C.11) — a **genuine** (C)-conflict, not a
closure bug. So the moving layer has no clean (C) width: **the first
moving-layer floor inhabitant**, confirming Prop C.19 and the transfer of the
floor witness's zero-absorption onto a moving layer.

k=2,3 hit BUDGET (|Σ_λ|=9, covered-set explosion) — a tooling limit; the
conflict is the window-blind `a·s^*·a` mechanism (Theorem C.12′) decorated by a
fixed `G(c→F d)` recurrence, so it persists at every width structurally.

Command: `python3 -m tests.cascade.k_e2_transfer`. Log:
`tests/cascade/logs/k_e2_transfer.txt`.

*(K-E2 steps 1/2 — the census frozen/moving stratum — are answered by
K-F7/K-F12 on the extended frame: the floor-track stratum is inhabited
**in-frame** (K-F12), and the C.19 construction remains the worked
beyond-frame **moving-layer** transfer of the mechanism.)*

## K-F10 — Cor C.9 stratum empty: prefix-independence forces a frozen final layer — CONFIRMED

`PAPER-EDIT` (settles a ⟨TBD⟩, not a refutation): C.3's ⟨TBD⟩ "prefix-independence
forces the final layer frozen" and Cor C.9's applicability.

Decider-free scan of all 6222 census languages: of the **1104
prefix-independent** ones, **0 have a non-frozen final layer** — every
prefix-independent language's terminal layer is a frozen (all-neutral)
SCC. So the Cor C.9 gating stratum (prefix-independent ∧ terminal
1-anchored **non-frozen** final layer ∧ upward-closed ∧ parked-rejecting)
is **empty on the census**: C.9's global bare-`Π₂` form has no instances,
and the config ladder's one-sided win (Cor C.8) is confined to
**non-prefix-independent** languages (e.g. `G(a→F b)`, K-F1). This is the
K-F2 mechanism generalized: the pending bit cannot survive in a
prefix-independent language's absorbing class. (Promotion to a theorem is
Theory todo 3 in `handoff_cascade.md`.)

One-sidedness of the moving final layers that *are* (C)-decided (74 with a
≥2-class collected `F`): **16 upward, 16 downward, 28 both, 14 neither** —
**balanced, not "predominantly upward"** as E3/C.8 predicted; the exact
up/down tie is **structural** — the catalogue is complement-closed and
complement swaps the closure direction. (The precise E3 claim is about the
`P|_R` recurrence rung; a rung-stratified recount is an Engineering todo,
but the raw distribution does not support upward-dominance.)

Data + regen: `reference/cascade/k_series.md` (`k_e3.csv`,
`k_e3_pfxind.txt`).

## K-F11 — config normal-form emitter + G(a→F b) conformance (DAG-only) — CONFIRMED

The config atoms and `Ω(R,·)` are emitted as `spot.formula` DAGs (spot
hash-conses; nothing stringified — the conformance gate translates the formula
object directly), per the K-E4 grammar (Prop C.7 / Cor C.8).

- **Atoms match C.3** on `𝓘(G(a→F b))`: `A_{(2,a)} ≡ b∧X((b∨s)U a)`,
  `A_{(4,b)} ≡ a∧X((a∨s)U b)` — Spot-equivalent (the quotient letters are
  `a`=`a&!b`, `b`=`b`, `s`=`!a&!b`; `a&b` folds into the b-class).
- **Ω assembled**: rec form `GF A_{(2,a)} ∧ GF A_{(4,b)}` (the single minimal
  ≥2-class accepted set) ∨ park `F(An(2)∧X G St(2))` ∨ entry park `G St(2)`
  (park verdicts read off the frozen restriction: park-at-2 accepts, park-at-4
  rejects). No mixed parks.
- **Conformance**: `Ω ≡ G(a→F b)` (raw and simplified). Sizes: raw dag=27
  flat=97; `_simp_f` dag=15 flat=24 — the DAG stays tiny; the flat form is
  bounded (`tree_node_count` limit) and never materialized as a string.

Machinery: `tests/cascade/emit.py` (`atom`, `omega`, `park_verdict`,
`letterset`). Commands: `python3 -m tests.cascade.k_e4_atoms`,
`python3 -m tests.cascade.k_e4_gaFb`.

*Remaining K-E4:* the full conformance sweep over every K-E1-decided layer needs
the config emitter wired into the production window engine (`aut2ltl/sos2ltl/
engine.py`) so the existing rebuild-𝓘 gate runs on the assembled whole-language
label (Ω is a confined-tail term; `G(a→F b)` gates directly only because its
final layer is terminal and it carries no safety). Plus the DG-size ledger.

## K-F12 — the floor-track stratum is inhabited INSIDE the census frame, at scale — CONFIRMED

The census (Wagner ceiling ω³/ω⁴) contains genuine aperiodic (C)-conflicts
in bulk. Over the 2176 heavy layers of K-F7 (their language over the 60 s
cap), the early-exit finder + inline ALG-7 (`k_e1_verify`, one CSV row per
layer, member toggle + non-conjugacy on every conflict):

| width | genuine CONFLICT | of which aperiodic | CLEAN (ladder rescues) | BUDGET |
|---|--:|--:|--:|--:|
| k=0 | 1021 | **806** | 625 | 530 |
| k=1 (on the 1021) | 263 | **246** | 118 | 640 |

Every reported conflict is ALG-7-genuine — zero closure artifacts. **The
aperiodic floor-track stratum is ≥246 in-frame layers genuinely failing
(C) at widths 0 and 1.** A width-bounded conflict is not yet floor
membership (Theorem C.12′ needs every width): the structural absorption
argument, or deeper passes on the 640 budget-open layers, closes that gap
(Theory todo 2 / Engineering todo 1 in `handoff_cascade.md`).

Type specimen `2state2ap1acc_parity_3772037665` — 13 classes, aperiodic,
Wagner **(ω³, σ)**, canonical D 6 states / 2 AP / parity-3; conflicting
layers are **frozen singletons**, so (C)@0 = (B)@1 (Lemma C.10): a genuine
**plain-(B) failure in-frame** — the "2 states × 2 AP at once" open-hunt
witness of the main paper §8. ALG-7 at k=0: `find_c_conflict` in 27
states, |F|=3, loop 12 rejects vs loop 5 accepts, non-conjugate.
Mechanism: verdict-splitting **zero absorption** over three 𝒥-minimal
classes `[5, 8, 11]` (a richer bottom than the floor witness's single
zero). The `aut2ltl` portfolio times out (90 s) on its det HOA —
consistent with a residual-stratum inhabitant.

Data + regen: `reference/cascade/k_series.md` (`k_e1v_conflicts_k0.csv`,
`k_e1w_conflicts_k1.csv`, `kf12_specimen_alg7.txt`). Specimen replay:
`python3 -m tests.cascade.k_e1_verify 2state2ap1acc_parity_3772037665 5 0`;
mechanism: `python3 -m tests.cascade.k_e7_triage … 5 0 absorption`.

`PAPER-EDIT` (open): draft C.2 remark, C.19 closing bold, C.4 map
paragraph, C.7 §8 bullet — every "zero conflicts / floor empty on the
census frame" statement; K-F9's "inhabited beyond it" becomes "inhabited
beyond *and within* the frame".
