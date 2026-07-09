"""Engine façade: the switch configuration resolved and validated on the
Python side, then forwarded to the C++ extension (`sos_sdd._core`) as one
coarse-grained call — no per-node traffic ever crosses the binding. The
extension import is lazy so the pure-Python layer (digests, errors,
contract) stands without a built extension."""

from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, Literal, Optional, Sequence, Union

from .contract import SoS
from .letters import letter_classes
from .model import Automaton, Input, Product

Discipline = Literal["layered", "chaining", "saturation"]
StatsSink = Union[None, str, Callable[[Dict[str, Any]], None]]


@dataclass
class Engine:
    """One resolved configuration; every experiment switch is a field here,
    never a code fork. `stats` is a JSONL file path or a per-record
    callable; the first record echoes the resolved configuration."""

    # slot-space encoding
    coords: Literal["factored", "flat"] = "factored"
    slot_perm: Union[Literal["natural", "reverse"], Sequence[int]] = "natural"
    slot_encoding: Literal["packed", "split-sm", "split-il"] = "packed"
    alpha: Literal["top", "bottom"] = "top"
    # fixpoint disciplines (closure / congruence refinement)
    fp1: Discipline = "layered"
    fp5: Discipline = "layered"
    # guards and fallbacks
    square: Literal["check", "on", "off"] = "check"
    quotient: Literal["explicit", "symbolic"] = "explicit"
    # budgets (0 = unlimited); exhaustion raises a Finding, not an error
    node_budget: int = 0
    time_budget: float = 0.0
    stats: StatsSink = None

    def build(self, aut: Input, until_phase: int = 6) -> SoS:
        """Run phases 0..until_phase on a digested input and return the
        (possibly partial) invariant object. The digest is reduced to a
        numeric payload here (letter-class refinement — C2's symbolic
        half never sees guard syntax)."""
        aut.validate()
        if not (1 <= until_phase <= 6):
            raise ValueError(f"until_phase {until_phase} out of range 1..6")
        if isinstance(aut, Product):
            raise NotImplementedError("Product inputs arrive with the scaling families")
        return _core().build(_payload(aut), self._config(), until_phase)

    def _config(self) -> Dict[str, Any]:
        cfg = asdict(self)
        cfg["stats"] = self.stats  # keep the callable; asdict deep-copies
        return cfg


def _payload(aut: Automaton) -> Dict[str, Any]:
    """Numeric digest crossing the binding: states, marks, and the sorted
    letter-behavior classes — no guard syntax reaches the C++ side."""
    return {
        "name": aut.name,
        "n_states": aut.states,
        "n_marks": aut.marks,
        "init": aut.init,
        "classes": [
            {"least": c.least, "count": c.count,
             "dst": list(c.dst), "marks": list(c.marks)}
            for c in letter_classes(aut)
        ],
    }


def align(s: SoS, t: SoS) -> SoS:
    """Explicit alignment of two invariants onto one shared table (one
    closure, priced in the stats stream). Boolean operators call this
    implicitly when their operands' tables differ."""
    return _core().align(s, t)


def _core() -> Any:
    try:
        from . import _core as core  # type: ignore[attr-defined]
    except ImportError as exc:
        raise RuntimeError(
            "sos_sdd._core extension not built — run `make` in sos_sdd/ "
            "(needs LIBDDD_HOME and pybind11)"
        ) from exc
    return core
