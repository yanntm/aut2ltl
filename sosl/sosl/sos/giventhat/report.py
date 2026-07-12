"""The `.gtr` report of one `simplify` run — the tool's machine-and-human
output, with its reader and writer both provided (the `.cat` sidecar pattern).

`.gtr` format (a header then `key: value` lines, like `.cat`):

    GT v1
    verdict: SIMPLIFIED            # or SETTLED / REFUTED
    seed: syntactic               # SIMPLIFIED only, below
    side: relax
    bits: 7
    neg_phi: 5                    # |C| of the six reference points
    k: 3
    table: 6
    p_min: 4
    p_max: 4
    b: 3
    rung: recurrence recurrence   # rung of ¬φ, of B
    stutter: 1 1                  # stutter bit of ¬φ, of B
    stutter_verdict: YES
    witness: '().(3,)^ω'          # SETTLED / REFUTED only

`dump_report` is the writer, `parse_report` the reader (a flat dict, the
inverse up to types) — a survey aggregator reads a run without importing the
simplifier.
"""
from __future__ import annotations

from typing import Dict, List

from .simplify import Simplification

_CLASS_KEYS = ("neg_phi", "k", "table", "p_min", "p_max", "b")


def dump_report(sm: Simplification) -> str:
    """One `Simplification` as `.gtr` text."""
    L: List[str] = ["GT v1", f"verdict: {sm.verdict}"]
    if sm.verdict in ("SETTLED", "REFUTED"):
        if sm.witness is not None:
            w = sm.witness
            L.append(f"witness: {w.stem!r}.{w.loop!r}^ω")
        return "\n".join(L) + "\n"
    L += [f"seed: {sm.seed}", f"side: {sm.side}", f"bits: {sm.bits}"]
    for key in _CLASS_KEYS:
        L.append(f"{key}: {sm.classes[key]}")
    L.append(f"rung: {sm.rung[0]} {sm.rung[1]}")
    L.append(f"stutter: {int(sm.stutter[0])} {int(sm.stutter[1])}")
    L.append(f"stutter_verdict: {sm.stutter_verdict}")
    return "\n".join(L) + "\n"


def parse_report(text: str) -> Dict[str, object]:
    """Read a `.gtr` body into a flat dict: ``verdict`` always; on SIMPLIFIED
    also ``seed / side / bits(int) / classes(dict of int) / rung(tuple) /
    stutter(tuple of bool) / stutter_verdict``; on SETTLED / REFUTED
    ``witness``. Lines the format does not define are ignored."""
    f: Dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line and not line.startswith("GT"):
            key, _, val = line.partition(":")
            f[key.strip()] = val.strip()
    out: Dict[str, object] = {"verdict": f.get("verdict", "")}
    if out["verdict"] != "SIMPLIFIED":
        out["witness"] = f.get("witness")
        return out
    out["seed"], out["side"] = f.get("seed", ""), f.get("side", "")
    out["bits"] = int(f["bits"])
    out["classes"] = {k: int(f[k]) for k in _CLASS_KEYS}
    rung = f.get("rung", "").split()
    out["rung"] = (rung[0], rung[1]) if len(rung) == 2 else ("", "")
    st = f.get("stutter", "").split()
    out["stutter"] = (st[0] == "1", st[1] == "1") if len(st) == 2 else (False, False)
    out["stutter_verdict"] = f.get("stutter_verdict", "")
    return out
