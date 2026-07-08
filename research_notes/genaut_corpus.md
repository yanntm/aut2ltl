# The genaut corpus — irredundant coverage of the small-ω-language space

**Working reference — 2026-07-08.** How the genaut census turns an exhaustive
enumeration of *automaton presentations* into an irredundant catalogue of
*languages*, and why the canonicalization it applies is the right one. Companion
to `genaut/README.md` (the tiers and pipeline) and `genaut/SHAPES.md` (the shape
funnel). The classification paper (`research_notes/sos_classification.md` §12)
consumes the resulting pool.

## 1. The object and the redundancy

genaut enumerates, for each **shape** `Shape(n, k, c, acc)`, every tiny
ω-automaton of that shape, reduces it, and carries it through the SoS
construction to the syntactic ω-semigroup `𝓘(L)` (`.sos`). The syntactic `𝓘` is
a **complete invariant**: two `.sos` are byte-equal iff the languages are equal
*over the same AP labeling* ([SωS26, Thm. 5.1]; `sosl/sosl/sos/io/sos_format.md`).

But one language is presented, and re-enumerated, many times over. There are
exactly **three** axes along which the same language recurs in an exhaustive
shape sweep — and an irredundant catalogue must quotient all three:

1. **Sub-shape inclusion.** A larger shape emits a *superset* of a smaller one's
   languages: more states, more colours, or a parity acceptance over the same
   alphabet can only add languages. So a language appears in every shape above
   its minimal one.
2. **Alphabet redundancy.** A language over `k` APs may not *use* all of them.
   `GF a` lives equally in the 1-AP world and, with a declared-but-unused `b`, in
   the 2-AP world; `universal` uses no AP at all. As *languages* these are the
   same object, but their `.sos` differ (a different alphabet ⇒ a different
   invariant), so they count as distinct until the alphabet is minimized.
3. **AP relabeling.** The `.sos` format fixes the AP order to lexicographic-by-
   name and the polarity to `absent < present`, so `GF a` and `GF(!a)`, or an
   `a↔b` twin, are *distinct* `.sos` bytes for what is the same language up to
   renaming the symbols. The residual symmetry is the signed permutations of the
   APs — the hyperoctahedral group `B_k`, order `2^k·k!`.

Axis 1 is folded by the cross-shape union (`corpus/flat/`, dedup by `.sos`
bytes). Axes 2 and 3 are what `corpus/flat_canon/` adds: the **canonical** pool,
one representative per language *up to renaming and unused symbols* — the
irredundant count.

**A note on acceptance families.** `gba` (`⋀ Inf`) and `parity` share the slot
id space but carry a *different* acceptance formula, so a given id denotes
*different* languages under the two — the `_parity` tag suffix is **load-bearing**,
never interchangeable with its bare twin. Consequently a **sampled** tier is only
meaningful for a **beyond-the-wall** shape: sampling a shape that is already
exhaustively enumerated adds no language (every draw is in the exhaustive tier)
and only risks family-mislabeled provenance, so such samples are excluded from the
pools.

## 2. The canonical procedure (`flat_canon`)

For each enumerated language, keyed off its **det HOA as ground truth** (the
stored `.sos` is derived, and a sampled entry can leave it non-minimal —
`tests/genaut/source_consistency`), `genaut/gen/flatten.py::build_canon`:

1. **Canonicalize the automaton.** `D0 = canonical(det)` — the deterministic,
   complete, transition-based, generic-acceptance form the SoS import layer reads.
2. **Minimize the alphabet.** `D0.remove_unused_ap()` sheds every AP no edge
   mentions. This is *not* automatic: `canonical` collapses only the all-`t`
   (universal) case on its own; a declared-but-unused AP otherwise survives (the
   same observation forces `aut2ltl/language.py` to call `remove_unused_ap`
   explicitly when it re-roots a sub-language — "no postprocess level reindexes
   the alphabet, so we do it ourselves"). After this step the language sits at a
   single, minimal alphabet size (axis 2 folded).
3. **Build the invariant.** `inv = invariant_of(D0)` — the syntactic `𝓘` over the
   minimized alphabet.
4. **Fold `B_k`.** `sigma*, canon_inv = canonical_relabeling(inv)`
   (`sosl/sosl/sos/relabel.py`): over all `≤ 2^k·k!` signed AP permutations, re-key
   the algebra and keep the one whose **semigroup core** (`ap; classes; letters;
   mult`) is byte-least. Selection ignores `accept`, so a language and its
   complement pick the **same** `sigma*` and `𝓘(L̄)` stays `𝓘(L)` with `accept`
   flipped, byte-exact — the classifier's duality gate is preserved (axis 3
   folded).
5. **Materialize a consistent pair.** `canon_sos = dump(canon_inv)` is the
   canonical `.sos`; `relabel_hoa(D0.to_str(), sigma*)` puts the *det* into the
   same labeling; a re-canonize round-trips as an assertion
   (`invariant_of(canonical(relabel_hoa(...))) == canon_sos`). Both files are
   stored under the smallest-shape `<tag>_<id>` name — the language traces to its
   minimal setting.

Dedup key is `canon_sos`; the first occurrence in traversal order wins.

## 3. Why this is the right irredundant cover

The three axes above are *exhaustive*: two presentations enumerated by genaut
denote the same language-up-to-renaming iff they agree after (1) taking the
canonical automaton, (2) minimizing the alphabet, and (3) folding `B_k`. Each
step is justified:

- **Completeness of `𝓘`.** After a fixed labeling, `.sos` byte-equality *is*
  language equality ([SωS26, Thm. 5.1]) — step 3's engine is exact, not a
  heuristic. (Contrast `survey.normalize.default_key`, the first-occurrence HOA
  key: it is only a *partial* fold — measured to leave ~1.75× more classes than
  the `B_k` orbit-min — because relabel twins need not have first-occurrence-
  aligned presentations. The algebra is the robust place to fold.)
- **Soundness of the fold.** Re-keying under a relabeling is language-faithful:
  membership agrees on every lasso under the induced letter permutation
  (`tests/genaut/relabel_soundness`, the anti-over-merge oracle), and the identity
  relabeling reproduces the input byte-for-byte (the re-keying equals the format's
  own keying). So the fold *never* merges two genuinely different languages.
- **Minimality is forced, not chosen.** A chain of `H`-descending idempotents or
  a superchain of `R`-descending stems needs a certain algebra size, but the
  *alphabet* is free to carry passengers; `remove_unused_ap` removes exactly the
  passengers, leaving the intrinsic alphabet. Only then does "distinct language"
  mean distinct.
- **`B_k`, not the full symmetric group.** We quotient by *signed permutations of
  APs*, not arbitrary permutations of the `2^k` letters: renaming/negating
  propositions is the equivalence that preserves "the same specification", the
  letters being valuations of a fixed proposition set. `|B_k| = 2^k·k! ≤ 48` for
  `k ≤ 3` (the census wall), so the search is a few dozen re-keys — the factorial
  is expected and cheap.

The result is the count of **distinct ω-languages up to renaming their symbols**
that small automata realize — a number no other tool computes, and the honest
denominator for the classification profile.

## 4. Traversal order and traceability

Shapes are visited in a **linear extension of the sub-shape order** — `A ⊑ B` when
`A` is componentwise ≤ `B` in `(n, k, c)` and no more permissive in acceptance
family (`gba ⊑ parity`) — so a language's first appearance is at a *minimal*
shape and the kept filename traces it there. Exhaustive shapes precede the
non-exhaustive `sampled/` folders, which then contribute only what no census
shape reached.

Caveat: with alphabet-minimization folding across `k`, minimal shapes can be
*incomparable* (a `k`-small/`n`-large shape vs. a `k`-large/`n`-small one), so the
attributed "smallest setting" depends on the chosen linear extension. The count is
order-independent; only the representative's name is not. (Open: whether to order
`k`-first, to attribute a folded language to its minimal *alphabet*.)

## 5. Gates

- `tests/genaut/relabel_soundness` — identity-repro, idempotence, membership
  faithfulness, and the measured `B_k` fold per `k`.
- `tests/genaut/hoa_relabel` — the signed-perm HOA edit agrees with the algebra
  relabeling byte-for-byte (so det and `.sos` share a labeling).
- `tests/genaut/source_consistency` — per tier, `canonize(det)` reproduces the
  stored `.sos` (strict), or at least agrees up to `B_k` (relabel twin); a
  *broken* verdict (different languages) flags a corrupt source pair.

## 6. Status and open items

- `flat/` (byte-`.sos` tier) is the **fixed-labeling** census — *not*
  alphabet-minimized, *not* relabel-folded: it is the honest "distinct `.sos`"
  count and the input to `flat_canon`. `flat_canon/` is the irredundant
  (alphabet-minimal + `B_k`-folded) catalogue.
- Measured folds (`2state2ap0acc` excluded as an alphabet dominator): `flat/` =
  3790 fixed-labeling languages; `B_k` orbit-min *without* alphabet-minimization =
  2008; *with* `remove_unused_ap` = **2007** (`flat_canon/`, 2007/2007
  strict-consistent). So the `B_k` relabeling is the dominant fold (3790→2008) and
  alphabet-minimization contributes a single case here (the corpus was already
  essentially alphabet-minimal — only the universal glitch below carried a
  redundant AP). k=3 (`1state3ap1acc`) folds ~6× under `B_3`, the expected
  `48`-fold symmetry.
- One sampled file (`2state1ap2acc_parity_3909429041`) is the universal language
  with a non-minimal stored `.sos` (kept a redundant `a`); building off the det
  handles it. The stored sampled `.sos`/det pair is otherwise strict-consistent
  (590/591, and 30/30 for the other sample).
- `canonize.py` does **not** call `remove_unused_ap`, so the per-shape `det/`,
  `sos/` tiers (and `flat/`) carry alphabet-redundant languages. Whether to
  minimize there too, or keep the raw census and minimize only in `flat_canon`, is
  a deliberate split: the raw tiers measure presentation multiplicity, `flat_canon`
  measures languages.
