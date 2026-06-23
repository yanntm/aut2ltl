#!/usr/bin/env python3
"""Scratch: dump the last N user<->assistant text exchanges from a session jsonl."""
import json
import sys
from typing import Any

path: str = sys.argv[1]
n_pairs: int = int(sys.argv[2]) if len(sys.argv) > 2 else 3


def text_of(msg: dict[str, Any]) -> str:
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        out = []
        for b in c:
            if not isinstance(b, dict):
                continue
            t = b.get("type")
            if t == "text":
                out.append(b.get("text", ""))
            elif t == "tool_use":
                out.append(f"[tool_use {b.get('name')}]")
            elif t == "tool_result":
                out.append("[tool_result]")
        return "\n".join(x for x in out if x)
    return ""


rows: list[tuple[str, str]] = []
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = rec.get("type")  # 'user' / 'assistant'
        msg = rec.get("message")
        if role in ("user", "assistant") and isinstance(msg, dict):
            txt = text_of(msg)
            if txt.strip():
                rows.append((role, txt))

# Keep only real user prose (skip tool_result-only user turns).
filtered = [(r, t) for (r, t) in rows if not (r == "user" and t.startswith("[tool_result"))]

# Take the tail: last n_pairs user turns and everything after each.
user_idx = [i for i, (r, _) in enumerate(filtered) if r == "user"]
start = user_idx[-n_pairs] if len(user_idx) >= n_pairs else 0
for r, t in filtered[start:]:
    print(f"\n===== {r.upper()} =====")
    print(t[:4000])
