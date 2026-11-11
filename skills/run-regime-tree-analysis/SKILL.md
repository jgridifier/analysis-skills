---
name: run-regime-tree-analysis
description: Use when the question is "which combinations of conditions mark different groups or regimes, and what happens in each?" — finding readable subgroups in a cross-section (which counties, firms or cases behaved differently and why), describing state-dependent behaviour with if-then rules, or testing whether a regression's slopes depend on observed state variables (model-based trees). Not for dating breaks in time (use run-changepoint-analysis) and not as a forecaster.
---

# Run a regime / subgroup tree analysis

Conditional inference trees (ctree) split the sample on the covariate most associated with the response,
chosen by a permutation test, and stop when no test is significant. Model-based trees (MOB) fit a small model
(e.g. a regression) and split where its parameters are unstable. The output is a short list of if-then rules with
an estimate per leaf, which is the point: description you can read and argue with.

## 1. Frame the question
- **Response**: what differs across groups (a shock size, a forward change, a residual).
- **Partitioning variables**: the conditions that may define groups. Measure them *before* the response
  (pre-shock traits, lagged states) or the tree will describe the outcome with itself.
- **Data shape**: cross-section (rows exchangeable) or time series (rows dependent). This decides the null and the bootstrap.

## 2. Choose the method
| question | method | package | notes |
|---|---|---|---|
| which conditions split the response into groups? | **ctree** (start here) | R `partykit` | unbiased variable selection (no preference for many-valued splits), built-in stopping; very fast (30k rows in 0.07 s) |
| does a regression's slope depend on the state? | **MOB `lmtree` / `glmtree`** | R `partykit` | splits where slope coefficients are unstable; reports a model per leaf |
| baseline | CART `rpart` with CV pruning | R `rpart` | always run it; similar fit, more leaves, biased toward many-split variables |
| baseline | OLS / historical mean | base R | the bar a forecasting claim must clear |
| globally optimal tree | *evtree* — watchlist | R | add a row once promoted |
| clustered / panel data (random effects) | *glmertree* — watchlist | R | add a row once promoted |
| stability of the selected tree | *stablelearner* — watchlist | R | add a row once promoted |
| *(next method)* | | | one row per promoted method |

Settings that worked: `ctree_control(alpha = 0.05, minbucket = 24, maxdepth = 3)` for ~400 monthly rows;
`alpha = 0.01, minbucket = 50` for ~3,000 counties; `lmtree(minsize = 36, alpha = 0.01, bonferroni = TRUE)` for MOB.

## 3. Robustness protocol (report all of it)
1. **Stability:** bootstrap the root split (≥ 200 refits). Cross-section: case bootstrap. Time series: **block bootstrap**
   (blocks ≈ 2 years of monthly data). Report how often the root variable is chosen and the threshold's 10–90% range.
2. **Null — matched to the data shape:**
   - cross-section: permute the response; the tree should split in about `alpha` of permutations (we saw 0% and 4%);
   - **time series: circularly shift the response** (keeps its autocorrelation). ctree's permutation p-values assume
     exchangeable rows; on monthly credit data a shifted response still produced a split **60%** of the time, and MOB with
     shifted state variables split **53%** of the time. If the shift null splits often, call the tree exploratory only.
3. **Windows:** refit on split samples (e.g. pre/post 2008) and without crisis months; report whether the root changes.
4. **Baseline:** CART and OLS (cross-section: 5-fold CV R² over 10 seeds); MOB vs pooled OLS and vs OLS with the
   tree's own split as a dummy interaction (part of MOB's BIC gain is a separate error variance per leaf).
5. **Forecasting (only if asked): walk-forward** with refits on past data only and a gap equal to the forecast horizon,
   scored against the historical mean. Be honest: our ctree regime tree was descriptive but **lost to the historical mean**
   as a forecaster of 6-month credit-spread changes (OOS R² −0.31; CART −0.40, OLS −0.43).

## 4. Interpret and report
- Give each leaf a plain-language rule, its n, and the response mean/sd (or the leaf model's coefficients for MOB).
- Thresholds are estimates: quote the bootstrap range, not just the point.
- For MOB, report the root instability-test p-values for every partitioning variable, including `time`: a state variable
  beating calendar time (NFCI p < 1e-5 vs time p = 0.83 in our data) is the interesting finding, *if* it survives the shift null.

Reporting template:
```
Question / response / partitioning variables / data shape (cross-section | time series), n, period
Method: ctree | MOB (settings), partykit <ver>
Tree: <rules with n and leaf estimate>
Stability: root = <var> in <x>% of <B> (block) bootstraps; threshold range <lo–hi>; windows: <roots>
Null: <iid | circular shift> split rate <x> (alpha <a>)   Baseline: CART <..>, OLS <..>, hist mean <..>
Verdict: <clears null and baseline | exploratory only | descriptive, not predictive>
```

## 5. Scripts
- `scripts/regime_tree.R` — the protocol on a CSV:
  `Rscript scripts/regime_tree.R --csv d.csv --formula "y ~ x1 + x2" [--mode mob --formula "y ~ x | z1 + z2"] [--time-col date --gap 6] --out report.json`.
  Without `--time-col`: case bootstrap, iid null, 5-fold CV vs CART/OLS. With it: block bootstrap, circular-shift null, walk-forward vs historical mean.
  `--synthetic` runs the self-test.
- Environment: R ≥ 4.4 with `partykit`, `rpart`, `jsonlite` (pinned lock in `env/r-conda-lock.txt`).
- Evidence: `reference/evidence.md`; examples: `examples/README.md`.

## Citations
- Hothorn, T., Hornik, K. & Zeileis, A. (2006). Unbiased Recursive Partitioning: A Conditional Inference Framework. *Journal of Computational and Graphical Statistics* 15(3):651–674.
- Zeileis, A., Hothorn, T. & Hornik, K. (2008). Model-Based Recursive Partitioning. *Journal of Computational and Graphical Statistics* 17(2):492–514.
- Hothorn, T. & Zeileis, A. (2015). partykit: A Modular Toolkit for Recursive Partytioning in R. *Journal of Machine Learning Research* 16:3905–3909.
