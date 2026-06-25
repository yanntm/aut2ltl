# aut2ltl.spotrun — time-bounded delegation to Spot

`translate(f, *, timeout)` is the single seam through which the construction
turns a formula into an automaton (`ltl2tgba`). Isolating that one heavy,
sometimes-erratic Spot call here lets the policy for *how* it runs — guarded,
bounded, declined — live in one place rather than inlined at the call site. It
returns the automaton, or raises `UntranslatableLanguage` (the per-node decline
the portfolio's `best_of` absorbs).

It declines a translate two ways:

- **Size guard (primary).** A formula whose temporal count or *unfolded* (flat)
  size is over budget is refused up front, O(DAG), before any flatten or call —
  we decline rather than drive Spot toward an OOM. Knobs
  `spotrun.translate_tree_limit` / `translate_temporal_limit`.
- **Wall-time (secondary).** A formula that passes the guard yet still translates
  slowly is bounded by `spotrun.translate_timeout` and killed on overrun. This
  needs a child process: an in-process Spot C++ call holds the GIL and cannot be
  interrupted, so `timeout` set routes through the killable `ltl2tgba` binary
  (via `aut2ltl.bounded`), while `timeout=None` keeps the fast in-process call.

It sits below `Language` (no `Language` import, no cache of its own) and depends
only on `spot`, `aut2ltl.bounded`, `aut2ltl.options`, and the leaf
`aut2ltl.ltl.metrics`. Only `ltl2tgba` is isolated; small in-process Spot
operations (`autfilt`-family) stay where they are.
