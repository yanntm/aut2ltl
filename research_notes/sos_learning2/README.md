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

Restructure in progress: §4 is rebuilt around the *alignment* primitive
(two signals — concordant bits confirm, discordant bits align; one
substitution-chain lemma serving all discordance sources; EQ as the
delegated discordance search, assent the exit). The wired sources are
`s4a_align.md` (preamble, chain, Theorem 4.2), `s4b_escalate.md`
(legality escalations), `s4c_life.md` (align assembled,
prefix-independence, bootstrap + alternation). `s4a_reap.md` and
`s4b_sow.md` are the superseded §4 sources, unwired but kept until the
cross-reference sweep. Known-stale until that sweep: §5–§7 cite the old
§4 numbering — map: old L4.1+L4.2+T4.3 → L4.1 (chain) + T4.2 (split);
L4.4 → L4.3; L4.5 → L4.4; P4.6 → P4.5; C4.7 → C4.6; L4.8 → L4.7 — and
the retired reap/sow–harvest vocabulary. §5 is slated for dissolution by
redistribution (legality → §3.2, termination/no-false-assent → end of
§4, complexity itemization → §7.2, FDFA size proposition → §7.4).
