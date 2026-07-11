# Build notes — `sos_measure` figures

The measured facts each figure rests on, and the drawing decisions that are not
forced by the data. Everything numeric here is emitted by a probe (see
[`reproduction.md`](reproduction.md)); this file is the audit trail, not a
second source of truth.

## The two source languages

Neither F-E nor F-D is aperiodic (each has a genuine `ℤ/2` in its algebra), so
neither is reachable from an LTL formula — the usual `build_sos 'φ'` route is
unavailable. They are coded directly from the paper's algebra in
[`sources.py`](../../sosl/tests/quant/figs/sources.py) and put through the
shared `canonicalize` normal form, so the resulting `.sos` is language-canonical
and byte-comparable, exactly like any other producer's invariant. The builder
asserts, against the paper:

- **F-E** (§4.1): `μ = p_b / (1 − p_a²)` — `2/3` at uniform, `3/4` at
  `p_a = 1/3`. Canonical ids: `0 = [ε]`, `1 = [¬a] = F₀` (θ = 1), `2 = [a] = A₁`,
  `3 = [a·¬a] = F₁` (θ = 0), `4 = [a·a] = A₀`.
- **F-D** (§3.4): `μ = 1` for every full-support `p` (`θ_K = 1`); the negative
  control `Val(fold(b), fold(ba)) = 1 ≠ 0 = Val(fold(bb), fold(ba))` (a
  non-kernel idempotent splits `R`-equivalent stems) against
  `Val(fold(b), fold(aa)) = Val(fold(bb), fold(aa)) = 1` (the kernel merges
  them). Kernel `K = {6, 8} = {fold(aa), fold(baa)}`, idempotent `k = 6`.

These are the fixture languages the spec's §8.5 asked M2 to promote (F-D, F-E);
they had not been added to `tests/quant/fixtures.py`, so the figure build stands
them up here. The paper-side numbers all replay green.

## FIG-1 (F-E)

- SCC structure: one transient SCC `{A₀, A₁} = {2, 4}` (boxed), two singleton
  bottom SCCs `{F₀} = {1}` and `{F₁} = {3}`. The kernel `{1, 3}` spans both
  bottom SCCs — the single fact the thick borders exist to show.
- x-vector at uniform by class id: `[2/3, 1, 1/3, 0, 2/3]`, so `μ = x_{[ε]} =
  2/3`. These are the `value_vector` entries, not recomputed for the drawing.
- Placement only: the `[ε]→F₀` `!a` edge is bent wide (40°) to clear the `A₀`
  node it would otherwise cross; `A₀`'s x-annotation sits north of the node for
  the same reason. Nothing else is hand-set.

## FIG-2 (F-D)

- `H(k) ≅ ℤ/2` is the one drawable case — the maximal group renders as a parity
  `r̄ = len(key) mod 2`, with `k` the even element. The probe verifies, per
  block, that folding the substring lands in `H(k)` and that its parity equals
  the block's length parity (the assertion `_r(cls) == len(block) % 2`).
- Seed choice: uniform sampling makes `aaaa` rare (`≈ 1/16` per position), so a
  short word rarely yields three `J`-cuts. `--scan` ranks seeds by word length
  and flags an *excursion* (the cumulative leaving `g` and returning — the
  pigeonhole recurrence the proof turns on). Seed `20260887` at length **56** is
  the shortest excursion found: block parities `[0, 0, 1, 1, 0]`, cumulative
  `[0, 0, 1, 0, 0]`, `g = 0`; the two `r̄ = 1` blocks straddle a non-`J` cut and
  their product returns to `k`. The seed and length are constants in `fig2.py`
  and printed in the figure's provenance; `_grow` would lengthen the word if a
  seed fell short of three `J`-cuts (it does not here).
- The stem `word[0:12]` happens to fold to `k` itself here, which is a legal
  member of `Stems(c, k)` (`k·k = k`); the bracket tags it as such.

## FIG-3 (F-D)

- Nine classes; SCCs `{0}`, `{1,3}`, `{2,5}`, `{4,7}`, `{6,8}`. The unique
  bottom SCC `K = {6, 8}` is the kernel (its two `R`-classes), double-circled
  and thick, tagged `≅ ℤ/2` and `θ = 1`.
- The right panel is four `Table.val` calls: `(fold(b), e')`, `(fold(bb), e')`,
  `(fold(b), k)`, `(fold(bb), k)` with `e' = fold(ba)`, `k = fold(aa)` — the
  tuple `(1, 0, 1, 1)`, asserted before drawing. The lasso names and the
  re-bracketing `u·(aa)^ω = (u·a)·(aa)^ω` are the paper's §3.4 text.
- x-annotations are suppressed here (`show_x=False`): F-D has `μ = 1` and the
  per-class value is `1` everywhere, which would only clutter the point of the
  figure (the kernel/phase contrast, not the measure).
- Placement only: intra-SCC node pairs are set 2.5 units apart so the two
  opposed edges and the merged loop-labels separate; the `4→8` edge is bent
  mildly to route below the graph.

## Toolchain

`pdflatex` (TeX Live 2023) + `pdftoppm` at 220 dpi. The `standalone` class crops
to the drawing, so a wide figure (FIG-2's ruler, FIG-3's two panels) simply
produces a wide PNG; the paper scales it to the column. All three compile in
well under a second with no warnings that reach the cropped output.
