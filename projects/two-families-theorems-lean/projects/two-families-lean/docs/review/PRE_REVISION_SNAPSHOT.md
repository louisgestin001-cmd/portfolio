# Pre-Revision Snapshot

Recorded directly from the repository at the start of the audit. Every figure below
was produced by running the indicated command; nothing is copied from a prior report.

## Git state

| Item | Value |
|------|-------|
| Branch (`git branch --show-current`) | `main` |
| Commit (`git rev-parse HEAD`) | `32161f9f36add9afd31372e387cdf8f95eca95c3` |
| Commit subject (`git log --oneline -1`) | `Initial commit` |
| Working tree (`git status --short`) | clean (no output) at snapshot time |
| Remote | `origin` (URL configured; no remote-tracking branches are fetched in this environment) |

**Discrepancy vs. previous report.** `ARISTOTLE_SUMMARY.md` states the latest commit
was `e02aa2d` and that work was "committed and pushed to `origin/main`". The actual
local history contains a single squashed `Initial commit` (`32161f9`), and no
remote-tracking branches are visible via `git branch -r`. The working files
themselves match the described state; only the Git history has been flattened. This
audit therefore treats `32161f9` as the ground-truth starting commit and makes no
claim about a remote until a push is independently confirmed.

## Toolchain

| Item | Value | Source |
|------|-------|--------|
| Lean | `leanprover/lean4:v4.28.0` | `lean-toolchain` |
| Mathlib pin | `rev = "v4.28.0"` | `lakefile.toml` |
| Mathlib commit | `8f9d9cff6bd728b17a24e163c9402775d9e6a365` | `.lake/packages/mathlib` HEAD |
| Build system | Lake, default target `RequestProject` | `lakefile.toml` |

## Lean source files (13)

```
RequestProject/SetPairs/Basic.lean                     58
RequestProject/SetPairs/PermutationOrders.lean         26
RequestProject/SetPairs/SeparationEvents.lean         481
RequestProject/SetPairs/WeightedBollobas.lean          76
RequestProject/SetPairs/Uniform.lean                   93
RequestProject/LinearAlgebra/TriangularIndependence.lean   91
RequestProject/LinearAlgebra/ExteriorDecomposable.lean     52
RequestProject/LinearAlgebra/ExteriorMultiplication.lean   55
RequestProject/LinearAlgebra/TwoFamiliesSubspaces.lean    144
RequestProject/LinearAlgebra/MomentCurve.lean             179
RequestProject/SkewSetPairs.lean                          66
RequestProject/Examples.lean                              64
RequestProject/Main.lean                                  53
TOTAL                                                    1438
```

## Declaration counts (`scripts/statistics.py`)

| Kind | Count |
|------|-------|
| `theorem` | 37 |
| `lemma` | 0 |
| `def` | 10 |
| `abbrev` | 2 |
| `instance` | 2 |
| `structure` | 0 |
| **total declarations** | **51** |
| total lines | 1438 |
| non-blank lines | 1175 |
| import lines | 35 |

## Forbidden-token scan

`bash scripts/check_forbidden.sh` reports **no** `sorry`, `admit`, `axiom`, or
`@[implemented_by]` in `RequestProject/`. The only match is the substring
`native_decide` inside a docstring in `Examples.lean` (documentation, not a tactic
call), which the script flags as acceptable.

Direct `rg` confirms the single textual occurrence of `sorry` in the tree is the word
`sorryAx` inside a docstring in `Main.lean` (line 45: "no `sorryAx`."). There is no
actual `sorry`/`admit`/`unsafe`/`axiom`/`implemented_by` declaration anywhere.

> Note: `scripts/statistics.py` previously used a naive substring test and reported
> `lines with sorry: 1` for this docstring word. The script has been corrected during
> this revision to use a word-boundary match that excludes `sorryAx`; it now reports 0.

## Build

`lake clean` (via `rm -rf .lake/build`) followed by `lake build`:

* Result: **Build completed successfully (8039 jobs).**
* Wall-clock (measured in this environment): **133 s**.
* `Main.lean` emits, for all seven audited theorems, `depends on axioms: [propext,
  Classical.choice, Quot.sound]`.

## Regression scripts

* `python3 scripts/verify_small_cases.py` → `OVERALL: PASS`
  (weighted inequality n=2..5; uniform bound ground size ≤ 6; skew bound ground size
  ≤ 4; canonical sharpness).
* `bash scripts/check_forbidden.sh` → exit 0.

## Paper and artifact

| Item | State |
|------|-------|
| `paper/main.tex` | present, 253 lines |
| `paper/references.bib` | present, 7 entries |
| `paper/main.pdf` | present, 5 pages (`pdfinfo`) |
| `two_families_lean_artifact.zip` | present, ~120 KB |
| LaTeX toolchain | `tectonic` available at `/usr/local/bin/tectonic` |

**Discrepancy vs. `.gitignore`.** `*.pdf` and `*.zip` are git-ignored, so
`paper/main.pdf` and `two_families_lean_artifact.zip` exist on disk but are **not**
tracked by Git. They are regenerated deliverables, not version-controlled artifacts.

## Principal declarations confirmed present (by `#check` in `Main.lean`, build clean)

* `SetPairs.weighted_bollobas`
* `SetPairs.uniform_bollobas`
* `SetPairs.uniform_bollobas_sharp`
* `LinearIndependent.of_upperTriangular_maps`
* `TwoFamilies.lovasz_frankl_subspaces`
* `GeneralPosition.momentCurve_linearIndependent`
* `SetPairs.frankl_kalai_skew`

All seven elaborate and each `#print axioms` lists only `propext, Classical.choice,
Quot.sound`.
