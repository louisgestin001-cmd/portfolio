# Style Review

Audit against current Mathlib conventions. Each item is classified:

* **[REQUIRED]** — must fix before a *Mathlib* submission (does not affect the
  standalone artifact's correctness);
* **[RECOMMENDED]** — cleanup improving quality;
* **[ACCEPTABLE]** — deliberate project-specific design, no change needed.

The standalone artifact builds cleanly with only the three standard axioms; none of the
items below is a soundness or correctness issue.

## Naming and namespaces — [ACCEPTABLE]

* Principal declarations use idiomatic dot-notation / namespacing:
  `LinearIndependent.of_upperTriangular_maps`, `ExteriorAlgebra.ιMulti_*`,
  `exteriorPower.ιMulti_ne_zero_of_linearIndependent`, `SetPairs.*`,
  `TwoFamilies.*`, `GeneralPosition.*`. These match Mathlib style and avoid
  collisions.
* Predicate names (`DiagonallyDisjoint`, `CrossIntersecting`,
  `SkewCrossIntersecting`) are descriptive and correctly `Prop`-valued.

## Imports — [RECOMMENDED for project / REQUIRED for Mathlib]

Every file uses the blanket `import Mathlib`.

* For the *standalone artifact* this is [ACCEPTABLE]: it is robust across Mathlib point
  releases and keeps the development legible.
* For *Mathlib extraction* it is [REQUIRED] to replace with minimal imports. The
  per-declaration minimal import sets are estimated in `docs/upstream/MATHLIB_PR_PLAN.md` (e.g.
  `TriangularIndependence` needs only `Mathlib.LinearAlgebra.LinearIndependent` +
  `Mathlib.Data.Fintype.Card`).

## `autoImplicit` — [REQUIRED for Mathlib / RECOMMENDED for project]

The project does not set `set_option autoImplicit false`, so Lean's default
(`autoImplicit true`) is in effect. Mathlib mandates `autoImplicit false`. Enabling it
project-wide would make binders like `{α ι : Type*}` explicit and is recommended before
extraction. (This default is the reason the automated hypothesis-minimizer reports the
`A B` statement binders as "removable": they are auto-bound, not unused.)

## Nonterminal `simp` — [RECOMMENDED]

`SetPairs/Uniform.lean` `uniform_bollobas_sharp` uses `simp [...]` mid-proof (e.g.
`simp [Sharp.famA, Sharp.famB]` followed by further tactics) rather than a terminal
`simp` or `simp only`. This works and is stable, but Mathlib prefers terminal `simp`
or explicit `simp only [...]` to guard against simp-set drift. Recommended to tighten
if extracted. The proofs are otherwise `simp only`-disciplined.

## Definitions vs. structures — [ACCEPTABLE]

The set-pairs predicates are plain `def ... : Prop`. Given they are used purely as
hypotheses (not bundled with data or instances), plain predicates are the right choice;
a structure would add friction without benefit.

## `Classical` usage — [ACCEPTABLE]

`classical` is invoked only where genuine case analysis / decidability of `Separates`
and finite filtering is needed. `Separates` carries an explicit `Decidable` instance
so `separationEvent` is a bona fide `Finset` (correctly marked `noncomputable` where a
choice/real-free computation is not intended). No gratuitous `Classical`.

## Coercions — [ACCEPTABLE]

The rational statements coerce `Nat.choose … : ℚ` explicitly and immediately; this is
the faithful form demanded by the specification and cannot be avoided (the bound is a
rational inequality). Coercion handling is localized (`exact_mod_cast`, `push_cast`).

## `simp`/`Fintype.card`/`finrank` consistency — [ACCEPTABLE]

Cardinalities are used consistently: `Fintype.card` for index/type counts,
`Finset.card` for set sizes, `Module.finrank` for dimensions, with explicit bridges
(`Fintype.card_coe`, `finrank_span_eq_card`). No conflation.

## `simp` attributes — [ACCEPTABLE]

Two `@[simp]` lemmas are declared (`mem_separationEvent`, `momentCurve_apply`). Both
are genuine rewrite rules pointing "toward normal form" and are safe.

## Leftover tactic debris — [checked, none]

No stray `exact?`, `apply?`, `skip`, or `sorry` remain (verified by
`scripts/check_forbidden.sh` and `rg`). `ExteriorMultiplication.lean` contains
explanatory comments describing the `List.ofFn`/`Fin.append` manipulation; these are
documentation, not debris, and are kept.

## Summary

| Item | Class |
|------|-------|
| Naming / namespaces | ACCEPTABLE |
| Blanket `import Mathlib` | RECOMMENDED (project) / REQUIRED (Mathlib) |
| `autoImplicit` default | RECOMMENDED (project) / REQUIRED (Mathlib) |
| Nonterminal `simp` in one proof | RECOMMENDED |
| Predicates as `def` | ACCEPTABLE |
| `Classical` / coercions / cardinalities / `simp` attrs | ACCEPTABLE |

**Required corrections performed in this revision:** none are required for the
standalone artifact (it is already clean and warning-free). The import/`autoImplicit`
items are deferred to the Mathlib-extraction stage and documented in
`docs/upstream/MATHLIB_PR_PLAN.md`, as changing them project-wide now would only serve a submission
that the task explicitly says not to open without authorization.
