# Example: `--synthetic`

From the repo root, with NumPy installed:

```bash
python skills/run-line-density-chart/scripts/line_density.py --synthetic
```

This replays the 2026-11-13 scout's gap-case construction (width 400, height 300, 50 series, 10 stopping at column 300) and checks the recorded invariants: the default path has 100 NaN columns (the reference's 0/0 behaviour); `gap_safe=True` has none, and the column sum after the stop is 40. It also checks that a full-span bundle has column sums equal to the number of series. Teaching page: https://jgridifier.github.io/research-lab/methods-scout/2026-11-13.html#m2.

Pixel-level parity against the authors' Rust reference is *not* re-run here (that needs a build of line-density-rust @ 083890c). The original parity aggregates are in `methods/denselines/original/parity_aggregates.json`.
