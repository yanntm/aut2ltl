"""survey.verify — optional spot-oracle equivalence check of a reconstruction.

Decoupled from build: the plain `aut2ltl_survey` run only builds + logs; the
correctness gate turns verification on. In an isolated, bounded spot subprocess
(the test-only oracle), classify the original (Manna-Pnueli class) and — when a
real flattened reconstruction is supplied — check `are_equivalent` against it.
A Spot blow-up (>32 acceptance sets, …) is reported, never our failure.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Optional, Tuple

from aut2ltl import bounded

# Test-only spot oracle: classify the original and (when a flattened
# reconstruction is supplied) check equivalence. Inputs travel via stdin — a
# multi-MB flat formula on argv dies with E2BIG.
_VERIFY_CHILD = '''
import sys, json
import spot
p = json.load(sys.stdin)
out = {}
orig = p["orig"]
is_hoa = p.get("is_hoa", False)
if is_hoa:
    # HOA-file original: the language is the automaton itself, so there is no
    # source formula to classify with mp_class. Load it once for equivalence.
    try:
        orig_aut = spot.automaton(orig)
        out["mp"] = "?"
    except Exception as e:
        orig_aut = None
        out["mp"] = "?"
        out["mp_err"] = str(e)[:90]
else:
    try:
        fo = spot.formula(orig)
        out["mp"] = spot.mp_class(fo)        # B/S/G/O/R/P/T
    except Exception as e:
        out["mp"] = "?"
        out["mp_err"] = str(e)[:90]
rec = p.get("rec")
if rec is None:
    out["equiv"] = None                      # nothing to verify (gated off / build failed)
else:
    try:
        if not is_hoa:
            orig_aut = spot.formula(orig).translate("Buchi")
        other = spot.formula(rec)
        if rec not in ("true", "false"):
            other = other.translate("Buchi")
        out["equiv"] = bool(spot.are_equivalent(orig_aut, other))
    except Exception as e:
        # Spot raises (not returns) on its limits; messages are multi-line, so
        # collapse whitespace before it reaches a CSV field. The >32-acceptance-
        # set wall is the standard case (a reconstruction with too many distinct
        # temporals) — give it a stable single-line tag.
        msg = " ".join(str(e).split())
        if "Too many acceptance sets" in msg:
            out["equiv"] = "SPOT_ERR:too-many-acceptance-sets"
        else:
            out["equiv"] = "SPOT_ERR:" + msg[:80]
print("VERIFY_JSON:" + json.dumps(out))
'''


@dataclass
class VerifyResult:
    """The oracle's verdict. `equiv` is True / False / None (nothing to verify) /
    "SPOT_TIMEOUT" / "SPOT_ERR:..."; `mp` is the Manna-Pnueli class or "?";
    `check_s` is the oracle subprocess wall time (distinct from the build time)."""
    mp: str
    equiv: object
    check_s: str = ""


def verify(orig: str, rec: Optional[str], *, is_hoa: bool,
           timeout: int) -> VerifyResult:
    """Classify `orig` and, when `rec` is a real flattened formula, check
    equivalence against it, in the isolated spot-oracle subprocess."""
    res = bounded.run(
        [sys.executable, "-c", _VERIFY_CHILD], timeout,
        stdin=json.dumps({"orig": orig, "rec": rec, "is_hoa": is_hoa}),
    )
    cs = f"{res.wall_s:.3f}"
    if res.timed_out:
        return VerifyResult(mp="?", equiv="SPOT_TIMEOUT", check_s=cs)
    for line in (res.out or "").splitlines():
        if line.startswith("VERIFY_JSON:"):
            d = json.loads(line[len("VERIFY_JSON:"):])
            return VerifyResult(mp=d.get("mp", "?"), equiv=d.get("equiv"), check_s=cs)
    return VerifyResult(mp="?", equiv="SPOT_ERR:no marker", check_s=cs)


def verify_witness(orig: str, witness: Optional[str], *, is_hoa: bool,
                   timeout: int) -> Tuple[str, str]:
    """Replay a NOT_LTL witness against `orig` via the `aut2ltl.verifier` CLI in a
    bounded, isolated subprocess (membership only — acceptance-agnostic). Returns
    `(token, check_s)`; the token is the same vocabulary as the LTL equivalence
    oracle:

      * TRUE    -- the counting family toggles with its period (sound certificate);
      * FAIL    -- it does not toggle, OR the family is incomplete / absent: a
                   NOT_LTL claim with no replayable certificate is unsound;
      * TIMEOUT -- the bounded replay overran;
      * ERROR   -- the verifier could not run (bad input / load error).
    """
    if not witness:
        return ("FAIL", "")  # NOT_LTL asserted with no witness to back it
    tool = [sys.executable, "-m", "aut2ltl.verifier", orig, witness,
            "--hoa" if is_hoa else "--ltl"]
    res = bounded.run(tool, timeout)
    cs = f"{res.wall_s:.3f}"
    if res.timed_out:
        return ("TIMEOUT", cs)
    for line in (res.out or "").splitlines():
        if line.startswith("VERIFY: ok"):
            return ("TRUE", cs)
        if line.startswith("VERIFY: fail") or line.startswith("VERIFY: no-witness"):
            return ("FAIL", cs)
    return ("ERROR", cs)
