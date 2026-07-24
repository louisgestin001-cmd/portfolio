# Semantic audit

For each principal theorem we check the fidelity of the formal statement.

## Common checks

* **Finite index types.** `ι` carries `[Fintype ι]` in the weighted/uniform
  theorems; the skew theorems index by `Fin m`, genuinely finite.
* **`Disjoint` = empty intersection.** Diagonal disjointness is `Disjoint (A i) (B i)`,
  which for `Finset` is defeq to `A i ∩ B i = ∅`.
* **Rational denominator nonzero.** `C(|A_i|+|B_i|, |A_i|) > 0` because
  `|A_i| ≤ |A_i|+|B_i|` (`Nat.choose_pos`); used explicitly in `weighted_bollobas`.
* **Subspace intersection uses `⊓`.** The subspace theorem uses `U i ⊓ W i = ⊥`
  and `U i ⊓ W j ≠ ⊥` — actual submodule intersection, **not** `U i ≠ W i`.
* **Injective moment-curve labels.** `frankl_kalai_skew` builds `t : α → ℚ` from
  `Fintype.equivFin` and proves `Function.Injective t`.

## Direction of cross-intersection

* Weighted/uniform: `i ≠ j → (A i ∩ B j).Nonempty` (symmetric family).
* Skew (sets and subspaces): `i < j → …`. This is strictly weaker than `i ≠ j`
  and is the correct hypothesis for the skew theorems. `CrossIntersecting.toSkew`
  records the implication.

## Non-vacuity

The hypotheses are simultaneously satisfiable and the bounds are attained:

* `uniform_bollobas_sharp` exhibits, on `Fin (a+b)`, a family with `|A_S| = a`,
  `|B_S| = b`, diagonal disjointness, cross-intersection, and exactly `C(a+b,a)`
  members. So `uniform_bollobas` is tight and non-vacuous.
* For the subspace theorem, the same complement construction (coordinate subspaces
  spanned by `a`-subsets of a basis) realises `C(a+b,a)` families; the moment-curve
  bridge shows the set and subspace theorems are mutually non-vacuous.

## Edge cases

* `a = 0`, `b = 0`, `m = 0` are handled without special-casing in the exterior
  argument: empty bases give `ιMulti K 0 = 1 ≠ 0`. In `frankl_kalai_skew` the
  degenerate `d = a+b = 0` case is discharged (a cross-intersecting `i<j` pair with
  `A_i = ∅` is contradictory).
* The counting route uses `(card α)! > 0` and `C(a+b,a) > 0`, so no division by
  zero occurs.

## No contradictory-hypothesis proofs

None of the principal theorems is proved by deriving `False` from the ambient
hypotheses in the generic case; the only `exfalso` use is the genuinely degenerate
`d = 0` branch of `frankl_kalai_skew`, where the set-level cross-intersection
hypothesis is itself unsatisfiable and the bound `m ≤ 1` still holds.
