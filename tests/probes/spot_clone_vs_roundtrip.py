"""Is `spot.automaton(aut.to_str("hoa"))` a clone?

The idiom appears seven times in this repo where a deep copy is wanted. It is a
serialize/parse round trip, so whatever the HOA text fails to carry is not
copied but *re-inferred by the parser*. This probe contrasts it with Spot's own
clone, `make_twa_graph(aut, twa_prop_set.all())`, on the three things the corpus
depends on: the acceptance reading, the AP order, and the automaton properties.

    python3 tests/probes/spot_clone_vs_roundtrip.py
"""
from __future__ import annotations

import spot


def _props(a: "spot.twa_graph") -> str:
    return (f"state_acc={a.prop_state_acc()} "
            f"det={a.prop_universal()} complete={a.prop_complete()} "
            f"weak={a.prop_inherently_weak()}")


def _aps(a: "spot.twa_graph") -> str:
    return " ".join(str(p) for p in a.ap())


def _case(label: str, src: "spot.twa_graph") -> None:
    rt = spot.automaton(src.to_str("hoa"))                       # the idiom
    cl = spot.make_twa_graph(src, spot.twa_prop_set.all())       # Spot's clone
    default, forced = src.to_str("hoa"), src.to_str("hoa", "t")

    print(f"--- {label} ---")
    print(f"  source     : {_props(src)}  |  AP: {_aps(src)}")
    print(f"  round trip : {_props(rt)}  |  AP: {_aps(rt)}")
    print(f"  clone      : {_props(cl)}  |  AP: {_aps(cl)}")
    print(f"  round trip preserves bytes : {rt.to_str('hoa') == src.to_str('hoa')}")
    print(f"  clone      preserves bytes : {cl.to_str('hoa') == src.to_str('hoa')}")
    print(f'  default declares state-acc  : {"state-acc" in default}')
    print(f'  "t"     declares state-acc  : {"state-acc" in forced}')
    print(f"  default == \"t\"              : {default == forced}")
    print(f"  round trip of default is still transition-based: "
          f"{spot.automaton(default).prop_state_acc()}")
    print()


def main() -> int:
    # 1. What importer.canonical() hands the corpus writers.
    d = spot.translate("GF a & GF b", "generic", "deterministic", "complete")
    d.prop_state_acc(spot.trival_maybe())
    _case("transition-based, prop_state_acc=maybe (importer.canonical)", d)

    # 2. The case Spot "thinks is trivial": a genuinely state-based automaton.
    s = spot.translate("GF a")
    _case("state-based translate (prop_state_acc left alone)", s)

    # 3. A state-based automaton reread as transition-based, the corpus's D.
    s2 = spot.translate("GF a")
    s2.prop_state_acc(spot.trival_maybe())
    _case("same, after prop_state_acc(maybe)", s2)

    # 4. `F a`: terminal, the shape Spot most wants to call state-based.
    f = spot.translate("F a")
    _case("F a, as translated", f)

    f2 = spot.translate("F a", "generic", "deterministic", "complete")
    f2.prop_state_acc(spot.trival_maybe())
    _case("F a through importer.canonical's recipe", f2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
