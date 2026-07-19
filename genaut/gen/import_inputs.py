"""genaut/gen/import_inputs.py — materialize a mixed inputs folder as one HOA per input.

The census pipeline consumes a folder of HOA automata (`corpus/tgba/<tag>/`).
This stage lets any presentation collection feed it: walk an inputs folder
(HOA files and `.ltl` lists, via `survey.discovery`), translate each LTL line
(`spot.translate`), and write every input as one canonically serialized HOA
(`aut2ltl.ltl.twa.dump_hoa`) under a single flat folder, named for its origin —
the input's path under the inputs root, flattened:

    <category>_<stem>.hoa           an HOA file
    <category>_<stem>_L<line>.hoa   one line of an .ltl list

The output folder is a valid `--in` for `gen/canonize.py`; nothing downstream
knows the inputs were not enumerated. A per-input `--timeout` (SIGALRM — a
wedged native call can overshoot it) skips-and-records; the funnel lands in the
output folder's `census.md`, every skipped input listed with its reason —
nothing is dropped silently.

Usage:
  python3 genaut/gen/import_inputs.py --inputs DIR --out DIR [--timeout S]
"""
from __future__ import annotations

import argparse
import os
import signal
import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Optional

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
for _p in (_REPO, os.path.join(_REPO, "sosl")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import spot                                              # noqa: E402

from aut2ltl.ltl.twa import dump_hoa                     # noqa: E402
from survey.discovery.scan import discover               # noqa: E402
from survey.example import Example                       # noqa: E402


class Budget(Exception):
    """One input outran its per-input wall clock."""


@contextmanager
def _deadline(seconds: float) -> Iterator[None]:
    """Raise `Budget` if the body outlasts `seconds` (0 disables). SIGALRM-based:
    main thread only, one nesting level; a wedged native call overshoots."""
    if seconds <= 0:
        yield
        return

    def _fire(signum: int, frame: object) -> None:
        raise Budget()

    prev = signal.signal(signal.SIGALRM, _fire)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, prev)


def ident_of(example: Example, inputs: str) -> str:
    """`<category>_<stem>` for an HOA file, `<category>_<stem>_L<line>` for one
    line of an LTL list — the input's path under `inputs`, flattened. Distinct
    sources give distinct idents, so the output names are collision-free."""
    src, _, line = example.source.partition(":") if example.kind == "ltl" \
        else (example.source, "", "")
    rel = os.path.relpath(src, inputs)
    stem = os.path.splitext(rel)[0].replace(os.sep, "_")
    return f"{stem}_L{int(line):02d}" if line else stem


def automaton_of(example: Example) -> "spot.twa_graph":
    """The input as a Spot automaton: an HOA file is parsed, an LTL formula is
    translated. Neither is reduced — downstream `canonical` normalizes."""
    if example.is_hoa:
        return spot.automaton(example.value)
    return spot.translate(spot.formula(example.value))


def import_inputs(inputs: str, out_dir: str, timeout: float) -> Dict[str, int]:
    """Write one canonical HOA per discovered input into `out_dir`, plus a
    `census.md` recording the funnel. Returns the tally."""
    os.makedirs(out_dir, exist_ok=True)
    tally: Counter = Counter()
    skipped: List[Dict[str, str]] = []
    for example in discover([Path(inputs)], keep={"ltl", "hoa"}):
        tally["scanned"] += 1
        ident = ident_of(example, inputs)
        path = os.path.join(out_dir, f"{ident}.hoa")
        if os.path.exists(path):
            raise AssertionError(f"ident collision: {ident}")
        try:
            with _deadline(timeout):
                text = dump_hoa(automaton_of(example))
        except Budget:
            tally["timeout"] += 1
            skipped.append({"ident": ident, "input": example.display,
                            "reason": f"timeout (>{timeout}s)"})
            continue
        except Exception as exc:                          # a malformed input
            tally["error"] += 1
            skipped.append({"ident": ident, "input": example.display,
                            "reason": f"{type(exc).__name__}: {exc}"})
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        tally["written"] += 1
    _write_census(out_dir, inputs, timeout, tally, skipped)
    return dict(tally)


def _write_census(out_dir: str, inputs: str, timeout: float,
                  tally: Counter, skipped: List[Dict[str, str]]) -> None:
    lines = [
        "# imported inputs — one canonical HOA per input\n",
        f"- inputs: `{os.path.relpath(inputs, _REPO)}`",
        f"- scanned: {tally['scanned']}",
        f"- **written: {tally['written']}**",
        f"- skipped: {tally['timeout']} timeout (>{timeout}s), "
        f"{tally['error']} error",
        "",
        "Built by `python3 genaut/gen/import_inputs.py`. Each `.hoa` is the",
        "input as-is (LTL lines `spot.translate`d), canonically serialized",
        "(`dump_hoa`) — not reduced, not deduplicated; `gen/canonize.py` owns",
        "the language dedup.",
    ]
    if skipped:
        lines += ["", "## Skipped (recorded, never silent)", ""]
        lines += [f"- `{s['ident']}` ({s['input']}): {s['reason']}"
                  for s in skipped]
    with open(os.path.join(out_dir, "census.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="import_inputs",
        description="Materialize an inputs folder as one canonical HOA per input.")
    ap.add_argument("--inputs", required=True, help="folder to walk (HOA + .ltl lists)")
    ap.add_argument("--out", required=True, help="output folder (one .hoa per input)")
    ap.add_argument("--timeout", type=float, default=15.0,
                    help="per-input wall clock in seconds (0 disables; default 15)")
    args = ap.parse_args(argv)
    t = import_inputs(args.inputs, args.out, args.timeout)
    print(f"imported {t.get('written', 0)}/{t.get('scanned', 0)} inputs "
          f"({t.get('timeout', 0)} timeout, {t.get('error', 0)} error) "
          f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
