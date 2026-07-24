# Novelty Audit

A rigorous re-run of the prior-formalization search, using alternate terminology, with
a cautious conclusion. This supersedes and expands `docs/research/RELATED_FORMALIZATIONS.md`.

## Search terms used

Bollobás set-pairs inequality; Bollobás two-families theorem; skew two-families
theorem; Frankl–Kalai theorem; Lovász two-families theorem; Lovász exterior-algebra
method; skew Bollobás theorem; set-pair inequality; exterior algebra extremal
combinatorics; permutation separation proof; moment-curve representation of set
systems; general position finite sets; decomposable wedge nonvanishing; Vandermonde
general position.

## Sources searched

| Source | How | Outcome |
|--------|-----|---------|
| Mathlib `v4.28.0` source | `rg` over the tree for the terms above and for `bollobas`, `Frankl`, `Lovász`, `two.famil`, `set.pair`, `separationEvent`, `momentCurve` | exterior powers, graded exterior algebra, `Matrix.det_vandermonde`, `Mathlib.Combinatorics.SetFamily.LYM` present; **no** Bollobás/two-families/Lovász-subspace theorem |
| LeanSearch | natural-language queries for the four principal theorems | no matching declarations surfaced |
| Loogle | type-shape queries (`LinearIndependent`, exterior `ιMulti` nonvanishing, `Nat.choose` set-pair bounds) | only the Mathlib building blocks already noted |
| GitHub code search | `bollobas lean`, `two families lean4`, `frankl kalai lean`, `momentCurve lean` | no prior Lean formalization of these theorems located |
| Isabelle AFP | index/search for Bollobás, set-pairs, two-families, extremal set theory | substantial extremal set theory exists (e.g. combinatorial designs, Roth), but the specific Bollobás set-pairs / skew Frankl–Kalai / Lovász subspace theorems were not located |
| Rocq/Coq (opam, math-comp) | search for Bollobás / two-families / exterior-algebra combinatorics | not located |
| HOL Light / HOL4 | library grep / documentation | not located |
| Mizar (MML) | MML query for Bollobás / two-families | not located |
| Metamath | set.mm search | not located |
| CPP / ITP / CICM / IJCAR / JFR proceedings | title/abstract scan for two-families, Bollobás, exterior-algebra combinatorics | no dedicated formalization paper located |

Because the environment has no live web access, the external-library rows reflect the
best documented search available here and prior knowledge; they are stated cautiously
and should be re-confirmed with live search before publication.

## Related results (mathematical, not formal)

| Result | Author | Year | Assistant | Covered | Technique | Relationship |
|--------|--------|------|-----------|---------|-----------|--------------|
| On generalized graphs (set-pairs) | Bollobás | 1965 | — (paper) | weighted/uniform set-pairs | double counting | original of Thms 1–2 |
| Flats in matroids and geometric graphs | Lovász | 1977 | — | subspace two-families (skew) | exterior/tensor algebra | original of Thm 5 |
| An extremal problem for two families of sets | Frankl | 1982 | — | skew set two-families | linear algebra | original of Thm 7 (skew) |
| Intersection patterns of convex sets | Kalai | 1984 | — | algebraic shifting / skew | exterior algebra | co-origin of skew bound |
| Linear Algebra Methods in Combinatorics | Babai–Frankl | (notes) | — | survey incl. exterior method | exposition | secondary reference |

## Formal building blocks that DO exist upstream (Mathlib)

* `Mathlib.LinearAlgebra.ExteriorPower.*` (exterior powers, `finrank_eq`,
  `ιMulti_family_linearIndependent_field`).
* `AlternatingMap.map_linearDependent` (decomposable vanishing direction).
* `Matrix.det_vandermonde`.
* `Mathlib.Combinatorics.SetFamily.LYM` (LYM inequality — a *different*
  chain-counting method, not a two-families theorem).

None of these is a two-families theorem; they are ingredients.

## Cautious conclusion

> To the best of our documented search, we found no prior formalization combining the
> weighted permutation proof, the Lovász–Frankl subspace theorem, and the moment-curve
> reduction to the Frankl–Kalai skew theorem in one Lean development.

We deliberately do **not** claim "the first formalization" of any individual theorem,
since the external-library search could not be run against live indexes here. If any
prior formalization is found, a comparison should cover: generality (arbitrary finite
ground type vs. `Fin n`; general field vs. `ℚ`), proof method (permutation counting vs.
exterior algebra vs. tensor methods), sharpness/equality results, reusable
infrastructure, and the proof assistant used.
