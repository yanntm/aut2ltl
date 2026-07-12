# survey — the aut2ltl evaluation harness

`survey` is a **client of aut2ltl**, not part of it. It *runs* examples through
the front-end tool and produces CSV + logs. It installs as the `aut2ltl_survey`
console tool, or runs as `python -m survey` from the repo root.

## The generic collector (`survey.collect`)

The reusable core — correct subprocess isolation, a crash-safe checkpointed CSV,
per-item budget — is factored out of the aut2ltl-specific pipeline so *any*
tool-plus-validation experiment reuses it instead of hand-rolling (and
mis-rolling) process plumbing. A client supplies a `Scenario` with three plug
points and nothing else:

| plug point | what it decides |
|---|---|
| `invoke(example) -> Invocation` | how the tool is spawned for one input (the fixed context — e.g. a knowledge `K` — is captured on the Scenario instance) |
| `extract(example, result) -> Row` | the tool's stats parsed into CSV cells |
| `validate(example, row) -> Row` | the post step: re-check on an independent path (default no-op) |

`collect(examples, scenario, ...)` drives the loop: `bounded` isolation, resume
from checkpoint, one flushed row per run, then the summary. **Enumeration** is
the other configurable axis — `survey.discovery.discover(paths, keep=...)` walks
folders into `Example`s and now recognizes `.sos` invariants (first line
`SOS v1`); `keep={"sos"}` restricts a client to sos-only. The aut2ltl path
(`build`/`verify`/`report`/`run`) is one such client, unchanged; the given-that
survey (`sosl/tests/giventhat/gt5_demo.py`) is another — one fixed `K` against a
discovered folder of properties, validated by an independent legality recompute.

### Example client: the given-that survey

`sosl/tests/giventhat/gt5_demo.py` is the reference `collect` client — copy its
shape for a new tool. It surveys `simplify(𝓘(¬φ), 𝓘(K))` for one fixed
knowledge `K` over a folder of `.sos` properties:

- **enumerate** — `discover([folder], keep={"sos"})` → one `Example` per `¬φ`;
- **invoke** — `python3 -m sosl.sos.giventhat ¬φ.sos K.sos -o B.sos --json …`
  (the fixed `K` and the work dir live on the `GivenThatScenario` instance;
  `cwd` is the `sosl/` root so the module imports);
- **extract** — read the tool's own `--json` report into the row (verdict,
  class counts of `¬φ / K / T / P_min / P_max / B`, freedom bits, rung and
  stutter transitions, whether `B` beats all three references);
- **validate** — **off for now.** A sound check is external (Spot) and takes
  only the inputs and the output via the two legality inclusions
  `P_min ⊆ L(B) ⊆ P_max`; that needs sos→HOA, which `calculus` is slated to
  deliver through the right-Cayley graph transform. Re-checking legality with
  our own calculus would be circular (a shared bug passes both sides), so the
  post step stays empty until the Spot oracle exists. Meanwhile legality is
  guaranteed by the always-on `B ∩ P_K == P_min` set identity inside the tool.

Run it from `sosl/`:

```
python3 -m tests.giventhat.gt5_demo --knowledge K.sos --folder DIR \
        [--budget S] [--limit N] [--logs DIR]
```

**Defaults** (all overridable — see [CLI](#cli)): verification **on**, per-input
budgets **15 s** build / **15 s** equivalence, the **default** technique, and the
CSV to **stdout** (pass `--logs DIR`, e.g. `--logs logs`, to write a file).

## Scope: run, don't curate

survey **runs and reports**; it does **not** author or curate corpora. Each
dataset owns its own curation, co-located under `samples/<set>/` — a sample
carries the scripts that build it, and they run fine installed or via `-m`.

The one exception is the dataset-agnostic **AP-normalization + dedup-key**
utility: every dataset's curation reuses it, so it lives here as
`survey/normalize` rather than being copied per sample.

## CLI

```
aut2ltl_survey [--ltl FORMULA] [--hoa FILE] [--folder PATH] \
               [--use TECH] [--logs DIR] [--no-verify] [--verbose] \
               [--build-timeout S] [--equiv-timeout S]
```

Inputs are explicit and **repeatable** — there are no bare positionals:

- `--ltl FORMULA` — an inline LTL/PSL formula.
- `--hoa FILE` — a HOA automaton file.
- `--folder PATH` — a file or directory, **recursed** for readable examples: HOA
  by content (any extension), or an LTL list one-formula-per-line in a
  `.ltl`/`.txt` file (`#` comments and blank lines skipped). `logs/`,
  `__pycache__/` and hidden dirs are pruned; unreadable / unrecognized files are
  skipped.

With no input given, usage is printed.

- `--use TECH` — **repeatable**, passed through opaquely. None given → the default
  technique. Several given → each is run over every example, all rows in **one
  flat CSV**, with a per-technique summary. The token `all` (every technique, for
  soundness coverage) needs runtime discovery and is **not yet supported**.
- `--logs DIR` — write the run's CSV here as `survey_<timestamp>.csv`; without it
  the CSV goes to **stdout**. The summary always prints to stdout.
- `--no-verify` — skip the spot-oracle equivalence check (on by default).
- `--verbose` — per-input live trace on stderr.
- `--build-timeout S` / `--equiv-timeout S` — per-input budgets (default 15s each).

survey is **agnostic to `--use` values**: it passes them through to the front end
and never enumerates or validates technique names — they evolve, and survey must
not track them. `all` is the sole token survey interprets, via discovery.

## Output (CSV)

One flat CSV per run; the columns, left to right, are a pipeline that
short-circuits — once a stage stops, the later cells stay empty:

| column | meaning |
|---|---|
| `input` | the example's display id — formula text (LTL) or file basename (HOA); **readable, may collide** |
| `result` | `LTL` / `NOT_LTL` / `PROBABLY_NOT_LTL` / `DECLINED` / `TIMEOUT` / `CRASH` |
| `technique` | the recipe that produced the answer |
| `build_s` | front-end wall time |
| `formula` | the reconstructed LTL (truncated), on `LTL` rows |
| `dag` `temporals` `tree` `sharing` | size metrics of that formula |
| `validation` | spot-oracle verdict — `TRUE` / `FAIL` / `SIZE` / `TIMEOUT` / `ERROR` / `OFF` |
| `source` | **unique** provenance key — relative path (HOA) / `file:line` (LTL list) / `--ltl:k` (inline) |

The run is FAIL iff any row is verified non-equivalent (`validation == FAIL`);
otherwise SUCCESS (size/timeout/error are *not* failures). `input` is
human-readable and may repeat; `source` is the unique key for dedup, joins, and
per-folder breakdowns.

## Module map

| module | concern |
|---|---|
| `collect.py` | **generic** run→row→validate collector: `Scenario` (invoke/extract/validate) + `collect` (isolation, checkpoint, summary) — reusable by any tool |
| `__main__.py` | `python -m survey` entry — delegates to `cli.main` |
| `cli.py` | argument parsing; gathers inputs → `Example`s, calls `run` |
| `run.py` | orchestrate examples × techniques → rows → CSV + per-technique summary |
| `example.py` | `Example` — one input (`kind`/`value`/`display`/`source` provenance) |
| `discovery/` | recurse `--folder` paths → readable examples (`walk` + `detect` + `read`) |
| `techniques.py` | resolve the `--use` set (pass-through; `all` → discovery — see TODO) |
| `build.py` | run the front end on one example × technique via `bounded` → `BuildResult` |
| `verify.py` | **optional** spot-oracle equivalence (the gate's VERIFY), decoupled from build |
| `report.py` | CSV schema + writer + per-technique summary |
| `normalize/` | shared AP-normalization + dedup-key (its own [README](normalize/README.md)) |
| `diff/` | comparison tooling: **language** diff (`ltl_diff`/`diff_hoa`) + **result** CSV diff (`results`) — its own [README](diff/README.md) |

## TODO

- **`--use all` → technique discovery.** survey must enumerate the available
  techniques from the portfolio registry **at runtime** (no hardcoded list) and
  run them all for soundness. Until that lands, `all` is unsupported.

## Running

From the repo root: `python3 -m survey --folder samples/kinska --logs logs`.
Installed (after `pip install -e .`): `aut2ltl_survey --folder samples/kinska`.
