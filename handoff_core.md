# Handoff — sos_core (the SωS paper, canonicity-first reboot)

## Task

Flesh `research_notes/sos_core.md` into full paper text, section by section, with
user review of each increment. Reservoir: `research_notes/sos_constructed.md` —
borrow freely, never edit it. Dependents adapt to us, never the reverse.

## State

**§2 through §3.2 are approved.** Everything else in the paper file — whatever its
state of polish — is indicative at most: not reference, not important, not binding,
rewritten when its turn comes.

## TODO queue (next action first)

1. **§3.3 "Canonicity: the invariant of `L`"** — drafted to the spec below, awaiting
   user review; not in the paper file. Review, amend, land, commit.
2. Parked, bites when §3.1 reopens: Def 3.1's isolation only constrains `λ`; the S¹
   axiom (word classes closed under `M`, i.e. `⟦u⟧ = [ε] ⟺ u = ε`) is still missing,
   and §3.3 needs it abstractly (`𝓘(L)` has it by construction).

## §3.3 spec (redraft from here if the draft is lost)

Numbering continues §3.2; next label is 3.5.

1. Inherited question: Def 3.4 reads one presentation; a lasso has many.
2. **Def 3.5** Arnold's congruence [Arn85] on `Σ⁺`, both shapes (linear / ω-power),
   in full; facts used: two-sided, finite index; coarsest = first minimality sense.
   Example on `aUGb`: `a ≉ b` (ω-power, empty paddings), `ab ≉ ba` (linear,
   `t = b`), `a ≈ aa`; the five Fig 1 classes.
3. **Def 3.6** `𝓘(L)`: `𝒞 = Σ⁺/≈_L` shortlex-keyed plus adjoined `[ε]`; `λ(x) = [x]`;
   `M` induced; `P(L)` = linked pairs of word classes tested on the representative
   lasso `w_s·(w_e)^ω ∈ L`. Remark: `⟦u⟧ = [u]` — letter-generated.
4. **Lemma 3.7** substitution: `u ≈ u'`, `v ≈ v'` (loops nonempty) ⟹ one verdict on
   `u·v^ω` / `u'·v'^ω`. Proof: ω-power shape at `x = u, y = ε` swaps the loop; linear
   shape at `x = y = ε, t = v'` swaps the stem. Replaces the moves apparatus.
5. **Thm 3.8** canonicity: rewrite `u·v^ω = (u·v^k)(v^k)^ω` with `⟦v⟧^k = e`, apply
   3.7 ⟹ every presentation gets `L`'s verdict; `L(𝓘(L)) = L`; complete invariant
   (byte-equal iff equal). Example: `Even`'s `a^ω` via `(ε,a)` vs `(a,a)` — distinct
   pairs, one verdict.
6. **Lemma 3.9** rotation, posed AFTER the theorem, on letter-generated algebras
   (hypothesis explicit), naming sentence first. **Def 3.10** saturation.
   **Cor 3.11** `P(L)` saturated. Close: saturation is the one law a layer must obey,
   table-checkable; §4 flips it, §7 re-reads rotation on two-sided contexts.

Open placement, decided with user when reached: the biconditional "saturated ⟺
well-defined for arbitrary `P`" (needs the moves lemma; consumers: complement flip,
construction's saturation obligation).

## Decisions (do not relitigate)

- Vocabulary: **classes** (never bins/types; "equivalence classes" spelled out only
  at §2's organizing sentence); classify/assign, never metaphorical "sorting"; `φ` is
  "the morphism"; algebraic **sort** reserved for the two-sorted structure.
- `𝓘` is **the invariant** (Def 3.2's term); "the object" is banned paper-wide.
  Binding text (§2–3.2) is clean; indicative sections still carry it — purge at
  their rewrite, including Def 3.4's competing "**object**" definition.
- §2 is PP04-faithful: `S₊` is a **semigroup** on `Σ⁺` (`ε` has no ω-power); the
  identity is adjoined only in §3. Morphism is `φ = (φ₊, φ_ω)`, equations displayed;
  after the "second sort not carried" hinge, `φ` means `φ₊`.
- Worked paragraphs are labeled `*Example.*` and anchored ("On Figure 1
  (`aUGb`), …"); no bare "In general". No individual non-lasso words as
  specimens — out of regular scope.
- Identity **adjoined** (S¹; "fresh" banned); "specimen" banned; shortlex keys;
  Cayley root a source; `P` typeset beneath figures; monochrome cycles only as group
  evidence; no idempotent ink.
- Master-2 accessible, no automata in Part A (Arnold's congruence is language-level,
  hence admissible in §3.3); no announcement sentences; object first, construction
  second; two minimality senses only; rotation lemma is the central contribution,
  general form first; "40 years unseen" as fact pattern, never boast; machine
  formats in Part B.

## Blockers

None. Next action: the §3.3 review.
