# genaut — exhaustive small-ω-automaton census

A standalone experiment (NOT wired into the `aut2ltl/` package): for a fixed
**shape**, exhaustively enumerate every tiny ω-automaton of that shape, reduce each
with Spot, then carry the survivors through the sosl construction to their
canonical forms — measuring how many *automata* collapse to how many *languages*,
and feeding the reference corpora the rest of the repo surveys and classifies. The
generator is parametric over `Shape(n, k, c, acc)` — `n` states, `k` atomic
propositions, `c` acceptance sets, and an acceptance **family** over those colours
(`gba` generalized-Büchi, the default; `parity`) — and the bestiary spans every
tractable shape; see [`corpus/SHAPES.md`](corpus/SHAPES.md) for the map, the dedup funnel, and
the tractability wall. Exhaustive enumeration does not scale far, so this is a
one-off census per shape, not a permanent runtime generator.

## The four corpus tiers

Each shape lives in `corpus/` under four tiers, coarsest to canonical:

    corpus/tgba/<tag>/     the enumerated survivors: deterministic-or-not, reduced
                         TGBA (HOA), deduplicated only up to a<->!a polarity and
                         AP renaming. Written by gen/enumerate.py. This is the raw
                         presentation census — many encodings per language.

    corpus/spot_det/<tag>/ the canonical deterministic automaton D (sosl's
                         importer.canonical, the SoS algorithm's input), deduplicated
                         STRUCTURALLY — by D's AP-canonical bytes, the tgba gate — not
                         by language. One per deterministic presentation. gen/canonize.py.

    corpus/det/<tag>/    the canonical automaton D of each distinct language:
                         deterministic, complete, transition-based, generic
                         acceptance (sosl's importer.canonical), as HOA. One
                         representative per language. Written by gen/canonize.py.

    corpus/sos/<tag>/    the syntactic ω-semigroup 𝓘(L) of each distinct language,
                         as `.sos` — the compact canonical form downstream runs
                         (e.g. the classifier) consume directly, no presentation to
                         reduce. One per language. Written by gen/canonize.py.

`det/` and `sos/` are 1:1 (one per language) and are deduplicated by the
**syntactic key**: the canonical `𝓘` dump ([SωS26 Thm. 5.1] — byte-equal iff the
languages are equal). Going `tgba/` -> `det/` collapses every relabel- and
presentation-distinct automaton of one language onto a single entry; the collapse
is large where nondeterminism proliferates presentations (`2state1ap1acc`: 929
TGBA -> 129 languages) and near 1 where the shape is already language-sparse.

## The flat pool — cross-shape union of distinct languages

The per-shape tiers language-dedup *within* a shape, but the same language recurs
*across* shapes: a bigger shape emits a superset of a smaller one's languages (more
states / colours / a parity acceptance over the **same** alphabet). `corpus/flat/`
folds that redundancy into one pool — `flat/det/` + `flat/sos/`, **one file per
distinct language**, kept from the **smallest** shape that emits it so the
`<tag>_<id>` name traces the language to its minimal setting — plus a `census.md` +
`flat.json` composition report. Built by `gen/flatten.py`.

The dedup notion is **language identity up to a fixed AP labeling** (the `.sos`
`𝓘` key; cross-`k` languages never collide, being over different alphabets).
Shapes are traversed in a linear extension of the subset order — `(n, k, c,
family)` with `gba < parity` — exhaustive shapes first, the non-exhaustive
`sampled/` folders appended last (contributing only languages no census shape
reached). Folding relabel/polarity twins (`GF(a) ≡ GF(!a)`) is a **later** work
item; until then a sampled folder may report "new" languages that are only
opposite-polarity twins of census ones (its encounter-order representative choice
— see "Polarity / relabeling" below).

    python3 genaut/gen/flatten.py            # (re)build corpus/flat/
    python3 genaut/gen/flatten.py --exclude 2state2ap0acc   # default: drop dominators

### corpus/flat_canon — the irredundant, complement-closed catalogue

`flat/` still counts a language once **per AP labeling and alphabet size**:
`GF(a)`, `GF(!a)`, and `GF(a)`-with-a-declared-unused-`b` are three entries.
`corpus/flat_canon/` folds those away — one representative per language **up to
renaming its symbols**: the `B_k` orbit-min of the syntactic `𝓘` (signed AP
permutations, `sosl.sos.relabel`) over the **alphabet-minimized** automaton
(`remove_unused_ap` sheds APs no edge uses). Both det and `.sos` are relabeled
into the canonical labeling (a self-consistent pair), smallest-shape name kept.
The relabeling is chosen on the semigroup core, so complement stays "flip
`accept`" byte-exact — which is used to **close the catalogue under complement**:
every language's dual is present, added (where the enumeration was one-sided) as
`<primal>_c` (`.sos` by flipping `P`, det by `spot.dualize`, the two cross-checked).
No language equals its own complement, so the closed catalogue is **even**.
Built by `flatten.py --canon` (heavier: it runs the sosl construction per
language). The rationale — why these axes are the complete redundancy of an
exhaustive sweep — is `research_notes/genaut_corpus.md`.

    python3 genaut/gen/flatten.py --canon    # also (re)build corpus/flat_canon/

Every language also carries a **`.cat` sidecar** next to its `.sos`
(`sos/<name>.cat`) — its *category*: the LTL / non-LTL cut, stutter-invariance
(the X-free refinement of LTL), and the Wagner degree `ϕ = (γ, s)` with
`(m⁺, m⁻, n⁺, n⁻)` coordinates and class name, read off the invariant `𝓘(L)`
(`sosl.sos.classify`, a pure table search — no automaton, no Spot). One `.cat`
per language covers both the `.sos` and the `det/` HOA of that basename (a
category is a language property). Written by `sosl.sos.classify.io` (also invoked
at the end of `flatten.py --canon`, so a rebuild keeps them in sync);
re-runnable standalone over any `sos/` tier:

    python3 -m sosl.sos.classify.io <sos-folder>   # from sosl/; writes *.cat

`flat_study.py` renders the language-level benchmark study
(`corpus/flat_canon/STUDY.md`): headline census, **the LTL cut** and its
**stutter-invariant** refinement, the **Wagner-degree profile** (aggregated from
the `.cat` sidecars — duality-symmetric
over the complement-closed catalogue), composition, and per-origin-shape states /
algebra size — the language view, complementary to `SHAPES.md`'s presentation
funnel (which shape-reading consumers still use).

    python3 genaut/flat_study.py             # -> corpus/flat_canon/STUDY.md

## The slot model (the tgba tier)

State `q0` is always initial. For every ordered pair `(src, dst)` and every
acceptance **markset** (subset of the `c` colours) there is one **edge slot**, whose
guard is any Boolean function over the `k` APs, with the all-false guard meaning
"edge absent". So `slots = n²·2^c`, each with `2^(2^k)` guard choices, giving
`N = (2^(2^k))^slots` raw automata. For `k = 1` the guard alphabet is `{0, a, !a, 1}`.
The acceptance **family** (`gba` / `parity`) is orthogonal to the slot enumeration —
same slots, guards, marksets, and combo ids; only the acceptance *formula* changes
(`gba`: `Inf(0)∧…∧Inf(c−1)`; `parity`: `parity max even c`). So a `_parity` shape
reuses the id space of its `gba` twin.

This slot set is **fully general** — a separate slot per markset covers parallel
coloured edges, and we deliberately do *not* hand-prune "useless" slots, so full
enumeration plus dedup cannot accidentally miss a language. The construction is
detailed in [`gen/algorithm.md`](gen/algorithm.md).

## Pipeline

1. **Enumerate** every combo for a shape (`gen/enumerate.py n,k,c[,acc]`), running
   **one** `spot.postprocess(generic, high, small)` pass on each (keeps the
   acceptance family, no determinization; Small is a polynomial structural reducer),
   and applying the two pre-write dedup gates — byte-identical (md5), then
   AP-canonical (polarity ∘ names, from `survey/normalize`). Survivors are written
   `raw/<tag>/<tag>_<id>.hoa` with a `census.md` (combos / byte-distinct / kept).

       python3 genaut/gen/enumerate.py 2,1,1            # -> genaut/raw/2state1ap1acc/
       python3 genaut/gen/enumerate.py 1,2,2,parity     # -> genaut/raw/1state2ap2acc_parity/
       # validate, then promote raw/<tag>/ -> corpus/tgba/<tag>/

2. **Canonize** the promoted TGBA tier to the canonical tiers (`gen/canonize.py
   <tag>`): each survivor -> canonical D -> `𝓘(L)`, deduplicated by the `𝓘` key,
   writing `corpus/det/<tag>/*.hoa` + `corpus/sos/<tag>/*.sos` and a `census.md`
   recording the **language-distinct** funnel step. `gen/rebuild.py` loops this over
   every shape (skips shapes already built; `--force` to regenerate).

       python3 genaut/gen/canonize.py 2state1ap1acc     # -> corpus/det + corpus/sos
       python3 genaut/gen/rebuild.py                    # (re)build all shapes

3. **Regenerate `corpus/SHAPES.md`** — the funnel table, joined from the tgba + det
   census.md by `shapes_table.py` (cheap, no re-run).

       python3 genaut/shapes_table.py

4. **Survey / classify** — genaut's corpora are just more reference corpora. Run
   `aut2ltl` over a tier with the repo harness (`survey`), or classify the language
   profile of a shape over the compact `sos/` tier (fast: no construction):

       python3 -m survey --folder genaut/corpus/tgba/2state1ap1acc \
           --logs genaut/reference/rerun/2state1ap1acc > .../SUMMARY.txt
       # from sosl/: the Wagner-degree profile of a shape's languages
       python3 -m tests.sosl.classify_census ../genaut/corpus/sos/2state1ap1acc \
           --logs tests/sosl/logs/<tag>
       python3 -m tests.sosl.classify_profile tests/sosl/logs/<tag>/records.csv

5. **Analyse** a survey run into a frontier report (pure CSV, no re-run):

       python3 genaut/analyze_frontier.py genaut/reference/<tag>/default.csv \
           --out genaut/reference/<tag>/frontier.pdf

## Extending the census — add a shape or an acceptance family

1. Pick a shape under the wall (`SHAPES.md`'s second table lists the first
   intractable ones). Add an acceptance family by passing the 4th `acc` token to
   `enumerate.py` (e.g. `1,2,2,parity`); the tag gains a `_<acc>` suffix, the `gba`
   default stays bare (retro-compatible: existing folders/ids are untouched, the
   acceptance being orthogonal to the combo enumeration).
2. `enumerate.py n,k,c[,acc]` -> validate `raw/<tag>/` -> promote to
   `corpus/tgba/<tag>/`.
3. `python3 genaut/gen/rebuild.py <tag>` builds its `det/` + `sos/` tiers.
4. `python3 genaut/shapes_table.py` refreshes `corpus/SHAPES.md` (into the
   scratch write root by default; `--out genaut/corpus` to adopt).
5. To add a *new acceptance family* beyond `gba`/`parity`, teach
   `gen/build.py::_set_acceptance` the family's Spot acceptance formula; everything
   downstream (tags, dedup, tiers, funnel) follows.

## File map

    corpus/SHAPES.md the bestiary map: every shape's combos -> byte -> kept ->
                     langs funnel + the wall. Generated by shapes_table.py.
    corpus/MANIFEST.md  the reduction funnel per shape x acceptance family.
                     Generated by manifest.py.
    shapes_table.py  regenerate corpus/SHAPES.md from corpus/tgba + corpus/det
                     census.md (--corpus reads, --out writes; default scratch).
    research_log.md  dated, dense log of observations (append-only).
    gen/             the generator (its own algorithm.md):
                       shape.py      Shape(n,k,c,acc): slot model, guard alphabet,
                                     marksets, acceptance family, id<->combo (pure).
                       build.py      a combo -> Spot automaton (family acceptance) + reduce.
                       enumerate.py  enumerate -> reduce -> 2 dedup gates -> write
                                     raw/<tag>/<tag>_<id>.hoa + census.md.
                       canonize.py   a tgba shape -> canonical D (det/) + 𝓘 (sos/),
                                     deduped by the syntactic key + census.md.
                       rebuild.py    loop canonize over shapes (skip built; --force).
                       flatten.py    cross-shape union -> corpus/flat/ (det + sos +
                                     census.md + flat.json), deduped by language;
                                     ends by writing the .cat sidecars via
                                     sosl.sos.classify.io.
    analyze_frontier.py
                     one frontier report from a survey CSV (digest + PDF).
    probes/          diagnostics from the original 2state1ap1acc study.
    raw/<tag>/       enumerate.py's scratch output (gitignored, regenerable). The
                     validated, git-tracked snapshot lives in corpus/tgba/<tag>/.
    corpus/tgba/<tag>/   enumerated TGBA survivors + census.md (git-tracked).
    corpus/det/<tag>/    canonical D per language (HOA) + census.md.
    corpus/sos/<tag>/    syntactic 𝓘 per language (.sos) + census.md.
    corpus/flat/         cross-shape union: one det+sos per distinct language,
                     smallest-shape naming + census.md + flat.json.
    corpus/flat_canon/   the irredundant catalogue: one det+sos per language up to
                     AP relabeling + unused-AP dropping (B_k orbit-min of flat/),
                     complement-closed; each language also carries a sos/*.cat
                     category sidecar (LTL cut + stutter-invariance + Wagner
                     degree). STUDY.md is the
                     language-level study (flat_study.py).
    logs/<tag>/      the committed reference survey run per shape.

## Sampling beyond the wall — `gen/sample.py`

For shapes past the tractability wall (`SHAPES.md`: id spaces of 1e9+), exhaustive
enumeration is infeasible, but a **reproducible random sample** of the id space is
cheap and, for our purposes, enough. `gen/sample.py` draws combo ids uniformly at
random under a fixed seed, decodes each with the **index trick** — a direct
base-`|guards|` decode, O(`|slots|`), *not* `Shape.combo_at` (which is O(index) and
unusable on a 1e9 space) — and runs the exact census chain on it
(`build → reduce → canonical D → 𝓘`), keeping a language only when it is new.

    python3 genaut/gen/sample.py 2,1,2,parity --target-langs 1024 --seed 0

It stops at `--target-langs` distinct languages (default 1024), or `--sample K`
draws, or a `--max-draws` safety cap — whichever first — and writes a
**clearly-non-exhaustive** tree so it never masquerades as a census:

    corpus/sampled/<tag>__seed<S>/det/  + /sos/  + sample.json  (exhaustive:false)

Dedup gates are the census's own: reduced-HOA md5, then `default_key`
(polarity∘names), then the `𝓘` dump. Sampling is uniform over *presentations*, so
a presentation-rich language is likelier drawn — the sample is a probe, not a
census, and cannot support an "all languages" claim (those live at the exhaustive
small shapes). Two placed tests guard it: `tests/sample_decode.py` (the fast
decoder equals `Shape.combo_at`) and `tests/sample_subset.py` (the per-id chain
reproduces the census `.sos` byte-for-byte — 129/129 on `2state1ap1acc`, proving
the sampler skips no pipeline step).

## Polarity / relabeling — a known non-canonicalization

The `𝓘` / `.sos` form is **polarity-sensitive**: `GF(a)` and `GF(!a)` produce
different `.sos`. Languages are deduplicated only **up to `polarity∘names` at the
HOA text level** (`enumerate.py`'s `default_key`, from `survey.normalize` — it
makes each AP's *first literal occurrence* positive and renames APs in order). That
is a dedup **key**, not a structure-robust language-up-to-relabeling canonical
form. Consequences:

- The kept representative's polarity is **encounter-order dependent**, so two runs
  — or the census vs. a sample — may store the *same language in opposite
  polarity*, i.e. different `.sos` bytes for one language. (This is representative
  choice, not a pipeline defect: `tests/sample_subset.py` shows the per-id chain is
  byte-faithful to the census.)
- Because the fold is text-first-occurrence based, structurally-different **relabel
  twins can slip through as distinct** — so the corpus (and any sample) may carry
  near-duplicate languages that differ only by an AP relabeling.

Two candidate fixes, **neither implemented**:

- **Option 1 — dedup at generation.** Build each HOA, map it straight to its
  language `𝓘`, polarity-normalize, dedup, and keep the HOA only if the language is
  new. *Downside:* this yields exactly one HOA per language — it destroys the
  presentation multiplicity the `tgba/` tier exists to measure (the whole
  combos→byte→kept→langs funnel collapses). Bad.
- **Option 2 — canonicalize the `.sos` we have.** For each language, try all
  `2^k · k!` AP relabelings of its `𝓘`, adopt the byte-smallest as the canonical
  representative. Then `.sos` byte-equality *is* language-equality up to relabeling
  ("`GF(a)`, never `GF(!a)`"). *Downside:* the relabeling group is explosive in `k`
  (`2^k·k!` = 48 at k=3), and it must be applied to the `det/` HOA and the `.sos`
  **together** — otherwise the learner, which learns from the det automaton and
  byte-compares its exported `.sos` to the reference, breaks on a mismatched
  polarity.

**Status: neither is done.** Consumers of `corpus/sampled/` (and, strictly, the
census tiers too) must read "distinct language" as "distinct over a fixed AP
labeling, deduped up to text-level `polarity∘names`" — relabel twins may appear.
