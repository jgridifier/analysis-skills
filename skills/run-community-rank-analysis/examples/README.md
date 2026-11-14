# Example: `--synthetic`

From the repo root, with `codyn` and `jsonlite` installed:

```bash
Rscript skills/run-community-rank-analysis/scripts/rank_clocks.R --synthetic
```

This builds two 8-unit, 40-time communities (seed 20261113): one sharing a common factor, one independent. It checks that the variance ratio of the co-moving set is above 1 and above a 19-draw cyclic-shift null, and that the independent set is not similarly synchronized. It also builds a four-unit share path in which A and B swap first and last rank, and checks that the swap is visible to `rank_shift`. Teaching page: https://jgridifier.github.io/research-lab/methods-scout/2026-11-12-adhoc.html#m1.

This is not a re-run of the 2026-11-12 Y-9C proxy scout (999 cyclic shifts, panel not in this repo). That scout's published aggregates are locked when `methods/codyn/original/scout_aggregates.json` is present.
