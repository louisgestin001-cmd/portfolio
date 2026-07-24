import Mathlib
import RequestProject.SetPairs.Uniform

/-!
# Computational examples and regression tests

Small `decide`/`native_decide`/`norm_num` checks corroborating the main theorems.
These are regression tests, not substitutes for the proofs.
-/

open scoped BigOperators

namespace RequestProject.Examples

/-- The uniform bound `C(a+b,a)` for a few small parameters. -/
example : Nat.choose (2 + 2) 2 = 6 := by decide
example : Nat.choose (1 + 3) 1 = 4 := by decide
example : Nat.choose (3 + 2) 3 = 10 := by decide

/-- The canonical sharp construction on `Fin (a+b)` has exactly `C(a+b,a)` members:
the number of `a`-subsets of `Fin (a+b)`. -/
example : (Finset.univ.powersetCard 2 : Finset (Finset (Fin 4))).card = Nat.choose 4 2 := by
  decide

/-- Sanity check of the weighted inequality on a concrete uniform family:
three pairs with `a = b = 1`, `∑ 1/C(2,1) = 3/2`?  No — a valid family has at most
`C(2,1) = 2` pairs, and `2 · (1/2) = 1 ≤ 1`. -/
example : (2 : ℚ) * ((Nat.choose 2 1 : ℚ)⁻¹) = 1 := by norm_num

/-!
### Regression checks for the separation-event count

`separationEvent A B` is noncomputable, so we verify instead the exact block-pattern
formula proved in `card_separationEvent_eq`,
`|E(A,B)| = C(n, a+b) · a! · b! · (n-(a+b))!`, together with the factorial identity of
`card_separationEvent_mul_choose`, `|E(A,B)| · C(a+b, a) = n!`.  Both are checked by
substituting the closed-form count and evaluating with `decide`, over the five cases
demanded by the specification.  Here `evCount n a b := C(n,a+b)·a!·b!·(n-(a+b))!`. -/

/-- The closed-form separation-event count. -/
def evCount (n a b : ℕ) : ℕ :=
  n.choose (a + b) * a.factorial * b.factorial * (n - (a + b)).factorial

-- Case 1: `A = ∅`, `B = ∅` (here `n = 3`): every ordering separates, count `= n!`.
example : evCount 3 0 0 = Nat.factorial 3 := by decide
example : evCount 3 0 0 * Nat.choose (0 + 0) 0 = Nat.factorial 3 := by decide

-- Case 2: `|α| = 2`, `|A| = |B| = 1`.
example : evCount 2 1 1 = 1 := by decide
example : evCount 2 1 1 * Nat.choose (1 + 1) 1 = Nat.factorial 2 := by decide

-- Case 3: `|α| = 4`, `|A| = 1`, `|B| = 2`.
example : evCount 4 1 2 = 8 := by decide
example : evCount 4 1 2 * Nat.choose (1 + 2) 1 = Nat.factorial 4 := by decide

-- Case 4: elements outside `A ∪ B` (`|α| = 5`, `|A| = |B| = 1`, so `3` extra elements).
example : evCount 5 1 1 = 60 := by decide
example : evCount 5 1 1 * Nat.choose (1 + 1) 1 = Nat.factorial 5 := by decide

-- Case 5: `A ∪ B = univ` (`|α| = 3`, `|A| = 1`, `|B| = 2`, no extra elements).
example : evCount 3 1 2 = 2 := by decide
example : evCount 3 1 2 * Nat.choose (1 + 2) 1 = Nat.factorial 3 := by decide

/-!
### Adversarial numeric checks

These corroborate `ADVERSARIAL_TESTS.md`: dropping a hypothesis of
`weighted_bollobas` makes the weighted sum exceed `1`. They are refutation
witnesses, not proofs of the (false) weakened statements.
-/

-- Case 1: dropping diagonal disjointness (three pairs `A = B = {0}`): sum `= 3/2 > 1`.
example : (3 : ℚ) * ((Nat.choose 2 1 : ℚ)⁻¹) = 3 / 2 := by norm_num
example : ¬ ((3 : ℚ) / 2 ≤ 1) := by norm_num

-- Case 2: only skew (i<j) cross-intersection, sizes (1,1),(1,1),(1,2): sum `= 4/3 > 1`.
example :
    ((Nat.choose 2 1 : ℚ)⁻¹) + ((Nat.choose 2 1 : ℚ)⁻¹) + ((Nat.choose 3 1 : ℚ)⁻¹)
      = 4 / 3 := by norm_num
example : ¬ ((4 : ℚ) / 3 ≤ 1) := by norm_num

end RequestProject.Examples
