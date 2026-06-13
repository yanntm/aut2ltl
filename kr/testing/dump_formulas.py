#!/usr/bin/env python3
"""kr/testing/dump_formulas.py — print FULL reconstructed LTL for argv formulas.

Subprocess-isolated per case (Spot/buddy stability). DAG out, flattened only
under KR_FLATTEN_TREE_LIMIT. Prints the whole string (no truncation) plus
tree-node count. Diagnostic helper for reading the current driver outputs.

    python3 kr/testing/dump_formulas.py "a U b" "F a & G b" "G a | F b"
"""
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHILD = '''
import sys, json
from pathlib import Path
sys.path.insert(0, r"{root}")
import spot
from kr import decompose_aut, reconstruct_ltl_1level_buchi
from kr.ltl_builders import _tree_size_f, _str_f
fs = {fs!r}
f = spot.formula(fs)
casc = decompose_aut(f.translate())
rec = reconstruct_ltl_1level_buchi(casc)
print("RESULT_JSON:" + json.dumps({{
    "formula": fs,
    "levels": casc.num_levels,
    "tree_nodes": _tree_size_f(rec),
    "recovered": _str_f(rec),
}}))
'''


def run(fs: str) -> dict:
    code = CHILD.format(root=str(PROJECT_ROOT), fs=fs)
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True, timeout=60, cwd=PROJECT_ROOT)
    out = (proc.stdout or "") + (proc.stderr or "")
    for line in out.splitlines():
        if line.strip().startswith("RESULT_JSON:"):
            return json.loads(line.strip()[len("RESULT_JSON:"):])
    return {"formula": fs, "error": out[-400:]}


def main():
    for fs in sys.argv[1:]:
        res = run(fs)
        print(f"=== {fs} ===")
        if "error" in res:
            print(f"  ERROR: {res['error']}")
            continue
        print(f"  levels={res['levels']} tree_nodes={res['tree_nodes']}")
        print(f"  {res['recovered']}")
        print()


if __name__ == "__main__":
    main()
