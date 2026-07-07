# sosl.sos.classify — classifying an ω-language on its invariant

Reads one `Invariant` `(𝒞, λ, M, P)` and emits the complete classification
record of the language: LTL-definability, the safety–progress / topological
rung, the chain and superchain numbers, the parity/Rabin index, and the Wagner
degree — every verdict carrying a replayable witness. Each classification is a
polynomial table search; no automaton and no external tool is consulted (the
one exception, the derivative recursion of the degree tail, is not yet wired —
see below). Normative math: `research_notes/sos_classification.md` (procedures
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

    chains/       C§5 — (m+, m-) by longest-alternating-path DP over the
                  H-descending idempotent DAG, per admissible stem; one maximal
                  witness of each sign, plus per-stem best lengths for §6.

    superchains/  C§6 — (n+, n-) by marking stems that carry a maximal chain,
                  then a longest sign-alternating strictly-R-descending path DP
                  over their R-classes; one maximal witness of each sign.

    readoff/      C§7-8 — pure arithmetic on the four integers: the rung table
                  (open/closed/weak/dba/dca), the parity/co-parity/boolean
                  lengths, and the Wagner data mu / sign / gamma. Carries an
                  Ordinal < omega^omega (Cantor normal form, CNF addition). The
                  m>=1 & n+=n- case is left PARTIAL (needs the derivative).

    witness.py    Renders each verdict as lassos over class keys (spec §1):
                  chain lassos key(s).key(e_i)^omega with expected bits,
                  superchain connecting words u_i by BFS in the right Cayley
                  graph, and the group carrier.

    record.py     classify(inv) -> Record: runs the bands + read-off, asserts
                  the always-on internal laws (4.1) and self-replays each chain
                  witness through Invariant.member, and packages the flat record.

    emit.py       Record -> flat dict (JSON) / text (spec §1 output shape).

    __main__.py   the `sos_classify` tool: `python3 -m sosl.sos.classify
                  <file.sos> [--hoa H] [--json OUT] [--certificates]
                  [--expect FIX]`, with the spec §2 exit codes (0 ok; 2 gamma
                  PARTIAL; 3 malformed; 4 internal-invariant violation).

## Not yet wired

The derivative recursion of C§8 (the `m>=1 & n+=n-` degree tail), the
certificate replay against a `--hoa` presentation (3.5 / harness item 5), and
the census campaign (X1-X3). The record reports `gamma_partial` with
`sign="PARTIAL"` and `gamma=None` on the derivative case rather than resolving
it; `--hoa`/`--certificates` are accepted but reserved. See the report for the
current coverage.

## Tests

Under `sosl/tests/sosl/`, each self-bound and run from the `sosl/` subtree:
`classify_primitives`, `classify_chains`, `classify_superchains`,
`classify_readoff`, `classify_record` (all assert against the C§9 triptych
values), and `classify_aperiodic` (band 1 on one `.sos`).
