import Mathlib

/-!
# Exterior multiplication: concatenation of decomposable products

The alternating product `ExteriorAlgebra.ιMulti R n` sends `v : Fin n → M` to the
product `v 0 ∧ ⋯ ∧ v (n-1)` inside the exterior algebra.  We record that the
product of two such decomposable elements is the decomposable element of the
concatenated family, via `Fin.append`.
-/

open scoped BigOperators
open ExteriorAlgebra

variable {R M : Type*} [CommRing R] [AddCommGroup M] [Module R M]

/-- **Concatenation.** The product of the `a`-fold and `b`-fold decomposable exterior
products is the `(a+b)`-fold decomposable product of the concatenated family. -/
theorem ExteriorAlgebra.ιMulti_mul_ιMulti {a b : ℕ} (u : Fin a → M) (w : Fin b → M) :
    ExteriorAlgebra.ιMulti R a u * ExteriorAlgebra.ιMulti R b w
      = ExteriorAlgebra.ιMulti R (a + b) (Fin.append u w) := by
  simp [ExteriorAlgebra.ιMulti]
  -- Goal: (List.ofFn fun i => ι R (u i)).prod * (List.ofFn fun i => ι R (w i)).prod 
  --      = (List.ofFn fun i => ι R (Fin.append u w i)).prod
  rw [← List.prod_append]
  congr 1
  -- Use native decidability for the simple list equality
  have : List.ofFn (fun i => ι R (Fin.append u w i)) = 
         List.ofFn (fun i => ι R (u i)) ++ List.ofFn (fun i => ι R (w i)) := by
    induction a with
    | zero => 
      simp [Fin.append, Fin.addCases]
    | succ n ih => 
      -- Use List.ext_get for element-wise equality
      apply List.ext_get
      · simp [List.length_ofFn, List.length_append]
        omega
      · intro i hi₁ hi₂
        simp only [List.length_ofFn] at hi₁ hi₂
        by_cases hi : i < n + 1
        · -- Case i < n + 1
          simp only [List.get_eq_getElem]
          rw [List.getElem_append_left (by simp [hi] : i < (List.ofFn fun j => ι R (u j)).length)]
          rw [List.getElem_ofFn, List.getElem_ofFn]
          simp [Fin.append, Fin.addCases]
          simp [show i ≤ n from Nat.lt_succ_iff.mp hi]
        · -- Case i ≥ n + 1
          simp only [List.get_eq_getElem]
          -- i >= n + 1, so we're in the right part of the append
          have hi' : i - (n + 1) < b := by omega
          rw [List.getElem_append_right (by simp; omega : (List.ofFn fun i => ι R (u i)).length ≤ i)]
          rw [List.getElem_ofFn, List.getElem_ofFn]
          simp [Fin.append, Fin.addCases]
          simp [Nat.not_le.mpr (Nat.lt_of_not_ge (fun h => hi (Nat.lt_succ_of_le h)))]
  exact this.symm
