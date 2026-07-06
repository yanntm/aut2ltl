# reference — building I(L) with a fresh identity

Dev-facing. This wrapper is thin, but it owns one obligation that the
definability pipeline underneath it does **not** discharge: adjoining the
identity as a *fresh* element so the class count is presentation-independent.
Getting this wrong is a canonicity bug, so it is described here rather than left
implicit.

## What the pipeline gives, and what it lacks

`quotient_of_hoa` returns the acceptance-enriched monoid `alg` of the automaton:
a set of monoid elements (state maps enriched with the marks a word can force),
a multiplication table over elements, a letter→element map, and the accepting
linked pairs. Its classes are **monoid elements** — equivalence classes of words
under "same enriched behaviour".

That is almost the syntactic ω-semigroup, but for one gap: the identity. The
pipeline reads the identity as `alg.word_cls(())`, the element of the *empty*
word. In some presentations a non-empty word's element **coincides** with that
identity element — same state map, no marks. The textbook case is `!a` in a
one-state automaton for `GF a`: reading `!a` neither changes the state nor
forces any mark, so `⟦!a⟧ = ⟦ε⟧` as elements. A quotient over elements alone
then cannot tell `[!a]` from `[ε]`: they are different classes of *words* that
happen to sit on the same element.

## Why that is a bug, not a harmless coincidence

The class count would then depend on the presentation. `GF a` comes out at 2
classes from the one-state automaton (where `⟦!a⟧ = ⟦ε⟧`) but 3 from a
presentation whose extra marks keep `⟦!a⟧ ≠ ⟦ε⟧`. Byte-equality of two `.sos`
files is supposed to mean *language* equality (the soundness criterion of the
whole tool); a presentation-dependent class count breaks that theorem outright.
The same language must yield the same invariant from every automaton that
denotes it.

## The obligation this wrapper discharges

Adjoin the identity as a **fresh** element that no word class can collide with,
following the identity convention of `objects/algorithm.md`:

- quotient only the elements reachable as images of **non-empty** words;
- adjoin `[ε]` as a fresh element, distinct from every one of those word
  classes — never reuse `alg`'s identity element for it;
- key every non-identity class by its shortlex-least **non-empty** word.

A word whose enriched element equals `⟦ε⟧` (like `!a` in one-state `GF a`) is
then an ordinary class with a non-empty key (`!a`), and `GF a` reports 3 classes
from every presentation.

One thing this does **not** collapse: a non-empty class may legitimately act as
the identity on all the *other* non-empty classes — `[aa]` in `Even` does, its
row and column in `M` are the identity on every class but `[ε]`. That class
stays its own class (key `a;a`), distinct from `[ε]`. `M(c, [ε]) = c` and
`M([ε], c) = c` hold for it too; there is no contradiction and nothing to
special-case.

## Regression fingerprints

The class counts these conventions must produce (the triptych rows are the guard
— they must not move under any change here):

| language     | classes | note                                  |
|--------------|:-------:|---------------------------------------|
| `GF a`       | 3       | the bug case: `[ε], [a], [!a]`        |
| `F a`        | 3       | —                                     |
| `a U b`      | 4       | —                                     |
| `GF(aa)`     | 6       | triptych — must not move              |
| `Even`       | 5       | triptych — must not move              |
| `EvenBlocks` | 7       | triptych — must not move              |
| `F(a & Xa)`  | 6       | —                                     |

The shared canonicalization (`objects.canonical`) re-keys and renumbers; it does
**not** adjoin the identity — that is this wrapper's job, done before handing the
raw algebra to `canonicalize`.
