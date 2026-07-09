"""Shared TikZ scaffolding for the generated figures.

One preamble, one palette, one set of node/edge styles, so figures drawn by
different probes read as one family. `standalone` wraps a list of TikZ body
lines into a `standalone` document that `pdflatex` compiles to a cropped PDF
(the figure folder's `Makefile` rasterizes it).

The palette distinguishes the two roles a drawing needs to keep apart: the
alphabet (one hue per letter, plus a dash pattern so the figure survives
greyscale printing) and the structure the construction imposes on it (layer
boxes, the R-order, memoization references) in neutral greys.
"""
from __future__ import annotations

from typing import Iterable, List, Sequence

PALETTE = {
    "letterA": "1F5FA9",      # the letter `a` — blue, solid
    "letterB": "B5651D",      # the letter `!a` — amber, dashed
    "order": "8A9099",        # the R-order between layers — grey
    "boxline": "B9BEC4",      # layer box outline
    "boxfill": "F4F5F7",      # layer box fill
    "frozen": "E9EEF6",       # the frozen (terminal) layer's fill
    "ref": "A6ADB4",          # memoization reference edges
    "ink": "222629",          # text
}

_PREAMBLE = r"""\documentclass[tikz,border=6pt]{standalone}
\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage{amssymb}
\usetikzlibrary{@LIBS@}
@COLORS@
\tikzset{
  % ---- classes and machines -------------------------------------
  cls/.style        = {circle, draw=ink, line width=.5pt, fill=white,
                       inner sep=0pt, minimum size=13mm, align=center,
                       font=\small},
  committed/.style  = {cls, double, double distance=1pt},
  entry/.style      = {draw=ink, line width=.8pt, -{Stealth[length=1.8mm]}},
  % ---- layers ----------------------------------------------------
  layerbox/.style   = {rounded corners=3pt, draw=boxline, fill=boxfill,
                       line width=.7pt},
  frozenbox/.style  = {layerbox, fill=frozen},
  layertag/.style   = {font=\scriptsize, text=ink, align=left,
                       inner sep=2pt},
  layername/.style  = {font=\scriptsize\bfseries, text=order},
  rorder/.style     = {draw=order, line width=2.2pt,
                       -{Stealth[length=3.2mm,width=3mm]}, opacity=.75},
  % ---- alphabet --------------------------------------------------
  ea/.style         = {draw=letterA, text=letterA, line width=.9pt,
                       -{Stealth[length=2mm]}},
  eb/.style         = {draw=letterB, text=letterB, line width=.9pt,
                       dashed, dash pattern=on 2.4pt off 1.6pt,
                       -{Stealth[length=2mm]}},
  eall/.style       = {draw=ink, text=ink, line width=.9pt,
                       -{Stealth[length=2mm]}},
  elab/.style       = {font=\scriptsize, inner sep=1.5pt,
                       fill=white, fill opacity=.85, text opacity=1},
  % ---- recursion panels ------------------------------------------
  dgnode/.style     = {circle, draw=ink, fill=white, line width=.5pt,
                       inner sep=0pt, minimum size=6.5mm,
                       font=\scriptsize},
  dgleaf/.style     = {dgnode, fill=boxfill, draw=order},
  treeedge/.style   = {draw=ink, line width=.4pt, opacity=.55},
  dagedge/.style    = {draw=ink, line width=.6pt, -{Stealth[length=1.6mm]}},
  refedge/.style    = {draw=ref, line width=.35pt, densely dotted,
                       -{Stealth[length=1.4mm]}},
  emult/.style      = {font=\tiny, text=ref, inner sep=1pt, fill=white},
  elide/.style      = {font=\scriptsize, text=ink, align=center},
  panelcap/.style   = {font=\scriptsize, text=ink, align=center},
}
"""


def _colors() -> str:
    return "\n".join(
        rf"\definecolor{{{k}}}{{HTML}}{{{v}}}" for k, v in PALETTE.items())


def standalone(body: Sequence[str], libs: Iterable[str] = ()) -> str:
    """A compilable `standalone` document around TikZ `body` lines."""
    names = ["arrows.meta", "shapes.geometric", "fit", "backgrounds",
             "calc", "positioning"]
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


def num(n: int) -> str:
    """A LaTeX-thin-space-grouped integer: `1991717` -> `1\\,991\\,717`."""
    s = str(n)
    groups: List[str] = []
    while len(s) > 3:
        groups.insert(0, s[-3:])
        s = s[:-3]
    groups.insert(0, s)
    return r"\," .join(groups)


__all__ = ["PALETTE", "num", "standalone"]
