"""Shared TikZ scaffolding for the symmetry figures.

One preamble, one palette, one set of node/edge styles, so the figures a
different probe draws read as one family. `standalone` wraps a list of TikZ
body lines into a `standalone` document that `pdflatex` compiles to a cropped
PDF (the figure folder's `Makefile` rasterizes it).

Conventions (shared with `sos_toltl_figs`, extended here — recorded in the
artifact's `figures.md`):

  - alphabet edges: solid blue = a Cayley step under ``a``; dashed amber = a
    step under ``¬a``; black = both letters agree (one hue *and* one dash
    pattern, so the figures survive greyscale);
  - green double arrow (`perm`) = a signed permutation's action on classes;
  - red cross (`xfail`) on a cell = the multiplicativity failure of a
    candidate automorphism;
  - hatched region (`gap`) = a gap language `L♯ ∖ L♭`.

The class/fiber greys and the `Z/2` group box reuse the neutral palette of
the measure figures so all three papers' figures look like one system.
"""
from __future__ import annotations

from typing import Iterable, List, Sequence

PALETTE = {
    "letterA": "1F5FA9",      # the letter `a` — blue, solid
    "letterB": "B5651D",      # the letter `!a` (spec's b) — amber, dashed
    "boxline": "B9BEC4",      # neutral box outline (subgroup / table frame)
    "boxfill": "F4F5F7",      # neutral box fill
    "fiberF":  "DCE6F4",      # a fat λ-fiber, tint of letterA
    "fiberN":  "F4E7D6",      # the other fat λ-fiber, tint of letterB
    "perm":    "2E7D46",      # a signed permutation's action — green
    "xfail":   "C1443C",      # a multiplicativity failure — red
    "hatch":   "8A9099",      # gap hatching — neutral grey
    "accept":  "3A3F45",      # an accepting linked pair — near-black
    "ref":     "8A9099",      # secondary structure (tags, brackets)
    "ink":     "222629",      # text
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
                       inner sep=0pt, minimum size=12mm, align=center,
                       font=\small},
  accpt/.style      = {cls, double, double distance=1pt, draw=accept},
  unit/.style       = {cls, fill=boxfill},
  % ---- λ-fibers (FIG-1 left) -------------------------------------
  fibF/.style       = {rounded corners=4pt, draw=letterA, fill=fiberF,
                       line width=.7pt},
  fibN/.style       = {rounded corners=4pt, draw=letterB, fill=fiberN,
                       line width=.7pt},
  mint/.style       = {rounded corners=2pt, draw=ink, fill=white,
                       line width=.5pt, inner sep=2pt, font=\small\ttfamily,
                       minimum width=10mm, minimum height=6mm},
  % ---- alphabet / Cayley edges -----------------------------------
  ea/.style         = {draw=letterA, text=letterA, line width=.9pt,
                       -{Stealth[length=2mm]}},
  eb/.style         = {draw=letterB, text=letterB, line width=.9pt,
                       dashed, dash pattern=on 2.4pt off 1.6pt,
                       -{Stealth[length=2mm]}},
  eall/.style       = {draw=ink, text=ink, line width=.9pt,
                       -{Stealth[length=2mm]}},
  elab/.style       = {font=\scriptsize, inner sep=1.5pt,
                       fill=white, fill opacity=.85, text opacity=1},
  % ---- the signed-permutation action -----------------------------
  perm/.style       = {draw=perm, text=perm, line width=1.1pt,
                       {Stealth[length=2mm]}-{Stealth[length=2mm]}},
  permd/.style      = {perm, dash pattern=on 3pt off 2pt},
  permlab/.style    = {font=\scriptsize, text=perm, inner sep=1.5pt,
                       fill=white, fill opacity=.85, text opacity=1},
  % ---- read-off decorations --------------------------------------
  grpbox/.style     = {rounded corners=3pt, draw=accept, line width=1.1pt},
  grptag/.style     = {font=\scriptsize\bfseries, text=accept},
  tag/.style        = {font=\scriptsize\itshape, text=ref, align=center},
  ktag/.style       = {font=\scriptsize, text=perm, align=center},
  fail/.style       = {font=\scriptsize\itshape, text=xfail, align=center},
  celltab/.style    = {font=\small\ttfamily, text=ink, inner sep=2pt},
  hdr/.style        = {font=\small\bfseries, text=ink},
}
"""


def _colors() -> str:
    return "\n".join(
        rf"\definecolor{{{k}}}{{HTML}}{{{v}}}" for k, v in PALETTE.items())


def standalone(body: Sequence[str], libs: Iterable[str] = ()) -> str:
    """A compilable `standalone` document around TikZ `body` lines."""
    names = ["arrows.meta", "shapes.geometric", "fit", "backgrounds",
             "calc", "positioning", "decorations.pathreplacing",
             "patterns", "matrix"]
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


def minterm_tex(inv, a: int) -> str:
    """A minterm mask as ``a\\,b`` / ``a\\,\\bar b`` … over the invariant's APs
    (overline = negated), for a compact square-vertex label."""
    trues = inv.alphabet.true_aps(a)
    return r"\,".join(p if p in trues else rf"\bar {p}" for p in inv.alphabet.aps)


def class_tex(inv, c: int) -> str:
    """The class's shortlex key as ``[\\varepsilon]``, ``[\\bar a]``, …"""
    key = inv.keys[c]
    if not key:
        return r"[\varepsilon]"
    return "[" + "".join(
        (a_ap if a_ap in inv.alphabet.true_aps(a) else rf"\bar {a_ap}")
        for a in key for a_ap in inv.alphabet.aps) + "]"


def esc(s: str) -> str:
    """Escape the few LaTeX-active characters that appear in our labels."""
    return s.replace("_", r"\_").replace("&", r"\&").replace("#", r"\#")


__all__ = ["PALETTE", "standalone", "minterm_tex", "class_tex", "esc"]
