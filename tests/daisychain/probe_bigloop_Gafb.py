"""Brainstorm probe: does the big-self-loop daisy design reproduce G(a|Fb) cleanly?

Checks the hand-derived chain for the 0<->1 SCC:
  detour folded by sl        -> (!b U b)
  generalized STAY at hub 0  -> G( (a|b) | (!a & !b & (!b U b)) )
  target (the input)         -> G(a | Fb)
all three "stay" forms should be language-equivalent.

It also separates "move-start" from "in-move": the corridor obligation (!b U b)
is the residual of the detour body; dropping the entry guard (!a & !b) should
NOT change the language, confirming that what G iterates is "currently inside a
valid stay-move", not "a move starts at this position".
"""
import spot

def equiv(x: str, y: str) -> bool:
    fx, fy = spot.formula(x), spot.formula(y)
    return spot.are_equivalent(fx, fy)

target   = "G(a | Fb)"
detour   = "!b U b"                                  # sl on the detour sub-aut
recon    = f"G( (a|b) | (!a & !b & ({detour})) )"    # move-start: entry & body
inmove   = f"G( (a|b) | ({detour}) )"                # in-move: residual only

print("detour folds to Fb     :", equiv(detour, "Fb"))
print("recon  == target       :", equiv(recon, target))
print("inmove == target       :", equiv(inmove, target))
print("inmove == recon        :", equiv(inmove, recon))
print("recon                  :", spot.formula(recon))
print("recon simplified       :", spot.simplify(spot.formula(recon)))
