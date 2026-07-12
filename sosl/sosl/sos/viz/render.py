"""Turning backend text into a picture: the external-tool steps.

`pdflatex` compiles a standalone `.tex`, `pdftoppm` rasterizes the result,
`dot` renders the dot backend directly. Each call is bounded and raises
RuntimeError with the tool's own message on failure — a missing or unhappy
external tool is reported, never worked around.

LaTeX's auxiliary files land beside the output (``-output-directory``) and are
removed on success; the `.pdf` is the only survivor.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from typing import List

TIMEOUT_S = 15.0
AUX_EXT = (".aux", ".log", ".out")


def _run(cmd: List[str], what: str) -> None:
    """Run ``cmd``, bounded; raise RuntimeError carrying its output on failure."""
    if shutil.which(cmd[0]) is None:
        raise RuntimeError(f"{cmd[0]} not on PATH (needed to {what})")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S)
    if proc.returncode != 0:
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-12:]
        raise RuntimeError(f"failed to {what}:\n  " + "\n  ".join(tail))


def compile_pdf(tex_path: str) -> str:
    """Compile a standalone `.tex` to a `.pdf` beside it; return the pdf path."""
    out_dir = os.path.dirname(os.path.abspath(tex_path)) or "."
    _run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
          "-output-directory", out_dir, tex_path], f"compile {tex_path}")
    stem = os.path.splitext(tex_path)[0]
    for ext in AUX_EXT:
        if os.path.exists(stem + ext):
            os.remove(stem + ext)
    return stem + ".pdf"


def pdf_to_png(pdf_path: str, dpi: int = 150) -> str:
    """Rasterize the first page of ``pdf_path`` to a `.png` beside it; return it."""
    stem = os.path.splitext(pdf_path)[0]
    _run(["pdftoppm", "-png", "-r", str(dpi), "-singlefile", pdf_path, stem],
         f"rasterize {pdf_path}")
    return stem + ".png"


def dot_to_png(dot_text: str, png_path: str, dpi: int = 150) -> str:
    """Render dot text straight to a `.png` with GraphViz; return the png path."""
    if shutil.which("dot") is None:
        raise RuntimeError("GraphViz `dot` not on PATH (needed to render a png)")
    proc = subprocess.run(["dot", "-Tpng", f"-Gdpi={dpi}", "-o", png_path],
                          input=dot_text, capture_output=True, text=True,
                          timeout=TIMEOUT_S)
    if proc.returncode != 0:
        raise RuntimeError(f"dot -Tpng failed: {proc.stderr.strip()}")
    return png_path
