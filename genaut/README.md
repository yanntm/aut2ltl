# genaut — exhaustive small-ω-automaton census

A standalone experiment (NOT wired into the `aut2ltl/` package): for a fixed
**shape**, exhaustively enumerate every tiny ω-automaton of that shape, reduce each
with Spot, then carry the survivors through the sosl construction to their
canonical forms — measuring how many *automata* collapse to how many *languages*,
and feeding the reference corpora the rest of the repo surveys and classifies. The
generator is parametric over `Shape(n, k, c, acc)` — `n` states, `k` atomic
propositions, `c` acceptance sets, and an acceptance **family** over those colours
(`gba` generalized-Büchi, the default; `parity`) — and the bestiary spans every
tractable shape; see [`SHAPES.md`](SHAPES.md) for the map, the dedup funnel, and
the tractability wall. Exhaustive enumeration does not scale far, so this is a
one-off census per shape, not a permanent runtime generator.

## The three corpus tiers

Each shape lives in `corpus/` under three tiers, coarsest to canonical:

    corpus/tgba/<tag>/   the enumerated survivors: deterministic-or-not, reduced
                         TGBA (HOA), deduplicated only up to a<->!a polarity and
                         AP renaming. Written by gen/enumerate.py. This is the raw
                         presentation census — many encodings per language.

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

3. **Regenerate `SHAPES.md`** — the funnel table, joined from the tgba + det
   census.md by `shapes_table.py` (cheap, no re-run).

       python3 genaut/shapes_table.py

4. **Survey / classify** — genaut's corpora are just more reference corpora. Run
   `aut2ltl` over a tier with the repo harness (`survey`), or classify the language
   profile of a shape over the compact `sos/` tier (fast: no construction):

       python3 -m survey --folder genaut/corpus/tgba/2state1ap1acc \
           --logs genaut/logs/rerun/2state1ap1acc > .../SUMMARY.txt
       # from sosl/: the Wagner-degree profile of a shape's languages
       python3 -m tests.sosl.classify_census ../genaut/corpus/sos/2state1ap1acc \
           --logs tests/sosl/logs/<tag>
       python3 -m tests.sosl.classify_profile tests/sosl/logs/<tag>/records.jsonl

5. **Analyse** a survey run into a frontier report (pure CSV, no re-run):

       python3 genaut/analyze_frontier.py genaut/logs/<tag>/default.csv \
           --out genaut/logs/<tag>/frontier.pdf

## Extending the census — add a shape or an acceptance family

1. Pick a shape under the wall (`SHAPES.md`'s second table lists the first
   intractable ones). Add an acceptance family by passing the 4th `acc` token to
   `enumerate.py` (e.g. `1,2,2,parity`); the tag gains a `_<acc>` suffix, the `gba`
   default stays bare (retro-compatible: existing folders/ids are untouched, the
   acceptance being orthogonal to the combo enumeration).
2. `enumerate.py n,k,c[,acc]` -> validate `raw/<tag>/` -> promote to
   `corpus/tgba/<tag>/`.
3. `python3 genaut/gen/rebuild.py <tag>` builds its `det/` + `sos/` tiers.
4. `python3 genaut/shapes_table.py` refreshes `SHAPES.md`.
5. To add a *new acceptance family* beyond `gba`/`parity`, teach
   `gen/build.py::_set_acceptance` the family's Spot acceptance formula; everything
   downstream (tags, dedup, tiers, funnel) follows.

## File map

    SHAPES.md        the bestiary map: every shape's combos -> byte -> kept ->
                     langs funnel + the wall. Generated by shapes_table.py.
    shapes_table.py  regenerate SHAPES.md from corpus/tgba + corpus/det census.md.
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
    analyze_frontier.py
                     one frontier report from a survey CSV (digest + PDF).
    probes/          diagnostics from the original 2state1ap1acc study.
    raw/<tag>/       enumerate.py's scratch output (gitignored, regenerable). The
                     validated, git-tracked snapshot lives in corpus/tgba/<tag>/.
    corpus/tgba/<tag>/   enumerated TGBA survivors + census.md (git-tracked).
    corpus/det/<tag>/    canonical D per language (HOA) + census.md.
    corpus/sos/<tag>/    syntactic 𝓘 per language (.sos) + census.md.
    logs/<tag>/      the committed reference survey run per shape.
