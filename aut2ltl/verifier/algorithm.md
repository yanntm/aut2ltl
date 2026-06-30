# Checking a non-LTL witness

A non-LTL witness is a counting family `(u, v, x, p)`: finite words `u`, `v`, an
ultimately-periodic tail `x = x_prefix . (x_cycle)^w`, and a claimed period `p > 1`,
such that membership of `u . v^n . x` toggles with `n mod p`. This package decides
whether a given family actually does so against a supplied automaton.

## The input

A `Witness` (the floor value type, `aut2ltl/witness.py`) and a `spot.twa_graph`. The
two are independent: the witness can come from the engine (`extract_witness`), from a
serialized line off the front end (`Witness.parse`), or be hand-written; the automaton
is whatever language the client wants to check membership in. Nothing engine-side is
referenced.

## The one load-bearing primitive: membership

```
member(aut, word)  ==  aut intersects the one-lasso automaton of word
```

Spot decides membership of an ultimately-periodic ω-word by intersecting `aut` with the
single-lasso automaton of the word. This is correct for **any** acceptance condition
(Büchi, parity, Rabin, generic Emerson-Lei) and any (non)determinism, because it is a
language operation — it never inspects states or marks. That is the whole point of
checking by membership rather than by replaying an internal run: **membership is
language-invariant, state indices are not**, so the check is valid against an automaton
the verifier never built and whose encoding it does not trust.

## The sample and the verdict

The words `u . v^n . x` are built in Spot syntax (`_lasso`: a prefix of letters then
`cycle{...}`) for `n = 0..2p`, giving a boolean pattern. The verdict
(`verify_suggestive`) is the conjunction of:

- **non-constant** — the pattern takes both values, so `x` is phase-sensitive across the
  `v`-orbit (the family witnesses *something*);
- **periodic** — `pattern[i] == pattern[i+p]` throughout, so it repeats with period `p`;
- **minimal** — no smaller `q < p` already repeats, so the claimed `p` is the true period
  (not a multiple of a shorter count).

`verify(aut, w)` wraps this for a `Witness`, returning `(None, [])` when the family is
incomplete (no `u`/`x` to replay) — read by callers as "no checkable witness", distinct
from a failure.

## The caveat: suggestive, not a proof

This is the **membership (suggestive) tier**. Finitely many samples witness phase
*distinguishability* — that the tail separates two phases of the orbit — but **not**
*periodicity*: an aperiodic language could reproduce the sampled pattern up to any finite
`n` and only diverge later. So:

- `ok = True` **corroborates** a witness; it is not, by itself, a proof of non-LTL-ness.
- `ok = False` is a genuine **red flag**: the printed certificate does not even toggle as
  claimed against the language, so it fails to certify anything.

The upgrade that makes a positive a proof — exhibiting the `p`-cycle of pairwise
residual-inequivalent configurations directly (per `bls/definability/witness/algorithm.md`)
— is deferred. This tier is what the survey cables in to turn silent `NOT_LTL` rows into
checked rows and to surface the certificates that fail to replay.

## Layering

Floor-level: imports only `Witness` and Spot, no `Cascade` / `Translator` / engine
module. Consumers: the survey (a bounded subprocess on `NOT_LTL` rows) and any client
iterating witnesses.
