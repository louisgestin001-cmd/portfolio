# NG-GuardedAffine-CEGIS-1

Counterexample-guided synthesis of guarded integer piecewise-affine protocol models from mixed black-box outputs.

## Capabilities

- discovers a translation coordinate basis;
- rejects guarded actions that merely resemble a basis action for one step;
- discovers bounded and unbounded coordinates;
- identifies affine maps, including singular resets;
- synthesizes axis-aligned guards from counterexamples;
- exhaustively verifies bounded transitions and safety;
- extrapolates an unbounded register far beyond the verification radius.

## Main result

On a reliable-credit protocol with saturation, retry state, fast retransmit, reset and an unbounded epoch:

- three latent coordinates recovered;
- all ten actions recovered exactly;
- eight guard counterexamples;
- deepest rule depth two;
- exact execution through a random trace of length 100,000;
- 5/5 accepted runs through 1% output noise.

This is preliminary research, not a major-discovery claim. Read [`docs/REPORT.md`](docs/REPORT.md).

## Install and test

```bash
python -m pip install -e ".[test]"
pytest -q
python benchmarks/protocol_demo.py
```
