import Mathlib
import RequestProject.LinearAlgebra.TriangularIndependence
import RequestProject.LinearAlgebra.ExteriorDecomposable
import RequestProject.LinearAlgebra.ExteriorMultiplication

/-!
# Lovász–Frankl skew two-families theorem for subspaces

Let `V` be a finite-dimensional `K`-vector space with `dim V = a + b`, and let
`U i, W i ≤ V` with `dim (U i) = a`, `dim (W i) = b`, `U i ⊓ W i = ⊥`, and
`U i ⊓ W j ≠ ⊥` whenever `i < j`.  Then `m ≤ C(a+b, a)`.

The proof forms decomposable exterior vectors `u i ∈ ⋀^a V` from bases of `U i`,
and test maps `T j : ⋀^a V →ₗ ExteriorAlgebra K V` given by right multiplication
with the decomposable vector of `W j`.  Upper-triangularity of `T` follows from the
vanishing/nonvanishing criteria for decomposable exterior products, and the
triangular independence principle bounds `m` by `dim (⋀^a V) = C(a+b, a)`.
-/

open scoped BigOperators
open ExteriorAlgebra Module

namespace TwoFamilies

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- `Sum.elim u w` reindexes to `Fin.append u w` along `finSumFinEquiv`. -/
theorem sumElim_comp_finSumFinEquiv_symm {a b : ℕ} (u : Fin a → V) (w : Fin b → V) :
    Sum.elim u w ∘ finSumFinEquiv.symm = Fin.append u w := by
  have key : ∀ x : Fin a ⊕ Fin b, Fin.append u w (finSumFinEquiv x) = Sum.elim u w x := by
    rintro (i | j)
    · rw [finSumFinEquiv_apply_left, Fin.append_left]; rfl
    · rw [finSumFinEquiv_apply_right, Fin.append_right]; rfl
  funext i
  simp only [Function.comp_apply]
  rw [← key (finSumFinEquiv.symm i), Equiv.apply_symm_apply]

/-- The concatenation of two linearly independent families whose spans meet only in `0`
is linearly independent. -/
theorem linearIndependent_append_of_disjoint {a b : ℕ}
    (u : Fin a → V) (w : Fin b → V)
    (hu : LinearIndependent K u) (hw : LinearIndependent K w)
    (hdisj : Disjoint (Submodule.span K (Set.range u)) (Submodule.span K (Set.range w))) :
    LinearIndependent K (Fin.append u w) := by
  have hsum : LinearIndependent K (Sum.elim u w) := hu.sum_type hw hdisj
  have hcomp := hsum.comp finSumFinEquiv.symm finSumFinEquiv.symm.injective
  rwa [sumElim_comp_finSumFinEquiv_symm] at hcomp

/-- If the spans of two families have nontrivial intersection, the concatenated family
is linearly dependent. -/
theorem not_linearIndependent_append_of_inf_ne_bot {a b : ℕ}
    (u : Fin a → V) (w : Fin b → V)
    (hspan : ¬ Disjoint (Submodule.span K (Set.range u)) (Submodule.span K (Set.range w))) :
    ¬ LinearIndependent K (Fin.append u w) := by
  intro hLI
  apply hspan
  have hsum : LinearIndependent K (Sum.elim u w) := by
    have := hLI.comp finSumFinEquiv finSumFinEquiv.injective
    rwa [← sumElim_comp_finSumFinEquiv_symm, Function.comp_assoc,
      Equiv.symm_comp_self, Function.comp_id] at this
  have h := (linearIndependent_sum.mp hsum).2.2
  simpa using h

/-- The span of the basis vectors of a submodule `U`, mapped into `V`, equals `U`. -/
theorem span_basis_coe {a : ℕ} (U : Submodule K V) (bU : Basis (Fin a) K U) :
    Submodule.span K (Set.range (fun i => (bU i : V))) = U := by
  have hrw : Set.range (fun i => (bU i : V)) = U.subtype '' Set.range bU := by
    rw [← Set.range_comp]; rfl
  rw [hrw, Submodule.span_image, bU.span_eq, Submodule.map_top, Submodule.range_subtype]

/-- The basis vectors of a submodule `U`, mapped into `V`, are linearly independent. -/
theorem linearIndependent_basis_coe {a : ℕ} (U : Submodule K V) (bU : Basis (Fin a) K U) :
    LinearIndependent K (fun i => (bU i : V)) :=
  (bU.linearIndependent).map' (U.subtype) (Submodule.ker_subtype U)

/-- The decomposable exterior product of the concatenation of bases of `U` and `W`
is nonzero when `U ⊓ W = ⊥`. -/
theorem append_wedge_ne_zero {a b : ℕ} (U W : Submodule K V)
    (bU : Basis (Fin a) K U) (bW : Basis (Fin b) K W)
    (hbot : U ⊓ W = ⊥) :
    ExteriorAlgebra.ιMulti K (a + b)
      (Fin.append (fun i => (bU i : V)) (fun i => (bW i : V))) ≠ 0 := by
  apply ExteriorAlgebra.ιMulti_ne_zero_of_linearIndependent
  apply linearIndependent_append_of_disjoint _ _
    (linearIndependent_basis_coe U bU) (linearIndependent_basis_coe W bW)
  rw [span_basis_coe U bU, span_basis_coe W bW, disjoint_iff]
  exact hbot

/-- The decomposable exterior product of the concatenation of bases of `U` and `W`
is zero when `U ⊓ W ≠ ⊥`. -/
theorem append_wedge_eq_zero {a b : ℕ} (U W : Submodule K V)
    (bU : Basis (Fin a) K U) (bW : Basis (Fin b) K W)
    (hne : U ⊓ W ≠ ⊥) :
    ExteriorAlgebra.ιMulti K (a + b)
      (Fin.append (fun i => (bU i : V)) (fun i => (bW i : V))) = 0 := by
  apply ExteriorAlgebra.ιMulti_eq_zero_of_linearDependent
  apply not_linearIndependent_append_of_inf_ne_bot
  rw [span_basis_coe U bU, span_basis_coe W bW, disjoint_iff]
  exact hne

/-- **Lovász–Frankl skew two-families theorem for subspaces.** -/
theorem lovasz_frankl_subspaces [FiniteDimensional K V]
    (a b m : ℕ)
    (hdimV : Module.finrank K V = a + b)
    (U W : Fin m → Submodule K V)
    (hdimU : ∀ i, Module.finrank K (U i) = a)
    (hdimW : ∀ i, Module.finrank K (W i) = b)
    (hdiag : ∀ i, U i ⊓ W i = ⊥)
    (hcross : ∀ ⦃i j⦄, i < j → U i ⊓ W j ≠ ⊥) :
    m ≤ Nat.choose (a + b) a := by
  classical
  -- Bases of each subspace, and the decomposable exterior vectors.
  set bU : ∀ i, Basis (Fin a) K (U i) := fun i => Module.finBasisOfFinrankEq K (U i) (hdimU i)
    with hbU
  set bW : ∀ i, Basis (Fin b) K (W i) := fun i => Module.finBasisOfFinrankEq K (W i) (hdimW i)
    with hbW
  set uu : Fin m → ⋀[K]^a V :=
    fun i => exteriorPower.ιMulti K a (fun k => (bU i k : V)) with huu
  set ww : Fin m → ExteriorAlgebra K V :=
    fun j => ExteriorAlgebra.ιMulti K b (fun k => (bW j k : V)) with hww
  set T : Fin m → (⋀[K]^a V) →ₗ[K] ExteriorAlgebra K V :=
    fun j => (LinearMap.mulRight K (ww j)).comp (⋀[K]^a V).subtype with hT
  -- The test maps evaluate to the decomposable product of the concatenated bases.
  have hTval : ∀ i j, T j (uu i) = ExteriorAlgebra.ιMulti K (a + b)
      (Fin.append (fun k => (bU i k : V)) (fun k => (bW j k : V))) := by
    intro i j
    simp only [hT, huu, hww, LinearMap.comp_apply, Submodule.subtype_apply,
      LinearMap.mulRight_apply]
    rw [exteriorPower.ιMulti_apply_coe, ExteriorAlgebra.ιMulti_mul_ιMulti]
  -- Upper-triangular independence of the `uu i`.
  have hLI : LinearIndependent K uu := by
    apply LinearIndependent.of_upperTriangular_maps uu T
    · intro j
      rw [hTval j j]
      exact append_wedge_ne_zero (U j) (W j) (bU j) (bW j) (hdiag j)
    · intro i j hij
      rw [hTval i j]
      exact append_wedge_eq_zero (U i) (W j) (bU i) (bW j) (hcross hij)
  -- Bound `m` by the dimension of the exterior power.
  have hcard := hLI.fintype_card_le_finrank
  rw [exteriorPower.finrank_eq K a, hdimV] at hcard
  simpa using hcard

end TwoFamilies
