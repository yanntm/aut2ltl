"""Does Spot parse `F!a` the same as `F !a`? (whitespace-sensitivity check)

One-shot diagnostic: parse both spellings, print their canonical forms, and
report whether Spot treats them as the same formula.
"""
import spot

for s in ["F!a", "F !a", "G((a & F!a) | (!b R !a))",
          "(a | !b | X!a) & G(((!a & b) | X(a | !b | X!a)) & F((a | !b) & X!a))"]:
    try:
        f = spot.formula(s)
        print(f"OK    {s!r:70}  ->  {f}")
    except Exception as e:  # noqa: BLE001
        print(f"ERROR {s!r:70}  ->  {type(e).__name__}: {e}")

a = spot.formula("F!a")
b = spot.formula("F !a")
print(f"\nF!a == F !a ?  {a == b}   ({a}  vs  {b})")
