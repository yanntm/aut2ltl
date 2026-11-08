"""Select saved atlas languages and run one bounded historical learner per input."""
from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterator
from itertools import permutations
import json
from math import factorial
from pathlib import Path
import sys
import time
from typing import Any

from synomega.atlas import Bound, Collection, Query, Slice
from synomega.runner import run, setup_signals


def selection(collection: Collection, scope: Slice) -> tuple[list[dict[str, Any]], int]:
    """Select one-state residual graphs from saved canonical FDFA descriptors."""
    selected: list[dict[str, Any]] = []
    unavailable = 0
    for key, record in collection.languages.items():
        dimensions = {name: record["metrics"][name] for name in ("classes", "symbols")}
        if not scope.contains(dimensions):
            continue
        recurrent = [d for d in collection.descriptors.get(key)
                     if d.parameters["variant"] == "recurrent"]
        if not recurrent:
            unavailable += 1
            continue
        if recurrent[0].measurements["leading_states"] == 1:
            selected.append(dict(key=key, **dimensions,
                input=str((collection.folder(key) / record["payload"]).resolve())))
    selected.sort(key=lambda row: (row["classes"], row["symbols"], row["key"]))
    return selected, unavailable


def letter_orders(symbols: int, *, all_orders: bool,
                  both_orders: bool) -> Iterator[tuple[int, ...]]:
    """Enumerate explicit orders without materializing a factorial pool."""
    forward = tuple(range(symbols))
    if all_orders:
        yield from permutations(forward)
    else:
        yield forward
        if both_orders and symbols > 1:
            yield forward[::-1]


def main() -> int:
    """Save scope before execution, preserve each outcome, and stop on a witness."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--min-classes", type=int, default=1)
    parser.add_argument("--max-classes", type=int, default=4)
    parser.add_argument("--symbols", type=int, help="omit to include every effective alphabet")
    order_options = parser.add_mutually_exclusive_group()
    order_options.add_argument("--both-orders", action="store_true")
    order_options.add_argument("--all-orders", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 0 < args.timeout <= 15:
        parser.error("Each input must have a positive bound of at most fifteen seconds")
    if not (args.collection / "languages").is_dir():
        parser.error("Collection must already exist")
    if args.output.exists():
        parser.error("Use a fresh output directory; saved outcomes are not overwritten")
    setup_signals()
    bounds = dict(classes=Bound(lower=args.min_classes, upper=args.max_classes))
    if args.symbols is not None:
        bounds["symbols"] = Bound(lower=args.symbols, upper=args.symbols)
    scope = Slice("stamp", bounds=bounds)
    collection = Collection(args.collection.resolve())
    candidates, unavailable = selection(collection, scope)
    full_selection = len(candidates)
    if args.limit is not None:
        candidates = candidates[:args.limit]
    args.output.mkdir(parents=True)
    saved_scope = dict(
        schema="atlas.historical-selection.v1", collection=str(collection.root),
        scope=scope.to_dict(), coverage=Query(collection).slices.coverage(scope),
        filter="one residual state, using saved recurrent FDFA leading size",
        eligible_languages=full_selection, missing_leading_descriptors=unavailable,
        selected_languages=len(candidates), both_orders=args.both_orders,
        all_orders=args.all_orders,
        timeout_per_input=args.timeout, candidates=candidates,
    )
    (args.output / "selection.json").write_text(json.dumps(saved_scope, indent=2) + "\n")
    rows: list[dict[str, Any]] = []
    started = time.monotonic()
    found = None
    interrupted = False
    with (args.output / "results.jsonl").open("w") as stream:
        for number, candidate in enumerate(candidates):
            orders = letter_orders(candidate["symbols"], all_orders=args.all_orders,
                                   both_orders=args.both_orders)
            for order in orders:
                label = ",".join(map(str, order))
                if not args.all_orders:
                    label = "forward" if order == tuple(range(candidate["symbols"])) else "reverse"
                name = f"{number:04d}-{label}"
                payload = (args.output / (name + ".json")).resolve()
                command = [sys.executable, "-m", "atlas_search.one", candidate["input"],
                           "--output", str(payload), "--order", ",".join(map(str, order))]
                bounded = run(command, timeout=args.timeout,
                    cwd=Path(__file__).resolve().parents[1],
                    stdout=args.output / (name + ".stdout"),
                    stderr=args.output / (name + ".stderr"),
                    env={"PYTHONDONTWRITEBYTECODE": "1"})
                if bounded.timed_out:
                    outcome = dict(verdict="TIMEOUT", detail="Per-input bound exhausted")
                elif payload.exists():
                    outcome = json.loads(payload.read_text())
                else:
                    outcome = dict(verdict="CRASH", detail=f"No result; exit code {bounded.rc}")
                row = dict(**candidate, order=label, symbol_indices=order,
                    verdict=outcome["verdict"], learned_classes=outcome.get("learned_classes"),
                    certification=outcome.get("certification"),
                    detail=outcome.get("detail", ""), elapsed_seconds=bounded.wall_s,
                    output=payload.name)
                rows.append(row)
                stream.write(json.dumps(row) + "\n")
                stream.flush()
                print(f"{name} c{candidate['classes']} s{candidate['symbols']}: "
                      f"{row['verdict']} {row['learned_classes']} {candidate['key']}", flush=True)
                if row["verdict"] == "STALL" and found is None:
                    found = row
                if found is not None and not args.keep_going:
                    interrupted = True
                    break
            if interrupted:
                break
    expected_runs = sum(factorial(row["symbols"]) if args.all_orders else
                        2 if args.both_orders and row["symbols"] > 1 else 1
                        for row in candidates)
    counts = dict(Counter(row["verdict"] for row in rows))
    summary = dict(schema="atlas.historical-campaign.v1",
        attempted_runs=len(rows), selected_runs=expected_runs,
        completed_selection=len(rows) == expected_runs,
        selection_is_full=args.limit is None and unavailable == 0,
        verdicts=counts, first_stall=found,
        coverage_status=saved_scope["coverage"]["status"],
        elapsed_seconds=time.monotonic() - started)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
