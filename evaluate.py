#!/usr/bin/env python3
"""
Random LTL round-trip evaluation harness for the BuchiToLTL backward reconstruction prototype.

Usage examples:
    python3 evaluate.py -n 100 --seed 42 --aps 3 --tree-size 10 -o results.csv
    python3 evaluate.py -n 500 --only-failures --output failures.csv
    python3 evaluate.py --count 50 --tree-size 12 --max-states 12
"""

import argparse
import csv
import time
from datetime import datetime

import spot

from buchi2ltl.reconstruction import reconstruct_ltl


def main():
    parser = argparse.ArgumentParser(
        description="Random LTL → TGBA → reconstructed LTL round-trip tester"
    )
    parser.add_argument("-n", "--count", type=int, default=100,
                        help="Number of random formulas to test")
    parser.add_argument("--aps", type=int, default=3,
                        help="Number of atomic propositions for randltl")
    parser.add_argument("--seed", type=int, default=42,
                        help="RNG seed for reproducibility")
    parser.add_argument("--tree-size", type=int, default=10,
                        help="Tree size passed to randltl (lower = simpler formulas)")
    parser.add_argument("--simplify", type=int, default=2,
                        help="randltl simplification level (0-3)")
    parser.add_argument("-o", "--output", type=str, default="results.csv",
                        help="Output CSV file path")
    parser.add_argument("--only-failures", action="store_true",
                        help="Only record formulas where equivalence failed or an error occurred")
    parser.add_argument("--progress", type=int, default=20,
                        help="Print a progress line every N formulas")
    parser.add_argument("--max-states", type=int, default=20,
                        help="Skip formulas whose TGBA has more than this many states (safety)")

    args = parser.parse_args()

    print("=== BuchiToLTL Random Round-Trip Evaluation ===")
    print(f"Formulas     : {args.count}")
    print(f"APs          : {args.aps}")
    print(f"Seed         : {args.seed}")
    print(f"Tree size    : {args.tree_size}")
    print(f"Max states   : {args.max_states}")
    print(f"Output       : {args.output}")
    print(f"Start time   : {datetime.now().isoformat(timespec='seconds')}")
    print()

    fieldnames = [
        "id", "seed", "aps", "tree_size", "original", "recovered",
        "equivalent", "states", "acceptance", "time_ms", "technique", "error"
    ]

    with open(args.output, "w", newline="", encoding="utf-8") as outf:
        writer = csv.DictWriter(outf, fieldnames=fieldnames,
                                quoting=csv.QUOTE_ALL, escapechar="\\")
        writer.writeheader()

        gen = spot.randltl(
            args.aps,
            n=args.count,
            seed=args.seed,
            tree_size=args.tree_size,
            simplify=args.simplify,
            output="ltl"
        )

        start = time.time()
        failures = 0
        errors = 0
        skipped = 0

        for i, f in enumerate(gen, 1):
            original = str(f)
            row = {
                "id": i,
                "seed": args.seed,
                "aps": args.aps,
                "tree_size": args.tree_size,
                "original": original,
                "recovered": "",
                "equivalent": "",
                "states": "",
                "acceptance": "",
                "time_ms": "",
                "technique": "",
                "error": "",
            }

            t0 = time.time()
            try:
                aut = f.translate("GeneralizedBuchi", "Small", "High")
                states = aut.num_states()
                row["states"] = states
                row["acceptance"] = str(aut.get_acceptance())

                if states > args.max_states:
                    skipped += 1
                    row["error"] = f"too_many_states:{states}"
                    row["equivalent"] = "skipped"
                else:
                    recovered, _, technique = reconstruct_ltl(aut)
                    row["recovered"] = recovered
                    row["technique"] = technique

                    rec_f = spot.formula(recovered)
                    eq = spot.are_equivalent(f, rec_f)
                    row["equivalent"] = "yes" if eq else "no"
                    if not eq:
                        failures += 1

            except Exception as e:
                errors += 1
                failures += 1
                row["error"] = str(e)[:300]
                row["equivalent"] = "error"

            row["time_ms"] = int((time.time() - t0) * 1000)

            if not args.only_failures or row["equivalent"] not in ("yes", "skipped"):
                writer.writerow(row)

            if i % args.progress == 0 or i == args.count:
                elapsed = time.time() - start
                rate = i / elapsed if elapsed > 0 else 0
                print(f"[{i:4d}/{args.count}]  "
                      f"fail={failures:3d}  err={errors:2d}  skip={skipped:2d}  "
                      f"{rate:5.1f}/s  {elapsed:6.1f}s")

    total = time.time() - start
    success = args.count - failures
    print()
    print("=== Final Summary ===")
    print(f"Formulas tested : {args.count}")
    print(f"Equivalence OK  : {success}")
    print(f"Failures        : {failures}")
    print(f"  - real errors : {errors}")
    print(f"  - skipped     : {skipped}")
    print(f"Success rate    : {success / args.count * 100:.1f}%")
    print(f"Total time      : {total:.2f}s")
    print(f"CSV written to  : {args.output}")


if __name__ == "__main__":
    main()
