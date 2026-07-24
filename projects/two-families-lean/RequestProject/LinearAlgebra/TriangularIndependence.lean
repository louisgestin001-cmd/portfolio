import Mathlib

/-!
# Triangular linear independence from linear maps

A reusable algebraic principle: if a family `u : Fin m → M` admits "test maps"
`T : Fin m → M →ₗ[K] N` that are upper-triangular in the sense that
`T j (u j) ≠ 0` and `T j (u i) = 0` for `i < j`, then `u` is linearly independent.

The proof uses a maximal-nonzero-coefficient argument: from a vanishing linear
combination `∑ c i • u i = 0`, apply `T j` at the largest `j` with `c j ≠ 0`.
-/

open scoped BigOperators

variable {K M N : Type*} {m : ℕ}
variable [Field K] [AddCommGroup M] [Module K M] [AddCommGroup N] [Module K N]

/-- **Upper-triangular linear independence.** If `T j (u j) ≠ 0` and `T j (u i) = 0`
whenever `i < j`, then the family `u` is linearly independent. -/
theorem LinearIndependent.of_upperTriangular_maps
    (u : Fin m → M) (T : Fin m → M →ₗ[K] N)
    (hdiag : ∀ j, T j (u j) ≠ 0)
    (hzero : ∀ ⦃i j⦄, i < j → T j (u i) = 0) :
    LinearIndependent K u := by
  classical
  rw [Fintype.linearIndependent_iff]
  intro g hg
  by_contra hne
  push_neg at hne
  obtain ⟨i0, hi0⟩ := hne
  set S : Finset (Fin m) := Finset.univ.filter (fun i => g i ≠ 0) with hS
  have hSne : S.Nonempty := ⟨i0, Finset.mem_filter.mpr ⟨Finset.mem_univ _, hi0⟩⟩
  set j := S.max' hSne with hj
  have hgj : g j ≠ 0 := (Finset.mem_filter.mp (S.max'_mem hSne)).2
  have hmap : ∑ i, g i • T j (u i) = 0 := by
    have := congrArg (T j) hg
    rw [map_sum, map_zero] at this
    simpa [map_smul] using this
  have hsum : ∑ i, g i • T j (u i) = g j • T j (u j) := by
    rw [Finset.sum_eq_single j]
    · intro i _ hij
      rcases lt_or_gt_of_ne hij with h | h
      · rw [hzero h, smul_zero]
      · have hgi : g i = 0 := by
          by_contra hgi
          have hiS : i ∈ S := Finset.mem_filter.mpr ⟨Finset.mem_univ _, hgi⟩
          exact absurd (S.le_max' i hiS) (not_le.mpr h)
        rw [hgi, zero_smul]
    · intro h; exact absurd (Finset.mem_univ j) h
  rw [hsum] at hmap
  rcases smul_eq_zero.mp hmap with h | h
  · exact hgj h
  · exact hdiag j h

/-- **Lower-triangular linear independence** (dual version). If `T j (u j) ≠ 0` and
`T j (u i) = 0` whenever `j < i`, then the family `u` is linearly independent. -/
theorem LinearIndependent.of_lowerTriangular_maps
    (u : Fin m → M) (T : Fin m → M →ₗ[K] N)
    (hdiag : ∀ j, T j (u j) ≠ 0)
    (hzero : ∀ ⦃i j⦄, j < i → T j (u i) = 0) :
    LinearIndependent K u := by
  classical
  rw [Fintype.linearIndependent_iff]
  intro g hg
  by_contra hne
  push_neg at hne
  obtain ⟨i0, hi0⟩ := hne
  set S : Finset (Fin m) := Finset.univ.filter (fun i => g i ≠ 0) with hS
  have hSne : S.Nonempty := ⟨i0, Finset.mem_filter.mpr ⟨Finset.mem_univ _, hi0⟩⟩
  set j := S.min' hSne with hj
  have hgj : g j ≠ 0 := (Finset.mem_filter.mp (S.min'_mem hSne)).2
  have hmap : ∑ i, g i • T j (u i) = 0 := by
    have := congrArg (T j) hg
    rw [map_sum, map_zero] at this
    simpa [map_smul] using this
  have hsum : ∑ i, g i • T j (u i) = g j • T j (u j) := by
    rw [Finset.sum_eq_single j]
    · intro i _ hij
      rcases lt_or_gt_of_ne hij with h | h
      · have hgi : g i = 0 := by
          by_contra hgi
          have hiS : i ∈ S := Finset.mem_filter.mpr ⟨Finset.mem_univ _, hgi⟩
          exact absurd (S.min'_le i hiS) (not_le.mpr h)
        rw [hgi, zero_smul]
      · rw [hzero h, smul_zero]
    · intro h; exact absurd (Finset.mem_univ j) h
  rw [hsum] at hmap
  rcases smul_eq_zero.mp hmap with h | h
  · exact hgj h
  · exact hdiag j h
