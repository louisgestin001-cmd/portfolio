# Louis Gestin — Portfolio

French student interested in **artificial intelligence, formal mathematics, programming, and software development**.

- **Location:** France
- **Contact:** [louis@gestin.net](mailto:louis@gestin.net)
- **Current tools:** Python, Lean 4, LaTeX, Git, GitHub Actions, and AI-assisted development

This repository is the central home for my technical projects. Each project includes its own documentation, reproducibility instructions, limitations, and—when relevant—a precise statement describing how artificial intelligence was used.

[![Two-Families Lean checks](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/two-families-ci.yml/badge.svg)](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/two-families-ci.yml)
[![NG Cell Lab checks](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/ng-cell-lab-ci.yml/badge.svg)](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/ng-cell-lab-ci.yml)
[![NG-StateMin checks](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/ng-statemin-ci.yml/badge.svg)](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/ng-statemin-ci.yml)

## Projects

### NG Cell Lab

A unified PyTorch research zoo for compact recurrent and collectively modulated neural-cell laws.

**Cells currently included**

- **NG-StateMin-U1:** minimal piecewise-linear oscillatory memory;
- **NG-ShiftCompare-Mul:** shifted multiplicative recurrent comparator;
- **NG-EnergyMax-1:** energy-modulated two-frame operator;
- **NG-EnergyMax-2:** derived sparse event/extremum memory;
- **NG-LagMean-1:** rank-one delayed collective modulator.

**Highlights**

- exact equations and a common `(input, state) -> (output, next_state)` API;
- algebraic tests for memory horizon, period-two behavior, clipping, and collective-state collapse;
- normalized results with protocol identifiers to prevent unfair comparisons;
- explicit documentation of positive results, negative results, and structural failure modes;
- CI on Python 3.10 and 3.12;
- transparent distinction between user-supplied candidates and derived variants.

**Open the project:** [`projects/ng-cell-lab/`](projects/ng-cell-lab/README.md)

**Equations and diagnostics:** [`docs/CELLS.md`](projects/ng-cell-lab/docs/CELLS.md)

**Experimental results:** [`docs/RESULTS.md`](projects/ng-cell-lab/docs/RESULTS.md)

> Preliminary research: the cells are currently best viewed as specialized primitives rather than replacements for standard RNN, GRU, LSTM, SSM, or attention architectures.

The original standalone **NG-StateMin-U1** artifact remains available at [`projects/ng-statemin-u1/`](projects/ng-statemin-u1/README.md) for its initial package and benchmark history.

### Two-Families Theorems in Lean 4

A reproducible Lean 4 / Mathlib development covering classical two-families results in extremal combinatorics and linear algebra.

**Highlights**

- 13 Lean source files and 37 theorem declarations;
- two proof routes: permutation counting and exterior algebra;
- exact Python regression tests and adversarial counterexamples;
- English and French technical reports;
- semantic, dependency, bibliography, and proof audits;
- automated verification with GitHub Actions;
- detailed disclosure of substantial AI assistance throughout the workflow.

**Open the project:** [`projects/two-families-lean/`](projects/two-families-lean/README.md)

**Reports:** [English PDF](projects/two-families-lean/paper/main.pdf) · [French PDF](projects/two-families-lean/paper/main_fr.pdf)

**AI disclosure:** [`AI_USE_STATEMENT.md`](projects/two-families-lean/AI_USE_STATEMENT.md)

> This project formalizes known mathematics. It does not claim a new theorem or unaided authorship.

## Compétences présentées

- structuration et documentation de projets techniques complexes ;
- programmation en Python et formalisation vérifiée avec Lean 4 ;
- expérimentation reproductible en apprentissage automatique ;
- tests automatisés et intégration continue ;
- rédaction technique bilingue français–anglais ;
- utilisation transparente et critique des outils d'intelligence artificielle.

## Repository structure

```text
portfolio/
├── README.md
├── LICENSE
├── .github/workflows/
│   ├── ng-cell-lab-ci.yml
│   ├── ng-statemin-ci.yml
│   └── two-families-ci.yml
└── projects/
    ├── ng-cell-lab/
    │   ├── benchmarks/
    │   ├── docs/
    │   ├── results/
    │   ├── src/
    │   └── tests/
    ├── ng-statemin-u1/
    └── two-families-lean/
```

Future projects will be added under `projects/`, while this README remains the main index.

## AI transparency

Artificial intelligence is treated as a development tool, not hidden authorship. The scope of AI assistance is documented inside each relevant project. AI contributed substantially to planning, research support, code, tests, documentation, auditing, and presentation. I directed the work, selected the verification strategies and final material, and remain responsible for understanding and presenting the published claims.

## License

The source code in this portfolio is available under the [MIT License](LICENSE). Individual projects may contain their own license and attribution information. Personal texts, identity elements, logos, screenshots, and visual assets are not automatically granted for reuse unless their project states otherwise.
