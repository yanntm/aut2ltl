"""Phase 2 (C4) gate: the crossing / idempotent-power map pi checked
against an explicit power-orbit ground truth — per element, iterate the
packed composition until the orbit closes and pick its unique idempotent
(deliberately a different algorithm from the engine's pairing lfp).

Cases: the triptych; a mod-3 cycle (odd orbit period — the case the
deferred squaring shortcut could never carry, the pairing must); an
EvenBlocks x EvenBlocks factored product (block_base at work, |pi| =
256); refusal probes (square modes other than "off" are deferred, and
pi readings on a phase-1 object must raise). A single case name as argv
runs just that case. Stats streams land in
tests/sos_sdd/logs/phase2_<name>.jsonl."""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from e0_triptych import TRIPTYCH  # noqa: E402
from e2_async import product as eb_product  # noqa: E402

from sos_sdd import Automaton, Engine  # noqa: E402
from sos_sdd.model import Input  # noqa: E402
from sos_sdd.slotmodel import SlotModel, async_factored, from_automaton  # noqa: E402

LOGS = Path(__file__).resolve().parent / "logs"

Elem = Tuple[int, ...]

# Period-3 power orbit on 'a' (states cycle mod 3, one mark on the
# 0 -> 1 edge): the general pairing must carry it.
MOD3 = Automaton("mod3", ("a",), 3, 0, 1, "Inf(0)", (
    (0, "a", 1, {0}), (0, "!a", 0, set()),
    (1, "a", 2, set()), (1, "!a", 1, set()),
    (2, "a", 0, set()), (2, "!a", 2, set())))


def compose(u: Elem, v: Elem, model: SlotModel) -> Elem:
    """u·v on packed slot values, straight from the declared packing:
    slot q of u·v continues v from the state u reached."""
    return tuple(
        v[model.block_base[q] + (u[q] >> model.mark_bits[q])]
        | (u[q] & ((1 << model.mark_bits[q]) - 1))
        for q in range(len(u)))


def gt_pi(elem: Elem, model: SlotModel) -> Elem:
    """The unique idempotent among the powers of elem, by explicit orbit
    walk."""
    powers: List[Elem] = [elem]
    nxt = compose(elem, elem, model)
    while nxt not in powers:
        powers.append(nxt)
        nxt = compose(nxt, elem, model)
    idems = [z for z in powers if compose(z, z, model) == z]
    assert len(idems) == 1, (model.name, elem, idems)
    return idems[0]


def check(aut: Input, model: SlotModel) -> None:
    log = LOGS / f"phase2_{model.name}.jsonl"
    eng = Engine(square="off", stats=str(log))
    s = eng.build(aut, until_phase=2)

    assert s.pi_count() == s.em1_count(), (model.name, s.pi_count())
    engine_pi: Dict[Elem, Elem] = {x: y for x, y in s.pi_pairs()}
    elems = [tuple(e) for e in s.elements()]
    assert len(engine_pi) == len(elems), model.name
    for x in elems:
        want = gt_pi(x, model)
        assert engine_pi[x] == want, (model.name, x, engine_pi[x], want)

    phase2 = [r for r in map(json.loads, log.read_text().splitlines())
              if r.get("ev") == "phase" and r.get("phase") == 2]
    assert len(phase2) == 1, (model.name, phase2)
    print(f"{model.name}: |pi|={int(s.pi_count())} "
          f"pi_nodes={s.pi_nodes()} "
          f"pairing_rounds={phase2[0]['pairing_rounds']}")


def case_triptych(name: str) -> None:
    aut = next(a for a, _ in TRIPTYCH if a.name == name)
    check(aut, from_automaton(aut))


def case_mod3() -> None:
    check(MOD3, from_automaton(MOD3))


def case_ebeb() -> None:
    # Factored product: the case split crosses block_base offsets.
    ebeb = eb_product(2)
    check(ebeb, async_factored(ebeb))


def case_refuse() -> None:
    # Deferred square modes are refused loudly, never silently ignored.
    try:
        Engine(square="check").build(TRIPTYCH[0][0], until_phase=2)
        raise AssertionError("square=check was not refused")
    except NotImplementedError:
        pass
    # Phase-2 readings on a phase-1 object must refuse too.
    s1 = Engine().build(TRIPTYCH[0][0], until_phase=1)
    try:
        s1.pi_count()
        raise AssertionError("pi_count on a phase-1 object did not raise")
    except RuntimeError:
        pass


CASES = {
    "gf_aa_parity": lambda: case_triptych("gf_aa_parity"),
    "even": lambda: case_triptych("even"),
    "evenblocks": lambda: case_triptych("evenblocks"),
    "mod3": case_mod3,
    "ebeb": case_ebeb,
    "refuse": case_refuse,
}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    for name in (sys.argv[1:] or CASES):
        CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
