## 6. The boundary: what counterexamples alone reach

The legality discipline is self-motivating — without it there is no
invariant to present — but it is fair to ask what a learner loses by
skipping it. The answer is everything past a precise boundary. Define the
**relaxed learner**: the same table, closedness, consistency, and harvest,
but no legality checks and no canonicalization; its hypothesis is the bare
classifier — the classes with their letter action and an on-demand pair
cache — predicting on `w·z^ω` operationally: compute the action orbit
`c_j = [ε]·z^j`, take the least `k` with `c_{2k} = c_k`, answer
`P([ε]·(w·z^k), c_k)`. This is precisely the hypothesis shape of
counterexample-guided ω-learning: a deterministic automaton on classes with
a verdict table. Its error signal is one-sided — predictions read the
literal word through the action and never consult a class under a left
context — so a merge of `≈_L`-distinct words whose separating prefix no
harvested column happens to carry is invisible to every prediction. The
consequence is not hypothetical:

**Proposition 6.1 (a certified stall).** Let `L = L(a → Xa)` — if the
first letter is `a`, so is the second — over `Σ = {b, a}`. The relaxed
learner reaches, before its first equivalence query, a closed and
consistent four-class table — `[ε]`, the singleton `⟨a⟩`, a committed-in
class `C₁ = b·Σ* ∪ aa·Σ*`, a committed-out class `C₀ = ab·Σ*` — whose
hypothesis language is exactly `L`. Every equivalence oracle therefore
assents, bounded or exact, and the fixpoint is permanent, one class short
of `N = 5`: the two accepting idempotents `[b]` and `[aa]`,
right-indistinguishable but `≈_L`-separated by the left context `a`, stay
merged inside `C₁`.

*Proof.* Membership of an ω-word depends only on its first two letters, so
on lassos it is a function of the *commitment* of the literal prefix:
every word of `C₁` begins a member, every word of `C₀` a non-member, and
the only uncommitted non-empty word is the single letter `a`. The
four-class partition is closed and consistent (`C₁` and `C₀` absorb both
letters; `a` steps into one or the other), and the relaxed learner
provably lands on it: every pre-equivalence column has prefix `x = ε` —
the initial column does, and consistency mints preserve the prefix
(Definition 3.2) — and an `x = ε` context evaluates any word of length ≥ 2
by its commitment alone, so no such column can split `C₁` or `C₀`, while
the inconsistency of `a` against `b` at `(ε, ε)` forces the mint `(ε, b)`
that isolates `⟨a⟩`. Now take any lasso `w·z^ω`. The normalized stem
`w·z^k` can never be the word `a` (either it is longer, or `w = ε`,
`z = a`, where `k = 1` fails the stabilization test and `k = 2` gives stem
`aa`), so its class is `C₁` or `C₀`, and the prediction — the teacher's
bit on the keyed lasso, with `u_{C₁} = b`, `u_{C₀} = ab` — equals the
commitment of the stem, which equals the truth of the queried lasso. No
counterexample exists. ∎

<table>
<tr>
<td align="center"><img src="../sos_figs/img/a_implies_xa.png" alt="a implies Xa automaton" width="260"></td>
<td align="center"><img src="../sos_core_figs/img/a_implies_xa_pairs.png" alt="a implies Xa syntactic invariant" width="260"></td>
</tr>
<tr>
<td align="center"><b>(a) <code>a → Xa</code></b>: 4 states, <code>Inf(0)</code> (Büchi).</td>
<td align="center"><b>(b) <code>𝓘(a → Xa)</code></b>, <code>N = 5</code>: both committed-in stems<br><code>[b]</code>, <code>[aa]</code> accept with every idempotent loop —<br>six pairs, two stems the stall merges.</td>
</tr>
</table>

**Figure 4.** The boundary's exhibit, teacher automaton and target
invariant (Figure 2's conventions). The specimen was *searched for*: an
exhaustive census of the smallest one-atom automaton shapes (at one state
every fixpoint is canonical, so two states are minimal) finds the
permanent stall already here, simpler than the classical
trivial-right-congruence example `FG(a ∨ Xa)` [AF21].

The same search yields one more two-letter witness, `a ∧ XG¬a` — the
language of the single ω-word `a·b^ω`, `N = 4`, stalled at 3 after one
counterexample, the canonical `[b·a]` merged into `[b]` — the fourth named
case of §7's tables. And "one class short" undersells what is lost: the
stalled partition supports no export at all. Forcing §3.2's product recipe
on it yields a table that is not associative —
`(⟨a⟩·⟨a⟩)·⟨a⟩ = ⟨b⟩·⟨a⟩ = ⟨b⟩` against
`⟨a⟩·(⟨a⟩·⟨a⟩) = ⟨a⟩·⟨b⟩ = ⟨ab⟩`, the second bracketing substituting a
key mid-product, which a merely-right-invariant quotient does not
license — and whose bracketing-dependent read-off gives `a^ω` two
verdicts: no language. The general theorem says this is no accident of the
specimen:

**Theorem 6.2 (certified fixpoints: canonical or no algebra).** Let a
closed, consistent table's relaxed hypothesis be certified by an exact
equivalence oracle — its prediction agrees with `L` on every lasso. Then
the following are equivalent: (i) the stamp-legality check is clean (the
kernel is a congruence, Lemma 3.4); (ii) the export is exactly `𝓘(L)`,
byte-equal after re-keying. In particular a certified *non-canonical*
fixpoint — a permanent stall — is never a congruence: its product
`c·c' = c·u_{c'}` genuinely depends on the choice of keys, and no
operation on its classes recognizes anything. What the relaxed learner
delivers is its operational acceptor — correct — and, provably, nothing
more.

*Proof.* (ii)⟹(i): `𝓘(L)`'s classes form a semigroup. (i)⟹(ii): with the
kernel a congruence (Lemma 3.4), the export is an invariant whose lasso
membership is the hypothesis's operational prediction — multiplicativity
makes the action orbit the power sequence, so the stabilized `c_k` is the
idempotent power of `𝒮_T(z)` and the predicting pair is
[SωS26, Def 3.4]'s queried name — and the certification makes it denote
`L`; [SωS26, Cor 4.2] then forces the kernel to refine `≈_L` and the pair
set to be the names of `L`'s accepted lassos. Every split — promotion,
consistency mint, harvest — was witnessed by an Arnold context, so `≈_L`
refines the kernel; the two inclusions pin the kernel to `≈_L`, and the
export is `𝓘(L)`, byte-equal after re-keying. *In particular*: a certified
fixpoint whose kernel were a congruence would be canonical; a certified
stall is non-canonical, so its kernel is no congruence. ∎

(One asymmetry is worth a sentence: exactness is what closes the door —
under a bounded oracle a congruent relaxed fixpoint may be a genuine
algebra strictly coarser than the syntactic one, a correct-so-far quotient
the oracle was too weak to refute; certified *and* congruent forces
canonical, [SωS26, Cor 4.2]'s *nowhere else* met from below.)

The right vocabulary for this result is not defect but **boundary**, and
the boundary is a shared observation. That the right congruence
under-determines an ω-regular language is [AF21]; the field's two
responses to it bracket this paper. The FDFA line stays on the near side:
right-congruence-seeded families of acceptors, which counterexample-guided
refinement does reach — completely and canonically, at acceptor precision
[AF16, LCZL21]. This paper wants the far side, where the algebra and its
read-offs live, and Theorem 6.2 is [AF21]'s observation refined in tighter
vocabulary: what separates the two sides is not the size of the right
congruence but the absence, at every certified stall, of a congruence at
all. Crossing requires a query no counterexample will ever supply, posed
on the learner's own initiative — the legality escalations of §4.2 are
exactly those queries. §7.3 measures the boundary at census scale: half of
6222 languages sit strictly beyond it.
