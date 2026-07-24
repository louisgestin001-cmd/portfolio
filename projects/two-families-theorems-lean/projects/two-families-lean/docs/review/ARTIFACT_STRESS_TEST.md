# Artifact Stress Test

Simulating a skeptical artifact evaluator who reconstructs the project **only** from
`two_families_lean_artifact.zip` in a fresh directory. Exact commands and outputs below.

## Environment

* Lean pin: `leanprover/lean4:v4.28.0` (`lean-toolchain`).
* Mathlib pin: `rev = "v4.28.0"` = commit `8f9d9cff` (`lakefile.toml`).
* LaTeX: `tectonic` (for the optional paper build).

## Evaluator workflow

```bash
# 1. Extract into a fresh directory
mkdir /tmp/artifact_test && cd /tmp/artifact_test
python3 -c "import zipfile; zipfile.ZipFile('.../two_families_lean_artifact.zip').extractall('.')"

# 2. (Lean) build — see note below on Mathlib fetch
lake build

# 3. Forbidden-token scan
bash scripts/check_forbidden.sh

# 4. Exact regression tests
python3 scripts/verify_small_cases.py
python3 scripts/adversarial_checks.py     # optional, extra hypothesis checks

# 5. Statistics regeneration
python3 scripts/statistics.py

# Optional: rebuild the paper
cd paper && tectonic main.tex
```

## Results (fresh extraction, this environment)

| Step | Command | Result |
|------|---------|--------|
| Extract | `zipfile.extractall` | 49 files, full tree (`RequestProject/`, `scripts/`, `paper/`, docs, config) |
| Forbidden scan | `bash scripts/check_forbidden.sh` | exit `0` (no `sorry`/`admit`/`axiom`/`implemented_by`) |
| Regression | `python3 scripts/verify_small_cases.py` | `OVERALL: PASS` |
| Adversarial | `python3 scripts/adversarial_checks.py` | `OVERALL: PASS` |
| Statistics | `python3 scripts/statistics.py` | `declarations: 51`, `lines with sorry: 0` |
| Paper | `pdfinfo paper/main.pdf` | `Pages: 8` (PDF shipped; recompiles with `tectonic`) |
| Toolchain | `cat lean-toolchain` | `leanprover/lean4:v4.28.0` |

All non-build steps reproduce **identically** from the extracted archive.

## Note on `lake build` from a bare extraction

The archive contains the pinned `lakefile.toml`, `lake-manifest.json`, and
`lean-toolchain` but **not** the compiled Mathlib oleans (build outputs are excluded by
`.gitignore`, correctly). A from-scratch `lake build` therefore first resolves and
builds Mathlib at the pinned `v4.28.0`, which requires network access to fetch Mathlib
and a substantial compile (well beyond a few minutes; a *cold* build compiling Mathlib
is on the order of an hour or more, hardware-dependent). This was **not** re-run offline
in this environment.

What *was* verified for the build:

* The in-place project builds cleanly: `lake build` → **success, 8039 jobs, ≈133 s**
  wall-clock **with a warm Mathlib cache** (oleans already present). See
  `docs/review/PRE_REVISION_SNAPSHOT.md`.
* The extracted sources are **byte-identical** to the in-place sources
  (`diff -rq RequestProject`, `md5sum` match), so the build result is guaranteed to be
  the same given the same pinned Mathlib.

An evaluator with network access reproduces the full build with
`lake exe cache get && lake build` (fetching prebuilt Mathlib oleans) or a plain
`lake build` (compiling Mathlib).

## Duplicate-build verification (Build A vs Build B)

| Quantity | Build A (in-place) | Build B (extracted archive) | Agree? |
|----------|--------------------|-----------------------------|--------|
| Sources (`RequestProject/`, `paper/main.tex`) | — | `diff -rq` clean, `md5sum` match | yes (byte-identical) |
| Theorem/decl counts | 37 / 51 | 37 / 51 | yes |
| `lines with sorry` | 0 | 0 | yes |
| Forbidden scan | exit 0 | exit 0 | yes |
| Regression | PASS | PASS | yes |
| Adversarial | PASS | PASS | yes |
| Paper pages | 8 | 8 | yes |
| Axiom report (from source) | 3 std axioms | identical source | yes |

Because Build B's inputs are byte-identical to Build A's and the Mathlib pin is fixed,
the Lean build outcome and axiom report are guaranteed identical; only the one-time
Mathlib compilation differs by wall-clock.

## Hygiene

The archive contains no user-specific absolute paths, git credentials, `.lake` build
outputs, or private metadata (it is generated from `git ls-files` plus the PDF; see
`scripts/build_artifact.sh`). The internal handoff note `ARISTOTLE_SUMMARY.md` is
excluded. No archived document references a nonexistent file.
