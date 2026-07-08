# tests/genaut — canonicalization checks for the genaut corpus

Placed scripts (no `/tmp`, no one-liners) validating the AP-relabeling
canonicalization `sosl.sos.relabel` and its use in building `genaut/corpus/`.
Run with `python -m` from the `sosl/` root:

    python -m tests.genaut.relabel_soundness   # orbit-min soundness + the B_k fold
    python -m tests.genaut.hoa_relabel         # the signed-perm HOA relabeler

Both read the committed `genaut/corpus/flat/` pool as their dataset. They are
whole-corpus soundness sweeps (a few seconds); pass a substring on argv to
restrict to matching case ids.

## What they check

- **`relabel_soundness`** — that `relabel.py` is a *sound* canonical form:
  identity-σ reproduces the (already-canonical) input bytes (the re-keying equals
  the format's own keying), `canon∘canon = canon`, and membership is faithful
  under every non-identity relabeling (the anti-over-merge oracle). Then it
  reports the `B_k` fold — distinct languages up to AP relabeling, per `k`.
- **`hoa_relabel`** — that `genaut.gen.flatten.relabel_hoa` (the signed-perm HOA
  edit) agrees with the algebra relabeling: `canonize(relabel_hoa(det, σ*))`
  equals `canonical_sos(native_sos)` byte-for-byte, so det and `.sos` land in the
  same canonical labeling.
