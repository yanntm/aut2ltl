"""§6 calculus moves that live on the digest side and never touch a
diagram. Currently: lasso membership (§6.1) and its building blocks —
word folding through the letter-class maps and the concrete
idempotent-power iteration.

The §6.1 assertion ("Phase 1 never runs on a membership query") is held
structurally: this module never imports the C++ core, so no closure can
run on this code path — the member gate asserts `sos_sdd._core` stays
unloaded.

Scope: single `Automaton` digests (products are refused loudly; the
blockwise generalization arrives with alignment, §6.3). Words are
sequences of cube strings over the digest's APs; a cube must lie within
one letter-behavior class (partial cubes are legal exactly when every
valuation they cover behaves identically)."""

from typing import Dict, List, Sequence, Tuple

from .letters import LetterClass, letter_classes, parse_cube, _meet
from .model import Automaton
from .quotient import compose
from .slotmodel import SlotModel, from_automaton

Word = Sequence[str]
Elem = Tuple[int, ...]


def class_of(cube: str, aut: Automaton, classes: Sequence[LetterClass]) -> int:
    """Index of the letter-behavior class covering `cube`, by cube-cover
    counting; a cube spanning several classes is ambiguous and refused."""
    n_ap = len(aut.ap)
    want = parse_cube(cube, aut.ap)
    size = 1 << (n_ap - len(want))
    for ci, lc in enumerate(classes):
        covered = 0
        for c in lc.cubes:
            m = _meet(want, parse_cube(c, aut.ap))
            if m is not None:
                covered += 1 << (n_ap - len(m))
        if covered == size:
            return ci
        if covered:
            raise ValueError(
                f"{aut.name}: cube {cube!r} spans several letter classes")
    raise AssertionError(f"{aut.name}: classes do not cover {cube!r}")


def fold(word: Word, aut: Automaton, classes: Sequence[LetterClass],
         model: SlotModel) -> Elem:
    """⟦word⟧ as a packed slot vector: the identity pushed through each
    letter's per-slot value map (right multiplication, left to right)."""
    x: Elem = tuple(model.identity)
    for cube in word:
        maps = model.classes[class_of(cube, aut, classes)].maps
        x = tuple(maps[q][x[q]] for q in range(len(x)))
    return x


def idempotent_power(d: Elem, model: SlotModel) -> Elem:
    """d^π by concrete power iteration: walk d, d², … to the orbit's
    first repeat (index i, period p), then the unique idempotent in ⟨d⟩
    is d^m for the least multiple m of p with m ≥ i."""
    seen: Dict[Elem, int] = {d: 1}
    seq: List[Elem] = [d]
    x = d
    while True:
        x = compose(x, d, model)
        if x in seen:
            i, p = seen[x], len(seq) + 1 - seen[x]
            m = p * -(-i // p)
            return seq[m - 1]
        seq.append(x)
        seen[x] = len(seq)


def member(aut: Automaton, u: Word, v: Word) -> bool:
    """u·v^ω ∈ L(aut)? — §6.1, closure-free: fold both words, take the
    loop's idempotent power e = ⟦v⟧^π concretely, and read the verdict
    Val(⟦u⟧, ⟦v⟧) = A(st_⟦u⟧(ι), e). For idempotent e the loop state
    q₁ = st_e(q₀) is a fixpoint, so the inf-mark set is exactly e's
    marks at q₁, evaluated against the grounded acceptance table."""
    if not isinstance(aut, Automaton):
        raise NotImplementedError(
            "membership is defined on single Automaton digests "
            "(the blockwise form arrives with alignment)")
    if not v:
        raise ValueError(f"{aut.name}: empty loop — a lasso needs v ≠ ε")
    classes = letter_classes(aut)
    model = from_automaton(aut)
    c = fold(u, aut, classes, model)
    e = idempotent_power(fold(v, aut, classes, model), model)
    bits = model.mark_bits[aut.init]
    q1 = e[c[aut.init] >> bits] >> bits
    return (e[q1] & ((1 << bits) - 1)) in model.accept[q1]
