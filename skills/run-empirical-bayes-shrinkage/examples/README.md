# Example: `--synthetic`

From the repo root, with `ebnm` and `jsonlite` installed:

```bash
Rscript skills/run-empirical-bayes-shrinkage/scripts/shrinkage.R --synthetic
```

This draws 400 spike-and-slab normal means (seed 20261113), fits ebnm with a normal scale mixture, and checks that the posterior-mean RMSE beats both the raw observations and the complete-pooled mean, and that lfsr < 0.05 calls have a low false-sign rate. It is a usage example and a CI self-test, not a re-run of the 2026-11-13 mock-budget scout. That scout's aggregates (and the published RMSE / call counts) are locked when `methods/ebnm/original/scout_aggregates.json` is present; the teaching page is https://jgridifier.github.io/research-lab/methods-scout/2026-11-13.html#m1.

On a real file, pass a CSV with an observation column and a standard-error column (`--x`, `--s`). Do not commit raw private rows to this repo.
