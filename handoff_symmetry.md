# Handoff — SoS symmetry

Bootstraps a session on the symmetry thread. The thread has two roles:
**theory** owns the paper and works markdown-only (no code, no probes,
no browsing the tree); **practice** (engineering) implements the spec,
gates it, reports numbers. Read this, then jump to your role's TODO
list below; open the paper/spec/report only at their named sections.

## The documents and their roles

- **Paper — theory's product:** `research_notes/sos_symmetry.md`.
  Pre-paper draft. Three kinds of symmetry on `𝓘(L) = (𝒞, λ, M, P)`:
  *outer* (Thm 3.1 symmetry=automorphism, signed group `Sym±`,
  Lemma 3.2 pair-count obstruction, witness, symmetrization),
  *relational* (Thm 4.2 block substitution → stutter / invisible
  letters / `k`-ladder, Thm 4.4 the tolerated independence relation
  `Î_L`), *inner* (group spectrum, Prop 6.2 LTL hull/kernel
  `L♭ ⊆ L ⊆ L♯`), and the workflows (§7, incl. Prop 7.4 the symmetric
  envelope). Worked examples A–C + `EvenHead` are restated as
  machine-checkable predictions in §9 P1–P5. **Every unproven leap is
  flagged ⟨TBD⟩ — the ⟨TBD⟩s ARE the theory queue.**
- **Spec — engineering work order:** `research_notes/sos_symmetry_spec.md`.
  Milestones SY1–SY5, function-level. SY1 and SY3 are DONE; SY2, SY4,
  SY5 are OPEN (SY2/SY4 commissioned, SY5 after them, Y2 blocked). The
  paper is normative math; where spec and paper disagree, STOP and
  report — do not reconcile silently.
- **Report — engineering's channel to theory:**
  `research_notes/sos_symmetry_report.md`. Findings F1–F16; F1–F4
  (SY1) and F8–F11 (SY3) are filled, the rest pending. Its **To
  theory** section is what theory answers; it is current-state (open
  asks only — resolved items are removed once their outcome lands in
  the paper).
- **Figures — separate commission:** `research_notes/sos_symmetry_figures.md`.
  FIG-1 (kernel vs `Aut`), FIG-2 (`EvenHead` gap triptych), FIG-3
  (envelope schema). FIG-1/2 are buildable now (fixtures exist).
- **Code:** `sosl/sosl/sos/symmetry/` — `sigma.py` (SY1: `SignedPerm`,
  `apply_perm`, the checks, kernel read-off), `relations.py` (SY3:
  block-substitution read-offs). Gates + summary generators in
  `sosl/tests/symmetry/`; validated artifacts in `reference/symmetry/`
  (CSV + summary + gate log per milestone).

## State

- **Milestones:** SY1 accepted (F1–F4), SY3 accepted (F8–F11: the F8
  stutter oracle is 6 222/6 222, read-off count 896 = the `.cat`
  stutter-tag total). SY2, SY4, SY5 open.
- **Proofs landed:** Prop 6.2 (LTL hull/kernel) has a full proof —
  Lemma 6.2a (collapse-and-close is the least aperiodic congruence
  `θ_ap`), Lemma 6.2b (hull acceptance is the conjugacy closure of
  `q(P)`; `kernel = ¬∘hull∘¬`). The pair-count obstruction is
  Lemma 3.2.
- **Corpus:** `genaut/corpus/flat_canon/` — 6 222 canonical cases,
  2 484 non-LTL; by AP count 2 / 4 006 / 1 438 / 776 (0–3 APs). Two
  structural facts every census claim respects: alphabet-minimal (so
  `inert_aps` and invisible letters are 0 by construction, F3/F9), and
  64 % 1-AP (so symmetry rates are reported stratified by AP, never
  pooled).
- **Library** (`papers/`, gitignored — never pushed):
  - *Read and cited:* Arnold85, Thomas79, KR65, ES96, CEFJ96, ID96,
    Pel93, Godefroid-thesis, PW97, Straubing94, Etessami 2000,
    Diekert–Muscholl 1994, Gastin–Petit 1995, Sistla–Godefroid 2004
    (closest prior art to §7.4), Emerson–Havlicek–Trefler 2000
    (virtual symmetry), Moeller–Mohnke–Weber 1993, Wilke 1991.
  - *Held, unread — relevant to theory TODO 3–4:* Diekert–Gastin 2008,
    Diekert–Kufleitner 2009, Thérien–Weiss 86, Thérien–Wilke 01;
    Straubing–Thérien–Thomas 1995 (bitmap scan, no text extract,
    identity unverified — user has another route).

## TODO — theory (priority order)

1. **Confirm the `k`-ladder rung prose fix** (report open ask): change
   "`|v| ≤ k`" to "`|v| = k`" in paper §4.2 and spec §5. The `≤ k`
   reading is nested and makes the ladder parameter vacuous; `= k` is
   what the per-rung count, the F11 data, and the fixture gate all
   agree on. One word each, no math moves — cheap, do it first.
2. **Integrate SY3 into the paper.** F8 (stutter read-off = semantic
   tag, 6 222/6 222), F10 (`Î_L` density stratified 0.014 / 0.377 /
   0.771 at 1/2/3 APs — the §4.3 POR datum), F11 (the `k`-ladder is
   populated: 896 / 736 / 326 / 4 264). Numbers enter the paper in
   pure form only after they appear in the report — they now do.
3. **Thm 3.1 folklore status** (§3): the literature pass on
   automorphisms of syntactic monoids / minimal-DFA relabel-isomorphism
   (used in circuit symmetry detection) — decides how §3 is sold.
   Partly blocked on fetches (below).
4. **The ω-trace question** (§4.3): does `Î_L`-closure under disjoint
   swaps imply full ω-trace closure for recognizable `L`? Decides the
   POR claim's citation weight. Needs the Diekert–Muscholl /
   Gastin–Petit reading (both now held).
5. **Smaller ⟨TBD⟩s:** PW97-equivalence of Def 4.1's stutter closure;
   the deletion corollary (§4.2); Thm 5.1's renderer clause (needs a
   look at the ToLTL renderer — coordinate, don't wander);
   Emerson–Trefler positioning of §7.4.

**Fetches the user still grabs** (we never cite unread; PREFER papers
or single chapters — whole books are hard to get): Baziramwabo–
McKenzie–Thérien LICS'99 (modular temporal logic — may settle §6.1's
conjecture), Emerson–Trefler CHARME'99, Weeg 62 / Fleck 62 / Bavel 68
(automata automorphisms, the folklore trail for Thm 3.1), Pin
"Syntactic semigroups" (Handbook of Formal Languages ch. 10, 1997).

## TODO — practice (priority order)

1. **SY2 — the group, witness, symmetrization** (spec §4). Unblocks
   the entire Y-series. Note from F4: generator scans under-detect —
   they find only ~35 % of nontrivial groups at `n = 3` (most
   symmetric elements are composite signed swaps / 3-cycles), so the
   full group walk is not optional. Fills F5–F7.
2. **SY4 — spectrum + LTL hull/kernel** (spec §6). Highest theory
   value: F12 (the LTL-bit oracle — run FIRST, the §6 twin of F8),
   F13 (**any nonabelian/non-solvable spectrum specimen is a headline
   find — file the moment it appears**), F14 (the leastness probe now
   gates the `aperiodic_reflection` implementation of Lemma 6.2a).
   One commissioned `classify` change only: promote the group
   `H`-class walk to a shared helper (§6.1). Fills F12–F14.
3. **SY5 — the Y-series campaigns** (spec §7), after SY2/SY4. Y0a/Y0s/
   Y1 need SY2; Y0b/Y0c need SY4. **Y2 is BLOCKED on a ToLTL engine
   hook — do not start it, do not build the hook.** Fills F15–F16.
4. **Loose end:** countersign `max |𝒞| = 208` into `sy1_summary.md`
   at the next SY1 regen (the paper's §3.1 cost remark cites it).
5. **Figures:** FIG-1/FIG-2 can run independently now — fixtures live
   in `sosl/tests/symmetry/fixtures.py`.

Recommended next round: **practice — SY4** (its F12/F13/F14 feed open
theory items, and theory's own TODO 3–4 is fetch-blocked). SY2 is the
alternative if you would rather build toward the Y-series.

## The one theorem to keep in your head

Thm 3.1 (iii): `σ(L) = L` iff the canonical keying of
`(𝒞, λ∘σ, M, P)` is byte-equal to `𝓘(L)` — one free λ-rewire, one
keying pass, one byte comparison; no product, no language query. Its
runtime shadow (the kernel law): `λ∘σ = λ` cellwise forces the full
check true; a violation is an upstream keying bug, never a fact about
`L`.

## Gotchas

- Concurrent sessions commit to this repo. Commit ONLY your files by
  explicit path; never `git add -A`; never rewrite history. Commit
  style: `git commit -F -` heredoc, terse. Standing authorization:
  commit as you go without asking; pushing is ALWAYS asked separately.
- `papers/` is gitignored deliberately (copyright — never push its
  content). The paper's reference entries carry the library filename
  of everything read.
- The paper states results in pure form and cites no artifact paths;
  numbers enter it only after they appear in the report.
- Spec/report/paper move together: renumbering or renaming in one
  propagates to the other two in the same commit (grep the old name).
- Worked-example arithmetic in the paper is load-bearing (spec fixture
  gates assert it). If you touch an example, re-derive by hand and
  update §9 P1–P5 and the spec's §3.4/§6.3 expectations together.
