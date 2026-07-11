# Minimality does not tame the recurrence sub-questions: a star-free counterexample

*Experimental report answering the protocol in
[`experiment_pi2_hunt.md`](experiment_pi2_hunt.md).*

**Result in one line.** The conjecture is **false**: there exist state-minimal
deterministic ω-automata whose language is star-free yet whose recurrence
sub-question `Inf(C)` is **not** star-free — the smallest being the minimal
3-state automaton of `GF(a & X(b & Xb))`. Such forms are not rare (≈24 % of a
formula-generated corpus). State-minimality is therefore **not** a sufficient
condition for the BLS cascade to be sound; the tool stays sound only because its
gate *declines* these inputs.

---

## 1. Context

The BLS (Boker–Lehtinen–Sickert) cascade translates a deterministic ω-automaton
`D` to LTL by asking, for each configuration `C` of a Krohn–Rhodes holonomy
decomposition, a sub-question `Fin(C)` = "the run visits `C` only finitely
often". This is sound exactly when the dual language `Inf(C)` = "the run visits
`C` infinitely often" is itself star-free (LTL-definable). The construction's
soundness on LTL inputs was conjectured to follow from **state-minimality**:

> **(Π₂ conjecture).** If `D` is state-minimal and `L(D)` is star-free, then for
> every configuration `C` the language `Inf(C)` is star-free.

A prior fixture, [`gfa_pad2.hoa`](../samples/fixtures/hoa/definability/gfa_pad2.hoa),
shows the failure mode *off* the minimum — a **padded** form of `GFa` (a
position-parity bit inert to acceptance) whose transition monoid carries a `Z₂`
that a recurrence question reads but the language does not. The open question was
whether **minimality forbids** this. This experiment set out to break the
conjecture: to exhibit `P1 ∧ P2 ∧ P3` on a single automaton, where

- **P1** — `L(D)` is star-free (every LTL language is; for a formula-generated
  corpus this holds by construction);
- **P2** — `D` is state-minimal, certified by **SAT-min** (not bisimulation);
- **P3** — some `Inf(C)` is **not** star-free.

## 2. Setup and existing infrastructure

The experiment reused the repository's decision procedures as trusted oracles and
added a thin, self-contained harness under
[`tests/pi2_hunt/`](../tests/pi2_hunt/) (see its
[`README.md`](../tests/pi2_hunt/README.md)). No code in `aut2ltl/` was modified —
this is a pure hunt.

**Reused, in-repo:**
- the star-free/LTL-definability oracle `aut2ltl.bls.definability.oracle.decide`
  (P1, and the language-level judge for `Inf(C)`);
- `Language.det_generic_minimal` / `spot.sat_minimize` (P2, SAT-minimality);
- the holonomy decomposition `decompose_gens` / `extract_generators`, and the
  premise checker [`casc_cover_check.py`](../tests/probes/casc_cover_check.py).

**Added harness (7 small scripts):** a formula→minimal-form corpus generator, a
per-automaton `P1∧P2∧P3` predicate, a bounded parallel folder sweep, a
cascade-free transition-monoid aperiodicity test and corpus screener, a witness
certificate extractor, and a census canonicaliser. All run one input per
invocation under `aut2ltl.bounded` (the `timeout --signal=INT` runner that reaps
GAP), stream results incrementally, and respect the ≤15 s/example discipline.

**One methodological correction was essential.** `decompose_aut` re-normalises its
input with `spot.postprocess("parity min even", "deterministic", "complete",
"sbacc")`, a *heuristic* reducer that **pads even a SAT-minimal input** (e.g.
`GFa`'s minimal form 2→3 states, and the 4-state witness below 4→5). Grounding the
recurrence questions on that padded form conflates a genuine minimal-form group
with padding — the `gfa_pad2` trap. The predicate therefore grounds configurations
on the minimal form **verbatim** (the `build_cascade_unstripped` path, replicating
`decompose_aut` below its `postprocess` line), so P3 is tested on the true target.

## 3. Experiments and results

Three independent, mutually-corroborating verdicts were required before accepting
any hit: (a) the language-level oracle on the grounded `Inf(C)`; (b) the paper's
reset/cover premises via `casc_cover_check`; and (c) a **cascade-free, oracle-free**
computation of the automaton's transition-monoid aperiodicity. All three agree on
the witnesses below.

### 3.1 The counterexample (headline)

**`GF(a & X(b & Xb))`** — "infinitely often, a window `a·b·b`". Fixture:
[`gf_abb_min_z2.hoa`](../samples/fixtures/hoa/definability/gf_abb_min_z2.hoa).

| property | value | how certified |
|---|---|---|
| P1 star-free | **yes** | `oracle_probe`: "syntactic ω-semigroup is aperiodic; an LTL formula exists" |
| P2 minimal | **3 states** | `det_generic_minimal` = `sat_minimize` = 3 |
| P3 non-star-free `Inf(C)` | **yes**, at `(1,1,1)`,`(2,1,1)` | `decide` = NOT_LTL, period-2 family `u=[] v=[a&b] tail=[a&b; !a&b]` |
| transition monoid | **non-aperiodic (`Z₂`)** | letter `a&b` has period 2, image `(2,2,0)` |
| shipped tool | **DECLINES** | sound (no wrong answer), but incomplete on this LTL language |

So a **state-minimal** automaton for a **star-free** language poses a recurrence
sub-question that **counts modulo 2** — the conjecture is refuted at 3 states.

### 3.2 A second witness with a wrong assembled output

**`GF(a & X(b & X(a & !b)))`**, minimal at 4 states. Fixture:
[`gf_ab_anb_min_z2.hoa`](../samples/fixtures/hoa/definability/gf_ab_anb_min_z2.hoa).
Transition monoid carries `Z₂` (word `(a&!b)·(a&b)`, period 2, image `(3,3,1,1)`);
four configurations have non-star-free `Inf(C)`. Grounded verbatim on the minimal
form (no padding), the **ungated cascade builds a formula that is not equivalent
to `L(D)`** — a concrete unsound sub-term assembled into a wrong output. The gate
declines it, so the shipped tool is unaffected.

### 3.3 The phenomenon is common

A cascade-free transition-monoid screen over the whole formula-generated corpus
(894 minimal recurrence forms over 2 atoms) ran in **0.17 s** and found:

| | count | share |
|---|---|---|
| aperiodic (no group) | 680 | 76 % |
| **group-bearing (`Z₂`/`Z₃`, hit candidates)** | **214** | **24 %** |

Both period-2 (`Z₂`) and period-3 (`Z₃`) groups occur. Pattern-detection
recurrences `GF(window)` are a rich source: the minimal detector of a fixed window
routinely carries a group in its transition monoid.

### 3.4 Why minimality does not help (the mechanism)

For languages of *finite* words, the minimal DFA's transition monoid **is** the
syntactic monoid, so star-free ⇒ aperiodic transition monoid. For **ω-languages
this identity fails**: the minimal deterministic (Büchi) automaton is not
"syntactic", and its transition monoid can be **non-aperiodic even when the
language is star-free** — the group lives in the state/acceptance encoding, not in
the language's syntactic congruence. A group in `D`'s transition monoid forces a
group into any holonomy decomposition of `D`, which is exactly a recurrence
sub-question that counts. Minimising the *state count* does nothing to remove it.

The controls confirm the reading: `gf_aa` is aperiodic (`P3-none`); `gf_aa_parity`,
once grounded on its true 2-state minimal form, is also `P3-none` (its apparent
group was a `decompose_aut` **padding** artifact); and `gfa_pad2` / `stag1` are
`P2-fail` — genuinely padded non-minimal forms on which the P3 arm does fire,
validating detection.

## 4. Conclusion

- **The Π₂ conjecture is false.** State-minimality does not imply that the
  recurrence sub-questions of a star-free language are star-free. Two explicit,
  triply-verified witnesses are committed as fixtures, the smallest at 3 states.
- **Root cause:** the minimal DBA of a star-free ω-language may have a
  non-aperiodic transition monoid — the finite-word "minimal ⇒ syntactic ⇒
  aperiodic" chain does not carry over to ω-automata.
- **Consequence for the tool:** the BLS cascade's soundness cannot rest on
  "minimised" alone; it must screen definability **per sub-term** (which the
  present gate effectively does by declining — the shipped tool never returns a
  wrong answer on these inputs, only an honest decline).
- **For the theory session:** minimality is the wrong invariant; the property to
  screen is **aperiodicity of the transition monoid** of the form the cascade
  actually grounds on. The padding behaviour of `decompose_aut` (§2) is a separate
  soundness-relevant fact worth carrying forward.

Follow-ups left open: the exhaustive `genaut` census (3B, canonicaliser in place)
to pin an exact coverage bound, and a directed minimal `Z₃` witness (3C).

## 5. Reproduction annex

All commands run from the repository root; each is self-terminating and bounded.

```bash
# P1 (star-free) — independent oracle
python3 tests/probes/oracle_probe.py samples/fixtures/hoa/definability/gf_abb_min_z2.hoa

# P2 + P3 — the transition monoid carries a group (cascade-free, ~instant)
python3 tests/pi2_hunt/monoid_check.py samples/fixtures/hoa/definability/gf_abb_min_z2.hoa

# P3 — the non-star-free Inf(C) counting certificates on the minimal form
python3 tests/pi2_hunt/witness_config.py samples/fixtures/hoa/definability/gf_abb_min_z2.hoa

# independent premise check (reset/cover) on the 4-state witness
python3 tests/probes/casc_cover_check.py samples/fixtures/hoa/definability/gf_ab_anb_min_z2.hoa

# the shipped tool is SOUND here (declines, never wrong)
python3 -m aut2ltl --hoa samples/fixtures/hoa/definability/gf_abb_min_z2.hoa

# reproduce the corpus and the 24% statistic
python3 tests/pi2_hunt/gen_dba_corpus.py --out tests/pi2_hunt/corpus_3a
python3 tests/pi2_hunt/monoid_screen.py tests/pi2_hunt/corpus_3a
```

**Fixtures (committed):**
- [`samples/fixtures/hoa/definability/gf_abb_min_z2.hoa`](../samples/fixtures/hoa/definability/gf_abb_min_z2.hoa)
  — the 3-state headline counterexample.
- [`samples/fixtures/hoa/definability/gf_ab_anb_min_z2.hoa`](../samples/fixtures/hoa/definability/gf_ab_anb_min_z2.hoa)
  — the 4-state witness with a wrong assembled output.

**Harness:** [`tests/pi2_hunt/`](../tests/pi2_hunt/) and its
[`README.md`](../tests/pi2_hunt/README.md). **Protocol answered:**
[`experiment_pi2_hunt.md`](experiment_pi2_hunt.md).
