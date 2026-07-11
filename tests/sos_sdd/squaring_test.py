"""C4 completion gate: the squaring shortcut (the 2k relation encoding
recorded in sos_sdd/README.md) against the general pairing and an
explicit ground truth.

Per case: build with square="check" (the engine itself compares the
converged shortcut against the pairing pi — a disagreement would raise
StopTheLine before this test sees anything); verify every (z, z·z) row
of the relation R against the explicit packed composition; assert the
square-outcome record matches the case's convergence expectation; and
check pi equality against a square="off" build. Convergence cases also
run square="on" (pairing skipped); divergence cases assert "on" raises
StopTheLine.

Expectations follow the loop's termination theorem — convergence iff
every orbit period is a power of two: the triptych and ebeb converge,
mod3 (period 3) must diverge, and MOD2 (period 2) must converge despite
being periodic (squaring detects powers of two, not aperiodicity).
A single case name as argv runs just that case. Streams land in
tests/sos_sdd/logs/squaring_<name>.jsonl."""

import json
import sys
from pathlib import Path
from typing import Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from e0_triptych import TRIPTYCH  # noqa: E402
from e2_async import product as eb_product  # noqa: E402
from phase2_test import MOD3, compose  # noqa: E402

from sos_sdd import Automaton, Engine  # noqa: E402
from sos_sdd.errors import StopTheLine  # noqa: E402
from sos_sdd.model import Input  # noqa: E402
from sos_sdd.slotmodel import SlotModel, async_factored, from_automaton  # noqa: E402

LOGS = Path(__file__).resolve().parent / "logs"

# Mod-2 counter: [[a]]'s state map swaps forever, so its orbit has
# period 2 — squaring must still converge (2^j is eventually 0 mod 2).
MOD2 = Automaton("mod2", ("a",), 2, 0, 1, "Inf(0)", (
    (0, "a", 1, {0}), (0, "!a", 0, set()),
    (1, "a", 0, set()), (1, "!a", 1, set())))


def check(aut: Input, model: SlotModel, expect_converge: bool) -> None:
    log = LOGS / f"squaring_{model.name}.jsonl"
    s = Engine(square="check", stats=str(log)).build(aut, until_phase=2)

    # R element-exact against the explicit packed composition.
    rel = s.square_rel_pairs()
    assert len(rel) == s.em1_count(), (model.name, len(rel))
    for z, zz in rel:
        want = compose(tuple(z), tuple(z), model)
        assert tuple(zz) == want, (model.name, z, zz, want)

    # The outcome record agrees with the termination theorem.
    outcome = [r for r in map(json.loads, log.read_text().splitlines())
               if r.get("op") == "square-outcome"]
    assert len(outcome) == 1, (model.name, outcome)
    assert outcome[0]["converged"] is expect_converge, (model.name, outcome)

    # pi identical to the pairing-only build (the engine already
    # compared internally when converged; this also covers divergence).
    s_off = Engine(square="off").build(aut, until_phase=2)
    assert sorted(s.pi_pairs()) == sorted(s_off.pi_pairs()), model.name

    if expect_converge:
        s_on = Engine(square="on").build(aut, until_phase=2)
        assert sorted(s_on.pi_pairs()) == sorted(s_off.pi_pairs()), model.name
        print(f"{model.name}: converged, square_rounds="
              f"{outcome[0]['rounds']}")
    else:
        try:
            Engine(square="on").build(aut, until_phase=2)
            raise AssertionError(f"{model.name}: square=on did not stop the "
                                 "line on divergence")
        except StopTheLine:
            pass
        print(f"{model.name}: diverged as expected (rounds="
              f"{outcome[0]['rounds']}), pairing pi stands")


def case_triptych(name: str) -> None:
    aut = next(a for a, _ in TRIPTYCH if a.name == name)
    check(aut, from_automaton(aut), expect_converge=True)


def case_refuse() -> None:
    try:
        Engine(square="bogus").build(MOD2, until_phase=2)  # type: ignore[arg-type]
        raise AssertionError("square=bogus was not refused")
    except NotImplementedError:
        pass


CASES = {
    "gf_aa_parity": lambda: case_triptych("gf_aa_parity"),
    "even": lambda: case_triptych("even"),
    "evenblocks": lambda: case_triptych("evenblocks"),
    "mod3": lambda: check(MOD3, from_automaton(MOD3), expect_converge=False),
    "mod2": lambda: check(MOD2, from_automaton(MOD2), expect_converge=True),
    "ebeb": lambda: check(eb_product(2), async_factored(eb_product(2)),
                          expect_converge=True),
    "refuse": case_refuse,
}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    for name in (sys.argv[1:] or CASES):
        CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
