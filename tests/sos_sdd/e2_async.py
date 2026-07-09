"""E2 scaffolding: asynchronous scaling on EvenBlocks^{⊗n} in factored
coordinates — |EM1| = 16^n by model count (Proposition 4.1's cardinality),
the isomorphism checked exactly (element sets equal the cartesian product
of component element sets) where enumeration is affordable, and the
diagram-node line recorded (prediction: additive, n × the component's
nodes). Flat coordinates smoke-checked at small n (same counts, the E3
divergence measured later). One stats stream per point in logs/."""

import itertools
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sos_sdd import Automaton, Engine, Product, TimeBudget  # noqa: E402

LOGS = Path(__file__).resolve().parent / "logs"
N_FACTORED = 6
N_FLAT = 3
EXACT_CAP = 70000


def evenblocks(i: int) -> Automaton:
    a = f"a{i}"
    return Automaton(f"eb{i}", (a,), 2, 0, 2, "Fin(0)&Inf(1)", (
        (0, a, 1, set()), (0, f"!{a}", 0, {1}),
        (1, a, 0, set()), (1, f"!{a}", 0, {0})))


def product(n: int) -> Product:
    return Product(f"evenblocks_x{n}",
                   tuple(evenblocks(i) for i in range(n)), "async")


def main() -> None:
    # Optional single-point probe: e2_async.py <n> [flat]
    only_n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    only_flat = len(sys.argv) > 2 and sys.argv[2] == "flat"

    LOGS.mkdir(exist_ok=True)
    base = Engine().build(evenblocks(0), until_phase=1)
    base_nodes, _ = base.nodes
    component_elems = [tuple(e) for e in base.elements()]

    factored_ns = ([only_n] if only_n and not only_flat
                   else [] if only_flat else list(range(1, N_FACTORED + 1)))
    flat_ns = ([only_n] if only_flat
               else [] if only_n else list(range(2, N_FLAT + 1)))

    for n in factored_ns:
        t0 = time.monotonic()
        eng = Engine(stats=str(LOGS / f"e2_factored_{n}.jsonl"))
        s = eng.build(product(n), until_phase=1)
        ms = (time.monotonic() - t0) * 1000
        assert s.em1_count() == float(16 ** n), (n, s.em1_count())
        nodes, _ = s.nodes
        if 16 ** n <= EXACT_CAP:
            got = {tuple(e) for e in s.elements(EXACT_CAP)}
            want = {sum(combo, ())
                    for combo in itertools.product(component_elems, repeat=n)}
            assert got == want, f"Prop 4.1 isomorphism violated at n={n}"
            iso = "exact"
        else:
            iso = "count-only"
        print(f"factored n={n}: |EM1|=16^{n} nodes={nodes} "
              f"(component={base_nodes}) depth={s.depth} iso={iso} "
              f"ms={ms:.0f}")
        # The paper's prediction: additive diagram size. A factored blowup
        # would refute a proved corollary — stop the line (spec §5).
        assert nodes <= n * base_nodes, (n, nodes, base_nodes)

    for n in flat_ns:
        # Flat coordinates carry Lemma 4.2's long-range correlation; n=3
        # already blows a 15s cap on this machine. Explicit per-point
        # budget, exhaustion ledgered as the finding it is (spec §3/§5).
        eng = Engine(coords="flat", time_budget=8.0,
                     stats=str(LOGS / f"e2_flat_{n}.jsonl"))
        try:
            s = eng.build(product(n), until_phase=1)
            assert s.em1_count() == float(16 ** n), (n, s.em1_count())
            nodes, _ = s.nodes
            print(f"flat     n={n}: |EM1|=16^{n} nodes={nodes}")
        except TimeBudget as f:
            k, card, nodes = f.layer_profile[-1]
            print(f"flat     n={n}: TIME_BUDGET finding — reached layer {k} "
                  f"(card={card:.0f}, nodes={nodes}) within 8s")

    print("SUCCESS")


if __name__ == "__main__":
    main()
