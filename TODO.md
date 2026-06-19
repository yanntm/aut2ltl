# COMBINATOR ALGEBRA — core cleanup (in progress, 2026-06-19)

PROGRESS: Step A (vocabulary: `identity` / `compose` / `Decorator` sort) LANDED 718c839.
Step B (recipes as point-free `compose` terms) LANDED fd0f5ff — survey SUCCESS, DAG=414
unchanged. REMAINING: Step C (unify the decomposers) + Step D (`COMBINATORS.md`), below.
(Scratch progress mirror: `algebra_todo.md`; approved plan: enchanted-dreaming-hopper.)

SCOPE FENCE: free named combinators only
— NO DSL / operator overloading, NO term-as-data/AST, NO meta-level reflection on
composition (we never navigate or rewrite the term). The algebra is a conceptual
lens + a fixed vocabulary, not a runtime structure. Carrier = language-manipulators
(Translators carrying the invariant *faithful-or-⊥*); the one real law is that
**soundness is closed under every operation** (any writable term is sound by
construction → reason locally, never look up a level).

- **Unify strength/acceptance/scc into ONE `decompose(split, connective, tag)`.**
  The three are byte-identical scaffolding (`__init__`/`__call__`/`_recombine`)
  differing only in (split, connective, tag): strength-pieces/`Or`, conjuncts/`And`,
  accepting-SCCs(+restrict)/`Or`. Collapse to
  `decompose(split, connective, tag)(leaf) = recurse(λself.λlang.
  combine(connective, tag, [self(p) for p in split(lang)]) if split(lang) else leaf(lang))`,
  where `combine` = the result composition-monoid (`fuse`/`credit`) finished with
  `own_simplify(connective(forms))`. NO new concept — wires `fix` (have) + the result
  monoid (have); this IS the deferred `recurse(decompose, combine, floor)` item, now
  with 3 concrete instances. `inv` already clean (a pure Decorator `∘`) — leave it.
  daisy's recurse body is a *choice* (`⊕`); decomp's is a *combine* (`∧/∨`) — same
  `fix`, different body op. VERIFIED: the three `_recombine` are byte-identical modulo
  (connective, tag) — so this is behavior-preserving, survey DAG must stay 414. Keep
  the split fns (strength_pieces / conjunct_pieces / scc accepting_sccs+restrict_marks)
  and the public import paths. (Supersedes the older "recurse/fix combinator (idea)".)

- **Write `COMBINATORS.md` — the (almost-)algebra note (lens, not a spec).** Record:
  carrier + the operations (`⊕`/`⊞`/`∘`/`fix` and the `∧/∨` combine) + neutrals
  (`decline`/`identity`); the soundness-closure property as the load-bearing theorem;
  and the PARTIAL/NEGATIVE laws *loudly* — `⊕` non-commutative (order=priority),
  `⊞`-with-margin non-associative, `fix` no monoid — so nobody "simplifies" a recipe
  into a different language. Optional: laws-as-behavioral-tests (idempotence of `inv`,
  `id` neutrality, `⊕` associativity) — checks, not a rewrite engine.

---

# aut2ltl — Project TODO

Open project-level items only. Completed campaigns are recorded in `docs/HISTORY.md`
and git history. (The big docs + contract/combinator refactors + the `decomp/` regroup
and the `kr → bls` engine reorg all landed — see HISTORY 2026-06-17.)

## Portfolio / combinators

- **Benchmark `best_inv_loop` (inv per-descent).** The `recurse` brick now lets the
  invariant strip ride every descent level (`daisy_pair_inv`); A/B it vs
  `best_daisy2` on the full benchmark — total size, and especially whether
  per-descent `inv` makes NOT_LTL verdicts cheaper / decidable on the kinška
  `counting/` automata (where `best` currently times out, by shrinking the monoid
  the LTL-definability gate tests). Top-only `best_inv` is benchmark-neutral (the
  global `Σ = ⋁(all guards)` is usually vacuous); the per-descent local `Σ` is the
  one that should fire.
- **Refine `best_of`'s cost policy, then wire it in.** The brick landed
  (`aut2ltl/best_of/` + `LTLResult.cost`), still unwired. Open: (a) a **switch
  margin** so it keeps the first-cited form unless a challenger is smaller by a real
  margin — `dag_node_count` is noisy at the margin (a better-factored form can carry
  more nodes), so harvest the big collapses and ignore churn; the scalar stays
  swappable (e.g. temporals-first). (b) Swap a `first_success` for `best_of` where
  running every branch pays (the `recurse` seam; pairing an inv-variant with its
  non-inv form to keep only per-input wins).
- **A `recurse`/`fix` combinator (idea — revisit with `best_of`).** `daisy`, the
  `strength`/`acceptance` decomposers all share ONE shape: structural recursion over a
  well-founded decomposition — `leaf = combine([leaf(sub) for sub in decompose(lang)])`
  with a floor base case. NOT Kleene (not iteration of one op on the same input; it
  hands strictly-smaller subproblems back, terminating by well-founded descent). A
  shared `recurse(decompose, combine, floor)` would unify the three and give ONE place
  to swap `first`→`best_of`, memoize subproblems on the `Language`, and tag uniformly.
  Today each combinator owns its own recursion (honest, explicit) — extract only when
  the `best_of` + memo payoff is real.
- **Retire the transitional shim** `aut2ltl/contract.py` once importers repoint.
- **`fuse2` is unwired** (`heur/fuse2`). Decision: leave it out; let fuzzing measure
  whether its absence costs `best` before deciding to wire it.

## Open

- **Output size at scale (the live research front).** The construction is cheap; the
  flat form explodes and Spot hits its 32-acceptance-set wall. Representation/
  verification, not fidelity. Analysis: `docs/dag_folding.md`.
- **Benchmark sub-project (`tests/benchmark/`).** A size bench, `default` vs `best`,
  reusing the survey engine over file-based `inputs/` (the survey corpus + W/U/R chains
  + 105 Kinská HOA; survey already routes HOA, oracle vs the source automaton — the old
  "HOA input to the survey" item, now done). Collection done for those three categories.
  Next: more categories, a *very* progressive `randltl` ladder (the construction is
  multiply-exponential — lean on the per-input timeout), and curation (dedup via
  `normalize.py`, a representative classified set). Reference: `tests/benchmark/logs/reference/`.
- **Flags manual.** The `--use` / `-O` reference doc the root README points to (add
  the `--use best` recipe and the recipe-vs-leaf distinction).

## Housekeeping

- Two stale bls probes (`tests/kr/test_kr_zoom.py`, `tests/kr/measure_formula_dag.py`)
  import the removed `reachability` shell — repoint to `aut2ltl.bls.operators` or drop.

## Deferred (intentional — revisit only if needed)

- **Options wiring, Buckets 2 & 3.** The remaining `KR_*` knobs (fuse_letters,
  fold_fin_reach, simp.*, tracing, resource/safety limits) are declared in the package
  `options.py` contracts but still read from `os.environ`. Process-scoped by nature,
  so they stay env unless per-instance A/B is ever required.
- **Infra compartment.** Share `bdd_dict`/buddy and the DAG unifier as refs on the
  threaded context (the Options and Caches compartments already landed).
