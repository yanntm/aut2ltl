# Handoff — SoS symmetry

Bootstraps a session continuing the symmetry thread. This thread is
**theory**: it owns the paper and works on markdown only — no probes,
no code, no browsing the tree (concurrent sessions own the code side).
Read this, then the paper's header + §1; open the spec/report only at
their named sections.

## The four documents and their roles

- **Paper (this thread's product):** `research_notes/sos_symmetry.md`
  — pre-paper draft, 2026-07-11. Three kinds of symmetry on
  `𝓘(L) = (𝒞, λ, M, P)`: outer (Thm 3.1 symmetry=automorphism, signed
  group `Sym±`, anti-symmetries + pair-count obstruction, witness,
  symmetrization), relational (Thm 4.2 block substitution → stutter,
  invisible letters, `k`-ladder, `Î_L` Thm 4.4), inner (group
  spectrum, Prop 6.2 LTL hull/kernel `L♭ ⊆ L ⊆ L♯`), workflows
  (§7, incl. Prop 7.4 the symmetric envelope — sound quotient
  checking for ANY `G`, no symmetry assumed). Four hand-worked
  examples (A `GFa`, B `GFa∧GFb`, C `a·Σ^ω`, `EvenHead a^{2n}b^ω`)
  are restated as machine-checkable predictions §9 P1–P5. Every
  unproven leap is flagged ⟨TBD⟩ — the TBDs ARE the theory queue.
- **Spec (engineering work order, NOT ours to execute):**
  `research_notes/sos_symmetry_spec.md` — milestones SY1–SY5; SY1
  (signed perms, single check, kernel read-off) is commissioned to
  the function level, nothing built yet. We revise it when theory
  changes; disagreements found by engineering come back via the
  report, and we own the resolution.
- **Report (engineering's channel to us):**
  `research_notes/sos_symmetry_report.md` — slots F1–F16 all
  *pending*; its **To theory** section is what we must answer when
  it fills.
- **Figures (separate commission):**
  `research_notes/sos_symmetry_figures.md` — FIG-1 (kernel vs `Aut`),
  FIG-2 (`EvenHead` gap triptych), FIG-3 (envelope schema); 1–2 are
  buildable now (canonize + small probe), for a figure session.

## State (2026-07-11)

- Paper: skeleton complete, examples integrated, one editorial pass
  done (proof gaps of Thm 3.1 closed, log-speak scrubbed, numbering
  consistent — Prop is **6.2**, not 6.4). Citation-verified against
  the library: every referenced entry we hold has been read
  (Arnold's congruence stated in his original form + context-form
  equivalence; KR65 divisor fact = proof of Cor. 3.2(b); Str94
  Thm VII.2.1; ID96 is scalarsets NOT a formula check).
- Library: `papers/` (gitignored, never pushed) holds Arnold85,
  Thomas79, KR65, ES96, CEFJ96, ID96, Pel93, Godefroid-thesis,
  PW97, Straubing94, and (unread, relevant to queue items 2–3)
  Diekert–Gastin 2008, Diekert–Kufleitner 2009, Thérien–Weiss 86,
  Thérien–Wilke 01. Fetched 2026-07-11 (renamed + .txt extracted):
  Etessami_2000_IPL, Diekert_Muscholl_1994_ActaInf (pp. 379–397),
  Gastin_Petit_1995_BookOfTraces, Sistla_Godefroid_2004_TOPLAS
  (reduced symmetry — closest prior art to §7.4),
  Emerson_Havlicek_Trefler_2000_LICS (virtual symmetry),
  Moeller_Mohnke_Weber_1993_ICCAD, Wilke_1991_ICALP;
  Straubing_Therien_Thomas_1995_IC.pdf is a bitmap scan — NO text
  extract yet (user has another route), identity unverified. Still
  to fetch (user grabs; we do not cite without reading; PREFER
  PAPERS or single chapters — whole books are hard to get):
  Baziramwabo–McKenzie–Thérien LICS'99 (modular temporal logic —
  may settle §6.1's conjecture), Emerson–Trefler CHARME'99 [ET99],
  Weeg 62 / Fleck 62 / Bavel 68 (automata automorphisms, folklore
  trail for Thm 3.1), Pin "Syntactic semigroups" (Handbook of
  Formal Languages ch. 10, 1997 — the paper-sized Eilenberg/Almeida
  substitute).
- Engineering: SY1 accepted; `sosl.sos.symmetry` exists (sigma.py:
  SignedPerm, apply_perm, both checks, kernel read-off, obstruction).
  Fixtures live in `sosl/tests/symmetry/fixtures.py`; gates + census
  in `sigma_gate.py`; validated artifacts in `reference/symmetry/`
  (CSV, summary, gate log); report F1–F4 filled from them. SY2/SY3
  are the open milestones. The corpus is 6 222 cases (2 484 non-LTL);
  paper/spec counts are current. The report's four **To theory**
  items are ANSWERED (2026-07-11, responses appended in place):
  counts swept (incl. max `|𝒞|` 121→208, countersign asked); F3
  decided as (a) — coincidence-of-read-offs is the finding,
  §3.1/§9 rewritten, spec §3.4 FIX_A now calculus-built; the
  obstruction is now **Lemma 3.2** (proof + census sharpness);
  measurement design adopted (b)+(c) — stratified-by-AP mandate
  (spec §0) + new **Y0s** symmetrized-ground-truth campaign
  (spec §7), 4-AP sampling named follow-up, not SY5.

## Next tasks

Theory queue, priority order (all are ⟨TBD⟩s in the paper):

1. **Prove Prop 6.2** — DONE (2026-07-11, commit 70ca83a82).
   Lemma 6.2a: collapse-and-close IS the least aperiodic congruence
   (proved); Lemma 6.2b: lifting + saturation law (pair set is a
   language iff conjugacy-closed); full proof of Prop 6.2 incl. a
   CORRECTION — hull acceptance is the conjugacy closure of `q(P)`
   after projecting, one-shot `q⁻¹(q(P))` is not presentation-
   independent — plus duality `kernel = ¬∘hull∘¬`. EvenHead/P5
   unaffected (closure trivial there, now asserted). Spec §6.2
   rewritten to match; F14 probe now gates the implementation.
   Open sub-question kept in the paper as a remark: whether one
   collapse round always suffices (census datum, F14).
2. **Literature pass for Thm 3.1's folklore status** (automorphisms
   of syntactic monoids; minimal-DFA relabel-isomorphism is used in
   circuit symmetry detection) — decides how §3 is sold. Blocked
   partly on fetches; Eilenberg vol. A and Almeida are candidates.
3. **The ω-trace question** (§4.3): does `Î_L`-closure under
   disjoint swaps imply full ω-trace closure for recognizable `L`?
   Needs Diekert–Muscholl / Gastin–Petit. Decides the POR claim's
   strength.
4. Smaller: PW97-equivalence of Def 4.1's stutter closure; the
   deletion corollary (§4.2); Thm 5.1's renderer clause (needs a
   look at the ToLTL renderer — coordinate, don't wander);
   Emerson–Trefler positioning of §7.4 once fetched.

Engineering next (separate session, weaker model, spec-driven):
**SY2** (group, witness, symmetrization — spec §4) and/or **SY3**
(relational read-offs — spec §5; its corpus stutter oracle F8 runs
FIRST). SY1 is done, acceptance passed (report F1–F4). Note for
SY2: the census says most symmetric elements are composite —
generator scans find only ~35 % of nontrivial groups at n = 3
(report F4) — so the full group walk is not optional. Figures
session can run FIG-1/FIG-2 independently (fixtures exist:
`sosl/tests/symmetry/fixtures.py`).

The four To-theory items are DONE (2026-07-11, commit
3f03c5c46 — see State). Theory next is the queue above, Prop 6.2
first. One loose end from item 1: engineering should countersign
max `|𝒞| = 208` in `sy1_summary.md` at the next regen.

## The one theorem to keep in your head

Thm 3.1 (iii): `σ(L) = L` iff the canonical keying of
`(𝒞, λ∘σ, M, P)` is byte-equal to `𝓘(L)` — one free λ-rewire, one
keying pass, one byte comparison; no product, no language query.
Its runtime shadow (the kernel law): `λ∘σ = λ` cellwise forces the
full check true; a violation is an upstream keying bug, never a fact
about `L`.

## Gotchas

- Concurrent sessions commit to this repo. Commit ONLY your files by
  explicit path; never `git add -A`; never rewrite history. Commit
  style: `git commit -F -` heredoc, terse. Current standing
  authorization (this thread): commit as you go without asking;
  pushing is ALWAYS asked separately.
- `papers/` is gitignored deliberately (copyright — never push
  content from it). Reference entries in the paper carry the library
  filename of everything read.
- The paper states results in pure form and cites no artifact paths;
  numbers enter the paper only after they appear in the report.
- Spec/report/paper must move together: renumbering or renaming in
  one propagates to the other two in the same commit (grep for the
  old name — "Prop 6.4" was one such sweep).
- Worked-example arithmetic in the paper is load-bearing (spec
  fixture gates assert it). If you touch an example, re-derive by
  hand and update §9 P1–P5 and the spec's §3.4/§6.3 expectations
  together.
