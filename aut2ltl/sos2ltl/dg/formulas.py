"""The internal `LTL[XU]` AST and the three exact [DG] transformations
(`algorithm.md` layers 2, 5, 7).

The AST is hash-consed in an `Ast` arena: nodes are interned on structure, so
equal builds return equal ids and shared subterms are stored once. Atoms are
*abstract letters* — indices into whatever alphabet the recursion node that
built the formula speaks; nothing here knows automata, algebras, or `AP`s.
The only primitive modality is strict next-until (`φ XU ψ`: at some strictly
later position `ψ`, and `φ` strictly in between); `X`, `U`, `F`-like shapes
are derived. Constructors are literal — no rewriting, no reordering — so the
arena id of a formula is a function of exactly how it was assembled, which is
what makes deterministic assembly a normal form.

The transformations are the paper's, clause for clause:

- `lift(φ, b)` — [DG] Lemma 8.3, `φ^b`: evaluate `φ` on the largest `b`-free
  factor from the current position (current letter exempt);
  `(φ XU ψ)^b = (¬b ∧ φ^b) XU (¬b ∧ ψ^b)`, atoms unchanged, homomorphic else.
- `tilde(ξ, c, sub)` — [DG] Lemma 8.4, `ξ̃`: transport a formula over the
  compressed alphabet to the host alphabet; compressed atoms map through
  `sub` (the caller supplies each atom's block formula, already lifted and
  decorated), and `(ξ₁ XU ξ₂)~ = (¬c ∨ ξ̃₁) U (c ∧ ξ̃₂)`.
- `pe(φ, fresh)` — [DG] Remark 7.1: partial evaluation at the phantom
  position, whose letter is known to be `fresh`; touches only position-0
  subterms: atoms decide, `PE(φ XU ψ) = φ U ψ`, homomorphic else.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

Op = str
_TOP: Op = "top"
_ATOM: Op = "atom"
_NOT: Op = "not"
_OR: Op = "or"
_XU: Op = "xu"


class Ast:
    """A hash-consed arena of `[XU]` formulas; ids are ints, valid within
    one arena. Transformations are memoized on (name, node, parameter)."""

    def __init__(self) -> None:
        self._nodes: List[Tuple] = []
        self._index: Dict[Tuple, int] = {}
        self._memo: Dict[Tuple, int] = {}

    def __len__(self) -> int:
        return len(self._nodes)

    def _mk(self, key: Tuple) -> int:
        i: Optional[int] = self._index.get(key)
        if i is None:
            i = len(self._nodes)
            self._nodes.append(key)
            self._index[key] = i
        return i

    def node(self, i: int) -> Tuple:
        """The structure of node `i`: `(op, ...operands)`."""
        return self._nodes[i]

    # -- the five primitive constructors ---------------------------------
    def top(self) -> int:
        return self._mk((_TOP,))

    def atom(self, a: int) -> int:
        return self._mk((_ATOM, a))

    def neg(self, i: int) -> int:
        return self._mk((_NOT, i))

    def or_(self, i: int, j: int) -> int:
        return self._mk((_OR, i, j))

    def xu(self, i: int, j: int) -> int:
        return self._mk((_XU, i, j))

    # -- derived forms ----------------------------------------------------
    def bot(self) -> int:
        return self.neg(self.top())

    def and_(self, i: int, j: int) -> int:
        return self.neg(self.or_(self.neg(i), self.neg(j)))

    def x(self, i: int) -> int:
        """Next: `X φ = ⊥ XU φ`."""
        return self.xu(self.bot(), i)

    def u(self, i: int, j: int) -> int:
        """Until (non-strict): `φ U ψ = ψ ∨ (φ ∧ (φ XU ψ))`."""
        return self.or_(j, self.and_(i, self.xu(i, j)))

    def xf(self, i: int) -> int:
        """Strictly-later eventually: `⊤ XU φ` — "at some later position"."""
        return self.xu(self.top(), i)

    def f_(self, i: int) -> int:
        """Eventually (non-strict): `F φ = φ ∨ (⊤ XU φ)`."""
        return self.or_(i, self.xf(i))

    def map_atoms(self, i: int, f: Callable[[int], int]) -> int:
        """The formula with every atom `a` renamed to `f(a)` — the embedding
        of a sub-alphabet formula into the parent's letter indices."""
        memo: Dict[int, int] = {}

        def go(j: int) -> int:
            r: Optional[int] = memo.get(j)
            if r is None:
                n = self._nodes[j]
                if n[0] == _TOP:
                    r = j
                elif n[0] == _ATOM:
                    r = self.atom(f(n[1]))
                elif n[0] == _NOT:
                    r = self.neg(go(n[1]))
                elif n[0] == _OR:
                    r = self.or_(go(n[1]), go(n[2]))
                else:
                    r = self.xu(go(n[1]), go(n[2]))
                memo[j] = r
            return r

        return go(i)

    # -- the three transformations ----------------------------------------
    def lift(self, i: int, b: int) -> int:
        """`φ^b` ([DG] 8.3): `φ` read on the largest `b`-free factor
        starting here, the current letter exempt. `b` is an atom index."""
        key = ("lift", i, b)
        r: Optional[int] = self._memo.get(key)
        if r is None:
            n = self._nodes[i]
            if n[0] in (_TOP, _ATOM):
                r = i
            elif n[0] == _NOT:
                r = self.neg(self.lift(n[1], b))
            elif n[0] == _OR:
                r = self.or_(self.lift(n[1], b), self.lift(n[2], b))
            else:
                nb = self.neg(self.atom(b))
                r = self.xu(self.and_(nb, self.lift(n[1], b)),
                            self.and_(nb, self.lift(n[2], b)))
            self._memo[key] = r
        return r

    def tilde(self, i: int, c: int, sub: Callable[[int], int]) -> int:
        """`ξ̃` ([DG] 8.4): compressed positions become the `c`-positions of
        the host word. `c` is a host atom index; `sub` maps each compressed
        atom to its host formula (built by the caller)."""
        memo: Dict[int, int] = {}

        def go(j: int) -> int:
            r: Optional[int] = memo.get(j)
            if r is None:
                n = self._nodes[j]
                if n[0] == _TOP:
                    r = j
                elif n[0] == _ATOM:
                    r = sub(n[1])
                elif n[0] == _NOT:
                    r = self.neg(go(n[1]))
                elif n[0] == _OR:
                    r = self.or_(go(n[1]), go(n[2]))
                else:
                    # [DG] prints a non-strict U here; that admits the anchor
                    # itself (its letter is always c), which strict XU on the
                    # compressed word forbids — XU is required.
                    r = self.xu(self.or_(self.neg(self.atom(c)), go(n[1])),
                                self.and_(self.atom(c), go(n[2])))
                memo[j] = r
            return r

        return go(i)

    def pe(self, i: int, fresh: Optional[int]) -> int:
        """`PE(φ)` ([DG] Remark 7.1): evaluate the position-0 subterms at the
        phantom position, whose letter is `fresh` (`None`: no atom matches).
        `XU` operands speak of real positions and pass through untouched."""
        key = ("pe", i, fresh)
        r: Optional[int] = self._memo.get(key)
        if r is None:
            n = self._nodes[i]
            if n[0] == _TOP:
                r = i
            elif n[0] == _ATOM:
                r = self.top() if n[1] == fresh else self.bot()
            elif n[0] == _NOT:
                r = self.neg(self.pe(n[1], fresh))
            elif n[0] == _OR:
                r = self.or_(self.pe(n[1], fresh), self.pe(n[2], fresh))
            else:
                r = self.u(n[1], n[2])
            self._memo[key] = r
        return r

    # -- rendering ---------------------------------------------------------
    def tree_size(self, i: int) -> int:
        """The node count of the unshared tree of `i` — the flat size the
        DAG avoids, computed without materializing it."""
        memo: Dict[int, int] = {}

        def go(j: int) -> int:
            r: Optional[int] = memo.get(j)
            if r is None:
                n = self._nodes[j]
                r = 1 + sum(go(k) for k in n[1:] if n[0] not in (_ATOM,))
                memo[j] = r
            return r

        return go(i)

    def to_spot(self, i: int, letters: Sequence[str]) -> str:
        """Spot-syntax string of node `i`; `letters[a]` is the cube of atom
        `a` (e.g. `'!a & b'`). `XU` renders as `X(· U ·)`. For display and
        the step-5 equivalence probes; the host-DAG render lands with the
        assembly."""
        memo: Dict[int, str] = {}

        def go(j: int) -> str:
            r: Optional[str] = memo.get(j)
            if r is None:
                n = self._nodes[j]
                if n[0] == _TOP:
                    r = "1"
                elif n[0] == _ATOM:
                    r = f"({letters[n[1]]})"
                elif n[0] == _NOT:
                    r = f"!{go(n[1])}"
                elif n[0] == _OR:
                    r = f"({go(n[1])} | {go(n[2])})"
                else:
                    r = f"X({go(n[1])} U {go(n[2])})"
                memo[j] = r
            return r

        return go(i)


__all__ = ["Ast"]
