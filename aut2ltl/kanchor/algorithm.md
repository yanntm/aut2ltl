# The k-anchor algorithm

A combinator translator that labels the **initial SCC** of a state-based
ω-automaton by transcribing its transition structure onto the input word,
delegating every exit target to a child translator. It applies when the
component's **phase** — the state occupied while the run remains inside the
component — is recoverable from the last **k adjacent letters** of the word,
*modulo stuttering*: letters that do not move the run may be shared freely
between states. The label is a disjunction `STAY∞ ∨ LEAVE` — stay in the
component forever, accepting; or traverse it and exit — and is **exact by
construction** at every window width: no equivalence gate, no oracle.

This document is standalone and deliberately slow: the construction is built
in numbered layers, each relaxing exactly one assumption of the previous one,
and each layer's formula survives verbatim as a degenerate case of the next —
so every term can be audited at the layer that introduces it. Layers 2–4
develop the single-letter window (k = 1);
layers 5–6 widen the window to adjacent pairs (k = 2); layer 7 shows the two
are one construction graded by k. The reader in a hurry can read layer 6's
label and layer 7 — but the hurry will cost more than the layers do.

## 1 — Setting

A translator maps a language to a label; k-anchor is parameterized by the
child `Λ` it delegates exit targets to:

```
Label       =  Some φ  |  NotLTL(w)  |  ⊥    -- φ an LTL formula; w a non-LTL witness; ⊥ = decline
Translator  =  Language → Label
```

k-anchor asks the Language for its **state-based** form `A = sbacc(tgba(L))`,
with `A = (Q, Σ, δ, q0, {F_1,…,F_m})`, `Σ = 2^AP`, edges `(s, g, t) ∈ δ`
carrying a Boolean guard `g` (a BDD over `AP`), and **state-based
generalized-Büchi** acceptance: each color `F_i ⊆ Q` is a set of states, and a
run accepts iff it visits every `F_i` infinitely often (`m = 0` ⇒ every
infinite run accepts). State-based acceptance is the setting this
transcription can read: it identifies "occupying `s`" with a letter pattern,
so state-level colors — visited whenever the state is occupied, including
across a self-loop stretch — transcribe directly, whereas transition-level
marks on self-loops leave no letter-visible trace.

The construction applies at the SCC `C` of the initial state `q0`. Being
initial, `C` has no incoming edge from outside: every reachable state descends
from `q0`, so an edge back into `C` would enlarge the component. Runs
therefore *start* in `C` and each run leaves it at most once — an SCC, once
left, is never re-entered. No size is assumed: a single-state `C` is a border
case that falls into line below.

Each state `s ∈ C` carries two guard-disjunctions,

```
I(s)  =  ⋁ { g : (t, g, s) ∈ δ, t ∈ C }      -- inputs:  letters that can put the run at s
O(s)  =  ⋁ { g : (s, g, t) ∈ δ }             -- outputs: letters available from s
```

each split by whether the letter *moves* the run:

```
L(s)  =  ⋁ { g : (s, g, s) ∈ δ }                    -- Loops:   stay at s
A(s)  =  ⋁ { g : (t, g, s) ∈ δ,  t ∈ C, t ≠ s }     -- Anchors: move the run INTO s
M(s)  =  ⋁ { g : (s, g, t) ∈ δ,  t ∈ C, t ≠ s }     -- Moves:   travel onward within C
E(s)  =  { (g, d) : (s, g, d) ∈ δ,  d ∉ C }         -- Exits:   leave C toward d
```

so `I(s) = L(s) ∨ A(s)` and `O(s) = L(s) ∨ M(s) ∨ ⋁E(s)`. (The label `L(s)`
always takes a state argument; a bare `L` remains the language. The label `M`
is never used as the LTL operator `M` in this document.)

Exit guards are entirely unconstrained throughout: an exit may overlap loops,
moves, anchors, or other exits. Nondeterminism *toward an exit* is absorbed by
disjunction — each exit is one more way to accept, never a constraint on the
others.

## 2 — The loop-free, exit-free read-off (k = 1, L = ∅, E = ∅)

Assume first that `C` is the whole automaton and moves are all there is: no
exits (`E(s) = ∅`) and no self-loops (`L(s) = false`, so `I(s) = A(s)`). Every
run lives in `C` forever and every letter moves the run. Require one test:

- **P1 — anchors partition.** The `A(s)` are pairwise disjoint:
  `A(s) ∧ A(t) = false` for `s ≠ t`.

Then the phase is a function of the **last letter**: the letter that just
moved the run names its destination uniquely. LTL, which has no state, can now
track the run — each letter *promises* the next step:

```
step    =  ⋀_{s ∈ C} ( A(s) → X M(s) )                 -- the transition law, per position
fair_i  =  GF( ⋁_{s ∈ F_i} A(s) )                      -- F_i is entered infinitely often

STAY∞   =  M(q0)  ∧  G step  ∧  ⋀_{i=1..m} fair_i
```

- **The steady regime, and the start.** `G step` describes the *steady*
  regime: each state's constraint is triggered by the anchor that just entered
  it. But `q0` itself is never entered — position 0 has no incoming letter —
  so nothing anchors the start, and the steady law alone would over-approximate
  the language. The conjunct `M(q0)` supplies the missing anchoring: the
  *input* places the run at `q0`, and the first letter must be a move actually
  available there. (Keep this in mind: the start needing its own, sharper rule
  because position 0 lacks history is a theme that returns amplified at layer
  6.)
- **The law chains itself.** A letter in `M(s)` lies on an actual edge
  `s → t`, hence in `A(t)` for that `t` — unique by P1 — whose own implication
  in `step` takes over. Legality comes from the consequence (`X M(s)`
  constrains the next letter to a real edge of the occupied state);
  identification comes from the trigger (P1 makes the trigger fire exactly at
  its target). This division of labor — the trigger identifies, the
  consequence legislates — is the load-bearing idea of the whole construction
  and survives every relaxation below.
- **Fairness transcribes visits.** "The run is at `s` at position `i ≥ 1`" ⟺
  "letter `i−1` fired `A(s)`"; `GF` being shift-invariant, "visit `F_i`
  infinitely often" is `GF(⋁_{s∈F_i} A(s))`.

## 3 — Relaxing E: exits

Reinstate the exits (still loop-free). A run now either stays in `C` forever —
`STAY∞` above, unchanged: its anchors and moves are in-`C` by construction, so
it still confines the run — or leaves `C` exactly once, through some exit
edge. The leaving runs get their own branch, with `φ_d = Λ(of(A↓d))` the child
label of exit target `d` (`A↓d` the sub-automaton rooted at `d`, rewrapped as
a `Language` by `of(·)`):

```
leave(s)  =  ⋁_{(g,d) ∈ E(s)} ( g ∧ X φ_d )            -- take an exit, child continues

LEAVE     =  leave(q0)  ∨  ( M(q0) ∧ ( step U ⋁_{s ∈ C} ( A(s) ∧ X leave(s) ) ) )

Final     =  STAY∞ ∨ LEAVE
```

- **`G` versus `U`.** `step` is the *per-position* law. `STAY∞` runs it
  forever; `LEAVE` runs it only up to the final anchor — the `U` both iterates
  the law and marks where it stops applying, so the exit letter is never
  constrained by a law it is about to escape.
- **Two ways out.** The first disjunct exits straight from `q0` at position 0
  (again the start needs its own case: no anchor precedes it); the second
  traverses — the `M(q0)` anchoring, the law until a *last* anchor into the
  exiting state, then that state's exit.

## 4 — Relaxing L: stuttering, and the k = 1 label

Now reinstate the self-loops. A letter in `L(s)` read at `s` does not move the
run, so the phase is no longer a function of the last letter — but half of the
loops are not a problem at all, and the split is corrected before anything
else is built. A loop letter `σ` every one of whose in-`C` occurrences is at
`s` — `σ ∧ (L(t) ∨ A(t)) = false` for every `t ≠ s` — still *names its
state*: whoever reads it knows the run sits at `s`. Such a letter is an
anchor in everything but edge shape, and it is **promoted** at build time —
into `A(s)` on the trigger side, into `M(s)` on the consequence side (a unit
re-entry ends a sojourn exactly as a move does — the promoted letter must be
a legal stay-ender wherever `M(s)` legislates), out of `L(s)`. From here on
`A(s)`, `M(s)` and `L(s)` denote the promoted split: `A(s)` collects all of `s`'s *identifying* letters, entering
or looping; `L(s)` keeps only the **necessary** stay letters — those a run
could also be reading somewhere else, which no stateless observer can
attribute. Nothing above changes: a promoted letter fires `s`'s own row and
promises one more step at `s`, which is exactly what its loop does; and the
same correction applies verbatim at every window width below (a loop
*window* shared with no other state's windows identifies its state and
joins the triggers). What this layer actually has to solve is the residual
`L(s)`: genuinely ambiguous stuttering, where the phase is a function of the
**last anchor** only — the state entered by the last identifying letter,
unchanged by the ambiguous letters read since. That recovery needs one test
beyond P1 (which constrains only the anchors, not the full inputs):

- **P2 — loop letters never fake an anchor elsewhere.**
  `L(s) ∧ A(t) = false` for `s ≠ t`. A letter that loops somewhere is not an
  anchor anywhere *else*.

`s = t` is deliberately exempt: a letter in `L(s) ∧ A(s)` — looping at `s` and
also entering `s` from elsewhere — is harmless, since every reading of it
lands the run at `s`. (After promotion the exemption is mostly moot: such a
letter, unshared, was already promoted out of `L(s)`; shared, it trips P1 or
P2 through the other state. The diagonal was never the problem.)

### 4.1 — Derived facts

Several facts are *derived*, not assumed:

- **No stay-vs-move ambiguity.** A letter moving out of `s` lies on an edge
  `s → t` (`t ≠ s`), hence in `A(t)`; P2 already forbids it from `L(s)`. So
  from any state, loop letters and moving letters are disjoint:
  `L(s) ∧ M(s) = false` — a sojourn's end is sharp.
- **Tightness is automatic.** For `|C| ≥ 2`, strong connectivity gives every
  state a non-self in-edge inside `C`, so `A(s) ≠ false`; then `A(s) = true`
  would force every other anchor empty, a contradiction. (For `|C| = 1` all
  anchors are empty and nothing is needed.) No separate tightness test exists.
- **Machine determinism follows.** From any `s ∈ C`, a letter is a loop letter
  or an anchor into a unique target (P1 + P2 make these exclusive), so `A`
  restricted to `C` is deterministic *as a machine*. The converse fails: the
  precondition is about **transcription** — a stateless observer must recover
  the phase from the letters alone — and that is strictly stronger than
  determinism. (A letter on an edge `u → t` that also loops at an unrelated
  `s` leaves each machine step deterministic, yet is ambiguous to the
  observer; P2 rules exactly this out.)
- **The loop-free condition is strictly subsumed.** If the full inputs `I(s)`
  are pairwise disjoint, P1 and P2 hold a fortiori — and every loop promotes,
  so `L = ∅`: this layer adds nothing, the stays decompose into unit
  re-entries, and the label is layer 2–3's one-step law. The sojourn `W`
  below therefore survives exactly where it is load-bearing — on stay
  letters genuinely shared across states, where the last anchor is the only
  carrier of the phase. The converse fails on any component with a shared
  idle letter (see the worked example, 9.1): a shared idle promotes nowhere
  and is precisely what the residual `L` machinery exists for.

### 4.2 — The phase lemma (letters)

Under P1 + P2, at every position of a word whose run has stayed in `C`, the
occupied state is the target of the last anchor letter read, and every letter
since that anchor is a loop letter of that state. (Positions before any anchor
behave as if a *virtual anchor into `q0`* were read at position −1 — the input
places the run at `q0` without consuming a letter.) In past temporal logic the
phase is `L(s) S A(s)`; pure-future LTL transcribes the same information
forward: each anchor promises the **stretch** that follows it, and an
unbounded stretch of loop letters is compressed by a single `W`/`U` — bounded
formula, unbounded history.

The lemma yields a clean picture of the runs on a word `w`: within `C`, `w`
has **at most one run** (the machine is deterministic there), and every other
run of `w` is a **branch** of it — it follows the same walk and leaves through
an exit edge at some position. `STAY∞` transcribes the unique in-`C` run being
infinite and accepting; `LEAVE` transcribes some branch exiting into an
accepting continuation. Their union is everything an accepting run can do.

### 4.3 — The k = 1 label

Each piece of layers 2–3 generalizes by absorbing a stretch: the promised next
move `X M(s)` becomes a promised *sojourn* `X( L(s) W M(s) )`; the immediate
exit becomes loop-then-exit; fairness gains the runs that eventually stop
moving.

```
sojourn(s)  =  L(s) W M(s)                                -- loop at s, then move on (or park)
step        =  ⋀_{s ∈ C} ( A(s) → X sojourn(s) )          -- the anchored transition law
park(s)     =  A(s) ∧ XG L(s)                             -- a final anchor into s, then loop forever
F_all       =  { s : s ∈ F_i for every i }                -- the states where parking accepts

fair        =  ⋀_{i=1..m} GF( ⋁_{s ∈ F_i} A(s) )          -- every color anchored infinitely often,
            ∨  ⋁_{s ∈ F_all ∩ C} F park(s)                --   or park on a state carrying every color,
            ∨  [ q0 ∈ F_all ] ∧ G L(q0)                   --   or park on q0 from position 0

STAY∞       =  sojourn(q0)  ∧  G step  ∧  fair

leave(s)    =  L(s) U ⋁_{(g,d) ∈ E(s)} ( g ∧ X φ_d )      -- loop at s, then take an exit
LEAVE       =  leave(q0)  ∨  ( sojourn(q0) ∧ ( step U ⋁_{s ∈ C} ( A(s) ∧ X leave(s) ) ) )

Final       =  STAY∞ ∨ LEAVE
```

`[ q0 ∈ F_all ]` is a construction-time test, not a temporal subformula: when
`q0` carries every color the disjunct is `G L(q0)`, otherwise it is dropped.

### 4.4 — The moves

- **Sojourn** (`L(s) W M(s)`). Having just anchored into `s`, the run loops on
  `s`'s own letters until a moving letter carries it onward — or forever: the
  `W`'s weak arm makes parking *legal*, and deliberately so. Whether a parked
  run *accepts* is fairness's business, not the law's — the split is what
  keeps every `U`-vs-`W` case analysis out of the law. The two arms are
  disjoint (`L(s) ∧ M(s) = false`, derived in 4.1), and the moving letter lies
  on an actual edge `s → t`, hence fires `A(t)`, whose own implication in
  `step` takes over: the law still chains itself.
- **Fairness, restructured around parking.** A run confined to `C` either
  moves infinitely often or eventually parks. If it moves infinitely often,
  each stay is finite and opened by an anchor, so "visit `F_i` infinitely
  often" is "anchor into `F_i` infinitely often" — for *every* color at once,
  the first disjunct. If it parks at `s`, the colors it visits infinitely
  often are exactly the colors of `s` — accepting iff `s` carries **every**
  color, i.e. `s ∈ F_all`. So only `F_all`-states need a park term; a run
  parking anywhere else is simply not accepting, and needs no formula to say
  so. `park(s)` is letter-exact: after `A(s)`, letters in `G L(s)` can fire no
  foreign anchor (P2), so the run provably never moves again. The third
  disjunct is `park(q0)` under the virtual anchor — the run that never moves
  at all, fair only when `q0` itself carries every color.
- **Leave.** `leave(s)` looks finitely many loop letters ahead (strong `U`),
  then asserts an exit guard now and the child label next, exactly as in
  layer 3 with the stretch absorbed.

The two branches share everything but the wrapper — one component read twice,
as a place to *live* (`G` + fairness) and as a place to *cross* (`U` to an
exit). All guards are symbolic BDDs: no `2^AP` enumeration anywhere; work and
output size scale with the states and edges of `C`, not with the alphabet.

### 4.5 — Two construction-time reductions

Both are BDD tests at build time, not rewrites of a built formula:

- **The park-subsumption drop.** If `L(s) ∧ ¬A(s) = false` — every loop
  letter of `s` fires `s`'s own anchor — a run parked at `s` anchors into `s`
  at every position of the park, so the first `fair` disjunct already accepts
  it (`s ∈ F_all` carries every color, and `GF A(s)` witnesses each color's
  `GF` at once). The `F park(s)` term for such an `s` is omitted, and the
  `G L(q0)` disjunct likewise when the test holds at `q0`. The test is only
  meaningful on `F_all` states — parking elsewhere is not accepting and never
  had a term. Layer 6 states the same drop for any window width.
- **The sojourn-tautology collapse.** `sojourn(s) ≡ ⊤` whenever
  `L(s) ∨ M(s) = true`: at each position either a loop or a move is legal, so
  `L(s) W M(s)` imposes nothing — the weak arm is what makes it a tautology.
  A state whose loop letters and moves complement each other contributes no
  law; on a *total* component the entire law can vanish and the label reduce
  to its fairness (see 9.1). The transcription is exactly as tight as the
  structure requires.

## 5 — Relaxing P1: widening the window to pairs (k = 2)

Layers 2–4 stand on P1: a moving letter names its destination alone. Many
components fail exactly this — the same letter enters different states from
different places — while remaining perfectly transparent to an observer who
remembers **one more letter**. The minimal DBA of `GF(a ∧ Xa)` is the type
specimen (worked in 9.2): `a` enters `s1` from `s0`, enters `s2` from `s1`,
and loops at `s2` — P1 and P2 both fail on `a` — yet the *pair* of adjacent
letters always tells the truth: `¬a·a` can only mean "now at `s1`", `a·a`
"now at `s2`". The window, not the letter, is the anchor.

One trap must be avoided in widening. "The last k *anchors*, with loop
stretches between them" does not work: the stretches are unbounded, so the
trigger would need `U`-nesting and the law would stop being `X`-shaped. The
window is instead over **adjacent letters**, and a stretch is absorbed by
weakening a context letter's constraint from `A(v)` ("just entered `v`") to
`I(v) = L(v) ∨ A(v)` — *any* letter consistent with the run being at `v`,
whether it just arrived or has been looping. `I(v)` is the stutter
abstraction; the window stays rigid and the law stays `X`-shaped.

### 5.1 — The pair data

Two relations over `Σ × Σ`, one per phase-relevant reading of a pair:

```
Enter₂(s)  =  ⋁ { I(v) × g : (v, g, s) ∈ δ,  v, s ∈ C,  v ≠ s }   -- pairs that move the run INTO s
Stay₂(s)   =  I(s) × L(s)                                          -- pairs that keep the run AT s
```

These relations are conceptual: both are unions of *rectangles*
`first × second` with plain one-letter BDDs on each coordinate, and every test
below decomposes over the rectangles — two unions intersect iff some rectangle
pair intersects coordinate-wise, and the one containment test is an exact
recursive rectangle-cover. Nothing doubles the BDD variables, and the label
never materializes a product: it uses `I(v)` and `g` as separate one-letter
guards under `X`.

### 5.2 — The pair preconditions

- **P1² — entering pairs partition.** `Enter₂(s) ∧ Enter₂(t) = false` for
  `s ≠ t`.
- **P2² — staying pairs never fake an entry elsewhere.**
  `Stay₂(s) ∧ Enter₂(t) = false` for `s ≠ t`.

`Stay₂(s) ∧ Stay₂(t) ≠ false` is allowed — that overlap *is* the stuttering
tolerance (two states waiting on shared idle pairs), resolved by the phase
lemma below. The `s = t` overlap `Stay₂(s) ∧ Enter₂(s)` is exempt exactly like
`L(s) ∧ A(s)` at layer 4: either reading lands the run at `s`.

P1 and P2 imply P1² and P2² componentwise on the second coordinate
(`Enter₂(s) ⊆ Σ × A(s)`, `Stay₂(s) ⊆ Σ × L(s)`): a component transparent to
single letters is transparent to pairs. The k hierarchy is monotone — layer 7
makes that a ladder.

### 5.3 — Derived facts, one level up

The layer-4 derivations re-run through pairs, same mechanism:

- **Sojourn ends stay sharp:** `L(s) ∧ M(s) = false`, re-derived. A letter `x`
  looping at `s` and moving `s → t` puts `(y, x)` in `Stay₂(s) ∧ Enter₂(t)`
  for every `y ∈ I(s)` (nonempty for `|C| ≥ 2`) — P2² forbids it. So
  `sojourn(s)` keeps its disjoint arms and layer 4's letter-level pieces are
  reused verbatim.
- **Move targets are unique in context:** `x` on edges `s → t` and `s → t'`
  puts `I(s) × x` in `Enter₂(t) ∧ Enter₂(t')` — P1² forbids it.
- **What k = 2 strictly gains:** a letter may loop at `v` and move `u → t`
  (`u ≠ v`) — forbidden outright by P2 — provided `I(v) ∧ I(u) = false`: the
  predecessor letter disambiguates the current letter's role. The phase is a
  function of the last *two* letters where it was not a function of the last
  one.

### 5.4 — The phase lemma (pairs), and its license

Under P1² + P2² (+ P0² of layer 6 for the start), for a word whose run has
stayed in `C`: any pair `(w_{i−1}, w_i)` of the word that lies in `Enter₂(s)`
puts the run **at `s`** after position `i` — the run's actual step read that
pair either as a loop at its current state `u` (then
`Stay₂(u) ∧ Enter₂(s) ≠ false` forces `u = s`: it was already there) or as a
move into some `t` (then `Enter₂(t) ∧ Enter₂(s) ≠ false` forces `t = s`). A
pair lying in no `Enter₂` was a loop: the run is where it was. Hence the phase
is the target of the **last entering pair**, with the start rule of layer 6
standing in before any pair has entered. As at layer 4, a word has at most one
run within `C` and every other run is an exit branch of it.

The lemma has a corollary the label leans on: a trigger may fire on a
*spurious* source (`w_i ∈ I(v)` while the run sits elsewhere), but the promise
it makes is then true anyway — the pair is in `Enter₂(s)`, so the run is at
`s` regardless of which edge the trigger named. Spurious firings are harmless,
not forbidden. The corollary is stronger than a convenience: it is the
**license for the only law LTL can state**. A trigger cannot be conditioned on
"the run is at `v`" — the phase is what the formula is *transcribing*, not
something it can consult — so any per-edge law is necessarily eager, firing on
every pair that merely looks like the edge. P1² and P2² are exactly the price
of that eagerness: they force every look-alike pair to tell the same truth
about the next state, so the eager law is not an over-approximation that
happens to be tolerable — it *is* the transcription, and no tighter law exists
to compare it against.

## 6 — The start, and the k = 2 label

One position resists the pairs. At k = 1 the virtual anchor closed the start:
`sojourn(q0)` covered position 0, and every entry at position ≥ 1 carried a
real anchor. At k = 2 an entry at position **1** — the run's first letter
already moves — has no predecessor pair: the earliest `G`-wrapped pair trigger
constrains position 2 onward, so nothing lawful would bind `w₁`. The remedy is
the same idea that closed the start at layer 2, sharpened: position 0 is the
one place the observer has *certain* knowledge (the run is at `q0`), so the
guard alone can play the anchor there — a **0-step anchor**. It needs its own
partition test:

- **P0² — the start is 0-step-anchored.** `q0`'s **in-`C`** out-edges toward
  distinct targets have pairwise disjoint guards. The self-loop counts as a
  target (a loop/move overlap at position 0 is machine nondeterminism, which
  no window can recover); exit edges do **not** — exit nondeterminism is
  absorbed by disjunction as everywhere, the start law never ranges over
  exits, and a word exiting at position 0 is `leave(q0)`'s business.

This is the whole start policy: the run enters the transcription only at
position 0, only through a 0-step anchor. (Prepending virtual history to `q0`
instead — an automaton surgery — is noted in layer 12, not taken.)

### 6.1 — The label

Layer 4's letter-level pieces `sojourn(s)`, `leave(s)`, `park`, `F_all` are
reused unchanged (their soundness needed only the disjointness re-derived in
5.3). Triggers become pairs, consequences gain one `X`, and position 0 gets
the 0-step law. Conjuncts are grouped per source–target pair
(`(A → C) ∧ (B → C) ≡ (A ∨ B) → C`), written per edge below for clarity:

```
enter₂(s)  =  ⋁_{(v,g,s) ∈ δ|C, v≠s} ( I(v) ∧ X g )                  -- the pair-anchor, as LTL
step₂      =  ⋀_{(v,g,s) ∈ δ|C, v≠s} ( I(v) ∧ X g  →  XX sojourn(s) )
start      =  ⋀_{(q0,g,s) ∈ δ|C, s≠q0} ( g → X sojourn(s) )          -- position 0 only, not G-wrapped

fair₂      =  ⋀_{i=1..m} GF( ⋁_{s ∈ F_i} enter₂(s) )
           ∨  ⋁_{s ∈ F_all ∩ C} F( enter₂(s) ∧ XXG L(s) )            -- park after a pair-entry
           ∨  ⋁_{(q0,g,s) ∈ δ|C, s ∈ F_all, s≠q0} ( g ∧ XG L(s) )    -- park after the 0-step entry
           ∨  [ q0 ∈ F_all ] ∧ G L(q0)                               -- park on q0 from position 0

STAY∞      =  sojourn(q0) ∧ start ∧ G step₂ ∧ fair₂

LEAVE      =  leave(q0)
           ∨  ⋁_{(q0,g,s) ∈ δ|C, s≠q0} ( g ∧ X leave(s) )            -- move at 0, exit from s's stretch
           ∨  ( sojourn(q0) ∧ start ∧
                ( step₂ U ⋁_{(v,g,s) ∈ δ|C, v≠s} ( I(v) ∧ X g ∧ XX leave(s) ) ) )

Final      =  STAY∞ ∨ LEAVE
```

### 6.2 — The moves

- **The law chains itself, one position of overlap.** The pair ending a
  sojourn at `s` has its first component in `I(s)` — the entering letter or
  the last loop letter — so the move out of `s` is itself the second component
  of a live `step₂` trigger. Identification comes from the pair (P1²/P2² make
  it unambiguous), legality from the consequence: layer 2's division of labor,
  intact.
- **The start.** If `w₀` moves within `C`, its target is unique by P0² and
  `start` supplies the promise `G step₂` cannot reach. If `w₀` loops,
  `sojourn(q0)` covers it and the eventual first move is pair-covered (its
  predecessor is a `q0`-loop letter, in `I(q0)`). Entries at position 1 are
  the *only* pair-less entries; everything later has a full window.
- **Fairness.** Moving forever: every stay is finite and opened by an entering
  pair, so color visits are `GF` of pair-entries — the single pair-less entry
  at position 1 is invisible to `GF` and harmless. Parking now has three
  shapes: after a pair entry, after the 0-step entry (`g ∧ XG L(s)`: the run
  that moves at position 0 and parks immediately — a case the pair term cannot
  see, and the `GF` cannot rescue), and never moving at all (`G L(q0)`, the
  construction-time `q0 ∈ F_all` test of layer 4).
- **The park drop generalizes:** `Stay₂(s) ⊆ Enter₂(s)` (the rectangle-cover
  test) makes every park term for `s` redundant — each staying pair of the
  parked run re-fires `enter₂(s)`, so the `GF` disjunct already accepts it;
  sound only on `F_all` states, as at layer 4. The same test at `q0` drops the
  `G L(q0)` disjunct.
- **`G` versus `U`, one `X` deeper.** In `LEAVE`'s traversal branch the law
  holds strictly before the witness pair, whose own `XX leave(s)` places the
  exit two positions later; the deepest reach of an *imposed* trigger (at
  witness − 1) is the final move letter, never the exit letter — the exit
  still escapes the law it is leaving. `start` joins the traversal branch (its
  reach, position 1, is strictly inside `C` there) but **not** the second
  disjunct: a run exiting from `s` at position 1 must not be held to
  `sojourn(s)`.

## 7 — One graded construction (k as a parameter)

The letter and pair constructions are one production graded by the window
width `k`; nothing in the label is hand-matched between levels.

- **Windows.** An entry at position `p` has `p` letters of history. Positions
  `p ≥ k` use **full windows**: `k` adjacent letters, `I`-weakened context
  components, the entering guard last. Positions `0 < p < k` use **truncated
  windows rooted at `q0`**: actual paths of length `p` out of `q0`, the
  certainty of being at `q0` at time 0 standing in for the missing context
  letters. `p = 0` is the run that never entered anything — `sojourn(q0)` and
  the `G L(q0)` park, present at every level.
- **The trigger table.** Each window class contributes entries
  `(trigger, offset, target)`. Full windows generate the `G`-wrapped law
  (`trigger → X^offset sojourn(target)`), the `GF` fairness disjuncts, the
  park terms (`trigger ∧ X^offset G L(target)`) and the `LEAVE` witnesses
  (`trigger ∧ X^offset leave(target)`); truncated windows generate the same
  four shapes one-shot — `start`, the truncated park disjuncts, the truncated
  leave disjuncts — instead of `G`-wrapped. Layer 6's label is this table
  written out at k = 2; layer 4's is the same table at k = 1.
- **k = 1 is the level where the truncation falls off.** The range
  `0 < p < 1` is empty — no `start`, no truncated park or leave; full triggers
  carry no context component, so they group per target state (`⋁ g = A(s)`)
  at offset 1, and what remains is layer 4's label, clause for clause. The
  letter version is not a special case bolted underneath; it is this
  construction at k = 1, reached because the truncated sets are empty, not
  because a branch tests for it.
- **Graded preconditions, and the ladder.** P1ᵏ/P2ᵏ on the full windows, one
  partition test per truncated class (P0² is the single k = 2 instance);
  level k passing implies level k + 1 passing. The brick tries k = 1, 2, … to
  a small cap and adopts the first level that passes — every level's label is
  exact, so first-fit needs no gate; the park drop is the same test
  (`Stay_k ⊆ Enter_k`) at every level.

## 8 — Degenerate cases (no special-casing)

The one equation covers every regime; no dispatch precedes it.

- **No self-loops**: `sojourn(s)` collapses to `M(s)`, `leave(s)` to the
  immediate exit, the park terms to `false` — layers 2–3 verbatim at k = 1;
  at k = 2 every `Stay₂` is empty and the construction is the plain 2-definite
  (local-on-digrams) read-off.
- **`C` rejecting.** For state-based generalized Büchi inside one SCC,
  rejecting means some color misses `C` entirely (`F_i ∩ C = ∅` — a strongly
  connected component can cycle through any states it owns, so it accepts iff
  it owns a state of every color). Then the first `fair` disjunct contains
  `GF(false)` and `F_all ∩ C = ∅` empties every park term: `fair = false`,
  `STAY∞ = false`, and `Final = LEAVE` — the traversal regime, with no
  rejecting-SCC test anywhere.
- **`C` terminal** (no exits): every `E(s)` is empty, `leave(s) = false`, so
  `LEAVE = false` and `Final = STAY∞` — the steady-state regime, with no
  terminality test anywhere.
- **`C` rejecting *and* terminal**: `Final = false` — correct, the component's
  language is empty.
- **`C` accepting *and* exiting**: nothing to do — both branches live, the
  component shared between them rather than split upstream and duplicated.
- **`|C| = 1`**: anchors and moves are empty, so `sojourn(q0) = G L(q0)`,
  `step = true`, the `U` has a `false` right arm, and
  `Final = ( G L(q0) when q0 ∈ F_all ) ∨ leave(q0)` — loop forever on a state
  carrying every color, or loop then exit. The border case falls into line
  (and P1/P2 hold trivially, so the ladder resolves it at k = 1).
- **`m = 0`**: the first `fair` disjunct is an empty conjunction,
  `fair = true`; `STAY∞` is the bare anchored safety skeleton.

## 9 — Worked examples

### 9.1 — k = 1: `G(a → Fb)`, and the collapse

The minimal deterministic Büchi automaton — state 0 accepting ("no pending
obligation"), state 1 ("owe a `b`"); the fixture is
[`samples/fixtures/hoa/anchor/gafb_response.hoa`](../../samples/fixtures/hoa/anchor/gafb_response.hoa):

```
State 0 {F_1}:   [!a | b] → 0     [a & !b] → 1
State 1:         [!b]     → 1     [b]      → 0
```

One terminal SCC, `q0 = 0`. The full inputs **overlap**: `I(0) = !a | b` and
`I(1) = !b` share the idle letter `!a & !b` — both states wait on it — so the
loop-free read-off declines. The anchor split:

```
L(0) = !a | b     A(0) = b          M(0) = a & !b     E(0) = ∅
L(1) = !b         A(1) = a & !b     M(1) = b          E(1) = ∅
```

P1: `A(0) ∧ A(1) = b ∧ (a & !b) = false`. P2: `L(0) ∧ A(1) = false`,
`L(1) ∧ A(0) = false`. (The exempt overlap even occurs: `L(1) ∧ A(1) = a & !b
≠ false` — read at 1 it loops at 1, read at 0 it moves to 1; either way the
run is at 1 next.) The component is terminal, so `LEAVE = false`; with
`F_1 = {0}`, `F_all = {0}`, the raw read-off is

```
Final =  ( (!a | b) W (a & !b) )                          -- q0's sojourn
      ∧  G( b → X( (!a | b) W (a & !b) ) )                -- the law of state 0's stretch
      ∧  G( (a & !b) → X( !b W b ) )                      -- the law of state 1's stretch
      ∧  ( GF b  ∨  G(!a | b)  ∨  F( b ∧ XG(!a | b) ) )   -- fair: anchor 0 i.o., or park on 0
```

Now watch the collapse (4.5) at work: `L(1) ∨ M(1) = !b ∨ b = ⊤` and
`L(0) ∨ M(0) = (!a|b) ∨ (a&!b) = ⊤` — the automaton is *total*, every letter
is legal from either state — so **both** sojourns are tautologies, the two law
conjuncts and `q0`'s sojourn all evaporate, and the built label is the bare
fairness

```
Final =  GF b  ∨  G(!a | b)  ∨  F( b ∧ XG(!a | b) )
```

— equivalent to `G(a → Fb)`, whose safety content was an illusion all along.
The park term for state 0 is *not* droppable (`L(0) = !a | b ⊄ A(0) = b`); the
sibling fixture `park_drop.hoa` shows the drop firing.

### 9.2 — k = 2: `GF(a ∧ Xa)`

The minimal DBA — `s0` "last letter was ¬a" (initial), `s1` "one a after a
¬a", `s2` "aa seen" (accepting, `F_1 = {s2}`); the fixture is
[`samples/fixtures/hoa/kanchor/gf_a_xa.hoa`](../../samples/fixtures/hoa/kanchor/gf_a_xa.hoa):

```
State s0:        [!a] → s0     [a] → s1
State s1:        [a]  → s2     [!a] → s0
State s2 {F_1}:  [a]  → s2     [!a] → s0
```

k = 1 declines twice over: `A(s1) = A(s2) = a` (P1 fails) and
`L(s2) = a = A(s1)` (P2 fails). The pairs:

```
Enter₂(s1) = ¬a × a      Enter₂(s2) = a × a      Enter₂(s0) = a × ¬a
Stay₂(s0)  = ¬a × ¬a     Stay₂(s2)  = a × a
```

P1²/P2² pass (the exempt overlap occurs: `Stay₂(s2) = Enter₂(s2)`); P0² passes
(`s0`'s two guards are `¬a`/`a`). Every `L(s) ∨ M(s)` is `true`, so every
sojourn — including `sojourn(q0)` and with it all of `step₂` and `start` —
collapses to `⊤`: the component is pure liveness and the law is empty. In
`fair₂`, the `GF` disjunct is `GF(I(s1) ∧ Xa) = GF(a ∧ Xa)`; the park term for
`s2` drops by `Stay₂(s2) ⊆ Enter₂(s2)`; no `q0`-edge reaches `F_all` and
`q0 ∉ F_all`, so no other park term exists. `C` is terminal, so
`LEAVE = false` and

```
Final  =  GF(a ∧ Xa)
```

— exact and minimal, with no simplifier involved.

## 10 — Exactness

For the graded preconditions the read-off is exact — `L(A) = Final`, given
correct child labels — with no oracle. The three legs, stated once for every
level:

- **Uniqueness.** The phase lemma (4.2 at k = 1, 5.4 at k = 2): within `C` a
  word has at most one run, and every run of the word is that walk or a branch
  of it through an exit edge.
- **Completeness.** An accepting run either stays in `C` forever or leaves it
  exactly once. Staying: it satisfies `sojourn(q0)` and the start law (its
  position-0 step is an actual edge), and every trigger it fires is true of it
  — genuinely (the promised edge is the one taken) or spuriously (5.4's
  corollary: the window still pins the run at the promised target, whose
  actual future is a legal sojourn). Its color visits fall into the
  moving-forever / parked dichotomy that `fair` transcribes — at k = 2 the
  position-1 entry covered by the 0-step park term. Leaving: from `q0`'s
  stretch (`leave(q0)`), from the first stretch after a position-0 move (the
  truncated leave disjunct), or after at least one full window — the `U`'s
  witness (strictly earlier sojourns end in genuine moves).
- **Soundness.** The formula *forces* a run, by induction along the word, one
  window at a time. `sojourn(q0)` and the start law root the run through the
  first positions; each active sojourn confines the next letter to `L` of the
  current state (an actual self-loop) or `M` (an actual out-edge, the second
  component of a window in exactly one `Enter`, where the next trigger takes
  over). In `STAY∞`, each `fair` disjunct certifies the acceptance of *that*
  run: entering windows firing infinitely often yield real visits to every
  color when the run keeps moving — and a parked run's windows are staying
  windows, which P2/P2² bar from firing foreign entries, so parks are
  letter-exact and a park term pins the run on its `F_all`-state forever. In
  `LEAVE`, the law holds strictly before the `U`'s witness, so the final
  window is still constrained by the last active sojourn (it must be a legal
  move), and `leave(s)` walks actual self-loops to an actual exit edge, after
  which `φ_d` asserts the continuation lies in `L(A↓d)`. Every step is an edge
  of `A`; the assembled path *is* a run.

The argument nowhere consults whether `C` is accepting, rejecting, or
terminal — each branch is an exact transcription of one run shape, and their
union is the component's language. That is why the degeneracies of layer 8
need no cases, and why no equivalence gate is kept: under the stated
preconditions — which are decided, not guessed, by BDD tests on `C` — there is
nothing left for a gate to catch. A child's correctness is the child's own
recursive responsibility, exactly as a context-free production composes;
k-anchor never inspects a child's formula.

## 11 — Non-LTL exit children (the witness lift)

An exit child may return `NotLTL(w)`: the residue `of(A↓d)` is not
LTL-definable, witnessed by a counting family `w` anchored at `d`. k-anchor
propagates the verdict (absorbing, taken before any decline) and lifts `w` to
`L`'s initial state by prepending a **reaching word** to the family's `u`: one
path `q0 ⟶* s ⟶(g) d` through `C`, each step's guard **restricted to the
letters enabling no edge to a different target** from its source — so the word
has a single continuation at every step and its left quotient *is* the residue
(star-free, hence LTL, is closed under left quotient; a strict-union quotient
would not preserve non-LTL-ness). The restriction subtracts *all* other-target
edges, self-loops included, so the shared idle letters that motivate the
construction are already excluded per step; parallel edges to the same target
are harmless (finite-prefix marks never touch an `Inf` set). A route whose
restriction empties is skipped; if no exact route survives, the verdict does
not lift and the peel degrades to a non-absorbing `PROBABLY_NOT_LTL` decline.
The lift is a letter-level, path-local construction — blind to the window
width, shared by every level.

## 12 — Peers, literature, out of scope

**Peers.** Two portfolio neighbors remain complementary, not subsumed. The
single-state peel (`daisy`) works on the TGBA form and reads
**transition-based** acceptance directly — a per-acceptance-set petal
condition (`⋀_i GF σ_i`) that the state-based form can only express by
splitting states; a recipe may well order it before k-anchor, whose own
single-state reading is the state-based degeneracy of layer 8. The
per-accepting-SCC union split (`sccdecomp`) remains the enabler where every
window level fails: k-anchor recurses down the SCC DAG through its exits, so
an anchored component needs no splitting, but a non-anchored one still does. A
genuinely shared *moving* window (`Enter_k(s) ∧ Enter_k(t) ≠ false`, `s ≠ t`,
at every affordable k) stays out of scope by design: the phase is then not a
function of the word's recent letters, and disambiguating with a fresh
proposition is not legal into LTL (projecting it out leaves LTL for QPTL).

**Literature.** The k = 1 precondition is a stuttering relaxation of **local
automata** — automata in which all transitions on a letter share their target,
the recognizers of local languages (Chomsky & Schützenberger 1963; Berstel &
Pin 1996): erase each state's loop letters and `C` becomes local on its
anchors. Where a local (or 1-definite — Perles, Rabin & Shamir 1963)
automaton's phase is a function of the last *letter*, layer 4's is a function
of the last *anchor* — "definite modulo stuttering" — and layer 6 relaxes
**k-definite / k-testable** the same way: erase the loop letters and the
component is recognized by its width-k factors; the law is the allowed-factor
constraint (`step` the digrams at k = 1, `step₂` the trigrams at k = 2), the
start law the allowed-prefix constraint, `fair` the ω-substitute for allowed
suffixes, and `I(v)` the stutter abstraction that keeps the window rigid over
unbounded sojourns.

**Out of scope (the assembly's concern).** k-anchor computes one local label
and trusts its inputs. The child `Λ`'s well-foundedness, the fixpoint `Λ*`
closing the open recursion, first-fit dispatch among translators, and
memoization by language belong to the assembly that wires it. Also noted, not
taken:

- **General k.** `Enter_k(s)` ranges over paths of length `k−1` into `s` with
  `I`-weakened interior components; the law stays `X`-shaped
  (`I(v₁) ∧ XI(v₂) ∧ … ∧ X^{k−1}g → X^k sojourn(s)`). Cost is per-edge at
  k = 2 but per-path beyond — cap k at 2–3.
- **Uniformizing the start.** Prepending `k−1` letters of virtual history to
  `q0` (a finite entry path into a transformed automaton — a prefix a
  daisy-style peel can reabsorb) would dissolve P0² and the start law into the
  general case. An automaton surgery, secondary to the point of multi-step
  anchors.
- **Measurement.** Corpus behavior — label sizes, which levels fire in
  practice, whether a higher level ever simplifies better where a lower one
  also passes — is another session's concern; the construction is validated on
  crafted fixtures.
- **Form dependence.** The preconditions are tested on `sbacc(tgba(L))`, and
  an input can pass in one automaton form and fail in another; which forms to
  try is a portfolio decision, not this production's.
