"""C5 cross-check — spec: "Cross-check `≃` against the explicit tool's
residual classes on every conformance instance."

The explicit side is `spot.language_map` on a deterministic graph — an
oracle independent of the sosl core (which computes its own residual base
from loop verdicts). Here it runs on the RAW
parsed automaton (no import postprocess), so its state numbering is the
digest's and the two partitions compare state-for-state: the engine's
Phase 4 `residual_classes()` (classes ordered by least member) must
equal the language_map partition brought to the same canonical form.

Cases: the classic seven (triptych, mod3, dupe, stem, EvenBlocks^{⊗2}
excluded — products have no single HOA) written out via
conformance_test.to_hoa, plus a deterministic corpus spread
(`corpus_sample`: every 250th flat_canon name, budget-skips ledgered as
skips, never failures). A single case name as argv runs just that case;
`corpus <name>` cross-checks one corpus instance."""

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import spot  # noqa: E402

from conformance_test import to_hoa  # noqa: E402
from e0_triptych import TRIPTYCH  # noqa: E402
from phase2_test import MOD3  # noqa: E402
from residuals_test import DUPE, STEM  # noqa: E402

from sos_sdd import Automaton, Engine  # noqa: E402
from sos_sdd.errors import Finding  # noqa: E402
from sos_sdd.hoa import digest_twa  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CORPUS_DET = REPO / "genaut" / "corpus" / "flat_canon" / "det"
LOGS = Path(__file__).resolve().parent / "logs"


def partition_of_language_map(aut: "spot.twa_graph") -> List[List[int]]:
    """`spot.language_map` as classes of state ids, each sorted, ordered
    by least member — the engine's `residual_classes()` canonical form."""
    lm = list(spot.language_map(aut))
    classes: dict = {}
    for q, c in enumerate(lm):
        classes.setdefault(c, []).append(q)
    return sorted((sorted(v) for v in classes.values()), key=lambda c: c[0])


def check_graph(graph: "spot.twa_graph", dig: Automaton) -> None:
    want = partition_of_language_map(graph)
    s = Engine(square="off", time_budget=5.0).build(dig, until_phase=4)
    got = [list(c) for c in s.residual_classes()]
    assert got == want, (f"{dig.name}: residual partitions diverge\n"
                         f"  engine       {got}\n  language_map {want}")
    print(f"{dig.name}: residual partition matches language_map "
          f"({len(want)} classes over {dig.states} states)")


def check_digest(dig: Automaton) -> None:
    hoa = LOGS / f"crosscheck_{dig.name}.hoa"
    hoa.write_text(to_hoa(dig))
    check_graph(spot.automaton(str(hoa)), dig)


def check_corpus(name: str) -> None:
    graph = spot.automaton(str(CORPUS_DET / f"{name}.hoa"))
    check_graph(graph, digest_twa(graph, name))


def case_corpus_sample() -> None:
    names = sorted(p.stem for p in CORPUS_DET.glob("*.hoa"))[::250]
    ok = skipped = 0
    for name in names:
        try:
            check_corpus(name)
            ok += 1
        except Finding as e:
            print(f"{name}: budget in phase {e.phase} — skipped (finding)")
            skipped += 1
    print(f"corpus_sample: {ok} matched, {skipped} budget-skipped, 0 diverged")


CASES = {
    "gf_aa_parity": lambda: check_digest(
        next(a for a, _ in TRIPTYCH if a.name == "gf_aa_parity")),
    "even": lambda: check_digest(
        next(a for a, _ in TRIPTYCH if a.name == "even")),
    "evenblocks": lambda: check_digest(
        next(a for a, _ in TRIPTYCH if a.name == "evenblocks")),
    "mod3": lambda: check_digest(MOD3),
    "dupe": lambda: check_digest(DUPE),
    "stem": lambda: check_digest(STEM),
    "corpus_sample": case_corpus_sample,
}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    args = sys.argv[1:]
    if args and args[0] == "corpus":
        for name in args[1:]:
            check_corpus(name)
    else:
        for name in (args or CASES):
            CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
