#!/usr/bin/env python3
"""
kr/testing/probe_gate_inspect.py

Manual inspection of what the buchi2ltl gate actually emits for given formulas,
vs the kr (gate-off) output, and whether Spot's / kr's simplifier shrinks the
gate output (testing the hypothesis that buchi2ltl does NOT wire Spot's LTL
simplifications, so its formula looks bigger but is not really bigger).

Per formula, in an isolated subprocess, prints the formula string + size
(DAG / tree / distinct-temporals) for:
  raw    : try_heuristic_gate(aut) output as-is
  +spot  : spot full tl_simplifier on that output
  +krsimp: kr's own _simp_f on that output (the pipeline's per-node pass)
  kr-off : reconstruct_decomposed(aut) with the gate OFF (the pure kr form)

Run from project root:
    python3 kr/testing/probe_gate_inspect.py "Fa | Gb" "Ga | Fb"
"""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

PER = int(os.environ.get("KR_INSPECT_TIMEOUT", "15"))
DEFAULT = ["Fa | Gb", "Ga | Fb"]

_CHILD = r'''
import os, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(r"{root}").resolve()))
import spot

def sz(f):
    seen, st, t = set(), [f], 0
    def ts(g, memo):
        if g.id() in memo: return memo[g.id()]
        v = 1 + sum(ts(c, memo) for c in g); memo[g.id()] = v; return v
    while st:
        g = st.pop(); i = g.id()
        if i in seen: continue
        seen.add(i)
        if g.kindstr() in ("U","M","R","W","F","G"): t += 1
        for c in g: st.append(c)
    return [len(seen), ts(f, {{}}), t]

fs = {fs!r}
info = {{"formula": fs}}
try:
    from kr.decompose_recombine import reconstruct_decomposed
    from kr.heuristic_gate import try_heuristic_gate
    from kr.ltl_builders import _simp_f
    aut = spot.formula(fs).translate()
    raw = try_heuristic_gate(aut)
    if raw is not None:
        info["raw"] = [str(raw), sz(raw)]
        sp = spot.simplify(raw)
        info["spot"] = [str(sp), sz(sp)]
        try:
            ks = _simp_f(raw)
            info["krsimp"] = [str(ks), sz(ks)]
        except Exception as e:
            info["krsimp"] = ["<err: %s>" % str(e)[:60], None]
    else:
        info["raw"] = ["<gate declined>", None]
    os.environ["KR_GATE_BUCHI2LTL"] = "0"
    off = reconstruct_decomposed(aut)
    info["off"] = [str(off), sz(off)]
    info["result"] = "OK"
except Exception as e:
    import traceback
    info["result"] = "ERROR"; info["error"] = str(e)[:160]
    info["tb"] = traceback.format_exc()[-300:]
print("RESULT_JSON:" + json.dumps(info))
'''


def run(fs):
    child = _CHILD.format(root=PROJECT_ROOT, fs=fs)
    try:
        p = subprocess.run([sys.executable, "-c", child], capture_output=True,
                           text=True, timeout=PER, cwd=PROJECT_ROOT)
    except subprocess.TimeoutExpired:
        return {"formula": fs, "result": "TIMEOUT"}
    out = (p.stdout or "") + (p.stderr or "")
    for line in out.splitlines():
        if line.strip().startswith("RESULT_JSON:"):
            return json.loads(line.strip()[len("RESULT_JSON:"):])
    return {"formula": fs, "result": "ERROR", "error": out[-300:]}


def show(label, pair):
    if not pair:
        return
    s, size = pair
    sst = f"[{size[0]}/{size[1]}/{size[2]}]" if size else ""
    print(f"    {label:8s} {sst:14s} {s}")


def main():
    cases = sys.argv[1:] or DEFAULT
    for fs in cases:
        r = run(fs)
        print(f"\n=== {fs} ===")
        if r.get("result") != "OK":
            print(f"    {r.get('result')}: {r.get('error','')}")
            continue
        show("raw", r.get("raw"))
        show("+spot", r.get("spot"))
        show("+krsimp", r.get("krsimp"))
        show("kr-off", r.get("off"))


if __name__ == "__main__":
    main()
