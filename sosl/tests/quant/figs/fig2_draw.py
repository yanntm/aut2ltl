"""The word-ruler drawing for FIG-2 (see `fig2.py` for the computation).

One horizontal ruler of the sampled word: the letter strip with the
``aaaa`` occurrences highlighted, a vertical bar at every midpoint cut, and
four stacked read-offs — each inter-cut block's ``H(k)`` value, the
cumulative product with its ``g``-valued cuts circled (the ``J``-cuts), the
inter-``J`` brackets tagged ``fold = k``, and the stem bracket. Placement
only; every value comes from the `Structure` the probe computed.
"""
from __future__ import annotations

from typing import List

from tests.quant.figs import tikz
from tests.quant.figs.fig2 import A, Structure

CW = 0.32           # cm per character
Y_LET = 0.0         # letter baseline
Y_PAR = -1.05       # block-parity row
Y_CUM = -1.95       # cumulative row
Y_BRK = -2.75       # inter-J bracket row
Y_TAG = -3.15       # bracket tags
BAR_TOP = 0.75
BAR_BOT = -2.55


def _x(i: int) -> float:
    return i * CW


def draw(inv, st: Structure, n: int) -> str:
    positions = [c.pos for c in st.cuts]
    # cut states: baseline g before block 0, then the cumulative after each block.
    cut_state = [0] + list(st.cumulative)
    circled = [j for j, v in enumerate(cut_state) if v == st.g]
    body: List[str] = []

    # occurrence highlights (behind the letters).
    for c in st.cuts:
        s = c.occ_start
        body.append(rf"  \fill[hi] ({_x(s):.2f},{Y_LET - 0.28:.2f}) rectangle "
                    rf"({_x(s + 4):.2f},{Y_LET + 0.28:.2f});")

    # the letter strip.
    for i, x in enumerate(st.word):
        col = "letterA" if x == A else "letterB"
        ch = "a" if x == A else "b"
        body.append(rf"  \node[cell, text={col}] at ({_x(i) + CW / 2:.2f},"
                    rf"{Y_LET:.2f}) {{{ch}}};")

    # vertical cut bars; J-cuts dark, the rest grey.
    for j, p in enumerate(positions):
        sty = "jcut" if j in circled else "cut"
        body.append(rf"  \draw[{sty}] ({_x(p):.2f},{BAR_TOP:.2f}) -- "
                    rf"({_x(p):.2f},{BAR_BOT:.2f});")

    # block parities (H(k) value under each inter-cut block).
    for i in range(len(positions) - 1):
        mid = (positions[i] + positions[i + 1]) / 2
        body.append(rf"  \node[font=\small] at ({_x(mid):.2f},{Y_PAR:.2f}) "
                    rf"{{$\bar r={st.block_parity[i]}$}};")

    # cumulative parities at each cut; g-valued ones circled (the J-cuts).
    for j, p in enumerate(positions):
        val = cut_state[j]
        if j in circled:
            body.append(rf"  \node[circle,draw=ink,line width=1pt,inner sep=1pt,"
                        rf"minimum size=5.5mm,font=\small,fill=white] "
                        rf"at ({_x(p):.2f},{Y_CUM:.2f}) {{${val}$}};")
        else:
            body.append(rf"  \node[font=\small,text=ref,fill=white,inner sep=2pt] "
                        rf"at ({_x(p):.2f},{Y_CUM:.2f}) {{${val}$}};")

    # inter-J brackets, each tagged fold = k.
    cpos = [positions[j] for j in circled]
    for a, b in zip(cpos, cpos[1:]):
        body.append(rf"  \draw[brk] ({_x(b):.2f},{Y_BRK:.2f}) -- "
                    rf"({_x(a):.2f},{Y_BRK:.2f});")
        body.append(rf"  \node[font=\scriptsize,text=ink] at "
                    rf"({_x((a + b) / 2):.2f},{Y_TAG:.2f}) "
                    rf"{{$\mathrm{{fold}}=k$}};")

    # stem bracket above the letters, left of the first cut.
    p0 = positions[0]
    body.append(rf"  \draw[brk] ({_x(0):.2f},{BAR_TOP + 0.15:.2f}) -- "
                rf"({_x(p0):.2f},{BAR_TOP + 0.15:.2f});")
    body.append(rf"  \node[font=\scriptsize,text=ink,anchor=south] at "
                rf"({_x(p0 / 2):.2f},{BAR_TOP + 0.32:.2f}) "
                rf"{{fold$(y)\in\mathrm{{Stems}}(c,k)$}};")

    # legend.
    legend = (r"$k=\mathrm{fold}(aa),\quad H(k)=\{\bar r{=}0{:}\,k,\ "
              r"\bar r{=}1{:}\,m\}\cong\mathbb{Z}/2,\quad g=" + str(st.g) + r"$")
    body.append(rf"  \node[font=\scriptsize,text=ink,anchor=west] at "
                rf"({_x(0):.2f},{Y_TAG - 0.7:.2f}) {{{legend}}};")

    return tikz.standalone(body)


__all__ = ["draw"]
