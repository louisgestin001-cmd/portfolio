import RequestProject.SetPairs.Basic
import RequestProject.SetPairs.PermutationOrders
import RequestProject.SetPairs.SeparationEvents
import RequestProject.SetPairs.WeightedBollobas
import RequestProject.SetPairs.Uniform
import RequestProject.LinearAlgebra.TriangularIndependence
import RequestProject.LinearAlgebra.ExteriorDecomposable
import RequestProject.LinearAlgebra.ExteriorMultiplication
import RequestProject.LinearAlgebra.MomentCurve
import RequestProject.LinearAlgebra.TwoFamiliesSubspaces
import RequestProject.SkewSetPairs
import RequestProject.Examples

/-!
# Two Proof Technologies for the Two-Families Theorem

Top-level module collecting the five principal theorems of the development.

```text
Permutation counting                Vandermonde general position
        ↓                                     ↓
Weighted Bollobás                   Lovász–Frankl subspace theorem
        ↓                                     ↓
Uniform Bollobás  ← ← ← ← ← ← ← ← Frankl–Kalai skew set theorem
```

The five principal theorems:

1. `SetPairs.weighted_bollobas`
2. `SetPairs.uniform_bollobas`
3. `TwoFamilies.lovasz_frankl_subspaces`
4. `GeneralPosition.momentCurve_linearIndependent`
5. `SetPairs.frankl_kalai_skew`
-/

-- The five principal theorems (type-checked references).
#check @SetPairs.weighted_bollobas
#check @SetPairs.uniform_bollobas
#check @TwoFamilies.lovasz_frankl_subspaces
#check @GeneralPosition.momentCurve_linearIndependent
#check @SetPairs.frankl_kalai_skew

/-
Axiom audit.  All five principal theorems depend only on the standard accepted
axioms `propext`, `Classical.choice`, `Quot.sound` (no `sorryAx`).
-/
#print axioms TwoFamilies.lovasz_frankl_subspaces
#print axioms GeneralPosition.momentCurve_linearIndependent
#print axioms SetPairs.frankl_kalai_skew
#print axioms SetPairs.uniform_bollobas_sharp
#print axioms LinearIndependent.of_upperTriangular_maps
#print axioms SetPairs.weighted_bollobas
#print axioms SetPairs.uniform_bollobas
