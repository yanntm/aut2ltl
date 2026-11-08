"""Audit saved lower-bound coverage and retain the three-class witness's orders."""
from __future__ import annotations

from itertools import permutations
import json
from pathlib import Path
from typing import Any


def read(path: Path) -> dict[str, Any]:
    """Read one saved machine outcome."""
    return json.loads(path.read_text())


def summarize(root: Path) -> None:
    """Check all smaller pairs and exact witness controls before writing aggregates."""
    results, logs = root / "results", root / "tests/logs"
    plan = read(results / "all-through-two-selection.json")
    prefix = [json.loads(line) for line in
              (results / "through-four-permutations-results.jsonl").read_text().splitlines()
              if json.loads(line)["classes"] < 3]
    multiple = [(path, read(path)) for path in
                sorted((logs / "multiple-through-two-parallel").glob("*.json"))]
    multiple = [(path, row) for path, row in multiple
                if row.get("schema") == "atlas.historical-stall.v1"]
    rows = [dict(key=r["key"], order=r["symbol_indices"],
        reference_classes=r["classes"], learned_classes=r["learned_classes"],
        verdict=r["verdict"], certification=r["certification"],
        source="through-four-permutations-results.jsonl") for r in prefix]
    rows.extend(dict(key=r["key"], order=["ab".index(name) for name in r["symbol_order"]],
        reference_classes=r["reference_classes"], learned_classes=r["learned_classes"],
        verdict=r["verdict"], certification=r["certification"],
        source="multiple-through-two-parallel/" + path.name)
        for path, r in multiple)
    expected = {(r["key"], p) for r in plan["candidates"]
                for p in permutations(range(r["symbols"]))}
    actual = {(r["key"], tuple(r["order"])) for r in rows}
    assert len(rows) == len(actual) == len(expected) == 16 and actual == expected
    assert plan["coverage"]["status"] == "COMPLETE" and len(plan["candidates"]) == 9
    assert all(r["verdict"] == "CANONICAL" and r["certification"] == "exact" for r in rows)
    rows.sort(key=lambda row: (row["reference_classes"], row["key"], row["order"]))
    (results / "all-through-two-results.json").write_text(json.dumps(dict(
        schema="atlas.historical-lower-bound.v1", coverage_status="COMPLETE",
        languages=9, ordered_runs=16, all_pairs_present_once=True,
        canonical_runs=16, rows=rows), indent=2) + "\n")

    orders = [read(path) for path in sorted((logs / "three-class-orders").glob("*.json"))]
    assert len(orders) == len({tuple(row["symbol_order"]) for row in orders}) == 6
    assert all(row["certification"] == "exact" for row in orders)
    stalls = [row for row in orders if row["verdict"] == "STALL"]
    assert len(stalls) == 2 and all(row["cyclic_stall"] and row["learned_classes"] == 2
                                  and row["symbol_order"][0] == "c" for row in stalls)
    assert all(row["learned_classes"] == 3 for row in orders if row["verdict"] == "CANONICAL")
    forward = read(logs / "three-class-orders/2-0-1.json")
    closure = read(results / "three-class-closure.json")
    assert all(forward[field] == closure[field] for field in
               ("hypothesis", "columns", "counterexamples", "verdict", "cyclic_witness"))
    saturated = read(results / "three-class-saturated.json")
    assert saturated["verdict"] == "CANONICAL" and saturated["learned_classes"] == 3
    (results / "three-class-orders.json").write_text(json.dumps(dict(
        schema="atlas.historical-orders.v1", runs=orders), indent=2) + "\n")
    print("PASS: every smaller language/order is canonical; exact three-class cyclic stall")


if __name__ == "__main__":
    summarize(Path(__file__).resolve().parents[1])
