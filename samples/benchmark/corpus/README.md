# corpus — the language tier of the benchmark inputs

The distinct ω-languages realized by [`../inputs/`](../inputs/README.md), in the
genaut corpus layout — built by **plain calls to the genaut pipeline**, nothing
benchmark-specific (see `genaut/README.md`, "Imported sources"):

    python3 genaut/gen/import_inputs.py --inputs samples/benchmark/inputs \
        --out logs/genaut/bench_hoa --timeout 15
    python3 genaut/gen/canonize.py benchmark --in logs/genaut/bench_hoa \
        --out logs/genaut/bench_corpus --timeout 15 --max-sos 1048576
    python3 genaut/gen/flatten.py --corpus logs/genaut/bench_corpus \
        --out logs/genaut/bench_flat --exclude --canon

Adopting a regenerated drop into this folder is a separate, deliberate copy
(genaut convention: a run never writes where it read).

    det/benchmark/   canonical D per distinct language at fixed AP labeling
                     (syntactic 𝓘 dedup of the imported inputs), + census.md —
                     the funnel, every budget-skipped input listed by name.
    sos/benchmark/   the paired syntactic ω-semigroup 𝓘(L) as .sos, + census.md.
    flat_canon/      the consumable catalogue: one language per B_k orbit
                     (relabel/polarity twins folded, unused APs shed),
                     complement-closed (`<primal>_c`), with a `.cat` category
                     sidecar per language, + census.md.

Budgets (`--timeout 15`, `--cap 20000`, `--max-sos 1048576`) bound the heavy
tails of the Kinská `counting-*` families; a tripped budget is recorded in
`{det,sos}/benchmark/census.md`, never dropped silently. Structural claims are
asserted by `python3 -m tests.corpus.check_corpus` (over `flat_canon/`).

The survey bench reads `samples/benchmark/inputs` — one folder deeper than this
tier — so these derived automata never join the bench's own input set.
