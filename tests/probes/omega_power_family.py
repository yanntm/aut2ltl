#!/usr/bin/env python3
"""
tests/probes/omega_power_family.py <file.hoa> [max_n]

Membership patterns separating the two non-LTL witness family shapes, on one
automaton over AP {a}:

  omega-power family   (a^n !a)^w     -- the period rides INSIDE the lasso cycle
  linear family        a^n (!a)^w     -- the period sits in the finite prefix

Prints one 0/1 membership line per shape for n = 0..max_n (default 6). On a
prefix-independent language the linear line is constant for EVERY choice of
(u, v, x) -- the linear witness shape is blind there -- while a genuine modular
count still toggles the omega-power line.
"""
import sys
from typing import Callable, List

import spot


def member(aut: "spot.twa_graph", word: str) -> bool:
    """Whether the ultimately-periodic word (Spot word syntax) is in L(aut)."""
    w = spot.parse_word(word, aut.get_dict())
    return not spot.product(aut, w.as_automaton()).is_empty()


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    aut = spot.automaton(argv[1])
    max_n = int(argv[2]) if len(argv) > 2 else 6
    shapes: List[tuple] = [
        ("omega-power (a^n !a)^w",
         lambda n: "cycle{" + "; ".join(["a"] * n + ["!a"]) + "}"),
        ("linear      a^n (!a)^w",
         lambda n: "; ".join(["a"] * n) + ("; " if n else "") + "cycle{!a}"),
    ]
    name: str
    shape: Callable[[int], str]
    for name, shape in shapes:
        pat = "".join("1" if member(aut, shape(n)) else "0" for n in range(max_n + 1))
        print(f"{name}: n=0..{max_n} pattern={pat}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
