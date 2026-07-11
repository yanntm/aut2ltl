"""Phase 6 — quotient and exports: the explicit invariant table assembled
from the engine's Phase 1-5 readings, and its canonical `.sos` text.

This is the `quotient="explicit"` route (the recorded small-side
fallback). The identity convention is the normative one of the reference
construction (`sosl.sos.core.quotient`): word classes are the ~-classes
of the elements that are images of NON-EMPTY words — the identity
element included exactly when some non-empty word folds onto it (e.g.
`!a` in a one-state component of GF a) — and `[eps]` is a fresh class no
word can collide with, a two-sided unit on every class. Multiplication
folds packed representative values (never `Comp`); accepting linked
pairs are saturated by enumeration, each verdict read off the engine's
Phase 3 profile rows at the initial state.

Canonical keying mirrors `sosl.sos.core.canonical.shortlex_bfs`: ids and
keys come from a BFS over the small quotient algebra itself
(`step(c, a) = mult[c][letter_class[a]]` from `[eps]`, letters in mask
order) — the first word reaching a class is its shortlex-least key. The
serialized layout mirrors `sosl/sosl/sos/io/serialize.py` line for line
(core sections only; the optional residuals trailer does not participate
in language identity).

Scope: single `Automaton` digests with canonically ordered APs (sorted
by name — the `.sos` spine); anything else is refused loudly."""

from typing import Any, Dict, List, Tuple

from .letters import letter_classes, parse_cube
from .model import Automaton
from .slotmodel import SlotModel

Elem = Tuple[int, ...]
Bits = Tuple[int, ...]


def compose(u: Elem, v: Elem, model: SlotModel) -> Elem:
    """u·v on packed slot values, from the declared packing: slot q of
    u·v continues v from the state u reached, keeping u's marks."""
    return tuple(
        v[model.block_base[q] + (u[q] >> model.mark_bits[q])]
        | (u[q] & ((1 << model.mark_bits[q]) - 1))
        for q in range(len(u)))


def _mask_bits(mask: int, k: int) -> Bits:
    """Letter rank -> characteristic tuple (ap 0 on the most significant
    bit — the canonical letter order of sos_format.md)."""
    return tuple((mask >> (k - 1 - i)) & 1 for i in range(k))


def _render_letter(bits: Bits, ap: Tuple[str, ...]) -> str:
    return "&".join(n if b else f"!{n}" for n, b in zip(ap, bits)) if ap else "t"


class QuotientSoS:
    """The Phase 6 object: delegates every core reading to the C++ `SoS`
    and adds the assembled table + `to_sos()`. Built lazily — the table
    is paid once, on the first Phase 6 reading."""

    def __init__(self, core: Any, aut: Automaton, model: SlotModel) -> None:
        if aut.ap != tuple(sorted(aut.ap)):
            raise NotImplementedError(
                f"{aut.name}: APs must be canonically ordered for .sos "
                f"emission (got {aut.ap})")
        self._core = core
        self._aut = aut
        self._model = model
        self._table: Dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:
        return getattr(self._core, name)

    # -- the table -------------------------------------------------------

    def _assemble(self) -> Dict[str, Any]:
        if self._table:
            return self._table
        aut, model, core = self._aut, self._model, self._core
        n_ap = len(aut.ap)
        identity: Elem = tuple(model.identity)

        # Element -> ~-class block, from Phase 5.
        block_of: Dict[Elem, int] = {}
        for b, cls in enumerate(core.congruence_classes()):
            for e in cls:
                block_of[tuple(e)] = b

        # Letter elements, one per behavior class (images of 1-letter words).
        lelems: List[Elem] = [
            tuple(sc.maps[q][model.identity[q]] for q in range(len(model.doms)))
            for sc in model.classes]

        # Word elements: everything but the identity element, plus the
        # identity itself when some non-empty word folds onto it (it is
        # then a right-translate of some element by some letter class).
        elems: List[Elem] = [tuple(e) for e in core.elements()]
        word_elems: List[Elem] = [e for e in elems if e != identity]
        if any(tuple(sc.maps[q][e[q]] for q in range(len(e))) == identity
               for e in elems for sc in model.classes):
            word_elems.append(identity)

        # Word classes: the ~-classes among word elements, any raw ids —
        # the shortlex BFS below renumbers. Fresh identity gets id k.
        rep_of: Dict[int, Elem] = {}
        for e in word_elems:
            rep_of.setdefault(block_of[e], e)
        wc: Dict[int, int] = {b: i for i, b in enumerate(rep_of)}
        reps: List[Elem] = list(rep_of.values())
        k = len(reps)

        mult: List[List[int]] = [[0] * (k + 1) for _ in range(k + 1)]
        for i, ri in enumerate(reps):
            for j, rj in enumerate(reps):
                mult[i][j] = wc[block_of[compose(ri, rj, model)]]
            mult[i][k] = i  # fresh eps is a two-sided unit on every
            mult[k][i] = i  # class, yet a distinct class itself
        mult[k][k] = k

        # Letter mask -> word class of its one-letter word, via the
        # behavior class covering the mask's valuation.
        cubes = [[parse_cube(c, aut.ap) for c in lc.cubes]
                 for lc in letter_classes(aut)]
        letter_class: List[int] = []
        for mask in range(1 << n_ap):
            bits = _mask_bits(mask, n_ap)
            ci = next(i for i, cs in enumerate(cubes)
                      if any(all(bits[a] == int(v) for a, v in c.items())
                             for c in cs))
            letter_class.append(wc[block_of[lelems[ci]]])

        # Saturated accepting linked pairs over the word classes: (s, e)
        # with e idempotent and s·e = s, verdict A(st_{x_s}(iota), x_e)
        # off the profile rows. The fresh class never links (eps·e = e).
        prof: Dict[Elem, Tuple[int, ...]] = {
            tuple(x): tuple(b) for x, b in core.profile_rows()}
        init = aut.init  # single block: global state = state index
        accept: List[Tuple[int, int]] = []
        for e in range(k):
            if mult[e][e] != e:
                continue
            for s in range(k):
                if mult[s][e] != s:
                    continue
                q = reps[s][init] >> model.mark_bits[init]
                if prof[reps[e]][q]:
                    accept.append((s, e))

        # Canonical re-keying: BFS over the algebra from the fresh
        # identity, letters in mask order — discovery order is shortlex
        # order on the keys (mirrors sosl.sos.core.canonical).
        keys: Dict[int, Tuple[int, ...]] = {k: ()}
        order: List[int] = [k]
        i = 0
        while i < len(order):
            c = order[i]
            i += 1
            for a in range(1 << n_ap):
                d = mult[c][letter_class[a]]
                if d not in keys:
                    keys[d] = keys[c] + (a,)
                    order.append(d)
        assert len(order) == k + 1, f"{aut.name}: classes unreachable from eps"
        new_id = {c: i for i, c in enumerate(order)}

        self._table = {
            "keys": [keys[c] for c in order],
            "letter_class": [new_id[letter_class[a]]
                             for a in range(1 << n_ap)],
            "mult": [[new_id[mult[c][d]] for d in order] for c in order],
            "accept": sorted((new_id[s], new_id[e]) for s, e in accept),
        }
        return self._table

    # -- readings ----------------------------------------------------------

    def n_classes(self) -> int:
        return len(self._assemble()["keys"])

    def to_sos(self) -> str:
        """The canonical `.sos` core text — the byte-level layout of the
        reference serializer (`sosl.sos.io.serialize.dump_invariant`)."""
        t = self._assemble()
        ap = self._aut.ap
        n_ap = len(ap)
        out: List[str] = ["SOS v1", "ap: " + " ".join(ap),
                          f"classes: {len(t['keys'])}"]
        for cid, word in enumerate(t["keys"]):
            text = ";".join(_render_letter(_mask_bits(a, n_ap), ap)
                            for a in word) or "eps"
            out.append(f"{cid} {text}")
        out.append("letters: " + " ".join(
            f"{_render_letter(_mask_bits(m, n_ap), ap)}->{c}"
            for m, c in enumerate(t["letter_class"])))
        out.append("mult:")
        for cid, row in enumerate(t["mult"]):
            out.append(f"{cid}: " + " ".join(str(v) for v in row))
        out.append("accept:")
        for s, e in t["accept"]:
            out.append(f"{s} {e}")
        return "\n".join(out) + "\n"
