"""One-off: the fast base-G decoder combo_of must equal the reference combo_at."""
import os
import sys

GEN = "/home/ythierry/git/BuchiToLTL/genaut/gen"
sys.path.insert(0, GEN)
from shape import Shape          # noqa: E402
from sample import combo_of      # noqa: E402

shape = Shape(2, 1, 1)           # N = 65536
bad = 0
for i in range(0, 2000):
    if combo_of(shape, i) != shape.combo_at(i):
        bad += 1
        if bad <= 5:
            print(f"  mismatch at {i}: {combo_of(shape,i)} != {shape.combo_at(i)}")
# and a few large ids (combo_at is O(index), so keep them modest)
for i in (65535, 40000, 12345):
    if combo_of(shape, i) != shape.combo_at(i):
        bad += 1
        print(f"  mismatch at {i}")
print("DECODE OK" if bad == 0 else f"DECODE FAIL ({bad})")
sys.exit(1 if bad else 0)
