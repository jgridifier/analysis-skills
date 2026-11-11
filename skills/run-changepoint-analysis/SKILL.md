---
name: run-changepoint-analysis
description: Use when the question is "when did the behaviour of this series (or set of series) change?" — finding regime breaks in time-ordered data, including breaks in volatility, correlation or distribution shape and not only in the mean; dating structural breaks before modelling; or checking whether a claimed regime shift is real. Not for forecasting the next break, and not for cross-sectional subgroups (use run-regime-tree-analysis).
---

> **DRAFT (pending approval).** The method behind this skill is recommended but awaiting Jared's approval (docs/WORKFLOW.md, Stage 4b). Use it only as a draft, and say so in your output.

# Run a change-point analysis

Change-point detection splits a time-ordered sample into segments whose joint distribution differs. It answers
"when did things change, and how?". It does not forecast, and every method assumes something about dependence
*within* a segment that real economic data usually violate, so the protocol below is mostly about not fooling yourself.

## 1. Pre-process (mandatory)
1. **Never run on persistent levels.** Rates, spreads, stress indices and prices in levels are near unit-root;
   every detector here returns many evenly spaced breaks on them. Our weekly panel in levels gave 63 breaks about
   27 weeks apart, and a stationary VAR(1) with the same persistence (spectral radius 0.997) gave 64–71: pure artifact.
   Use changes (`diff`), log changes for strictly positive series (`log` then `diff`), or returns.
2. **Standardize** each column (z-score) so no series dominates the splitting criterion.
3. **Check persistence of the transformed data**: fit a VAR(1) and read the spectral radius of its coefficient matrix.
   Weekly averages of daily data and smoothed indices (NFCI, STLFSI) stay persistent after differencing
   (our weekly changes: 0.957). **If the radius is above ~0.8, prewhiten**: rerun on VAR(1) residuals
   (`scripts/changepoint.py --prewhiten auto` does this). Daily changes (0.50) and monthly changes (0.42) did not need it.
4. Trim only gross data errors (e.g. beyond the 99.99th percentile of |change|) and say so.

## 2. Choose the method
| question | method | language / package | notes |
|---|---|---|---|
| any change in the joint distribution (variance, correlation, shape), multivariate | **changeforest, random_forest** (start here) | Rust core; `pip install changeforest` / R `changeforest` | non-parametric classifier-based likelihood ratio; near-linear in n (16k × 5 in 0.7 s) |
| same, smaller n, smoother alternatives | changeforest `knn` | same | slower (O(n²)); tended to cluster breaks in crisis periods |
| shift in the mean only | changeforest `change_in_mean`; `ruptures` Binseg/PELT `l2` | Python | **baseline**; on our changes data it found 0 breaks every time, which is itself informative |
| kernel (distributional) baseline | `ruptures` Binseg/PELT `rbf` | Python | PELT-rbf is O(n²)+; 25 s at n = 2,000 |
| fast exact segmentation with a parametric cost (mean/variance/GLM/AR) | *fastcpd* (R, C++) — **watchlist, not yet through the workflow** | R | add a row here once promoted |
| *(next method)* | | | add one row per promoted method |

Never cluster time points with k-means as a substitute: on our weekly panel it switched labels 1,529 times.

## 3. Robustness protocol (report all of it)
1. **Seeds:** rerun with 10 seeds (`Control(seed=s)`). Report only breaks that recur within ± tol in **≥ 8 of 10**
   seeds (tol: ~1 quarter, i.e. 13 weeks / 63 trading days / 3 months). The raw count moved 32–47 across seeds on one panel.
2. **iid shuffle null:** permute rows; expect 0 breaks. Necessary, not sufficient: it passed (0 breaks) on a panel
   that the next check failed.
3. **Stationary VAR(1) null:** simulate from a VAR(1) fitted to the transformed data with constant Gaussian innovations
   (no breaks by construction); count breaks over ≥ 5 simulations. If the null produces about as many breaks as the
   data, **do not report regimes**; prewhiten and redo.
4. **Baseline:** change-in-mean and a kernel Binseg with the same K; say what the main method finds that they do not.
5. **Sub-sample / drop-one:** refit on the first 70% and with each series dropped; report the share of breaks recovered.

## 4. Interpret and report
- Describe each stable segment by per-series sd, cross-correlations and mean level, not just dates.
- Name events only after the dates are fixed; don't tune settings until breaks line up with events you expected.
- Binary segmentation can merge short spikes (on monthly credit data 2008–09 and 2020 did not get their own segments).

Reporting template:
```
Data: <series, frequency, period, n>; transform: <diff/logdiff>; persistence radius <r> (prewhitened: yes/no)
Method: changeforest random_forest (bs), v<ver>; seeds 0–9; tolerance <tol>
Stable breaks (≥8/10 seeds): <k> — <dates>
Nulls: iid shuffle <counts>; VAR(1) <counts> (radius <r0>)   Baseline: change-in-mean <k0>, Binseg-rbf overlap <x>
Segments: <table of sd / corr / level per segment>
Verdict: <distinguishable from null | not distinguishable — exploratory only>
```

## 5. Scripts
- `scripts/changepoint.py` — the whole protocol on a CSV:
  `python scripts/changepoint.py --csv panel.csv --cols A,B,C --log-cols A --transform diff --prewhiten auto --tol 13 --out report.json`.
  `--synthetic` runs the self-test used in CI.
- Worked examples: `examples/README.md`; evidence: `reference/evidence.md`.

## Citations
- Londschien, M., Bühlmann, P. & Kovács, S. (2023). Random Forests for Change Point Detection. *Journal of Machine Learning Research* 24(216):1–45.
- Truong, C., Oudre, L. & Vayatis, N. (2020). Selective review of offline change point detection methods. *Signal Processing* 167 (ruptures baselines).
