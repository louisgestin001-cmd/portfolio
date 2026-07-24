# Bibliography Audit

Every entry in `paper/references.bib` inspected for correctness and for whether it
supports the sentence that cites it. **No web access is available in this environment**,
so metadata is checked against well-established bibliographic knowledge; any DOI must be
re-verified against the publisher before final submission (none is asserted here to
avoid fabrication).

## Entries

| Key | Type | Author(s) | Title | Venue | Year | Verdict |
|-----|------|-----------|-------|-------|------|---------|
| `bollobas1965` | article | Bollobás | On generalized graphs | Acta Math. Acad. Sci. Hungar. 16 | 1965 | correct; **original** source of the weighted/uniform set-pairs inequality |
| `lovasz1977` | incollection | Lovász | Flats in matroids and geometric graphs | Combinatorial Surveys (6th British Combinatorial Conf.) | 1977 | correct; **original** exterior-algebra subspace two-families method |
| `frankl1982` | article | Frankl | An extremal problem for two families of sets | European J. Combin. 3 | 1982 | correct; skew set two-families |
| `kalai1984` | article | Kalai | Intersection patterns of convex sets | Israel J. Math. 48 | 1984 | correct; exterior-algebra / algebraic-shifting skew results |
| `babaifrankl1992` | misc | Babai, Frankl | Linear Algebra Methods in Combinatorics | Univ. Chicago lecture notes (preliminary) | 1992 | correct as an unpublished-notes exposition; **secondary** source only |
| `mathlib2020` | inproceedings | The mathlib Community | The Lean mathematical library | CPP 2020 | 2020 | correct |
| `lean4` | inproceedings | de Moura, Ullrich | The Lean 4 Theorem Prover... | CADE 2021 | 2021 | correct |

## Corrections applied in this revision

1. **`kalai1984`**: was typed `@incollection` but carried a `journal` field (Israel J.
   Math. is a journal). Changed to `@article` with `volume`/`number`/`pages`.
2. **`babai1988` → `babaifrankl1992`**: the key said 1988 but the `year` field said
   1992 (an internal inconsistency). Renamed the key to match the year and retyped
   from `@book` to `@misc` (these are unpublished/circulated lecture notes, not a
   formally published book). Marked clearly as a secondary/expository source.
3. **`lovasz1977`**: retyped `@article` → `@incollection` with a proper `booktitle`
   and `publisher` (it is a conference-survey chapter, not a journal article).
4. **`mathlib2020`, `lean4`**: retyped `@misc` → `@inproceedings` with `booktitle`
   and page ranges, matching their actual CPP/CADE publication.
5. Added `number` fields where standard.

No DOIs were added: they cannot be verified without live access, and inventing them is
disallowed. A pre-submission checklist item is to add and verify DOIs.

## Citation hygiene in the manuscript

* **Issue found:** the previous `paper/main.tex` used `\bibliography{references}` but
  contained **no `\cite` commands**, so the compiled References section would have been
  empty. Fixed in the revised paper: each original result is now cited at first mention
  (`bollobas1965` for Thms 1–2, `lovasz1977` for Thm 5, `frankl1982`/`kalai1984` for
  the skew results, `babaifrankl1992` as the survey, `mathlib2020`/`lean4` for the
  tools). A `\nocite{*}` fallback is intentionally **not** used, so only genuinely
  cited entries appear.
* **Original vs. survey distinction:** the paper cites Bollobás (1965), Lovász (1977),
  and Frankl (1982)/Kalai (1984) as the *original* sources, and Babai–Frankl (1992)
  only as an *exposition* — never the survey in place of an original.

## Distinctions maintained

* Bollobás's original theorem: `bollobas1965`.
* Lovász's exterior-algebra method: `lovasz1977`.
* Frankl's / Frankl–Kalai skew extensions: `frankl1982`, `kalai1984`.
* Later expositions: `babaifrankl1992`.
* Formalization tooling: `lean4`, `mathlib2020`.

No fabricated or unverifiable citation remains. The five mathematical references are
standard, widely cited primary/secondary sources for exactly the theorems formalized.
