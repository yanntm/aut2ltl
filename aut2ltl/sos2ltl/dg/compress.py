"""One visible-pivot node's data: the compression tables (`algorithm.md`
layers 4–6). Pure tables — no formula is produced here.

Given a frame `(Δ, h, T)`, a target, and a visible pivot `c`, this module
materializes everything the assembly reads:

- the sub-alphabet `A = Δ ∖ {c}` and its frame `fa` (same monoid, fewer
  letters) — `fa.gen = h(A⁺)`, `fa`'s ω-classes are the ω-letters of `T₂`;
- the local divisor `T'` at `m = h(c)` and the compressed alphabet
  `T₁ ⊎ T₂` with its `g`-images (`T₁`-letter `n ↦ m·n·m`, every `T₂`-letter
  to the neutral `m`) — and its frame `fc`, the monoid-induction child;
- the `X_{n,m}` tables: `X[n][m] = {x ∈ T' | Accept(n·x, m)}`, where
  `Accept` is a fiber test of the target for the finite tail letters
  (`[ε]`: `n·x ∈ fin`; fiber `f`: `n·x·f ∈ fin`) and a pair-class lookup
  for the ω ones (`(n·x·s, e)` classified in the parent frame, membership
  in `target.om`);
- `K₀`: the `T₂`-letters wholly inside the target (ε flag, fiber set,
  ω-letter set);
- `K₂`: per leading block `n`, the set of `fc` ω-classes whose `T₁^ω`-words
  denote target words. Every query is one level of table arithmetic: a
  class is rendered as `T₁`-letter words for its least pair (the BFS reps
  of the `T₁`-only frame `fk`), the denoted prefix value `n·g(w₁)` and
  cycle value `h(z) = n₁·m·⋯·n_j·m` are folded in the parent monoid, the
  cycle value is raised to its idempotent power (aperiodicity), and the
  resulting parent pair is classified — no block is ever rendered as a
  word of the original alphabet.

Conjugacy over the child's full letter set and over its `T₁`-letters agree
(`T₂`-images are the neutral element, so both generate the same `S¹`), which
is why `fk` classes inject into `fc` classes — `K₂` is reported in `fc` ids,
the universe the child target speaks.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, List, Tuple, Union

from aut2ltl.sos2ltl.dg.divisor import Divisor, local_divisor
from aut2ltl.sos2ltl.dg.frame import Frame, Pair, Target, Word, make_frame

T2Letter = Union[Tuple[str], Tuple[str, int]]
"""A tail letter of the compressed alphabet: `("eps",)`, `("fib", element)`,
or `("om", fa-class id)`."""


@dataclass(eq=False)
class NodeData:
    """The tables of one visible-pivot node. Treat as immutable."""

    frame: Frame                    # the node's own frame (Δ, h, T)
    target: Target                  # the node's target, over `frame`
    c: int                          # the pivot letter (index in frame)
    m: int                          # h(c) ≠ unit
    A: Tuple[int, ...]              # sub-alphabet, as frame letter indices
    fa: Frame                       # (A, h|A, T) — alphabet-induction child
    div: Divisor                    # T', the local divisor at m
    t1: Tuple[int, ...]             # T₁ = h(A*), ascending element ids
    t2: Tuple[T2Letter, ...]        # tail letters: eps, fibers, ω-classes
    g_img: Tuple[int, ...]          # child letter -> T' position (t1 then t2)
    fc: Frame                       # (T₁⊎T₂, g, T') — monoid-induction child
    k0_eps: bool                    # [ε] ∈ target
    k0_fib: FrozenSet[int]          # fibers of fa.gen wholly in target
    k0_om: FrozenSet[int]           # fa ω-class ids wholly in target
    x: Tuple[Tuple[FrozenSet[int], ...], ...]   # X[t1 idx][t2 idx] ⊆ T' positions
    k2: Tuple[FrozenSet[int], ...]  # per t1 idx: fc ω-class ids in target


def _idem_power(mult: Tuple[Tuple[int, ...], ...], t: int) -> int:
    """The stabilized power of `t`: aperiodicity makes `t^{i+1} = t^i`
    eventually; the fixpoint is the unique idempotent power."""
    cur: int = t
    for _ in range(len(mult) + 1):
        nxt: int = mult[cur][t]
        if nxt == cur:
            return cur
        cur = nxt
    raise AssertionError("power sequence does not stabilize: not aperiodic")


def compress(frame: Frame, target: Target, c: int) -> NodeData:
    """Compress one node at pivot `c` (must be visible: `h(c) ≠ unit`)."""
    mult = frame.mult
    m: int = frame.images[c]
    assert m != frame.unit, "the pivot must be a visible letter"

    A: Tuple[int, ...] = tuple(li for li in range(len(frame.images)) if li != c)
    fa: Frame = make_frame([frame.images[li] for li in A], mult, frame.unit)
    div: Divisor = local_divisor(mult, m, frame.unit)
    pos = {el: i for i, el in enumerate(div.carrier)}

    t1: Tuple[int, ...] = tuple(sorted(set(fa.gen) | {frame.unit}))
    t2: Tuple[T2Letter, ...] = ((("eps",),)
                                + tuple(("fib", f) for f in fa.gen)
                                + tuple(("om", i) for i in range(len(fa.omega))))
    g_img: Tuple[int, ...] = (tuple(pos[mult[mult[m][n]][m]] for n in t1)
                              + tuple(div.unit for _ in t2))
    fc: Frame = make_frame(g_img, div.mult, div.unit)

    def omega_in_target(fr_pair: Pair) -> bool:
        """Whether the ω-words of the parent-frame pair lie in the target."""
        cid = frame.pair_cls.get(fr_pair)
        assert cid is not None, "pair escaped the parent's ω-universe"
        return cid in target.om

    def accept(nx: int, tl: T2Letter) -> bool:
        """Membership of the word with prefix value `nx` and tail `tl`."""
        if tl[0] == "eps":
            return nx in target.fin
        if tl[0] == "fib":
            return mult[nx][tl[1]] in target.fin
        s, e = fa.omega[tl[1]][0]
        return omega_in_target((mult[nx][s], e))

    # x ranges over the realizable middles g(T₁*) = ⟨g(T₁)⟩ ∪ {m}, not all
    # of T': an unrealizable x denotes no word, and its Accept pair need not
    # be letter-generated — the query would escape the node's ω-universe.
    fk: Frame = make_frame(g_img[:len(t1)], div.mult, div.unit)
    xs: Tuple[int, ...] = tuple(sorted(set(fk.gen) | {div.unit}))
    x: Tuple[Tuple[FrozenSet[int], ...], ...] = tuple(
        tuple(frozenset(xp for xp in xs
                        if accept(mult[n][div.carrier[xp]], tl))
              for tl in t2)
        for n in t1)

    k0_fib: FrozenSet[int] = frozenset(f for f in fa.gen if f in target.fin)
    k0_om: FrozenSet[int] = frozenset(
        i for i in range(len(fa.omega)) if omega_in_target(fa.omega[i][0]))

    # K₂: classify each T₁^ω ω-class (the T₁-only frame fk) by rendering its
    # least pair one level up. w₁, w₂ are T₁-letter words; the denoted word's
    # parent pair is (n·g(w₁)·e_T, e_T) with h(z) = n₁·m·⋯·n_j·m, e_T = h(z)^!.
    k2_sets: List[FrozenSet[int]] = []
    for n in t1:
        keep: List[int] = []
        for members in fk.omega:
            s_, e_ = members[0]
            w2: Word = fk.rep[e_]
            hz: int = frame.unit
            for li in w2:
                hz = mult[mult[hz][t1[li]]][m]
            e_t: int = _idem_power(mult, hz)
            s_t: int = mult[mult[n][div.carrier[s_]]][e_t]
            if omega_in_target((s_t, e_t)):
                keep.append(fc.pair_cls[(s_, e_)])
        k2_sets.append(frozenset(keep))

    return NodeData(frame=frame, target=target, c=c, m=m, A=A, fa=fa, div=div,
                    t1=t1, t2=t2, g_img=g_img, fc=fc,
                    k0_eps=target.eps, k0_fib=k0_fib, k0_om=k0_om,
                    x=x, k2=tuple(k2_sets))


__all__ = ["T2Letter", "NodeData", "compress"]
