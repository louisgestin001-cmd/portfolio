import Mathlib

/-!
# Decomposable exterior vectors: vanishing and nonvanishing

For a family `v : Fin r → V` in a vector space, the decomposable element
`v 0 ∧ ⋯ ∧ v (r-1)` (`ExteriorAlgebra.ιMulti K r v`) vanishes exactly when `v`
is linearly dependent.  We record both directions, plus the corresponding
statement at the level of the exterior power `⋀[K]^r V`.
-/

open scoped BigOperators
open ExteriorAlgebra

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] {r : ℕ}

/-- **Vanishing.** A linearly dependent family has vanishing decomposable exterior product. -/
theorem ExteriorAlgebra.ιMulti_eq_zero_of_linearDependent
    (v : Fin r → V) (hv : ¬ LinearIndependent K v) :
    ExteriorAlgebra.ιMulti K r v = 0 :=
  (ExteriorAlgebra.ιMulti K r).map_linearDependent v hv

/-- **Nonvanishing** in the exterior power. A linearly independent family has nonzero
decomposable exterior product `exteriorPower.ιMulti`. -/
theorem exteriorPower.ιMulti_ne_zero_of_linearIndependent
    (v : Fin r → V) (hv : LinearIndependent K v) :
    exteriorPower.ιMulti K r v ≠ 0 := by
  have hfam : LinearIndependent K (exteriorPower.ιMulti_family K r v) :=
    exteriorPower.ιMulti_family_linearIndependent_field r hv
  have huniv : (Finset.univ : Finset (Fin r)) ∈ Set.powersetCard (Fin r) r := by
    simp [Set.powersetCard]
  set s : ↑(Set.powersetCard (Fin r) r) := ⟨Finset.univ, huniv⟩ with hs
  have hne : exteriorPower.ιMulti_family K r v s ≠ 0 := hfam.ne_zero s
  have hid : ⇑(Set.powersetCard.ofFinEmbEquiv.symm s) = (id : Fin r → Fin r) := by
    rw [Set.powersetCard.ofFinEmbEquiv_symm_apply]
    exact (Finset.orderEmbOfFin_unique s.prop (fun i => Finset.mem_univ i) strictMono_id).symm
  have hval : exteriorPower.ιMulti_family K r v s = exteriorPower.ιMulti K r v := by
    rw [exteriorPower.ιMulti_family, hid]
    rfl
  rw [hval] at hne
  exact hne

/-- **Nonvanishing** in the exterior algebra. A linearly independent family has nonzero
decomposable exterior product. -/
theorem ExteriorAlgebra.ιMulti_ne_zero_of_linearIndependent
    (v : Fin r → V) (hv : LinearIndependent K v) :
    ExteriorAlgebra.ιMulti K r v ≠ 0 := by
  intro h
  have hc : (exteriorPower.ιMulti K r v : ExteriorAlgebra K V) = 0 := by
    rw [exteriorPower.ιMulti_apply_coe]; exact h
  exact exteriorPower.ιMulti_ne_zero_of_linearIndependent v hv
    (Submodule.coe_eq_zero.mp hc)
