# learn — the learner algorithm

Dev-facing: the learner's state, the normal form it maintains, the procedures
that repair it, and the pinned orders that make runs reproducible. The theory
is the paper (`research_notes/sos_learning2.md`, §3–§5); this file is the
working description the implementation follows.

The design in one sentence: **the learner never poses a hypothesis that is not
a language** — every equivalence query ships a well-formed `Invariant`, the
canonical form of the learner's current belief language.

## State

- **Evidence** (`evidence.py`) — the ground truth: a run-wide `lasso → bit`
  ledger keyed by `Lasso.canonical()` (the UP-word normal form: primitive
  loop, minimal stem). Every membership query threads through it, so one
  teacher query is paid per **distinct infinite word** per run; every later
  presentation of that word — a rotation, a pumped loop, a different
  stem/loop split — is a free replay. `n_member` counts the misses.
- **Table** (`table.py`) — the private ledger arranging evidence for
  comparison. Rows are *access words*: `R` starts as `{ε}` and grows only by
  closedness promotions (`rep·letter`); the frontier is `R·Σ`, filled under
  the **letter collapse**: real queries for rows, letters, and extensions by
  each letter class's least member (letters sharing a full signature); every
  other cell holds its rep-cousin's bit as a *proxy* — a bit already in
  evidence wins, proxies are recomputed at every fill and are never
  evidence, and `verify` grounds a word (queries its proxied cells) before
  any structural use. Columns come in two sorts — linear `(x, y, t)`: the bit of `p` is `[x·p·y·t^ω ∈ L]`;
  omega `(x, y)`: the bit is `[x·(p·y)^ω ∈ L]` — and the table opens with
  **no columns at all**: every column of every run is minted by a
  discordance; no experiment is given, all are found. `ε` is a permanent
  singleton class (the fresh adjoined identity): no word ever merges into it,
  so every other class has a non-empty key and every keyed lasso is
  well-formed.
- **Partition** (`partition.py`) — classes by equal bit-rows; `rep(c)` is the
  shortlex-least row of `c` (the class's *key*); `step(c, a) =
  class(rep(c)·a)`; `fold` is the letterwise step from `[ε]`.
- **Belief** (`export.py`) — the exported invariant: letter map
  `λ(a) = step([ε], a)`, induced product `M(c, d) = fold(c, rep(d))`,
  accepting pairs `P` filled on the keyed lassos `rep(s)·rep(e)^ω`, the whole
  re-keyed by shortlex BFS (`canonicalize`). Built after every clean legality
  pass; what the teacher sees, and the run's result.

## The normal form

Four constraints, checked in pinned order before any equivalence query; the
first failure is repaired and the loop restarts. Each repair splits at least
one class, witnessed by a genuine Arnold context, so repairs are bounded by
the target's class count across the entire run.

1. **closed & consistent** — a closedness failure promotes the shortlex-least
   witness, grounded first (`verify`; if grounding moves a bit the partition
   is recomputed instead — a speculative signature never promotes); a
   consistency failure at column `c` mints the migrated column
   (`(x, a·y, t)` linear / `(x, a·y)` omega): the entry of `p` at the mint
   equals the entry of `p·a` at `c`. Both events must separate on real
   bits — a pure-proxy difference mirrors its rep cousins, so the same
   witness fires there and nothing is lost.
2. **morphism** (stamp legality, `saturate.py`) — for every table word `p`
   with `rep(class(p)) = r0 ≠ p` and every class `d`, `fold(d, p)` must equal
   `fold(d, r0)`. Zero queries; clean ⟺ the kernel is a two-sided congruence
   and the induced product is well defined. A divergence escalates (two probe
   bits under a separating column `κ`, with `r = rep(d)`):
   - *bits differ* — mint `κ` with `r` absorbed: `(x·r, y, t)` linear; for an
     omega `κ` the candidate rides in the period, so `r` seeds prefix **and**
     period tail: `(x·r, y·r)` (the bare-prefix form is vacuous on a
     prefix-independent language and never converges);
   - *bits agree* — one of `r·p` / `r·r0` disagrees with its own fold class's
     key under `κ`: run the frozen-prefix chain on that word inside `κ`'s
     context; the minted column keeps `κ`'s prefix alone, the unconsumed
     segment migrating into the middle component.
3. **saturated** (pair legality, `pairs.py`) — `P`, read on the keyed lassos,
   must be constant across the one-step conjugates
   `(s, (c·d)^π) ∼ (s·c, (d·c)^π)`: one ω-word, two names, one verdict. The
   scan costs nothing beyond the `P` entries (each an evidence bit, memoized
   across rounds). A violation is refereed on the common rotated lasso — one
   membership bit, shared by both presentations through the canonical-form
   key — and the presentation naming the losing pair is a discordant lasso
   for the ordinary chain.
4. **evidence-coherent** — the belief is replayed against the whole ledger,
   query-free: `belief.member(lasso) == bit` for every witnessed bit. A
   contradiction is a discordant lasso whose teacher bit is already in hand —
   the chain runs with no new query for the seed.

At quiescence the export is already the syntactic invariant of its own belief
language: every table cell's lasso is in evidence, so coherence pins the
belief to every witnessed separation and `canonicalize` only re-keys, never
merges.

## The chain — one discordance, one split (`chains.py`)

A discordance is two concrete lassos bearing one name with differing teacher
bits — however found (a probe, a legality escalation, a coherence replay, a
teacher counterexample; all four sources feed the same code). Processing
`(w, z)`: normalize to `(w·z^k, z^k)` with `k` the loop's stabilization power;
one *junction* query `[rep(fold(w'))·z'^ω]` decides stem side or loop side;
binary-search the adjacent bit flip along the chain that replaces a growing
prefix by its class's key; mint the column the flip straddles — linear
`(ε, w'[i+2..], z')` from the stem chain, omega `(rep(fold(w')), z'[i+2..])`
from the loop chain. Exactly one column, which splits one class at the next
stabilization. Cost: the junction plus `O(log)` membership bits.

## Bootstrap and alternation (`learner.py`)

Open with `R = {ε}`, no columns, and the **probe sweep**: each letter's
ω-power queried into evidence, shortlex order — the last a-priori
experimentation the learner ever performs. Repair runs as on any state:
closedness promotes the shortlex-least letter (no column separates the
letters yet), and the one linked pair of the one-class product poses the
run's first `P` bit — the promoted letter's ω-power, deciding `∅` vs `Σ^ω`.
Discordances among the opening bits are caught by the coherence replay and
chained, membership queries only. Then the alternation: at each quiescence
pose `EQ(belief)`; assent ends the run (the belief is `I(L)`, byte-canonical);
a counterexample is one more discordant lasso for the chain. The teacher is
consulted exactly when no self-served finder points at any suspect lasso.

## Counting conventions (campaign / paper numbers)

- `n_member` counts **distinct infinite words** queried (evidence misses);
  replays are free. Per-phase counts attribute a word to its *first* asker.
- Driver phases: `fill` (table cells), `harvest` (junction + chain bits),
  `saturation` (stamp-escalation probes), `pcache` (`P` fills + pair-legality
  bits) — the paper's fill / harvest / legality / P.

## Pinned orders (a run is deterministic given the teacher)

- stamp scan: subjects in shortlex order, classes `d` in id order, first
  divergence fires; separating column: first in creation order;
- pair scan: `s`, `c`, `d` in class-id order, first violation fires;
- coherence replay: evidence in first-query order;
- probe sweep: letters in shortlex order;
- teacher counterexamples: minimal (shortest stem, then loop, then shortlex).

## Hard invariants

- every split is witnessed by a column and two differing membership bits, on
  concrete queried lassos — replayable from the evidence;
- the class count never decreases, and (checked post hoc by the harness,
  never by the learner) never exceeds the reference class count;
- a run is deterministic given the teacher's answers.
