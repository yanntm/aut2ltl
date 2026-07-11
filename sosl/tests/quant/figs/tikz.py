"""Shared TikZ scaffolding for the measure figures.

One preamble, one palette, one set of node/edge styles, so the figures a
different probe draws read as one family. `standalone` wraps a list of
TikZ body lines into a `standalone` document that `pdflatex` compiles to a
cropped PDF (the figure folder's `Makefile` rasterizes it).

The palette keeps two roles apart: the alphabet (one hue per letter, plus a
dash pattern so the figure survives greyscale printing) and the read-offs
the measure construction lays over it — the θ verdict of a bottom SCC
(green = 1, red = 0), the kernel (a thick border), a bottom SCC (a double
circle), and the transient SCC boxes — in neutral greys.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterable, List, Sequence

PALETTE = {
    "letterA": "1F5FA9",      # the letter `a` — blue, solid
    "letterB": "B5651D",      # the letter `!a` (spec's b) — amber, dashed
    "boxline": "B9BEC4",      # transient SCC box outline
    "boxfill": "F4F5F7",      # transient SCC box fill
    "kernel": "3A3F45",       # the kernel border — near-black, thick
    "thetaT": "2E7D46",       # θ = 1 — green
    "thetaF": "C1443C",       # θ = 0 — red
    "xval": "5A6470",         # the x-value annotation under a node
    "ref": "8A9099",          # secondary structure (cuts, brackets)
    "ink": "222629",          # text
}

_PREAMBLE = r"""\documentclass[tikz,border=6pt]{standalone}
\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage{amssymb}
\usepackage{amsmath}
\usetikzlibrary{@LIBS@}
@COLORS@
\tikzset{
  % ---- classes ---------------------------------------------------
  cls/.style        = {circle, draw=ink, line width=.5pt, fill=white,
                       inner sep=0pt, minimum size=13mm, align=center,
                       font=\small},
  bottom/.style     = {cls, double, double distance=1pt},
  kern/.style       = {draw=kernel, line width=1.6pt},
  % ---- SCC boxes -------------------------------------------------
  sccbox/.style     = {rounded corners=3pt, draw=boxline, fill=boxfill,
                       line width=.7pt},
  scctag/.style     = {font=\scriptsize\itshape, text=ref, align=center},
  % ---- alphabet edges --------------------------------------------
  ea/.style         = {draw=letterA, text=letterA, line width=.9pt,
                       -{Stealth[length=2mm]}},
  eb/.style         = {draw=letterB, text=letterB, line width=.9pt,
                       dashed, dash pattern=on 2.4pt off 1.6pt,
                       -{Stealth[length=2mm]}},
  eall/.style       = {draw=ink, text=ink, line width=.9pt,
                       -{Stealth[length=2mm]}},
  elab/.style       = {font=\scriptsize, inner sep=1.5pt,
                       fill=white, fill opacity=.85, text opacity=1},
  % ---- read-off decorations --------------------------------------
  thetaT/.style     = {circle, fill=thetaT, text=white, inner sep=0pt,
                       minimum size=4mm, font=\tiny\bfseries},
  thetaF/.style     = {circle, fill=thetaF, text=white, inner sep=0pt,
                       minimum size=4mm, font=\tiny\bfseries},
  xann/.style       = {font=\footnotesize, text=xval},
  result/.style     = {font=\small, text=ink},
  % ---- word ruler / verdict panels (FIG-2, FIG-3) ----------------
  cut/.style        = {draw=ref, line width=.8pt},
  jcut/.style       = {draw=ink, line width=1.1pt},
  cell/.style       = {font=\small\ttfamily, text=ink, inner sep=1pt},
  hi/.style         = {rounded corners=1pt, fill=letterA, fill opacity=.14},
  brk/.style        = {draw=ref, line width=.7pt,
                       decorate, decoration={brace, amplitude=4pt}},
  vrow/.style       = {font=\small, text=ink, anchor=west},
  vnote/.style      = {font=\scriptsize\itshape, text=ref, anchor=west},
}
"""


def _colors() -> str:
    return "\n".join(
        rf"\definecolor{{{k}}}{{HTML}}{{{v}}}" for k, v in PALETTE.items())


def standalone(body: Sequence[str], libs: Iterable[str] = ()) -> str:
    """A compilable `standalone` document around TikZ `body` lines."""
    names = ["arrows.meta", "shapes.geometric", "fit", "backgrounds",
             "calc", "positioning", "decorations.pathreplacing"]
    for extra in libs:
        if extra not in names:
            names.append(extra)
    preamble = (_PREAMBLE.replace("@LIBS@", ",".join(names))
                         .replace("@COLORS@", _colors()))
    doc: List[str] = [preamble,
                      r"\begin{document}", r"\begin{tikzpicture}"]
    doc += list(body)
    doc += [r"\end{tikzpicture}", r"\end{document}", ""]
    return "\n".join(doc)


def frac_tex(x: Fraction) -> str:
    """A rational as LaTeX math: an integer bare, else ``\\tfrac{p}{q}``.
    Never a decimal — the measure figures show exact values."""
    if x.denominator == 1:
        return str(x.numerator)
    sign = "-" if x < 0 else ""
    return rf"{sign}\tfrac{{{abs(x.numerator)}}}{{{x.denominator}}}"


def letter_txt(inv, a: int) -> str:
    """The letter of mask ``a`` as ``a`` / ``!a`` over the invariant's APs."""
    trues = inv.alphabet.true_aps(a)
    return "&".join(p if p in trues else "!" + p for p in inv.alphabet.aps)


def class_tex(inv, c: int) -> str:
    """The class's shortlex key as ``[\\varepsilon]``, ``[\\lnot a]``, …"""
    key = inv.keys[c]
    if not key:
        return r"[\varepsilon]"
    return "[" + r"{\cdot}".join(
        (a_ap if a_ap in inv.alphabet.true_aps(a) else rf"\lnot {a_ap}")
        for a in key for a_ap in inv.alphabet.aps) + "]"


__all__ = ["PALETTE", "standalone", "frac_tex", "letter_txt", "class_tex"]
