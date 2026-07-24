# Human Review Guide

This guide lets a human author genuinely understand and defend the development. Read it
alongside the source; every claim below points to a specific declaration.

## Dependency-ordered reading plan

Read the files in this order (it follows the import DAG; see `docs/proofs/DEPENDENCY_AUDIT.md`):

1. `SetPairs/Basic.lean` — the three predicates (`DiagonallyDisjoint`,
   `CrossIntersecting`, `SkewCrossIntersecting`) and their trivial API. 10 minutes.
2. `SetPairs/PermutationOrders.lean` — `OrderEnumeration` and the `n!` count. 5 min.
3. `SetPairs/SeparationEvents.lean` — the counting core (longest file). Read the
   module docstring first, then `Separates`/`separationEvent`, then the five counting
   lemmas in order. 60–90 min.
4. `SetPairs/WeightedBollobas.lean`, `SetPairs/Uniform.lean` — assembly + sharpness. 20 min.
5. `LinearAlgebra/TriangularIndependence.lean` — the generic principle. 15 min.
6. `LinearAlgebra/ExteriorDecomposable.lean`, `ExteriorMultiplication.lean` — exterior
   lemmas. 20 min.
7. `LinearAlgebra/TwoFamiliesSubspaces.lean` — the subspace theorem. 30 min.
8. `LinearAlgebra/MomentCurve.lean`, `SkewSetPairs.lean` — the bridge. 30 min.
9. `Main.lean`, `Examples.lean` — glue, axiom audit, regression checks.

## Informal proof of every principal theorem

**Weighted Bollobás.** Over all `n!` linear orders of the ground set, count those
"separating" `(Aᵢ,Bᵢ)` (all of `Aᵢ` before all of `Bᵢ`). Exactly
`C(n,a+b)·a!·b!·(n−a−b)!` orders separate a fixed disjoint pair of sizes `a,b`, and
multiplying by `C(a+b,a)` gives `n!`, so the count is `n!/C(a+b,a)`. If two indices
crossed both ways (`x∈Aᵢ∩Bⱼ`, `y∈Aⱼ∩Bᵢ`), no order could separate both pairs, so the
events are pairwise disjoint. Hence `∑ᵢ n!/C(|Aᵢ|+|Bᵢ|,|Aᵢ|) ≤ n!`; divide by `n!`.

**Uniform Bollobás + sharpness.** Constant sizes ⟹ `m/C(a+b,a) ≤ 1`. The complement
family (all `a`-subsets `S` of `Fin(a+b)`, `A_S=S`, `B_S=Sᶜ`) is diagonally disjoint,
cross-intersecting, and has exactly `C(a+b,a)` members, attaining the bound.

**Triangular independence.** From `∑ gᵢuᵢ=0`, apply the test map `Tⱼ` at the largest
`j` with `gⱼ≠0`: lower terms vanish by the triangular hypothesis, higher by maximality,
leaving `gⱼTⱼ(uⱼ)=0`; a field lets us conclude `Tⱼ(uⱼ)=0`, contradiction.

**Lovász–Frankl subspaces.** `uᵢ=⋀(basis of Uᵢ)∈⋀^aV`; test map `Tⱼ=(·∧⋀Wⱼ)`. Then
`Tⱼ(uᵢ)=⋀(Uᵢ-basis ⧺ Wⱼ-basis)`, nonzero when `Uᵢ⊕Wⱼ` is direct (diagonal, since
`Uᵢ∩Wᵢ=0` and dims add to `dim V`) and zero when `Uᵢ∩Wⱼ≠0` (off-diagonal `i<j`).
Triangular independence ⟹ the `uᵢ` are independent, so `m≤dim⋀^aV=C(a+b,a)`.

**Moment curve.** `∑ⱼuⱼ·vₜⱼ=0` gives `∑ⱼuⱼtⱼ^r=0` for `r<d`, hence `∑ⱼuⱼp(tⱼ)=0` for
every `deg p<d`. Take `p=∏_{k≠i}(X−t_k)` (degree `|s|−1<d`): it kills all `j≠i` and not
`i`, forcing `uᵢ=0`.

**Frankl–Kalai.** Label `α ↪ ℚ` injectively; `Uᵢ=span{momentCurve of Aᵢ}`,
`Wᵢ=span{... Bᵢ}` in `ℚ^{a+b}`. Disjointness of `Aᵢ,Bᵢ` with `|Aᵢ|+|Bᵢ|=a+b` ⟹
`Uᵢ∩Wᵢ=0`; a shared element of `Aᵢ∩Bⱼ` ⟹ a shared nonzero vector, `Uᵢ∩Wⱼ≠0`. Apply the
subspace theorem.

## Every nontrivial custom definition

* `OrderEnumeration α := α ≃ Fin (card α)` — a total order encoded as a ranking bijection.
* `Separates e A B` — `∀ x∈A, y∈B, e x < e y`: every `A`-element ranks before every
  `B`-element.
* `separationEvent A B` — the `Finset` of enumerations that `Separates`; `noncomputable`
  (it filters over all equivs) but a bona fide finite set.
* `momentCurve d t x : Fin d → ℚ := fun r => (t x)^r` — the moment-curve point of `x`.
* `spanMomentCurve d t S` — the ℚ-span of `{momentCurve of x : x∈S}`.
* `Sharp.Index/famA/famB` — the complement sharpness family on `Fin(a+b)`.

## Ten likely reviewer questions (with answers)

1. *Does the weighted theorem secretly assume `Aᵢ∪Bᵢ=univ`?* No; the count
   `card_separationEvent_eq` holds for any disjoint pair, with the `(n−a−b)!` factor
   counting elements outside `Aᵢ∪Bᵢ`.
2. *Where is both-direction cross-intersection used?* In `separationEvents_disjoint`,
   which needs `Aᵢ∩Bⱼ` and `Aⱼ∩Bᵢ` both nonempty.
3. *Is division used in the count?* No; two applications of
   `Nat.choose_mul_factorial_mul_factorial` give an exact product identity.
4. *Why the maximal index in triangular independence?* It matches the upper-triangular
   orientation; the minimal index is used in the lower dual.
5. *Why is `Tⱼ(uᵢ)=0` for `i<j`?* `Uᵢ∩Wⱼ≠0` makes the concatenated bases dependent, so
   their decomposable wedge is `0`.
6. *Why is the ambient dimension `C(a+b,a)`?* `exteriorPower.finrank_eq` gives
   `dim⋀^aV=C(dim V,a)`, and `dim V=a+b`.
7. *Is the `|s|<d` moment-curve case really handled?* Yes; the interpolation polynomial
   has degree `|s|−1<d` regardless, so no square matrix is assumed.
8. *Why are moment-curve vectors nonzero?* Their zeroth coordinate is `t x^0=1`.
9. *Can the ground set be larger than `a+b`?* Yes; only the ambient dimension `d=a+b`
   is fixed; `α` is arbitrary finite, labelled into ℚ.
10. *Which axioms are used?* Exactly `propext`, `Classical.choice`, `Quot.sound`.

## The standard axioms

* **`propext`** (propositional extensionality): logically equivalent propositions are
  equal. Used pervasively and universally accepted in classical mathematics.
* **`Classical.choice`**: a choice function exists for every nonempty type. Enables
  classical logic (excluded middle, non-constructive existence). Standard in Mathlib.
* **`Quot.sound`**: quotients respect the defining relation; the foundation of Lean's
  quotient types (e.g. `ℚ`, `Finset`).

Their presence is standard: essentially all classical mathematics in Mathlib depends on
these three. No *additional* or custom axiom appears here (checked by `#print axioms`).

## Glossary of relevant Lean objects

* `Finset α` — a finite subset of `α` (computable, with `card`).
* `Fintype α` — a typeclass witnessing `α` is finite; `Fintype.card α` its size.
* `α ≃ β` (`Equiv`) — a bijection with explicit inverse.
* `Module.finrank K V` — the dimension of a finite-dimensional `K`-vector space.
* `Submodule K V`, `⊓`, `⊥` — subspaces, their intersection (meet), the zero subspace.
* `LinearIndependent K v` — independence of a family `v`.
* `ExteriorAlgebra K V`, `⋀[K]^r V` (`exteriorPower`) — the exterior algebra and its
  degree-`r` piece; `ιMulti K r v` the decomposable `v₀∧⋯∧v_{r−1}`.
* `Polynomial ℚ` — univariate polynomials over ℚ; `.eval`, `.natDegree`, `.coeff`.

## Exercises (reproduce key steps)

1. Prove `card_orderEnumerations` yourself from `Fintype.card_equiv`.
2. On paper, verify `evCount 4 1 2 = 8` and `8·C(3,1)=4!` (cf. `Examples.lean`).
3. Fill in the maximal-index argument of `of_upperTriangular_maps` without looking.
4. Show `momentCurve 3 id {0,1,2}` is independent by evaluating the `3×3` Vandermonde.
5. Explain why `inf_spanMomentCurve_eq_bot` needs `|S|+|T|≤d`, using the `d=1` failure
   from `docs/proofs/ADVERSARIAL_TESTS.md`.
6. Trace where `hcross` enters `weighted_bollobas` (answer: via
   `separationEvents_pairwiseDisjoint`).
