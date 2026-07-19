# sos_learning2 — *Learning the Syntactic ω-Semigroup*

The learning paper, built on the vocabulary of the core paper
(`../sos_core.md`, cited [SωS26]). Self-contained: this folder plus the
core paper is the whole thread.

- `algorithm.md` — the design in brief: the legal-learner discipline, the
  split mechanism, why it converges, why it is necessary, and the pending
  engineering deltas (code refactor + census regeneration). **Read first.**
- `s0_front.md … s8_end.md`, `bib.md` — the paper parts, assembled by
  `make` into `../sos_learning2.md` (do not edit the assembled file).
- Figures are referenced from `../sos_figs/` and `../sos_core_figs/`
  (shared figure folders; the `sosl_*` images are the learner-side
  frames).

Status: full shadow draft. The theory sections (§3–§6) are current; the
evaluation numbers in `s7_eval.md` were measured with the pre-reboot
pipeline and carry a status note — regeneration is item 5 of
`algorithm.md`'s engineering deltas. Notation: learner's mid-run classes
`⟨u⟩`, syntactic classes `[u]`, keys `u_c`, letter action `c·w`; no
`fold`/`rep` vocabulary.
