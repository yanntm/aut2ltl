"""FIG-1 — the worked read-off, end to end, on F-E (paper §4.1).

    python3 -m tests.quant.figs.fig1 SRC.sos [OUT.tex]

The whole §4.1 algorithm in one picture on the paper's own example
("``b`` occurs and the first ``b`` is at an even position"): the five
classes of the invariant, the transient SCC ``{A0, A1}`` boxed, the two
bottom SCCs ``{F0}``, ``{F1}`` double-circled, the kernel (spanning both)
thick-bordered, each bottom SCC's θ badge, every class's x-value at
uniform ``p``, and the result line ``μ = x_[ε]``. Called without an output
path it prints the tuple the drawing consumes.
"""
from __future__ import annotations

import sys

from sosl.sos import load_invariant
from sosl.quant import bottom_sccs, kernel, measure, theta_profile, value_vector

from tests.quant.figs import cayley, tikz

# ids of the canonical F-E: 0=[eps] 1=[!a]=F0 2=[a]=A1 3=[a;!a]=F1 4=[a;a]=A0
LAYOUT = cayley.Layout(
    pos={0: (0.0, 3.4), 2: (-1.7, 1.5), 4: (1.7, 1.5),
         3: (-3.1, -0.9), 1: (3.1, -0.9)},
    loop_at={1: "right", 3: "left"},
    bend={(2, 4): 16, (4, 2): 16, (0, 1): 40},
    theta_at={1: "north east", 3: "north west"},
    x_at={0: "north", 2: "west", 4: "north", 1: "south", 3: "south"},
    scale=1.0,
)


def draw(src: str) -> str:
    inv = load_invariant(open(src).read())
    body = cayley.render(inv, LAYOUT)
    mu = measure(inv).value
    body.append(
        rf"  \node[result] at (0,-2.7) "
        rf"{{$\mu_p(L) \;=\; x_{{[\varepsilon]}} \;=\; {tikz.frac_tex(mu)}$}};")
    return tikz.standalone(body)


def report(src: str) -> None:
    inv = load_invariant(open(src).read())
    x = value_vector(inv)
    print(f"F-E: {inv.n} classes, keys {[' '.join(str(m) for m in k) or 'eps' for k in inv.keys]}")
    print(f"  bottom SCCs {[sorted(s) for s in bottom_sccs(inv)]}, "
          f"kernel {sorted(kernel(inv))}")
    print(f"  theta {theta_profile(inv).entries}")
    print(f"  x-vector {[str(v) for v in x]}")
    print(f"  mu = {measure(inv).value}")


def main() -> None:
    src = sys.argv[1]
    if len(sys.argv) > 2:
        open(sys.argv[2], "w").write(draw(src))
        print(f"wrote {sys.argv[2]}")
    else:
        report(src)


if __name__ == "__main__":
    main()
