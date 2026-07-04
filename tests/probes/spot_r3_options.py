"""Pin the tl_simplifier_options that actually equals `ltlfilt -r3`.

The CLI `ltlfilt -r3` drops a leading X on this formula, cold; a naive positional
options tuple did not. Inspect the fields each positional constructor sets and find
the combo that reproduces the CLI's cold drop — no prior translate, fresh instance.
"""
import spot

_F = "X(GF!b & F((!b & X(!b & XG(!b | X!c))) | (b & X(!c & G(!b | X!c)))))"
_f = spot.formula(_F)


def show(label: str, opts: "spot.tl_simplifier_options") -> None:
    out = spot.tl_simplifier(opts).simplify(_f)
    dropped = not str(out).startswith("X")
    print(f"{label:16} basics={int(opts.reduce_basics)} synt_impl={int(opts.synt_impl)} "
          f"event_univ={int(opts.event_univ)} contain={int(opts.containment_checks)} "
          f"contain_str={int(opts.containment_checks_stronger)} "
          f"-> {'DROPPED' if dropped else 'kept'}")


show("default()", spot.tl_simplifier_options())
show("(T,T,T)", spot.tl_simplifier_options(True, True, True))
show("(T,T,T,T)", spot.tl_simplifier_options(True, True, True, True))
show("(T,T,T,T,T)", spot.tl_simplifier_options(True, True, True, True, True))
