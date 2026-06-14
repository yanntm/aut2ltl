"""
kr/gap/runner.py — process-spawn service for the GAP bridge.

Everything that shells out to `gap` lives here: running a generated script and
probing whether a usable GAP (with SgpDec) is installed. Isolated from the pure
module API in bridge.py so the subprocess/tempfile machinery — and its failure
modes — stay in one place.
"""

from __future__ import annotations
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


def run_gap_script(
    script: str,
    *,
    gap_cmd: str = "gap",
    timeout: int = 180,
    workdir: Optional[Path] = None,
) -> str:
    """
    Write `script` to a temp file and execute `gap --no-window <script>`.

    Returns the captured stdout.  Stderr is logged but not returned.
    Raises on non-zero exit or timeout.
    """
    with tempfile.TemporaryDirectory(dir=workdir) as td:
        script_path = Path(td) / "decompose.gap"
        out_path = Path(td) / "cascade.out"

        script_path.write_text(script, encoding="utf-8")

        cmd = [gap_cmd, "--no-window", "--bare", str(script_path)]
        try:
            with open(out_path, "w", encoding="utf-8") as out_f:
                proc = subprocess.run(
                    cmd,
                    stdout=out_f,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    check=False,
                    text=True,
                )
            captured = out_path.read_text(encoding="utf-8")
            if proc.returncode != 0:
                raise RuntimeError(
                    f"GAP exited with code {proc.returncode}.\n"
                    f"stderr (last 2000 chars):\n{proc.stderr[-2000:]}\n"
                    f"stdout head:\n{captured[:1500]}"
                )
            return captured
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"GAP run timed out after {timeout}s") from None


def check_gap_available(gap_cmd: str = "gap") -> bool:
    """Return True iff a runnable GAP that can LoadPackage("SgpDec") exists."""
    try:
        out = subprocess.run(
            [gap_cmd, "--no-window", "--bare", "-c",
             'if LoadPackage("SgpDec")=fail then Print("NO\n"); else Print("YES\n"); fi; QUIT;'],
            capture_output=True, text=True, timeout=15
        )
        return "YES" in out.stdout
    except Exception:
        return False
