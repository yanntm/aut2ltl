# samples/validation — the correctness gate corpus

The curated 40-formula corpus that the soundness gate runs:

    aut2ltl_survey --folder samples/validation

one `.ltl` per Manna–Pnueli class (safety, guarantee, obligation, recurrence,
persistence, reactivity, bottom). A SUCCESS run = no verified non-equivalent
answer (build timeouts / size explosions are not failures). The same 40 seed the
bench at `samples/benchmark/inputs/core/`.

Status: currently LTL formulas; these will evolve toward ~40 automata.
