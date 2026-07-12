"""State-labelled Markov chains and their ``.mc`` text form.

A `Chain` is a finite discrete-time Markov chain whose states carry one
letter each (Moore): ``label[q]`` is the letter observed *at* ``q``, so the
word of a run ``q0 q1 q2 ...`` is ``label[q0] label[q1] label[q2] ...`` —
the initial state's letter IS the word's first letter, as in PRISM/Storm
path semantics.

``.mc`` is a restricted subset of the PRISM language: one ``dtmc``, one
module, one state variable, exactly one guarded command per state, and one
``label`` per letter of the alphabet, the labels partitioning the states.
Probabilities are rational literals (``1``, ``1/3``) and are read as exact
`fractions.Fraction`. The reader is strict: it validates the subset and
raises `ValueError` on anything else — it never repairs, never guesses, and
never accepts a file whose label names are not exactly the letters of the
alphabet it is given.

Letters are named by their canonical cube rendering (`sos.io.render_letter`:
``a``, ``!a``, ``a&!b``), which is what makes alphabet equality with a paired
`.sos` checkable rather than assumed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Dict, List, Tuple

from ..sos.alphabet import Alphabet, Letter
from ..sos.io.serialize import parse_letter, render_letter

_VAR_RE = re.compile(r"^(\w+)\s*:\s*\[\s*0\s*\.\.\s*(\d+)\s*\]\s*init\s+(\d+)\s*;$")
_CMD_RE = re.compile(r"^\[\s*\]\s*(\w+)\s*=\s*(\d+)\s*->\s*(.+?)\s*;$")
_BRANCH_RE = re.compile(r"^(\d+)(?:\s*/\s*(\d+))?\s*:\s*\(\s*(\w+)'\s*=\s*(\d+)\s*\)$")
_LABEL_RE = re.compile(r'^label\s+"([^"]*)"\s*=\s*(.+?)\s*;$')
_DISJUNCT_RE = re.compile(r"^(\w+)\s*=\s*(\d+)$")


@dataclass(frozen=True)
class Chain:
    """A state-labelled DTMC over ``alphabet``: states are ``0..n-1``,
    ``label[q]`` is the letter of state ``q``, ``trans[q]`` its outgoing
    branches ``((target, probability), ...)`` (all probabilities strictly
    positive, summing to exactly 1), and ``init`` the single initial state."""

    alphabet: Alphabet
    label: Tuple[Letter, ...]
    trans: Tuple[Tuple[Tuple[int, Fraction], ...], ...]
    init: int

    @property
    def n(self) -> int:
        """The number of states."""
        return len(self.label)

    def with_init(self, q: int) -> "Chain":
        """The same chain started at state ``q`` (no file rewriting)."""
        assert 0 <= q < self.n, q
        return replace(self, init=q)

    def validate(self) -> None:
        """Assert the DTMC laws: the initial state exists, every state has
        one outgoing distribution over existing states with strictly
        positive exact-rational branches summing to 1 (no duplicate
        targets), and every label is a letter of the alphabet."""
        n = self.n
        assert n > 0, "a chain has at least one state"
        assert 0 <= self.init < n, self.init
        assert len(self.trans) == n, (len(self.trans), n)
        letters = set(self.alphabet.letters())
        for q in range(n):
            assert self.label[q] in letters, (q, self.label[q])
            row = self.trans[q]
            assert row, f"state {q} has no outgoing branch"
            seen: set = set()
            total = Fraction(0)
            for d, pr in row:
                assert 0 <= d < n, (q, d)
                assert d not in seen, f"state {q} branches twice to {d}"
                seen.add(d)
                assert isinstance(pr, Fraction) and pr > 0, (q, d, pr)
                total += pr
            assert total == 1, f"state {q} branches sum to {total}, not 1"


def bernoulli_chain(alphabet: Alphabet, p: Dict[Letter, Fraction]) -> Chain:
    """The chain that emits i.i.d. letters distributed as ``p``: one state
    per letter (state ``a`` labelled ``a``), ``P(a -> b) = p(b)``, initial
    state the least letter. Its word from state ``a`` is ``a`` followed by a
    ``p``-Bernoulli word."""
    letters = alphabet.letters()
    trans = tuple(
        tuple((j, p[b]) for j, b in enumerate(letters)) for _ in letters
    )
    ch = Chain(alphabet=alphabet, label=tuple(letters), trans=trans, init=0)
    ch.validate()
    return ch


def _render_prob(pr: Fraction) -> str:
    """``1`` or ``1/3`` — a rational literal, never a decimal."""
    return str(pr.numerator) if pr.denominator == 1 else f"{pr.numerator}/{pr.denominator}"


def dump_mc(ch: Chain) -> str:
    """The canonical ``.mc`` text of ``ch``: states in id order, branches in
    target order, one ``label`` per letter in mask order (``false`` for a
    letter labelling no state)."""
    ch.validate()
    out: List[str] = ["dtmc", "", "module chain"]
    out.append(f"  s : [0..{ch.n - 1}] init {ch.init};")
    out.append("")
    for q in range(ch.n):
        branches = " + ".join(
            f"{_render_prob(pr)}:(s'={d})" for d, pr in sorted(ch.trans[q])
        )
        out.append(f"  [] s={q} -> {branches};")
    out += ["endmodule", ""]
    for a in ch.alphabet.letters():
        states = [q for q in range(ch.n) if ch.label[q] == a]
        rhs = "|".join(f"s={q}" for q in states) if states else "false"
        out.append(f'label "{render_letter(ch.alphabet, a)}" = {rhs};')
    return "\n".join(out) + "\n"


def _lines(text: str) -> List[str]:
    """The file's significant lines: comments (``//``) and blanks removed."""
    out: List[str] = []
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line:
            out.append(line)
    return out


def _reject(msg: str) -> None:
    raise ValueError(f".mc: {msg}")


def _parse_branches(body: str, var: str, n: int, q: int) -> Tuple[Tuple[int, Fraction], ...]:
    """The branches of one guarded command, exact and summing to 1."""
    out: List[Tuple[int, Fraction]] = []
    for tok in body.split("+"):
        m = _BRANCH_RE.match(tok.strip())
        if not m:
            _reject(f"state {q}: cannot read branch {tok.strip()!r}")
            raise AssertionError  # unreachable; keeps the type checker honest
        num, den, v, dst = m.group(1), m.group(2), m.group(3), int(m.group(4))
        if v != var:
            _reject(f"state {q}: branch updates {v!r}, not the state variable {var!r}")
        if not 0 <= dst < n:
            _reject(f"state {q}: branch target {dst} out of range 0..{n - 1}")
        pr = Fraction(int(num), int(den) if den else 1)
        if pr <= 0:
            _reject(f"state {q}: branch probability {pr} is not > 0")
        out.append((dst, pr))
    total = sum((pr for _, pr in out), Fraction(0))
    if total != 1:
        _reject(f"state {q}: branch probabilities sum to {total}, not 1")
    return tuple(out)


def parse_mc(text: str, alphabet: Alphabet) -> Chain:
    """Read a ``.mc`` file over ``alphabet``. Rejects (never repairs) any
    departure from the subset: a missing ``dtmc``/``module``/``endmodule``,
    a variable that is not ``x : [0..N-1] init i``, a state without exactly
    one command, a branch set not summing to 1, a label name that is not the
    cube rendering of a letter, a letter without a label, or a label set that
    does not partition the states."""
    lines = _lines(text)
    if not lines or lines[0] != "dtmc":
        _reject("the first line must be 'dtmc'")
    if len(lines) < 2 or not lines[1].startswith("module "):
        _reject("line 2 must open the single module")
    try:
        end = lines.index("endmodule")
    except ValueError:
        end = -1
        _reject("no 'endmodule'")
    m = _VAR_RE.match(lines[2]) if len(lines) > 2 else None
    if not m:
        _reject("line 3 must declare the state variable: 'x : [0..N-1] init i;'")
        raise AssertionError  # unreachable
    var, hi, init = m.group(1), int(m.group(2)), int(m.group(3))
    n = hi + 1
    if not 0 <= init < n:
        _reject(f"initial state {init} out of range 0..{hi}")

    trans: Dict[int, Tuple[Tuple[int, Fraction], ...]] = {}
    for line in lines[3:end]:
        cmd = _CMD_RE.match(line)
        if not cmd:
            _reject(f"not a guarded command: {line!r}")
            raise AssertionError  # unreachable
        if cmd.group(1) != var:
            _reject(f"guard reads {cmd.group(1)!r}, not the state variable {var!r}")
        q = int(cmd.group(2))
        if not 0 <= q < n:
            _reject(f"guard on state {q}, out of range 0..{hi}")
        if q in trans:
            _reject(f"state {q} has two commands (exactly one is required)")
        trans[q] = _parse_branches(cmd.group(3), var, n, q)
    missing = [q for q in range(n) if q not in trans]
    if missing:
        _reject(f"states without a command: {missing}")

    label: List[Letter] = [Letter(-1)] * n
    named: set = set()
    for line in lines[end + 1:]:
        lab = _LABEL_RE.match(line)
        if not lab:
            _reject(f"not a label definition: {line!r}")
            raise AssertionError  # unreachable
        name, rhs = lab.group(1), lab.group(2)
        try:
            a = parse_letter(alphabet, name)
        except Exception:
            a = Letter(-1)
        if a == Letter(-1) or render_letter(alphabet, a) != name:
            _reject(
                f"label {name!r} is not a letter of the alphabet "
                f"(ap: {' '.join(alphabet.aps) or '-'})"
            )
        if a in named:
            _reject(f"label {name!r} is defined twice")
        named.add(a)
        if rhs == "false":
            continue
        for tok in rhs.split("|"):
            d = _DISJUNCT_RE.match(tok.strip())
            if not d:
                _reject(f"label {name!r}: cannot read state predicate {tok.strip()!r}")
                raise AssertionError  # unreachable
            if d.group(1) != var:
                _reject(f"label {name!r} reads {d.group(1)!r}, not {var!r}")
            q = int(d.group(2))
            if not 0 <= q < n:
                _reject(f"label {name!r}: state {q} out of range 0..{hi}")
            if label[q] != Letter(-1):
                _reject(f"state {q} carries two letters (the labels must partition)")
            label[q] = a
    if named != set(alphabet.letters()):
        _reject(
            f"the labels name {len(named)} letters, the alphabet has "
            f"{alphabet.size} (every letter needs a label)"
        )
    unlabelled = [q for q in range(n) if label[q] == Letter(-1)]
    if unlabelled:
        _reject(f"states with no letter: {unlabelled} (the labels must partition)")

    ch = Chain(
        alphabet=alphabet,
        label=tuple(label),
        trans=tuple(trans[q] for q in range(n)),
        init=init,
    )
    ch.validate()
    return ch
