# The anchor algorithm

A combinator translator that labels the **initial SCC** of a state-based automaton
by transcribing its transition structure onto the input word, delegating every exit
target to a child translator. It applies when the component's **phase** — the state
occupied while the run remains inside the component — is recoverable from the word
alone: each state is identified by the letters that *move* the run into it (its
**anchors**), while letters that do not move the run (self-loop letters) may be
shared freely between states. The label is a disjunction `STAY∞ ∨ LEAVE` — stay in
the component forever, accepting; or traverse it and exit — and is **exact by
construction**: no equivalence gate, no oracle.

anchor unifies and supersedes two earlier translators, `partscc` (a terminal SCC,
read as `G` + fairness) and `daisystardet` (a rejecting exiting SCC, read as
`U`-to-an-exit). Both reappear as degenerate cases of the single equation below, and
their shared precondition — the full input-determinism of the entry letters — is
strictly weakened to anchored recoverability, which tolerates the shared idle
letters that pervade response-shaped languages (`G(a → Fb)` and kin).

## Setting

A translator maps a language to a label; anchor is parameterized by the child `Λ`
it delegates exit targets to:

```
Label       =  Some φ  |  NotLTL(w)  |  ⊥    -- φ an LTL formula; w a non-LTL witness; ⊥ = decline
Translator  =  Language → Label
```

anchor asks the Language for its **state-based** form `A = sbacc(tgba(L))`, with
`A = (Q, Σ, δ, q0, {F_1,…,F_m})`, `Σ = 2^AP`, edges `(s, g, t) ∈ δ` carrying a
Boolean guard `g` (a BDD over `AP`), and **state-based generalized-Büchi**
acceptance: each color `F_i ⊆ Q` is a set of states, and a run accepts iff it
visits every `F_i` infinitely often (`m = 0` ⇒ every infinite run accepts).
State-based acceptance is the natural fit here: the transcription identifies
"occupying `s`" with a letter pattern, so state-level colors — visited whenever the
state is occupied, including across a self-loop stretch — are exactly what it can
express. (Transition-level marks on self-loops leave no letter-visible trace; that
finer setting stays with `daisy`, see *Relation to the family*.)

anchor applies at the SCC `C` of the initial state `h = q0`, with `|C| ≥ 2`
(a singleton initial state is `daisy`'s fragment and is declined here). Being
initial, `C` has no incoming edge from outside: every reachable state descends from
`h`, so an edge back into `C` would enlarge the component. Runs therefore *start*
in `C` and each run leaves it at most once — an SCC, once left, is never re-entered.

## The labels

Each state `s ∈ C` carries the two classical guard-disjunctions,

```
I(s)  =  ⋁ { g : (t, g, s) ∈ δ, t ∈ C }      -- inputs:  letters that can put the run at s
O(s)  =  ⋁ { g : (s, g, t) ∈ δ }             -- outputs: letters available from s
```

each split by whether the letter *moves* the run:

```
σ(s)  =  ⋁ { g : (s, g, s) ∈ δ }                    -- loop letters: stay at s
α(s)  =  ⋁ { g : (t, g, s) ∈ δ,  t ∈ C, t ≠ s }     -- anchors: move the run INTO s
μ(s)  =  ⋁ { g : (s, g, t) ∈ δ,  t ∈ C, t ≠ s }     -- moves: travel onward within C
E(s)  =  { (g, d) : (s, g, d) ∈ δ,  d ∉ C }         -- exits: leave C toward d
```

so `I(s) = σ(s) ∨ α(s)` and `O(s) = σ(s) ∨ μ(s) ∨ ⋁E(s)`. (The `σ` deliberately
echoes `daisy`'s petal guards: a state's loop letters are its petals.)

## The precondition

anchor applies when two BDD-level tests hold over `C`; it declines otherwise:

- **P1 — anchors partition.** The `α(s)` are pairwise disjoint:
  `α(s) ∧ α(t) = false` for `s ≠ t`. An anchor letter names a unique state.
- **P2 — loop letters never fake an anchor elsewhere.**
  `σ(s) ∧ α(t) = false` for `s ≠ t`. A letter that loops somewhere is not an
  anchor anywhere *else*.

`s = t` is deliberately exempt from P2: a letter in `σ(s) ∧ α(s)` — looping at `s`
and also entering `s` from elsewhere — is harmless, since every reading of it lands
the run at `s`.

Several facts are *derived*, not assumed:

- **No stay-vs-move ambiguity.** A letter moving out of `s` lies on an edge
  `s → t` (`t ≠ s`), hence in `α(t)`; P2 already forbids it from `σ(s)`. So from any
  state, loop letters and moving letters are disjoint: `σ(s) ∧ μ(s) = false`.
- **Tightness is automatic.** `C` strongly connected with `|C| ≥ 2` gives every
  state a non-self in-edge inside `C`, so `α(s) ≠ false`; then `α(s) = true` for
  some `s` would force every other anchor empty, contradicting the previous point.
  No separate tightness test is needed.
- **Machine determinism follows.** From any `s ∈ C`, a letter is a loop letter or
  an anchor into a unique target (P1 + P2 make these exclusive), so `A` restricted
  to `C` is deterministic *as a machine*. The converse fails: the precondition is
  about **transcription** — LTL, which has no state, must recover the phase from the
  letters alone — and that is strictly stronger than determinism. (A letter on an
  edge `u → t` that also loops at an unrelated `s` leaves each machine step
  deterministic, yet makes the letter ambiguous to a stateless observer; P2 rules
  exactly this out.)
- **Input-determinism is strictly subsumed.** If the full `I(s)` are pairwise
  disjoint (the retired precondition), then P1 and P2 hold a fortiori — every
  overlap they forbid is an `I`-overlap. The converse fails on any component with a
  shared idle letter (see the worked example).

Exit guards are entirely unconstrained: an exit may overlap loops, moves, anchors,
or other exits. Nondeterminism *toward an exit* is absorbed by disjunction, exactly
as `daisy` absorbs overlapping stems.

## The phase lemma

Under P1 + P2, at every position of a word whose run has stayed in `C`, the
occupied state is **the target of the last anchor letter read**, and every letter
since that anchor is a loop letter of that state. (Positions before any anchor
behave as if a *virtual anchor into `h`* were read at position −1 — the input
places the run at `h` without consuming a letter.)

In past temporal logic the phase is the formula `σ(s) S α(s)` ("loop letters of
`s` since an anchor into `s`"); P1 + P2 are precisely what makes at most one state
satisfy it at each position. Pure-future LTL cannot look back, so the label below
transcribes the same information *forward*: each anchor **promises** the stretch
that follows it, and an unbounded stretch of loop letters is compressed by a single
`W`/`U` — bounded formula, unbounded history.

The lemma yields a clean picture of `A`'s runs on a word `w`: within `C`, `w` has
**at most one run** (the machine is deterministic there), and every other run of
`w` is a **branch** of it — it follows the same walk and leaves through an exit
edge at some position. `STAY∞` below transcribes the unique in-`C` run being
infinite and accepting; `LEAVE` transcribes some branch exiting into an accepting
continuation. Their union is everything an accepting run can do.

## The label

With `φ_d = Λ(of(A↓d))` the child label of exit target `d` (`A↓d` the
sub-automaton rooted at `d`, rewrapped as a `Language` by `of(·)`):

```
sojourn(s)  =  σ(s) W μ(s)                                -- loop at s, then move on (or park)
step        =  ⋀_{s ∈ C} ( α(s) → X sojourn(s) )          -- the anchored transition law
park(s)     =  α(s) ∧ XG σ(s)                             -- a final anchor into s, then loop forever
fair_i      =  GF( ⋁_{s ∈ F_i} α(s) )                     -- anchor into F_i infinitely often,
            ∨  ⋁_{s ∈ F_i} F park(s)                      --   or park on a state of F_i,
            ∨  G σ(h)              (when h ∈ F_i)         --   or park on h from position 0

STAY∞       =  sojourn(h)  ∧  G step  ∧  ⋀_{i=1..m} fair_i

leave(s)    =  σ(s) U ⋁_{(g,d) ∈ E(s)} ( g ∧ X φ_d )      -- loop at s, then take an exit
LEAVE       =  leave(h)  ∨  ( sojourn(h) ∧ ( step U ⋁_{s ∈ C} ( α(s) ∧ X leave(s) ) ) )

Final       =  STAY∞ ∨ LEAVE
```

### The moves

- **Sojourn** (`σ(s) W μ(s)`). Having just anchored into `s`, the run loops on
  `s`'s own letters until a moving letter carries it onward — or forever (the `W`'s
  weak arm: parking is legal; whether it *accepts* is fairness's business, not the
  law's). The two arms are disjoint (`σ(s) ∧ μ(s) = false`, derived above), so the
  sojourn's end is sharp; and the moving letter lies on an actual edge `s → t`,
  hence fires `α(t)`, whose own implication in `step` takes over. The law chains
  itself.
- **Step, under `G` or under `U`.** `step` is the *per-position* law; `STAY∞` runs
  it forever (`G step`), `LEAVE` runs it only up to the final anchor (`step U …`) —
  the `U` both iterates the law and marks where it stops applying, so the exit
  letter is never constrained by a sojourn it is about to escape.
- **Park** and **fairness**. A run confined to `C` visits `F_i` infinitely often
  in exactly one of two ways: it anchors into `F_i`-states infinitely often, or it
  eventually parks on one (each maximal stay at a state is opened by an anchor —
  or is the position-0 stay at `h`, the virtual anchor's stretch, whence the third
  disjunct). `park(s)` is letter-exact: after `α(s)`, letters in `G σ(s)` can fire
  no foreign anchor (P2), so the run provably never moves again.
- **Leave.** `leave(s)` is `daisy`'s stem move verbatim — loop finitely (strong
  `U`), then assert an exit guard now and the child label next. `LEAVE`'s first
  disjunct is the run that exits straight from the hub's initial stretch, never
  anchoring; the second traverses: hub sojourn, law until a last anchor into the
  exiting state `s`, then `leave(s)`.

The two branches share everything but the wrapper — one component read twice, as a
place to *live* (`G` + fairness) and as a place to *cross* (`U` to an exit). All
guards are symbolic BDDs: no `2^AP` enumeration anywhere; work and output size
scale with the states and edges of `C`, not with the alphabet.

## Degenerate cases (no special-casing)

The one equation covers every regime; no dispatch precedes it.

- **No self-loops** (`σ(s) = false` for all `s`): `sojourn(s)` collapses to
  `μ(s)`, `step` to the pointwise law `⋀ α(s) → X μ(s)`, `park` and the `G σ(h)`
  disjunct to `false`, `leave(s)` to the immediate exit `⋁ (g ∧ X φ_d)`. With
  `α = I` (no loops), this is *exactly* the retired input-deterministic read-off —
  `partscc`'s `O(q0) ∧ G(law) ∧ ⋀GF(fair)` and `daisystardet`'s
  `O(h) ∧ (exit_at_0 ∨ (law U exit_after_entry))`, recovered term for term.
- **`C` rejecting.** For state-based generalized Büchi inside one SCC, rejecting
  means some color misses `C` entirely (`F_i ∩ C = ∅` — a strongly connected
  component can cycle through any states it owns, so it accepts iff it owns a state
  of every color). Then `fair_i` is an empty disjunction, `= false`, so
  `STAY∞ = false` and `Final = LEAVE`: the traversal regime, with no
  `is_rejecting_scc` test anywhere.
- **`C` terminal** (no exits): every `E(s)` is empty, `leave(s) = σ(s) U false =
  false`, so `LEAVE = false` and `Final = STAY∞`: the steady-state regime, with no
  terminality test anywhere.
- **`C` rejecting *and* terminal**: `Final = false ∨ false = false` — correct, the
  component's language is empty.
- **`C` accepting *and* exiting** — the case neither parent covered — needs
  nothing: `Final = STAY∞ ∨ LEAVE` with both branches live. Previously this shape
  required an upstream decomposition (`sccdecomp`) to split "lasso here" from
  "traverse"; anchor reads it off in place, sharing the component between the two
  branches instead of duplicating it across disjuncts.
- **`m = 0`**: the fairness conjunction is empty (`true`); `STAY∞` is the bare
  anchored safety skeleton.

## Worked example

The minimal deterministic Büchi automaton for `G(a → Fb)` — state 0 accepting
("no pending obligation"), state 1 ("owe a `b`"); the fixture is
[`samples/fixtures/hoa/anchor/gafb_response.hoa`](../../samples/fixtures/hoa/anchor/gafb_response.hoa):

```
State 0 {F_1}:   [!a | b] → 0     [a & !b] → 1
State 1:         [!b]     → 1     [b]      → 0
```

One terminal SCC, `h = 0`. The classical input labels **overlap**:
`I(0) = !a | b` and `I(1) = !b` share the idle letter `!a & !b` — both states wait
on it — so the input-deterministic read-off (`partscc`) declines. The anchor split:

```
σ(0) = !a | b     α(0) = b          μ(0) = a & !b     E(0) = ∅
σ(1) = !b         α(1) = a & !b     μ(1) = b          E(1) = ∅
```

P1: `α(0) ∧ α(1) = b ∧ (a & !b) = false`. P2: `σ(0) ∧ α(1) = false`,
`σ(1) ∧ α(0) = false`. (The exempt overlap even occurs: `σ(1) ∧ α(1) = a & !b ≠
false` — read at 1 it loops at 1, read at 0 it moves to 1; either way the run is
at 1 next.) The component is terminal, so `LEAVE = false` and the read-off is

```
Final =  ( (!a | b) W (a & !b) )                          -- hub sojourn
      ∧  G( b → X( (!a | b) W (a & !b) ) )                -- the only live step (sojourn(1) ≡ true)
      ∧  ( GF b  ∨  F( b ∧ XG(!a | b) )  ∨  G(!a | b) )   -- fair_1, F_1 = {0}
```

— equivalent to `G(a → Fb)`; the raw read-off then passes through the shared
simplification pipeline like every other label. Note `sojourn(1) = !b W b ≡ true`:
a state whose loop letters and moves complement each other imposes no law — the
transcription is exactly as tight as the structure requires.

## Exactness

For P1 + P2 the read-off is exact — `L(A) = Final`, given correct child labels —
with no oracle. The three legs:

- **Uniqueness.** The phase lemma: within `C` a word has at most one run, and
  every run of the word is that walk or a branch of it through an exit edge.
- **Completeness.** An accepting run either stays in `C` forever or leaves it
  exactly once. Staying: its anchors and stretches satisfy `sojourn(h)` and every
  `step` trigger (a stretch letter can fire only its own state's anchor, by P2;
  an anchor letter fires exactly its target's, by P1), and its color visits fall
  into the anchor-infinitely-often / park dichotomy that `fair_i` transcribes.
  Leaving from the hub stretch: `leave(h)`. Leaving after at least one anchor: the
  prefix walk satisfies `step` up to the final anchor (strictly earlier sojourns
  end in genuine moves), and the final anchor-plus-exit is the `U`'s witness.
- **Soundness.** Conversely, the formula *forces* a run, by induction along the
  word. `sojourn(h)` (or the virtual anchor's reading of position 0) starts the run
  at `h`; each active sojourn confines the next letter to `σ` of the current state
  (an actual self-loop) or `μ` (an actual out-edge, entering the unique state whose
  anchor it fires, where `step`'s next trigger takes over). In `STAY∞`, each
  `fair_i` disjunct certifies real `F_i`-visits of *that* run — an anchor firing
  puts the run at its target, a park pins it there forever. In `LEAVE`, the law
  holds strictly before the `U`'s witness position, so the final anchor is still
  constrained by the last active sojourn (it must be a legal move), and
  `leave(s)` walks actual self-loops to an actual exit edge, after which `φ_d`
  asserts the continuation lies in `L(A↓d)`. Every step is an edge of `A`; the
  assembled path *is* a run.

The argument nowhere consults whether `C` is accepting, rejecting, or terminal —
each branch is an exact transcription of one run shape, and their union is the
component's language. That is why the degeneracies above need no cases, and why no
equivalence gate is kept: under the stated preconditions (which are decided, not
guessed — BDD tests on `C`) there is nothing left for a gate to catch. A child's
correctness is the child's own recursive responsibility, exactly as a context-free
production composes; anchor never inspects a child's formula.

## Non-LTL exit children (the witness lift)

An exit child may return `NotLTL(w)`: the residue `of(A↓d)` is not LTL-definable,
witnessed by a counting family `w` anchored at `d`. anchor propagates the verdict
(absorbing, taken before any decline) and lifts `w` to `L`'s initial state by
prepending a **reaching word** to the family's `u`: one path `h ⟶* s ⟶(g) d`
through `C`, each step's guard **restricted to the letters enabling no edge to a
different target** from its source — so the word has a single continuation at every
step and its left quotient *is* the residue (star-free, hence LTL, is closed under
left quotient; a strict-union quotient would not preserve non-LTL-ness). The
restriction subtracts *all* other-target edges, self-loops included, so the shared
loop letters that motivate anchor are already excluded per step; parallel edges to
the same target are harmless (finite-prefix marks never touch an `Inf` set). A
route whose restriction empties is skipped; if no exact route survives, the verdict
does not lift and the peel degrades to a non-absorbing `PROBABLY_NOT_LTL` decline.

## Relation to the family

```
anchor        initial SCC, anchored phase (P1+P2)      →  STAY∞ ∨ LEAVE, exact, no gate
partscc       terminal SCC, input-deterministic        →  retired: anchor's terminal + loop-free degeneracy
daisystardet  rejecting exiting SCC, input-det.        →  retired: anchor's rejecting + loop-free degeneracy
daisy         singleton initial state (1-weak peel)    →  kept: transition-based acceptance per petal set
daisystar     rejecting star, ANY entry partition      →  kept (open): the non-anchored fallback, gate-rescued
sccdecomp     per-accepting-SCC union split            →  kept: the enabler where anchor's precondition fails
```

`daisy` remains the singleton case on purpose: at `|C| = 1` the state-based form
loses the per-acceptance-set petal structure (`⋀ GF(σ_i)`) that transition-based
acceptance expresses without splitting, and daisy reads that richer condition
directly. `sccdecomp` remains the complement, not a casualty: anchor recurses down
the SCC DAG through its exits, so components that *do* satisfy P1 + P2 no longer
need splitting, but a non-anchored component still does. A genuinely shared
*moving* letter (`α(s) ∧ α(t) ≠ false`) stays out of scope by design: the phase is
then not a function of the word, and disambiguating with a fresh proposition is not
legal into LTL (projection leaves LTL for QPTL) — that is `daisystar`'s open
territory.

## Literature

The precondition is a stuttering relaxation of **local automata** — automata in
which all transitions on a letter share their target, the recognizers of local
languages (Chomsky & Schützenberger 1963; Berstel & Pin 1996): erase each state's
loop letters and `C` becomes local on its anchors, while the loop letters act as
state-preserving stutter that LTL absorbs with a single `W`/`U` per stretch. Where
a local (or 1-definite — Perles, Rabin & Shamir 1963) automaton's phase is a
function of the last *letter*, anchor's is a function of the last *anchor* —
"definite modulo stuttering". The read-off itself is the local-language
characterization transcribed to ω-words: allowed first letters (the hub sojourn),
allowed digrams (`step`), and, in place of allowed final letters, the fairness of
what recurs forever.

## Out of scope (the assembly's concern)

anchor computes one local label and trusts its inputs. As for the rest of the
family, the child `Λ`'s well-foundedness, the fixpoint `Λ*` closing the open
recursion, first-fit dispatch, and memoization by language belong to the assembly.
Two directions are noted, not taken: **k-anchor windows** (a phase recoverable from
the last *k* anchors — `X`-chained generalizations of `step`, the `k`-definite
analogue), and relaxing the **form dependence** — the precondition is tested on
`sbacc(tgba(L))`, and an input can pass in one automaton form and fail in another;
which forms to try is a portfolio decision, not this production's.
