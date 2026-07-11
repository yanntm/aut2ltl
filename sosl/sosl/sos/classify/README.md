# sosl.sos.classify — classifying an ω-language on its invariant

Reads one `Invariant` `(𝒞, λ, M, P)` and emits the complete classification
record of the language: LTL-definability, stutter-invariance (the X-free
refinement of LTL), the safety–progress / topological rung, the chain and
superchain numbers, the parity/Rabin index, and the Wagner degree — the
derivative recursion of the degree tail included — every verdict carrying a
replayable witness. Each classification is a polynomial table search; no
automaton and no external tool is consulted.
Normative math: `research_notes/sos_classification.md` (procedures
and sources, referenced here as C§n); tool shape and experiment plan:
`research_notes/sos_classifier_spec.md`; what is answered today:
`research_notes/sos_classifier_report.md`.

## Map

    primitives/   C§2 — the shared toolkit. Green's R/L/H preorders as
                  principal-ideal membership, the idempotent set E, the one-line
                  H-order on idempotents and its strict descents, the R-class
                  partition. Depends on nothing but the invariant.

    aperiodic/    C§4 — power orbits of every class; aperiodic (LTL-definable)
                  iff every orbit has period 1; on failure the first group
                  carrier in shortlex order. The cheap standalone "is LTL" cut,
                  kept off the full-classify path (it is called far more often).

    stutter.py    stutter-invariant iff every letter's class is idempotent
                  (M(λa, λa) = λa; sos_calculus.md Prop 3.3). The one-line
                  equational read-off beside aperiodicity — the X-free subclass
                  of LTL, complement-invariant.

    chains/       C§5 — (m+, m-) by longest-alternating-path DP over the
                  H-descending idempotent DAG, per admissible stem; one maximal
                  witness of each sign, plus per-stem best lengths for §6.

    superchains/  C§6 — (n+, n-) by marking stems that carry a maximal chain,
                  then a longest sign-alternating strictly-R-descending path DP
                  over their R-classes; one maximal witness of each sign.

    readoff/      C§7-8 — pure arithmetic on the four integers: the rung table
                  (open/closed/weak/dba/dca), the parity/co-parity/boolean
                  lengths, and the Wagner data mu / sign / gamma. Carries an
                  Ordinal < omega^omega (Cantor normal form, CNF addition,
                  spaceless rendering). The m>=1 & n+=n- (tied) case is flagged
                  needs_derivative and handed to derive/.

    derive/       C§8 — the degree derivation as restricted table recursion
                  (Theorem 4.5): zone from the maximal superchain tops
                  (B = T+ n T-), rerun chains/superchains on the kept stems
                  with the marking unchanged, fold the two virtual sinks, and
                  CNF-sum the per-level mu terms into gamma (the trace is the
                  Cantor normal form); the sign is read at the first untied
                  level. At most m(X) levels, one engine pass each.

    witness.py    Renders each verdict as lassos over class keys (spec §1):
                  chain lassos key(s).key(e_i)^omega with expected bits,
                  superchain connecting words u_i by BFS in the right Cayley
                  graph, and the group carrier.

    record.py     classify(inv) -> Record: runs the bands + read-off (+ the
                  derivation when the read-off is tied), asserts the always-on
                  internal laws (4.1) and self-replays each chain witness
                  through Invariant.member, and packages the flat record; a
                  derived record carries its level trace in
                  witnesses["derivation"].

    emit.py       Record -> compact human text (spec §1 output shape).

    io/           the `.cat` sidecar — the serialization of a classification.
                  writer (Record -> .cat text + batch write_cats over a folder),
                  reader (parse_cat -> flat dict), and the Wagner vocabulary
                  (class naming, weakest-first ordering) a study aggregates
                  without pulling the classifier. `python3 -m sosl.sos.classify.io
                  <sos-folder>` writes one `.cat` beside each `.sos`.

    __main__.py   the `sos_classify` tool: `python3 -m sosl.sos.classify
                  <file.sos> [--hoa H] [--cat OUT] [--certificates]
                  [--expect FIX.cat]`, with the spec §2 exit codes (0 ok; 2 gamma
                  PARTIAL; 3 malformed; 4 internal-invariant violation).

## Not yet wired

The certificate replay against a `--hoa` presentation (3.5 / harness item 5):
`--hoa`/`--certificates` are accepted but reserved. `gamma_partial` remains in
the `Record` shape (and the CLI keeps its exit-2 path) for consumers, but the
assembly never sets it — the derivation resolves every tied case. See the
report for the current coverage.

## Tests

Under `sosl/tests/sosl/`, each self-bound and run from the `sosl/` subtree:
`classify_primitives`, `classify_chains`, `classify_superchains`,
`classify_readoff`, `classify_record` (all assert against the C§9 triptych
values), `classify_aperiodic` (band 1 on one `.sos`), `classify_fork` (the
derivative regime resolved: `(omega+1, delta)` on the `Fork` fixture, its
complement, and the floor-shape twin `fork_floor.sos`, with the level trace
asserted), and `classify_escape` (the derivation's non-empty kept core and
sink-resolved sign: `(omega+1, sigma)` / dual `pi` on C§4's running example).
