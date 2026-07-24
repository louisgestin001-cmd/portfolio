# Scientific Thesis

## Central claim

The two classical proofs of the two-families theorem draw on disjoint mathematical
libraries — finite-order enumeration on one side, exterior algebra and general position
on the other — yet **both ultimately produce the same abstract object: a triangular
certificate of independence.** In the counting proof the certificate is a family of
*pairwise disjoint separation events* whose sizes sum to at most `n!`; in the algebraic
proof it is a family of *exterior-multiplication test maps* that annihilate strictly
below the diagonal and are nonzero on it. Formalizing both in one Lean development makes
this common structure explicit: the algebraic route factors literally through a
reusable `LinearIndependent.of_upperTriangular_maps`, and the counting route factors
through an exact fibre-counting identity that plays the analogous "one certificate per
index, no collisions" role.

This thesis is supported by the implementation, not merely asserted:

* the algebraic route's final step is a single call to
  `LinearIndependent.of_upperTriangular_maps` with `hdiag`/`hzero` supplied by the
  exterior nonvanishing/vanishing lemmas (`TwoFamiliesSubspaces.lean`);
* the counting route's final step is `separationEvents_pairwiseDisjoint` +
  `card_separationEvent_mul_choose`, i.e. disjoint events of exactly computed size
  (`WeightedBollobas.lean`);
* the *shared* precondition in both is a diagonal-nonvanishing / off-diagonal-vanishing
  dichotomy driven by cross-intersection.

## Three principal contributions

1. **A reusable triangular-independence principle**
   (`LinearIndependent.of_upperTriangular_maps` + dual): independence of a family from
   diagonal-nonzero, off-diagonal-annihilating test maps. Generic, set-pairs-free,
   directly Mathlib-shaped.
2. **An exact, division-free separation-event count**
   (`card_separationEvent_eq`, `card_separationEvent_mul_choose`) via a genuine
   ordering-factorization equivalence (position set × relative order × complement
   order), rather than an informal probability calculation.
3. **A field-general moment-curve general-position layer**
   (`momentCurve_linearIndependent` + span-intersection lemmas) that bridges finite set
   systems to subspace configurations, plus the exterior-decomposable
   vanishing/nonvanishing/concatenation lemmas that Mathlib currently lacks.

## Three lessons for formalization

1. **Exact combinatorial identities beat probabilistic phrasing.** Replacing "the
   probability that `A` precedes `B` is `1/C(a+b,a)`" by the integer identity
   `|E|·C(a+b,a) = n!` avoided all measure/`ℝ`-division friction and made the fibre
   factorization the natural proof skeleton.
2. **Degenerate cases dissolve when the algebra is set up uniformly.** The subspace
   theorem needs no `a=0`/`b=0`/`m=0` case split because empty bases and
   `ιMulti K 0 = 1` are absorbed by the exterior-algebra machinery — a case split
   planned on paper turned out to be an artifact of informal reasoning.
3. **Rectangular general position must be proved, not assumed.** The `|s| < d` case of
   moment-curve independence is exactly where a hand proof waves at "the Vandermonde
   matrix has full row rank"; the interpolation argument discharges it cleanly and is
   the honest formal content.

## Two limitations

1. **No equality/extremal classification.** Only the single canonical complement family
   is shown to attain the bound (`uniform_bollobas_sharp`); the full set of equality
   cases is not formalized.
2. **Finiteness and classical choice.** Ground and index types are finite and the
   development uses `Classical.choice` (standard, but a genuine reliance); the
   moment-curve layer is currently stated over `ℚ` rather than an arbitrary field.

## Evidence pointers (specific Lean declarations)

* Triangular certificate (algebraic): `LinearIndependent.of_upperTriangular_maps`,
  `append_wedge_ne_zero`, `append_wedge_eq_zero`, `lovasz_frankl_subspaces`.
* Triangular certificate (counting): `separationEvents_disjoint`,
  `separationEvents_pairwiseDisjoint`, `card_separationEvent_mul_choose`,
  `weighted_bollobas`.
* Bridge: `momentCurve_linearIndependent`, `inf_spanMomentCurve_eq_bot`,
  `inf_spanMomentCurve_ne_bot`, `frankl_kalai_skew`.

## Statements that must NOT be claimed

* That any individual theorem is "the first formalization" (novelty search could not
  be run against live external indexes; see `docs/research/NOVELTY_AUDIT.md`).
* That the work contains new mathematics — it does not.
* That kernel-checking guarantees semantic fidelity — it guarantees correctness
  *relative to the stated theorems*; fidelity is argued separately
  (`docs/proofs/INDEPENDENT_PROOF_AUDIT.md`, `docs/proofs/SEMANTIC_AUDIT.md`).
* That equality cases are classified — they are not.
