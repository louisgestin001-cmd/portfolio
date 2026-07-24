# Dependency Audit

Module- and theorem-level dependency analysis of the project, plus checks for circular
dependencies, unnecessary imports, unused hypotheses/variables, and Mathlib
duplication.

## Module dependency graph (project-local imports)

```
                         SetPairs/Basic
                        /       |        \
        PermutationOrders   (Uniform)   SkewSetPairs
              |                 ^            |   \
        SeparationEvents        |            |    \
              |                 |            |     \
        WeightedBollobas -------+            |      \
                                             |       \
   LinearAlgebra/TriangularIndependence      |        \
   LinearAlgebra/ExteriorDecomposable        |         \
   LinearAlgebra/ExteriorMultiplication      |          \
        \        |         /                 |           \
   LinearAlgebra/TwoFamiliesSubspaces -------+            |
   LinearAlgebra/MomentCurve ----------------------------- 
                                             |
                                           Main  (imports everything + Examples)
```

Precise edges (from `import RequestProject.*` lines):

| File | Imports (project-local) |
|------|--------------------------|
| `SetPairs/Basic` | — |
| `SetPairs/PermutationOrders` | Basic |
| `SetPairs/SeparationEvents` | PermutationOrders |
| `SetPairs/WeightedBollobas` | SeparationEvents |
| `SetPairs/Uniform` | WeightedBollobas |
| `LinearAlgebra/TriangularIndependence` | — |
| `LinearAlgebra/ExteriorDecomposable` | — |
| `LinearAlgebra/ExteriorMultiplication` | — |
| `LinearAlgebra/MomentCurve` | — |
| `LinearAlgebra/TwoFamiliesSubspaces` | TriangularIndependence, ExteriorDecomposable, ExteriorMultiplication |
| `SkewSetPairs` | Basic, MomentCurve, TwoFamiliesSubspaces |
| `Examples` | Uniform |
| `Main` | all of the above + Examples |

**Two independent routes.** The counting route
(`PermutationOrders → SeparationEvents → WeightedBollobas → Uniform`) and the algebraic
route (`Triangular/Exterior*/MomentCurve → TwoFamiliesSubspaces → SkewSetPairs`) share
only `SetPairs.Basic` (the predicate API). This cleanly reflects the paper's thesis of
two separate proof technologies.

**Circular dependencies:** none. The import relation is a DAG (topological order:
Basic, PermutationOrders, SeparationEvents, WeightedBollobas, Uniform;
Triangular/Exterior*/MomentCurve, TwoFamiliesSubspaces, SkewSetPairs; Examples; Main).

## Theorem-level dependency summary

| Principal theorem | Depends on (project-local) |
|-------------------|-----------------------------|
| `weighted_bollobas` | `card_separationEvent_mul_choose`, `separationEvents_pairwiseDisjoint`←`separationEvents_disjoint`, `card_orderEnumerations` |
| `uniform_bollobas` | `weighted_bollobas` |
| `uniform_bollobas_sharp` | (Mathlib only) |
| `of_upperTriangular_maps` | (Mathlib only) |
| `lovasz_frankl_subspaces` | `of_upperTriangular_maps`, `append_wedge_ne_zero`, `append_wedge_eq_zero` (←`ιMulti_*`, `ιMulti_mul_ιMulti`, `linearIndependent_append_of_disjoint`, `not_linearIndependent_append_of_inf_ne_bot`), `exteriorPower.finrank_eq` |
| `momentCurve_linearIndependent` | (Polynomial API only) |
| `frankl_kalai_skew` | `lovasz_frankl_subspaces`, `finrank_spanMomentCurve`, `inf_spanMomentCurve_eq_bot`, `inf_spanMomentCurve_ne_bot`, `momentCurve_linearIndependent` |

`card_separationEvent_mul_choose` internally depends on `card_separationEvent_eq` ←
`fiber_card_eq`, `card_separates_toP` ← `card_separates_full` ←
`separates_val_lt`, `card_le_separates_val`.

## Unnecessary imports

Every file uses blanket `import Mathlib` rather than fine-grained Mathlib imports.
This is a deliberate project-wide convention (robust across Mathlib point releases; see
`docs/review/STYLE_REVIEW.md`). It is not an *incorrect* dependency, but for Mathlib extraction the
per-file minimal import sets must be computed (recorded in `docs/upstream/MATHLIB_PR_PLAN.md`). No
project-local import is redundant: each imported module supplies a declaration actually
referenced (verified against the theorem-level table above).

## Unused hypotheses / variables

* Automated check (`lean_minimal_hypotheses`) on `weighted_bollobas` confirms
  `hdiag` **load-bearing**. The `A B` and `hcross` binders are reported "removable"
  only as an *auto-binding artifact* (they are used — `A`,`B` in the conclusion,
  `hcross` passed to `separationEvents_pairwiseDisjoint`); dropping the explicit
  binder merely lets Lean auto-bind/re-derive them. Source inspection confirms
  genuine use of every hypothesis.
* Source inspection of all seven principal theorems: no hypothesis is unused. Notable
  points:
  - `lovasz_frankl_subspaces` uses all of `hdimV, hdimU, hdimW, hdiag, hcross`.
  - `frankl_kalai_skew` uses `hcardA, hcardB` (for the dimensions), `hdiag`
    (diagonal `⊥`), `hcross` (nontrivial off-diagonal).
  - `momentCurve_linearIndependent` uses `ht` (injectivity) and `hs` (`|s|≤d`).
* The build produces **no `unusedVariables` linter warnings**, i.e. no
  non-underscore hypothesis is left unreferenced.

## Mathlib duplication check

No project declaration re-proves a Mathlib lemma. The closest overlaps are *uses*, not
duplicates:

* `card_orderEnumerations` is a one-line specialisation of `Fintype.card_equiv`
  (kept as a named, documented API entry point; trivial).
* `ExteriorAlgebra.ιMulti_eq_zero_of_linearDependent` is literally
  `AlternatingMap.map_linearDependent` specialised — a thin, intentional re-export.
* Everything else (`of_upperTriangular_maps`, the exterior nonvanishing/concatenation
  lemmas, moment-curve independence and span lemmas) has **no** Mathlib equivalent
  (searched; see `docs/research/NOVELTY_AUDIT.md`, `docs/upstream/MATHLIB_PR_PLAN.md`).

## Refactoring performed

No structural refactor was required: the module DAG is already minimal, acyclic, and
route-separated. The only code change in this revision is a correctness fix to
`scripts/statistics.py` (sorry-token false positive) and added adversarial regression
examples; no proof or public statement was altered.
