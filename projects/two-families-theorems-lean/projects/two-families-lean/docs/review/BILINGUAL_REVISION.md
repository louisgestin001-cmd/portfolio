# Bilingual portfolio revision

This revision adds a complete French version of the technical report while preserving
the English paper and all Lean proof sources.

## Changes

- Added `paper/main_fr.tex` and the compiled `paper/main_fr.pdf`.
- Attributed the portfolio report to `Louis Gestin, independent student, France` instead of the
  conference-oriented placeholder `Anonymous`.
- Clarified that the measured 133-second build uses already-cached pinned Mathlib
  artifacts; a cold reconstruction takes longer.
- Softened the Mathlib/novelty wording to match the documented limits of the search.
- Added artifact-availability paragraphs to both reports.
- Hid colored hyperlink borders and lightly improved line breaking.
- Updated `README.md`, `.gitignore`, and `scripts/build_artifact.sh` for both PDFs and
  for archive rebuilding outside a Git checkout.

## Proof integrity

No file under `RequestProject/` was modified. The theorem statements and proof terms are
identical to the original artifact.
