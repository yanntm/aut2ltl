# sosl.sos.giventhat — choosing a property given prior knowledge

Given the invariant of a property's complement `𝓘(¬φ)` and the invariant of
what is already known about the system `𝓘(K)`, every ω-regular `B` that is a
sound stand-in for `φ` under `K` satisfies
`ℒ(¬φ) ∩ ℒ(K) ⊆ ℒ(B) ⊆ ℒ(¬φ) ∪ ℒ(¬K)`. This package builds that interval
*once*, on one product table, and answers exactly and with witnesses: does `K`
settle `φ`; does `K` refute `φ`; and which legal `B`s exist between the
endpoints.

## Services

- **The interval object.** `given_that(neg_phi, k) -> Interval` — one align +
  one materialize, then two free surgeries: the endpoints
  `P_min = P_¬φ ∩ P_K` and `P_max = P_¬φ ∪ P_K^c` as pair sets on the product
  table. The legal choices form a powerset lattice `2^F` over the *freedom*
  classes `F` (the conjugacy classes of linked pairs outside `P_K`);
  `Interval.bits = |F|` is the freedom of the choice in bits. The lattice
  identity (paper Prop 3.1) is asserted on every construction, always on.
- **The endpoint decisions.** `k_settles_phi(iv)` — is `ℒ(¬φ) ∩ ℒ(K)` empty?
  True means `K ⊨ φ` with no model checker run. `k_refutes_phi(iv)` — is
  `ℒ(P_max)` universal, decided as emptiness of its complement? True means
  `K ⊨ ¬φ`. Both return `(bool, Optional[Witness])`; on the inconclusive side
  the witness is the globally minimal lasso (`ℒ(¬φ) ∩ ℒ(K)` resp.
  `ℒ(φ) ∩ ℒ(K)`).
- **The choice API.** `choose(iv, indices)` — the legal `B` with the selected
  freedom classes turned on; `decompose(iv, q)` — its inverse, the index set
  of any legal `q` (or `None` when `q` is not in the interval).

## Source map

| file | contents |
|---|---|
| `interval.py` | GT1: `Interval`, `given_that`, `k_settles_phi` / `k_refutes_phi`, `choose` / `decompose` |

Planned (specified in `research_notes/sos_giventhat_spec.md`, not yet built):
`ladder.py` (GT2, per-rung existence), `stutter.py` (GT3, the two-tier
stutter test), `degree.py` (GT4, band-minimal Wagner degree).

## Layering (hard)

Imports `sosl.sos` (objects, io), `sosl.sos.calculus` (table, align,
materialize, surgery, decide, witness) and `sosl.sos.classify` — nothing else
in the repo. Gates and campaigns live in `sosl/tests/giventhat/`.

## Reading

The specification of record is `research_notes/sos_giventhat_spec.md`; the
normative math is the paper `research_notes/sos_giventhat.md` (§3 for the
interval and the endpoint checks). `algorithm.md` next to this file carries
the hard ideas one level above the code.
