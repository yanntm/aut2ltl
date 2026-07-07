"""Rendering verdicts as replayable witnesses over the class keys.

Every non-trivial verdict ships a certificate expressed in lassos over class
keys, so it replays against any presentation of the language by plain
membership queries (spec section 1). This module renders the chain, superchain,
and group witnesses into JSON-friendly dicts and the lassos that carry them:

  - a chain ``(s; e_0, ..., e_m)`` becomes the ``m+1`` lassos
    ``key(s) . key(e_i)^omega`` with expected acceptance bits ``(s, e_i) in P``
    (each already decided by ``Invariant.member`` on the same invariant — a free
    self-check);
  - a superchain adds the connecting words ``u_i``: shortlex-shortest words with
    ``s_{i-1} . u_i = s_i``, found by BFS in the right Cayley graph;
  - a group carrier ships its key, index, period, and power cycle.

Normative math: `research_notes/sos_classification.md` sections 4-6.
"""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional

from ..alphabet import EMPTY, Word
from ..invariant import Invariant
from ..io.serialize import render_word
from ..lasso import Lasso
from .aperiodic import Orbit
from .chains import Chain
from .superchains import Superchain


def class_key(inv: Invariant, c: int) -> str:
    """The rendered shortlex-least key word of class ``c``."""
    return render_word(inv.alphabet, inv.keys[c])


def connecting_word(inv: Invariant, s_from: int, s_to: int) -> Optional[Word]:
    """A shortest non-empty word ``u`` with ``s_from . u = s_to`` (i.e.
    ``s_to <=_R s_from``), by BFS in the right Cayley graph over letter
    generators; ``None`` if ``s_to`` is unreachable to the right of ``s_from``."""
    mult, lc = inv.mult, inv.letter_class
    prev: Dict[int, tuple] = {s_from: (None, None)}
    q = deque([s_from])
    while q:
        cur = q.popleft()
        for a, gen in enumerate(lc):
            nxt = mult[cur][gen]
            if nxt not in prev:
                prev[nxt] = (cur, a)
                if nxt == s_to:
                    letters: List[int] = []
                    node = nxt
                    while prev[node][0] is not None:
                        node, a = prev[node]
                        letters.append(a)
                    return tuple(reversed(letters))
                q.append(nxt)
    return None  # s_to unreachable to the right of s_from


def chain_lassos(inv: Invariant, ch: Chain) -> List[Lasso]:
    """The ``m+1`` replay lassos ``key(stem) . key(e_i)^omega`` of a chain."""
    return [Lasso(inv.keys[ch.stem] or EMPTY, inv.keys[e]) for e in ch.idems]


def chain_witness(inv: Invariant, ch: Chain) -> Dict:
    lassos = chain_lassos(inv, ch)
    return {
        "stem": class_key(inv, ch.stem),
        "idems": [class_key(inv, e) for e in ch.idems],
        "positive": ch.positive,
        "length": ch.length,
        "lassos": [
            {"stem": render_word(inv.alphabet, la.stem),
             "loop": render_word(inv.alphabet, la.loop),
             "expect": bit}
            for la, bit in zip(lassos, ch.bits)
        ],
    }


def superchain_witness(inv: Invariant, sc: Superchain) -> Dict:
    connect = []
    for a, b in zip(sc.stems, sc.stems[1:]):
        u = connecting_word(inv, a, b)
        connect.append(render_word(inv.alphabet, u) if u is not None else None)
    return {
        "stems": [class_key(inv, s) for s in sc.stems],
        "signs": ["+" if s else "-" for s in sc.signs],
        "length": sc.length,
        "connect": connect,
    }


def group_witness(inv: Invariant, orbit: Orbit) -> Dict:
    return {
        "class": class_key(inv, orbit.cls),
        "index": orbit.index,
        "period": orbit.period,
        "cycle": [class_key(inv, c) for c in orbit.cycle],
    }
