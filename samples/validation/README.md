# samples/validation — the correctness gate corpus

The curated 40-formula corpus that the soundness gate runs:

    aut2ltl_survey --folder samples/validation        # both forms (ltl + hoa)
    aut2ltl_survey --folder samples/validation/hoa    # automata only

Two parallel sides, same substructure:

- **`ltl/`** — the 40 as LTL, one `.ltl` per Manna–Pnueli class (safety,
  guarantee, obligation, recurrence, persistence, reactivity, bottom).
- **`hoa/`** — the same 40 as ω-automata, generated from `ltl/` with
  `python3 -m survey.ltl2hoa samples/validation/ltl`. Each file is named for
  traceability: `<class>_l<line>.hoa` (its formula's line in the source `.ltl`).

A SUCCESS run = no verified non-equivalent answer (build timeouts / size
explosions are not failures). The same 40 seed the bench at
`samples/benchmark/inputs/core/`.
