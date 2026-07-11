# tests/sosl — probes and checks for the sosl tool

Placed scripts for exercising `sosl` (no `/tmp`, no `python -c` one-liners).
Each probe is self-bound and takes a single input on argv so it respects the
per-example diagnostic cap; long output is redirected under `logs/` here, never
`/tmp`.

## What lives here

- Property tests for `objects` (canonical serialization round-trips, the
  membership read-off, the Cayley prediction semantics).
- Teacher self-check probes (simulator vs. reference read-off on seeded lassos).
- Learner probes: table/fold coherence, split-witness replay, single-case
  end-to-end learn+validate.
- The harness entry points invoked by `sosl.experiment` during a campaign.

## See also

The soundness harness layers and the experiments they back:
`research_notes/sos_learning_spec.md` §5–6. Fixtures the probes run on:
`samples/sosl/`.
